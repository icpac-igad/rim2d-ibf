#!/usr/bin/env python3
"""
DEM to ASC Converter with Building Footprint Overlay
Handles requirements for lines 51 and 56 from readme.md:
- Line 56: Convert DEM TIF to ASC format
- Line 51: Create DEM with buildings as NoData values
"""

import os
import sys
import numpy as np
import json
from osgeo import gdal, ogr, osr
import time

class DEMProcessor:
    def __init__(self, dem_tile_path, buildings_geojson_path, output_dir="input"):
        """
        Initialize DEM processor

        Args:
            dem_tile_path: Path to DEM TIF file
            buildings_geojson_path: Path to building footprint GeoJSON
            output_dir: Output directory for ASC files
        """
        self.dem_tile_path = dem_tile_path
        self.buildings_geojson_path = buildings_geojson_path
        self.output_dir = output_dir

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def load_dem_info(self):
        """Load DEM file information"""
        print("Loading DEM information...")
        dataset = gdal.Open(self.dem_tile_path)
        if not dataset:
            raise ValueError(f"Cannot open DEM file: {self.dem_tile_path}")

        # Get geotransform and projection
        self.geotransform = dataset.GetGeoTransform()
        self.projection = dataset.GetProjection()
        self.dem_array = dataset.GetRasterBand(1).ReadAsArray()
        self.nodata = dataset.GetRasterBand(1).GetNoDataValue()

        # Get dimensions
        self.width = dataset.RasterXSize
        self.height = dataset.RasterYSize

        print(f"DEM dimensions: {self.width} x {self.height}")
        print(f"DEM bounds: {self.get_bounds()}")
        print(f"Pixel size: {abs(self.geotransform[1]):.6f} degrees")

        dataset = None  # Close dataset

    def get_bounds(self):
        """Get geographic bounds of DEM"""
        minx = self.geotransform[0]
        maxy = self.geotransform[3]
        maxx = minx + self.width * self.geotransform[1]
        miny = maxy + self.height * self.geotransform[5]
        return (minx, miny, maxx, maxy)

    def convert_dem_to_asc(self, output_filename="Nairobi_DEM.asc"):
        """Convert DEM TIF to ASC format (Line 56 requirement)"""
        print(f"Converting DEM to ASC format: {output_filename}")

        output_path = os.path.join(self.output_dir, output_filename)

        # Use GDAL translate for reliable conversion
        options = gdal.TranslateOptions(
            format='AAIGrid',
            outputType=gdal.GDT_Float32,
            noData=-9999
        )

        gdal.Translate(output_path, self.dem_tile_path, options=options)
        print(f"Basic DEM ASC file created: {output_path}")
        return output_path

    def rasterize_buildings_chunked(self, chunk_size=10000):
        """
        Efficiently rasterize building footprints using chunked processing
        Handles large GeoJSON files (1.4M+ polygons)
        """
        print(f"Rasterizing {self.buildings_geojson_path} in chunks of {chunk_size}...")

        # Create output raster for buildings
        buildings_raster = np.zeros((self.height, self.width), dtype=np.uint8)

        # Read GeoJSON in chunks to manage memory
        with open(self.buildings_geojson_path, 'r') as f:
            geojson_data = json.load(f)

        total_features = len(geojson_data['features'])
        print(f"Total building polygons: {total_features}")

        # Process in chunks
        processed = 0
        for start_idx in range(0, total_features, chunk_size):
            end_idx = min(start_idx + chunk_size, total_features)
            chunk_features = geojson_data['features'][start_idx:end_idx]

            print(f"Processing chunk {start_idx//chunk_size + 1}/{(total_features-1)//chunk_size + 1} "
                  f"({end_idx - start_idx} polygons)")

            # Create temporary GeoJSON for this chunk
            chunk_geojson = {
                'type': 'FeatureCollection',
                'features': chunk_features
            }

            # Rasterize this chunk
            self._rasterize_chunk(chunk_geojson, buildings_raster)
            processed += (end_idx - start_idx)

            if processed % (chunk_size * 5) == 0:
                print(f"Progress: {processed}/{total_features} polygons processed")

        print(f"Building rasterization complete. Buildings found in {np.sum(buildings_raster)} pixels")
        return buildings_raster

    def _rasterize_chunk(self, chunk_geojson, output_array):
        """Rasterize a chunk of building polygons"""
        # Create memory dataset for this chunk
        mem_driver = ogr.GetDriverByName('Memory')
        mem_ds = mem_driver.CreateDataSource('memData')

        # Create layer
        srs = osr.SpatialReference()
        srs.ImportFromWkt(self.projection)
        layer = mem_ds.CreateLayer('buildings', srs, ogr.wkbPolygon)

        # Add features from chunk
        for feature_data in chunk_geojson['features']:
            feature = ogr.Feature(layer.GetLayerDefn())

            # Create geometry from GeoJSON
            geom_json = json.dumps(feature_data['geometry'])
            geom = ogr.CreateGeometryFromJson(geom_json)
            feature.SetGeometry(geom)

            layer.CreateFeature(feature)
            feature = None

        # Create raster for this chunk
        mem_raster_driver = gdal.GetDriverByName('MEM')
        mem_raster = mem_raster_driver.Create('', self.width, self.height, 1, gdal.GDT_Byte)
        mem_raster.SetGeoTransform(self.geotransform)
        mem_raster.SetProjection(self.projection)

        # Rasterize
        gdal.RasterizeLayer(mem_raster, [1], layer, burn_values=[1])

        # Read result and add to main array
        chunk_result = mem_raster.GetRasterBand(1).ReadAsArray()
        output_array[chunk_result == 1] = 1

        # Cleanup
        mem_ds = None
        mem_raster = None

    def create_dem_with_buildings_nodata(self, output_filename="Nairobi_DEM_housesnodata.asc"):
        """
        Create DEM with buildings as NoData (Line 51 requirement)
        This is the main output needed for RIM2D simulation
        """
        print(f"Creating DEM with buildings as NoData: {output_filename}")

        # Rasterize buildings
        buildings_mask = self.rasterize_buildings_chunked()

        # Create output DEM array
        output_dem = self.dem_array.copy().astype(np.float32)

        # Set building pixels to NoData (-9999)
        building_pixels = buildings_mask == 1
        output_dem[building_pixels] = -9999

        print(f"Set {np.sum(building_pixels)} pixels to NoData (buildings)")

        # Write ASC file
        output_path = os.path.join(self.output_dir, output_filename)
        self._write_asc_file(output_dem, output_path, nodata_value=-9999)

        print(f"DEM with buildings as NoData created: {output_path}")
        return output_path

    def _write_asc_file(self, array, output_path, nodata_value=-9999):
        """Write numpy array to ESRI ASCII format"""
        minx, miny, maxx, maxy = self.get_bounds()
        cellsize = abs(self.geotransform[1])

        with open(output_path, 'w') as f:
            # Write header
            f.write(f"ncols {self.width}\n")
            f.write(f"nrows {self.height}\n")
            f.write(f"xllcorner {minx}\n")
            f.write(f"yllcorner {miny}\n")
            f.write(f"cellsize {cellsize}\n")
            f.write(f"NODATA_value {nodata_value}\n")

            # Write data (flip vertically for ASC format)
            for row in array:
                f.write(' '.join([str(val) for val in row]) + '\n')

    def create_building_footprint_raster(self, output_filename="Nairobi_OSM_buildings.asc"):
        """Create building footprint raster (1 = building, 0 = no building)"""
        print(f"Creating building footprint raster: {output_filename}")

        buildings_mask = self.rasterize_buildings_chunked()

        output_path = os.path.join(self.output_dir, output_filename)
        self._write_asc_file(buildings_mask.astype(np.float32), output_path, nodata_value=-9999)

        print(f"Building footprint raster created: {output_path}")
        return output_path

    def process_all(self):
        """Process all requirements"""
        print("=== DEM to ASC Processing Started ===")
        start_time = time.time()

        # Load DEM information
        self.load_dem_info()

        # 1. Basic DEM to ASC conversion (Line 56)
        basic_asc = self.convert_dem_to_asc("Nairobi_DEM.asc")

        # 2. DEM with buildings as NoData (Line 51) - Main requirement
        buildings_nodata_asc = self.create_dem_with_buildings_nodata("Nairobi_DEM_housesnodata.asc")

        # 3. Optional: Building footprint raster
        buildings_raster = self.create_building_footprint_raster("Nairobi_OSM_buildings.asc")

        elapsed_time = time.time() - start_time
        print(f"\n=== Processing Complete in {elapsed_time:.1f} seconds ===")
        print(f"Files created in '{self.output_dir}' directory:")
        print(f"- {os.path.basename(basic_asc)} (basic DEM)")
        print(f"- {os.path.basename(buildings_nodata_asc)} (DEM with buildings as NoData - for RIM2D)")
        print(f"- {os.path.basename(buildings_raster)} (building footprints)")

        return {
            'basic_dem': basic_asc,
            'dem_buildings_nodata': buildings_nodata_asc,
            'building_footprints': buildings_raster
        }

def main():
    """Main execution function"""
    # Configuration
    dem_tile = "dem_tiles/nairobi_dem_tile_00_00.tif"
    buildings_geojson = "nbo.geojson"
    output_dir = "input"

    # Verify input files exist
    if not os.path.exists(dem_tile):
        print(f"Error: DEM file not found: {dem_tile}")
        sys.exit(1)

    if not os.path.exists(buildings_geojson):
        print(f"Error: Building footprint file not found: {buildings_geojson}")
        sys.exit(1)

    # Process
    processor = DEMProcessor(dem_tile, buildings_geojson, output_dir)
    results = processor.process_all()

    print(f"\n✅ All ASC files ready for RIM2D simulation!")
    print(f"Main file for model: {os.path.basename(results['dem_buildings_nodata'])}")

if __name__ == "__main__":
    main()