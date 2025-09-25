#!/usr/bin/env python3
"""
Download DEM data as separate tiles instead of merging them.

This script divides the extent into smaller 0.5-degree tiles and downloads each separately
to avoid GDAL merge issues and ensure complete coverage.
"""

import os
import rasterio
import pystac_client
from pystac_client import Client
import numpy as np
from typing import List, Tuple, Optional
import logging
import requests
import math

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 36.6, -1.402004, 37.1, -1.098036
# Nairobi extent coordinates
NBO_EXTENT = {
    'lat_min': -1.402004,
    'lon_min': 36.6,
    'lat_max': -1.098036,
    'lon_max': 37.1
}

# Tile size (0.5 degrees as requested)
TILE_SIZE = 0.5

# Alternative STAC APIs with DEM data
STAC_ENDPOINTS = [
    {
        'name': 'Microsoft Planetary Computer',
        'url': 'https://planetarycomputer.microsoft.com/api/stac/v1',
        'collections': ['cop-dem-glo-30'],  # Copernicus DEM 30m
        'modifier': 'planetary_computer'
    },
    {
        'name': 'Element84 Earth Search',
        'url': 'https://earth-search.aws.element84.com/v1',
        'collections': ['cop-dem-glo-30'],
        'modifier': None
    }
]

def try_planetary_computer_auth():
    """Try to import and use planetary computer authentication."""
    try:
        import planetary_computer
        return planetary_computer.sign_inplace
    except ImportError:
        logger.warning("planetary_computer library not available. Install with: pip install planetary-computer")
        return None

def generate_tile_bboxes(extent: dict, tile_size: float) -> List[Tuple[float, float, float, float, str]]:
    """
    Generate smaller bounding boxes from the main extent.

    Args:
        extent: Dictionary with lat_min, lon_min, lat_max, lon_max
        tile_size: Size of each tile in degrees

    Returns:
        List of tuples (lon_min, lat_min, lon_max, lat_max, tile_name)
    """
    tiles = []

    # Calculate number of tiles needed
    lon_range = extent['lon_max'] - extent['lon_min']
    lat_range = extent['lat_max'] - extent['lat_min']

    lon_tiles = math.ceil(lon_range / tile_size)
    lat_tiles = math.ceil(lat_range / tile_size)

    logger.info(f"Creating {lon_tiles}x{lat_tiles} = {lon_tiles * lat_tiles} tiles of {tile_size}° each")

    for i in range(lon_tiles):
        for j in range(lat_tiles):
            # Calculate tile boundaries
            lon_min = extent['lon_min'] + i * tile_size
            lon_max = min(extent['lon_max'], lon_min + tile_size)
            lat_min = extent['lat_min'] + j * tile_size
            lat_max = min(extent['lat_max'], lat_min + tile_size)

            # Create tile name
            tile_name = f"nairobi_dem_tile_{i:02d}_{j:02d}"

            tiles.append((lon_min, lat_min, lon_max, lat_max, tile_name))
            logger.info(f"Tile {tile_name}: [{lon_min:.3f}, {lat_min:.3f}, {lon_max:.3f}, {lat_max:.3f}]")

    return tiles

def search_dem_tiles_for_bbox(bbox: List[float]) -> Tuple[List, str]:
    """
    Search for DEM tiles for a specific bounding box.

    Args:
        bbox: Bounding box as [lon_min, lat_min, lon_max, lat_max]

    Returns:
        Tuple of (items list, API name that worked)
    """
    for endpoint in STAC_ENDPOINTS:
        try:
            modifier = None
            if endpoint['modifier'] == 'planetary_computer':
                modifier = try_planetary_computer_auth()
                if modifier is None:
                    continue

            # Create STAC client
            catalog = Client.open(endpoint['url'], modifier=modifier)

            # Try each collection
            for collection_id in endpoint['collections']:
                try:
                    search = catalog.search(
                        collections=[collection_id],
                        bbox=bbox
                    )

                    items = list(search.items())
                    if items:
                        return items, f"{endpoint['name']} - {collection_id}"

                except Exception as e:
                    logger.warning(f"Error searching {collection_id}: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error with {endpoint['name']}: {e}")
            continue

    return [], "No API worked"

