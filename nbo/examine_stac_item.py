#!/usr/bin/env python3
"""
Examine a STAC item from COP-DEM collection to understand asset structure.
"""

import pystac_client
from pystac_client import Client

# STAC API endpoint for Copernicus Dataspace
STAC_API_URL = "https://catalogue.dataspace.copernicus.eu/stac"
COLLECTION_ID = "COP-DEM"

# Nairobi extent coordinates
NBO_EXTENT = {
    'lat_min': -1.402004,
    'lon_min': 36.6,
    'lat_max': -1.098036,
    'lon_max': 37.1
}

def examine_stac_item():
    """Examine the first STAC item to understand asset structure."""
    try:
        # Create STAC client
        catalog = Client.open(STAC_API_URL)
        print(f"Connected to STAC API: {STAC_API_URL}")

        # Create bbox from NBO extent
        bbox = [
            NBO_EXTENT['lon_min'],
            NBO_EXTENT['lat_min'],
            NBO_EXTENT['lon_max'],
            NBO_EXTENT['lat_max']
        ]

        # Search for items
        search = catalog.search(
            collections=[COLLECTION_ID],
            bbox=bbox
        )

        items = list(search.items())
        print(f"Found {len(items)} DEM tiles")

        if items:
            item = items[0]
            print(f"\nExamining first item: {item.id}")
            print(f"Item properties:")
            for key, value in item.properties.items():
                print(f"  {key}: {value}")

            print(f"\nItem assets ({len(item.assets)} total):")
            for asset_key, asset in item.assets.items():
                print(f"  Asset key: {asset_key}")
                print(f"    Title: {asset.title}")
                print(f"    Type: {asset.media_type}")
                print(f"    Href: {asset.href[:100]}...")
                if hasattr(asset, 'roles'):
                    print(f"    Roles: {asset.roles}")
                print()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    examine_stac_item()