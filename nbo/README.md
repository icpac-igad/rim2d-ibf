# Nairobi April 2024 Flood Model

This is a RIM2D urban flood model setup for simulating the April 2024 flood event in Nairobi, Kenya. The model is adapted from the Klotzsche pluvial example and uses Python-based preprocessing instead of R.

## Model Overview

- **Event**: Nairobi flood, April 2024
- **Model Type**: Urban pluvial flooding simulation
- **Resolution**: 10m grid cells
- **Duration**: 24 hours (86,400 seconds)
- **Precipitation**: 15-minute time steps (96 rainfall files)
- **Study Area**: Nairobi central urban area

## Model Files

- `Nairobi_flood_202404.def`: Model definition file for the April 2024 flood event
- `nairobi_flood_setup.py`: Python script for model preprocessing (replaces R workflow)
- `readme.md`: This documentation file
- `input/`: Directory containing model input files (to be populated)
- `output/`: Directory for simulation results

## Model Parameters

### Hydraulic Parameters
- **Time step**: 1 second (stable for urban conditions)
- **Simulation duration**: 86,400 seconds (24 hours)
- **Alpha value**: 0.5 (adaptive time step control)
- **Theta value**: 0.95 (numerical diffusion control)

### Urban Hydrology Parameters
- **Infiltration rate**: 15 mm/h (accounting for poor drainage in urban Nairobi)
- **Sewer capacity**: 20 mm/h (limited sewer infrastructure)
- **Sewer activation threshold**: 0.002 m water depth

### Precipitation Setup
- **Number of rainfall files**: 96
- **Time step between files**: 900 seconds (15 minutes)
- **Rainfall start time**: 0 seconds (simulation start)
- **Base file name**: `./input/rain/Nairobi_202404_t`

### Output Configuration
- **Number of output maps**: 20
- **Output intervals**: Every 3600 seconds (hourly) for first 20 hours
- **Output base name**: `./output/Nairobi_202404_flood_`

## Required Input Files

The following input files need to be prepared using the Python setup script or manually:

### Essential Raster Files (ESRI ASCII format)
1. **`Nairobi_DEM_housesnodata.asc`** - Digital Elevation Model with buildings as NoData
2. **`Nairobi_sewershed.asc`** - Sewershed mask (1 = inside sewershed, 0 = outside)
3. **`Nairobi_sealed_surface.asc`** - Impervious surface fraction (0-1)
4. **`Nairobi_pervious_surface.asc`** - Pervious surface fraction (0-1)
5. **`Nairobi_OSM_buildings.asc`** - Building footprints (1 = building, 0 = no building)
6. **`Nairobi_roughness.asc`** - Manning's roughness coefficients

### Boundary Condition Files
7. **`fluvial_boundary_none.txt`** - No fluvial inflow (pluvial simulation only)
8. **`outflowlocs_zero_template.txt`** - No specific outflow monitoring points

### Precipitation Data
9. **`rain/Nairobi_202404_t001.asc`** to **`rain/Nairobi_202404_t096.asc`** - Rainfall grids

## Python Preprocessing Workflow

The `nairobi_flood_setup.py` script replaces the original R-based workflow and provides:

### Key Features
- **Modern Python stack**: Uses xarray, geopandas, and rasterio
- **Modular design**: Class-based structure for easy modification
- **Comprehensive workflow**: From raw data to simulation-ready files
- **Nairobi-specific parameters**: Adapted for local urban conditions

### Usage
```bash
# Basic setup (creates directory structure and templates)
python nairobi_flood_setup.py

# Full setup with data files (modify paths in script)
# Edit the script to specify actual data file paths:
# - domain_shapefile: Nairobi study area boundary
# - dem_tiles_dir: Directory with DEM tiles
# - buildings_file: OSM buildings shapefile
# - imperviousness_data: Land cover/imperviousness data
# - rainfall_dir: Rainfall raster files
```

### Python Dependencies
```bash
pip install geopandas rasterio xarray matplotlib pandas numpy
```

## Running the Model

1. **Prepare input data** using the Python preprocessing script:
   ```bash
   cd nbo_202404
   python nairobi_flood_setup.py
   ```

2. **Verify input files** exist in the `input/` directory

3. **Run the simulation** from the `nbo_202404` directory:
   ```bash
   cd nbo_202404
   mkdir -p output
   ../bin/RIM2D Nairobi_flood_202404.def
   ```