def download_dem_tile(items: List, output_path: str, bbox: List[float], tile_name: str) -> bool:
    """
    Download DEM data for a single tile without merging.

    Args:
        items: List of STAC items
        output_path: Path to save the DEM tile
        bbox: Bounding box for clipping
        tile_name: Name of the tile for logging

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing {tile_name} with {len(items)} STAC items")

        # Process each item and find the best one
        best_data = None
        best_profile = None
        best_coverage = 0

        for i, item in enumerate(items):
            # Find DEM asset
            dem_asset = None
            possible_asset_names = ['data', 'dem', 'elevation', 'PRODUCT', 'tif', 'cog']

            # Try exact matches first
            for asset_name in possible_asset_names:
                if asset_name in item.assets:
                    dem_asset = item.assets[asset_name]
                    break

            # Try partial matches
            if not dem_asset:
                for asset_key, asset in item.assets.items():
                    if (asset.media_type and
                        ('tiff' in asset.media_type.lower() or 'cog' in asset.media_type.lower()) and
                        'tif' in asset.href.lower()):
                        dem_asset = asset
                        break

            if not dem_asset:
                logger.warning(f"No DEM asset found in item {item.id}")
                continue

            try:
                # Test accessibility
                response = requests.head(dem_asset.href, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Cannot access asset (HTTP {response.status_code}): {item.id}")
                    continue

                # Open and process the data
                with rasterio.open(dem_asset.href) as src:
                    # Check intersection with our bbox
                    tile_bounds = src.bounds
                    if (tile_bounds.right <= bbox[0] or tile_bounds.left >= bbox[2] or
                        tile_bounds.top <= bbox[1] or tile_bounds.bottom >= bbox[3]):
                        logger.warning(f"Item {item.id} does not intersect with tile bbox")
                        continue

                    # Calculate coverage
                    overlap_area = (
                        min(tile_bounds.right, bbox[2]) - max(tile_bounds.left, bbox[0])
                    ) * (
                        min(tile_bounds.top, bbox[3]) - max(tile_bounds.bottom, bbox[1])
                    )

                    tile_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    coverage = overlap_area / tile_area

                    logger.info(f"Item {item.id} covers {coverage:.1%} of tile {tile_name}")

                    if coverage > best_coverage:
                        try:
                            # Read the windowed data
                            window = rasterio.windows.from_bounds(
                                bbox[0], bbox[1], bbox[2], bbox[3],
                                src.transform
                            )

                            data = src.read(1, window=window)
                            transform = src.window_transform(window)

                            if data.size > 0:
                                profile = src.profile.copy()
                                profile.update({
                                    'height': data.shape[0],
                                    'width': data.shape[1],
                                    'transform': transform,
                                    'compress': 'lzw',
                                    'tiled': True,
                                    'blockxsize': 512,
                                    'blockysize': 512
                                })

                                best_data = data
                                best_profile = profile
                                best_coverage = coverage
                                logger.info(f"Found better data with {coverage:.1%} coverage")

                        except Exception as e:
                            logger.warning(f"Error reading windowed data from {item.id}: {e}")
                            continue

            except Exception as e:
                logger.warning(f"Error processing item {item.id}: {e}")
                continue

        # Save the best data found
        if best_data is not None and best_profile is not None:
            with rasterio.open(output_path, 'w', **best_profile) as dst:
                dst.write(best_data, 1)

            logger.info(f"Successfully saved {tile_name} to {output_path}")
            logger.info(f"Tile shape: {best_data.shape}, Coverage: {best_coverage:.1%}")
            return True
        else:
            logger.warning(f"No valid data found for {tile_name}")
            return False

    except Exception as e:
        logger.error(f"Error downloading tile {tile_name}: {e}")
        return False

def main():
    """Main function to download DEM tiles for Nairobi region."""

    logger.info(f"Downloading DEM data for Nairobi extent: {NBO_EXTENT}")
    logger.info(f"Using tile size: {TILE_SIZE} degrees")

    # Generate tile bounding boxes
    tile_bboxes = generate_tile_bboxes(NBO_EXTENT, TILE_SIZE)

    # Create output directory
    output_dir = "dem_tiles"
    os.makedirs(output_dir, exist_ok=True)

    successful_tiles = 0
    failed_tiles = 0

    # Process each tile
    for lon_min, lat_min, lon_max, lat_max, tile_name in tile_bboxes:
        bbox = [lon_min, lat_min, lon_max, lat_max]
        output_path = os.path.join(output_dir, f"{tile_name}.tif")

        logger.info(f"\n--- Processing {tile_name} ---")
        logger.info(f"Bbox: [{lon_min:.6f}, {lat_min:.6f}, {lon_max:.6f}, {lat_max:.6f}]")

        try:
            # Search for DEM data for this tile
            items, api_name = search_dem_tiles_for_bbox(bbox)

            if not items:
                logger.warning(f"No DEM data found for {tile_name}")
                failed_tiles += 1
                continue

            logger.info(f"Found {len(items)} items using {api_name}")

            # Download the tile
            success = download_dem_tile(items, output_path, bbox, tile_name)

            if success:
                successful_tiles += 1

                # Print tile summary
                with rasterio.open(output_path) as src:
                    data = src.read(1)
                    logger.info(f"Tile bounds: {src.bounds}")
                    logger.info(f"Tile shape: {src.shape}")
                    logger.info(f"Elevation range: {np.nanmin(data):.1f} to {np.nanmax(data):.1f} meters")
            else:
                failed_tiles += 1

        except Exception as e:
            logger.error(f"Failed to process {tile_name}: {e}")
            failed_tiles += 1

    # Summary
    total_tiles = len(tile_bboxes)
    logger.info(f"\n--- SUMMARY ---")
    logger.info(f"Total tiles: {total_tiles}")
    logger.info(f"Successful: {successful_tiles}")
    logger.info(f"Failed: {failed_tiles}")
    logger.info(f"Success rate: {successful_tiles/total_tiles:.1%}")

    if successful_tiles > 0:
        logger.info(f"DEM tiles saved in: {output_dir}/")
        logger.info("You can now load individual tiles in QGIS or merge them manually if needed")
    else:
        logger.error("No tiles were successfully downloaded")

if __name__ == "__main__":
    main()
