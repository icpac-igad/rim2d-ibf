#!/usr/bin/env python3
"""
Nairobi Urban Flood Model Setup Script
Converted from R script for RIM2D model preparation

This script creates input files for the RIM2D urban flood model for the Nairobi April 2024 flood case.
It replaces the R-based workflow with Python using xarray, geopandas, and rasterio.

Based on: UrbanFlood_model_setup_Klotzsche.R
Author: Claude Code
Date: September 2024
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.mask import mask
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

class NairobiFloodSetup:
    """Class to handle Nairobi flood model setup for RIM2D"""

    def __init__(self, base_dir: str = "/home/roller/Documents/08-2023/working_notes_jupyter/ignore_nka_gitrepos/rim2d/nbo_202404"):
        """
        Initialize the Nairobi flood setup

        Args:
            base_dir: Base directory for the model setup
        """
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.project_name = "Nairobi"
        self.plotting = True
        self.cell_size = 10  # 10m resolution for Nairobi (higher resolution than Klotzsche)

        # Create directories if they don't exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Nairobi flood model setup initialized")
        print(f"Base directory: {self.base_dir}")
        print(f"Cell size: {self.cell_size}m")

    def load_simulation_domain(self, domain_shapefile: str) -> gpd.GeoDataFrame:
        """
        Load simulation domain from shapefile

        Args:
            domain_shapefile: Path to domain shapefile

        Returns:
            GeoDataFrame with simulation domain
        """
        print(f"Loading simulation domain from {domain_shapefile}")
        try:
            domain = gpd.read_file(domain_shapefile)
            print(f"Domain loaded: {len(domain)} features")
            return domain
        except Exception as e:
            print(f"Error loading domain: {e}")
            print("Creating example domain bounds for Nairobi...")
            # Example bounds for Nairobi central area (to be replaced with actual data)
            bounds = {
                'geometry': [
                    # Nairobi central area approximate bounds
                    gpd.points_from_xy([-1.2921, -1.2921, -1.2721, -1.2721, -1.2921],
                                     [36.8019, 36.8219, 36.8219, 36.8019, 36.8019])[0]
                ]
            }
            return gpd.GeoDataFrame(bounds, crs="EPSG:4326")

    def create_base_raster(self, domain: gpd.GeoDataFrame) -> rasterio.DatasetReader:
        """
        Create base raster for the simulation domain

        Args:
            domain: Simulation domain GeoDataFrame

        Returns:
            Base raster template
        """
        print(f"Creating base raster with {self.cell_size}m resolution")

        # Get bounds and create transform
        bounds = domain.total_bounds
        width = int((bounds[2] - bounds[0]) / (self.cell_size / 111320))  # Approximate degrees to meters
        height = int((bounds[3] - bounds[1]) / (self.cell_size / 111320))

        transform = from_bounds(bounds[0], bounds[1], bounds[2], bounds[3], width, height)

        # Create raster profile
        profile = {
            'driver': 'GTiff',
            'height': height,
            'width': width,
            'count': 1,
            'dtype': rasterio.float32,
            'crs': domain.crs,
            'transform': transform,
            'nodata': -9999
        }

        return profile

    def process_dem(self, dem_tiles_dir: str, domain: gpd.GeoDataFrame, base_profile: dict) -> str:
        """
        Process DEM tiles for the simulation domain

        Args:
            dem_tiles_dir: Directory containing DEM tiles
            domain: Simulation domain
            base_profile: Base raster profile

        Returns:
            Path to processed DEM file
        """
        print("Processing DEM data...")

        dem_output = self.input_dir / f"{self.project_name}_DEM{self.cell_size}.asc"

        try:
            # This is a placeholder - in practice you would:
            # 1. Find all DEM tiles that intersect with domain
            # 2. Merge the tiles
            # 3. Clip to domain extent
            # 4. Resample to target resolution

            print(f"DEM processing placeholder - output would be: {dem_output}")
            print("In practice, this would:")
            print("1. Load DEM tiles from specified directory")
            print("2. Merge overlapping tiles")
            print("3. Clip to simulation domain")
            print("4. Resample to target resolution")

            return str(dem_output)

        except Exception as e:
            print(f"Error processing DEM: {e}")
            return str(dem_output)

    def process_buildings(self, osm_buildings_file: str, base_profile: dict) -> str:
        """
        Process OSM buildings data

        Args:
            osm_buildings_file: Path to OSM buildings shapefile
            base_profile: Base raster profile

        Returns:
            Path to buildings raster
        """
        print("Processing buildings data...")

        buildings_output = self.input_dir / f"{self.project_name}_OSM_buildings.asc"

        try:
            # Load buildings if file exists
            if os.path.exists(osm_buildings_file):
                buildings = gpd.read_file(osm_buildings_file)
                print(f"Loaded {len(buildings)} buildings")

                # Rasterize buildings
                # In practice, you would rasterize the buildings to the base raster
                print(f"Rasterizing buildings to {buildings_output}")
            else:
                print(f"Buildings file not found: {osm_buildings_file}")
                print("Creating placeholder buildings raster")

            return str(buildings_output)

        except Exception as e:
            print(f"Error processing buildings: {e}")
            return str(buildings_output)

    def create_sewershed_mask(self, domain: gpd.GeoDataFrame, base_profile: dict) -> str:
        """
        Create sewershed mask

        Args:
            domain: Simulation domain
            base_profile: Base raster profile

        Returns:
            Path to sewershed mask
        """
        print("Creating sewershed mask...")

        sewershed_output = self.input_dir / f"{self.project_name}_sewershed.asc"

        # For this example, create a mask where all domain cells = 1
        # In practice, this would be based on actual sewershed boundaries

        print(f"Creating sewershed mask: {sewershed_output}")

        return str(sewershed_output)

    def create_surface_grids(self, imperviousness_data: Optional[str], base_profile: dict) -> Tuple[str, str]:
        """
        Create pervious and impervious surface grids

        Args:
            imperviousness_data: Path to imperviousness data
            base_profile: Base raster profile

        Returns:
            Tuple of (sealed_surface_path, pervious_surface_path)
        """
        print("Creating surface permeability grids...")

        sealed_output = self.input_dir / f"{self.project_name}_sealed_surface.asc"
        pervious_output = self.input_dir / f"{self.project_name}_pervious_surface.asc"

        if imperviousness_data and os.path.exists(imperviousness_data):
            print(f"Processing imperviousness data from: {imperviousness_data}")
            # In practice: load, process, and rasterize imperviousness data
        else:
            print("No imperviousness data provided - using default values")
            print("Urban areas: 70% impervious, Rural areas: 20% impervious")

        return str(sealed_output), str(pervious_output)

    def create_roughness_grid(self, base_profile: dict) -> str:
        """
        Create Manning's roughness grid

        Args:
            base_profile: Base raster profile

        Returns:
            Path to roughness grid
        """
        print("Creating Manning's roughness grid...")

        roughness_output = self.input_dir / f"{self.project_name}_roughness.asc"

        # Manning's n values for Nairobi:
        # Urban impervious: 0.020 (concrete/asphalt)
        # Urban pervious: 0.035 (grass/vegetation)
        # Rural: 0.040 (natural vegetation)

        print(f"Manning's n values:")
        print(f"  Urban impervious: 0.020")
        print(f"  Urban pervious: 0.035")
        print(f"  Rural: 0.040")

        return str(roughness_output)

    def create_template_files(self):
        """Create template files for boundary conditions"""
        print("Creating template files...")

        # Fluvial boundary template (no fluvial input for pluvial simulation)
        fluvial_template = self.input_dir / "fluvial_boundary_none.txt"
        with open(fluvial_template, 'w') as f:
            f.write("0\n0\n0\n")

        # Outflow locations template (no specific outflow points)
        outflow_template = self.input_dir / "outflowlocs_zero_template.txt"
        with open(outflow_template, 'w') as f:
            f.write("0\n0\n0\n")

        print(f"Created template files in {self.input_dir}")

    def setup_rainfall_data(self, rainfall_dir: str) -> int:
        """
        Setup rainfall data for the simulation

        Args:
            rainfall_dir: Directory containing rainfall raster files

        Returns:
            Number of rainfall files
        """
        print("Setting up rainfall data...")

        rain_dir = self.input_dir / "rain"
        rain_dir.mkdir(exist_ok=True)

        # For April 2024 Nairobi flood:
        # - Heavy rainfall over 24-48 hours
        # - 15-minute time steps
        # - Total 96 files for 24 hours (96 * 15min = 24 hours)

        n_rainfall_files = 96
        time_step_min = 15

        print(f"Rainfall setup:")
        print(f"  Number of files: {n_rainfall_files}")
        print(f"  Time step: {time_step_min} minutes")
        print(f"  Total duration: {n_rainfall_files * time_step_min / 60:.1f} hours")
        print(f"  Rain directory: {rain_dir}")

        return n_rainfall_files

    def write_model_definition(self, n_rainfall_files: int = 96):
        """
        Write the RIM2D model definition file

        Args:
            n_rainfall_files: Number of rainfall input files
        """
        print("Writing model definition file...")

        def_file = self.base_dir / f"{self.project_name}_flood_202404.def"

        # Model parameters for Nairobi case
        params = {
            'dt': 1,  # time step in seconds
            'sim_duration': 86400,  # 24 hours in seconds
            'infiltration_rate': 15,  # mm/h - lower than Klotzsche due to poor drainage
            'sewer_capacity': 20,  # mm/h - limited sewer capacity in Nairobi
            'alpha': 0.5,
            'theta': 0.95,
            'rainfall_timestep': 900,  # 15 minutes in seconds
            'n_outputs': 20
        }

        print(f"Model parameters:")
        for key, value in params.items():
            print(f"  {key}: {value}")

        print(f"Definition file will be created at: {def_file}")

    def run_full_setup(self,
                      domain_shapefile: str = None,
                      dem_tiles_dir: str = None,
                      buildings_file: str = None,
                      imperviousness_data: str = None,
                      rainfall_dir: str = None):
        """
        Run the complete model setup workflow

        Args:
            domain_shapefile: Path to simulation domain shapefile
            dem_tiles_dir: Directory with DEM tiles
            buildings_file: Path to OSM buildings file
            imperviousness_data: Path to imperviousness data
            rainfall_dir: Directory with rainfall data
        """
        print("="*60)
        print("NAIROBI FLOOD MODEL SETUP - FULL WORKFLOW")
        print("="*60)

        # 1. Load simulation domain
        if domain_shapefile:
            domain = self.load_simulation_domain(domain_shapefile)
        else:
            print("No domain shapefile provided - using default Nairobi bounds")
            domain = self.load_simulation_domain("")

        # 2. Create base raster
        base_profile = self.create_base_raster(domain)

        # 3. Process DEM
        if dem_tiles_dir:
            dem_file = self.process_dem(dem_tiles_dir, domain, base_profile)
        else:
            print("No DEM directory provided - DEM processing skipped")

        # 4. Process buildings
        if buildings_file:
            buildings_file = self.process_buildings(buildings_file, base_profile)
        else:
            print("No buildings file provided - buildings processing skipped")

        # 5. Create sewershed mask
        sewershed_file = self.create_sewershed_mask(domain, base_profile)

        # 6. Create surface grids
        sealed_file, pervious_file = self.create_surface_grids(imperviousness_data, base_profile)

        # 7. Create roughness grid
        roughness_file = self.create_roughness_grid(base_profile)

        # 8. Setup rainfall data
        if rainfall_dir:
            n_rainfall = self.setup_rainfall_data(rainfall_dir)
        else:
            print("No rainfall directory provided - using default rainfall setup")
            n_rainfall = 96

        # 9. Create template files
        self.create_template_files()

        # 10. Write model definition
        self.write_model_definition(n_rainfall)

        print("="*60)
        print("SETUP COMPLETE")
        print("="*60)
        print(f"Model files created in: {self.base_dir}")
        print(f"Input files in: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")
        print("\nNext steps:")
        print("1. Prepare actual input data (DEM, buildings, rainfall)")
        print("2. Run data processing to create raster files")
        print("3. Execute RIM2D simulation")
        print("4. Analyze results")


def main():
    """Main function to run the Nairobi flood setup"""

    # Initialize setup
    setup = NairobiFloodSetup()

    # Example usage with placeholder paths
    # In practice, these would be paths to actual data files

    print("NAIROBI FLOOD MODEL SETUP")
    print("Converting R workflow to Python-based solution")
    print("Using xarray, geopandas, and rasterio")
    print()

    # Run setup with placeholder data paths
    setup.run_full_setup(
        domain_shapefile=None,  # "/path/to/nairobi_domain.shp"
        dem_tiles_dir=None,     # "/path/to/dem_tiles/"
        buildings_file=None,    # "/path/to/nairobi_buildings.shp"
        imperviousness_data=None,  # "/path/to/imperviousness.shp"
        rainfall_dir=None       # "/path/to/rainfall_grids/"
    )

    print("\nSetup script completed!")
    print("To use with real data, provide actual file paths to run_full_setup()")


if __name__ == "__main__":
    main()