4. **Monitor progress**:
   ```bash
   # GPU usage
   watch -n 2 nvidia-smi

   # Output files
   watch -n 10 'ls -la output/'

   # Simulation process
   ps aux | grep RIM2D
   ```

## Expected Runtime

- **Hardware**: NVIDIA GeForce RTX 5050 (8GB VRAM)
- **Estimated runtime**: 5-15 minutes (depending on domain size)
- **Memory usage**: ~2-4GB GPU memory
- **Disk space**: ~1-2GB for output files

## Model Outputs

### Water Depth Grids
- **Format**: ESRI ASCII (.asc) files
- **Frequency**: 20 output time steps (hourly)
- **Content**: Water depth in meters at each grid cell
- **Naming**: `Nairobi_202404_flood_HHHHH.asc` (where HHHHH is time in seconds)

### Key Output Times
- Hours 1-20: Hourly outputs from 3600 to 72000 seconds
- Focus periods: Peak flood (hours 6-12), recession (hours 16-20)

## Results Analysis

### Visualization
```python
import rasterio
import matplotlib.pyplot as plt
import numpy as np

# Load and plot maximum water depths
with rasterio.open('output/Nairobi_202404_flood_43200.asc') as src:
    water_depth = src.read(1)
    water_depth[water_depth < 0.01] = np.nan  # Remove negligible depths

plt.figure(figsize=(12, 8))
plt.imshow(water_depth, cmap='Blues', vmin=0, vmax=2)
plt.colorbar(label='Water Depth (m)')
plt.title('Nairobi Flood Depth - 12 Hours')
plt.show()
```

### Key Metrics
- **Maximum flood extent**: Area with >0.1m water depth
- **Critical depths**: Areas with >0.5m depth (dangerous for pedestrians)
- **Duration mapping**: Time above threshold depths
- **Flow velocities**: Available if full output enabled

## Differences from Klotzsche Example

### Geographic Adaptations
- **Larger domain**: Nairobi urban area vs. Dresden suburb
- **Lower resolution**: 10m vs. 5m (computational efficiency)
- **Different climate**: Tropical vs. temperate precipitation patterns

### Parameter Adjustments
- **Reduced infiltration**: 15 mm/h vs. 20 mm/h (urban soil compaction)
- **Lower sewer capacity**: 20 mm/h vs. 25 mm/h (infrastructure limitations)
- **Longer simulation**: 24h vs. 6h (sustained rainfall event)
- **Higher output frequency**: 20 vs. 15 time steps

### Technical Improvements
- **Python workflow**: Modern geospatial Python stack
- **Modular structure**: Easier to adapt for other cities
- **Better documentation**: Comprehensive setup guide

## Troubleshooting

### Common Issues

1. **"No such file or directory" errors**:
   - Ensure all input files exist in `input/` directory
   - Run from `nbo_202404/` directory, not main project directory

2. **GPU memory errors**:
   - Reduce domain size or increase cell size
   - Check `nvidia-smi` for memory usage

3. **Slow simulation**:
   - Normal for large domains
   - Monitor with `nvidia-smi` to confirm GPU usage

4. **Missing rainfall files**:
   - Ensure all 96 rainfall files exist
   - Check file naming convention: `Nairobi_202404_t001.asc` to `t096.asc`

### Performance Tips
- **Start small**: Test with reduced domain first
- **Check inputs**: Verify all raster files have same extent/resolution
- **Monitor resources**: Use `nvidia-smi` and `htop` during simulation

## Data Sources

### Recommended Data
- **DEM**: SRTM 30m or ALOS 12.5m (resample to 10m)
- **Buildings**: OpenStreetMap building footprints
- **Land cover**: ESA WorldCover or local urban planning data
- **Rainfall**: Satellite precipitation (GPM, CHIRPS) or gauge data
- **Validation**: Flood extent from satellite imagery or field reports

### Data Preparation Notes
- All rasters must have identical extent, resolution, and coordinate system
- Use UTM Zone 37S for Nairobi (EPSG:32737)
- NoData values should be -9999
- Building heights not required (footprints sufficient)

## Contact

This model setup was created as part of the RIM2D urban flood modeling framework. For technical questions about the model setup or Python preprocessing workflow, refer to the main project documentation in `claude.md`.

For RIM2D software questions, consult the original RIM2D documentation and research publications.