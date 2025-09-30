# DEM and Building Footprint Processing Guide

This guide explains how to convert DEM tiles to ASC format and overlay building footprints as NoData values for RIM2D urban flood modeling.

## Overview
Get the building footprint data fro overture by https://github.com/OvertureMaps/overturemaps-py

```
overturemaps download --bbox=36.6,-1.402004,37.1,-1.098036 -f geojson --type=building -o nbo.geojson
```


The processing addresses two key requirements from the Nairobi flood model setup:

- **Line 56 requirement**: Convert DEM TIF files to ESRI ASCII format
- **Line 51 requirement**: Create DEM with buildings as NoData values for flood simulation

## Data Overview

### Input Files
- **DEM Tile**: `dem_tiles/nairobi_dem_tile_00_00.tif` (6.2 MB)
  - Format: GeoTIFF, Float32
  - Size: 1439 × 1094 pixels
  - Coordinate System: WGS84 (EPSG:4326)
  - Pixel Size: ~0.0002778° (~30m at equator)
  - Elevation Range: 1505.5 - 2317.8 meters

- **Building Footprints**: `nbo.geojson` (706 MB)
  - Format: GeoJSON with 1,473,476 polygon features
  - Source: OpenStreetMap building footprints
  - Memory Usage: ~728 MB when loaded
  - Properties: id, version, sources, has_parts, is_underground

## Processing Challenges and Solutions

### Challenge 1: Large Building Dataset
- **Problem**: 1.4+ million building polygons (~700MB file)
- **Solution**: Chunked processing (10,000 polygons per chunk)
- **Benefits**:
  - Manages memory efficiently
  - Provides progress feedback
  - Prevents memory overflow errors

### Challenge 2: Vector to Raster Conversion
- **Problem**: Convert irregular polygons to raster grid
- **Solution**: GDAL rasterization with burn values
- **Process**:
  1. Load polygon chunks into memory vector layer
  2. Rasterize using DEM's spatial reference and resolution
  3. Accumulate results into final building mask

### Challenge 3: Coordinate System Alignment
- **Problem**: Ensure DEM and buildings use same projection
- **Solution**: Use DEM's projection as reference for all operations
- **Result**: Perfect pixel alignment between DEM and building mask

## Scripts

### 1. `examine_geojson.py`
**Purpose**: Analyze building footprint file structure

**Features**:
- Counts total features
- Examines geometry types and properties
- Estimates memory requirements
- Checks coordinate bounds

**Usage**:
```bash
python3 examine_geojson.py
```

**Output**:
```
=== GeoJSON File Analysis: nbo.geojson ===
Feature count: 1473476
Feature type: Polygon
Properties keys: ['id', 'version', 'sources', 'has_parts', 'is_underground']
Sample bounds - Lon: 36.600710 to 36.600803
Sample bounds - Lat: -1.400655 to -1.400594
CRS: Not specified (assuming WGS84)
Estimated memory usage: 728.1 MB
```

### 2. `dem_to_asc_processor.py`
**Purpose**: Main processing script for DEM conversion and building overlay

**Key Features**:
- Memory-efficient chunked processing
- Multiple output formats
- Progress monitoring
- Error handling and validation

**Usage**:
```bash
python3 dem_to_asc_processor.py
```

## Processing Workflow

### Step 1: DEM Information Loading
```python
# Load DEM metadata and raster data
self.load_dem_info()
```
- Reads geotransform and projection
- Loads elevation data into memory
- Determines output grid specifications

### Step 2: Basic DEM Conversion (Line 56)
```python
# Convert TIF to ASC using GDAL
self.convert_dem_to_asc("Nairobi_DEM.asc")
```
- Uses GDAL Translate for reliable conversion
- Maintains original elevation values
- Sets NoData to -9999 (RIM2D standard)

### Step 3: Building Rasterization
```python
# Process buildings in manageable chunks
buildings_mask = self.rasterize_buildings_chunked(chunk_size=10000)
```
- Processes 10,000 polygons at a time
- Creates binary mask (1=building, 0=no building)
- Accumulates results across all chunks

### Step 4: DEM with Buildings as NoData (Line 51)
```python
# Apply building mask to DEM
output_dem[building_pixels] = -9999
```
- Identifies pixels covered by buildings
- Sets building pixels to NoData (-9999)
- Preserves elevation data for non-building areas

## Output Files

### 1. `input/Nairobi_DEM.asc`
- **Purpose**: Basic DEM in ASC format (Line 56 requirement)
- **Content**: Original elevation values from TIF
- **Usage**: Reference or backup DEM

### 2. `input/Nairobi_DEM_housesnodata.asc` ⭐
- **Purpose**: Main input for RIM2D simulation (Line 51 requirement)
- **Content**: DEM with building areas as NoData
- **Usage**: Primary elevation model for flood simulation
- **Key Feature**: Buildings become "holes" allowing water accumulation

### 3. `input/Nairobi_OSM_buildings.asc`
- **Purpose**: Building footprint raster
- **Content**: Binary mask (1=building, 0=no building)
- **Usage**: Optional analysis or validation

## Performance Characteristics

### Processing Time
- **Total Runtime**: ~3-5 minutes on modern hardware
- **Bottlenecks**: Building rasterization (largest component)
- **Memory Usage**: Peak ~1GB during chunk processing

### Chunk Processing Statistics
- **Chunk Size**: 10,000 polygons per chunk
- **Total Chunks**: ~147 chunks for 1.4M polygons
- **Progress Updates**: Every 5 chunks (50K polygons)

### Output Statistics
- **DEM Grid**: 1439 × 1094 = 1,574,466 total pixels
- **Building Pixels**: Varies by area (typically 5-15% of total)
- **NoData Pixels**: Building footprint areas

## Technical Implementation

### Memory Management
```python
# Chunked processing prevents memory overflow
for start_idx in range(0, total_features, chunk_size):
    chunk_features = geojson_data['features'][start_idx:end_idx]
    self._rasterize_chunk(chunk_features, buildings_raster)
```

### GDAL Rasterization
```python
# Use GDAL for accurate polygon to raster conversion
gdal.RasterizeLayer(mem_raster, [1], layer, burn_values=[1])
```

### ASC File Format
```python
# Standard ESRI ASCII Grid header
f.write(f"ncols {width}\n")
f.write(f"nrows {height}\n")
f.write(f"xllcorner {minx}\n")
f.write(f"yllcorner {miny}\n")
f.write(f"cellsize {cellsize}\n")
f.write(f"NODATA_value -9999\n")
```

## Requirements and Dependencies

### Python Libraries
```bash
# Core geospatial processing
pip install gdal
# Or using conda:
conda install gdal

# Standard libraries (usually included)
import numpy as np
import json
import os
import sys
import time
```

### System Requirements
- **Python**: 3.6+
- **GDAL**: 3.0+ (with Python bindings)
- **Memory**: 2GB+ RAM recommended
- **Storage**: 1GB+ free space for outputs

## Usage Instructions

### 1. Verify Input Files
```bash
# Check DEM tile exists
ls -la dem_tiles/nairobi_dem_tile_00_00.tif

# Check building footprints
ls -la nbo.geojson
```

### 2. Run Analysis (Optional)
```bash
python3 examine_geojson.py
```

### 3. Process DEM and Buildings
```bash
python3 dem_to_asc_processor.py
```

### 4. Verify Outputs
```bash
ls -la input/
# Should show:
# - Nairobi_DEM.asc
# - Nairobi_DEM_housesnodata.asc
# - Nairobi_OSM_buildings.asc
```

### 5. Integration with RIM2D
The main output file `Nairobi_DEM_housesnodata.asc` can be directly used in the RIM2D model definition file:

```
# In Nairobi_flood_202404.def
elevationfile ./input/Nairobi_DEM_housesnodata.asc
```

## Validation and Quality Control

### Visual Verification
```python
import matplotlib.pyplot as plt
import numpy as np

# Load and visualize DEM with buildings
data = np.loadtxt('input/Nairobi_DEM_housesnodata.asc', skiprows=6)
plt.figure(figsize=(12, 8))
plt.imshow(data, cmap='terrain')
plt.colorbar(label='Elevation (m)')
plt.title('DEM with Buildings as NoData')
plt.show()
```

### Statistical Checks
- **NoData percentage**: Should be 5-15% for urban areas
- **Elevation range**: Should match original DEM bounds
- **Spatial alignment**: Buildings should align with urban areas

## Troubleshooting

### Common Issues

1. **"Cannot open DEM file" Error**
   - Verify DEM path: `dem_tiles/nairobi_dem_tile_00_00.tif`
   - Check file permissions
   - Ensure GDAL can read GeoTIFF format

2. **Memory Errors with Buildings**
   - Reduce chunk_size parameter (e.g., 5000 instead of 10000)
   - Close other applications to free memory
   - Consider processing subsets of buildings

3. **Missing GDAL Python Bindings**
   - Install: `pip install gdal` or `conda install gdal`
   - On Ubuntu: `sudo apt-get install python3-gdal`

4. **Coordinate System Misalignment**
   - Script automatically uses DEM's coordinate system
   - No manual intervention needed
   - Both inputs are in WGS84

### Performance Optimization

1. **Faster Processing**:
   - Use SSD storage for input/output files
   - Increase chunk_size if memory allows
   - Close unnecessary applications

2. **Lower Memory Usage**:
   - Decrease chunk_size (e.g., 5000)
   - Process buildings in multiple passes
   - Use 64-bit Python for larger memory access

## Integration with RIM2D Workflow

This processing step fits into the larger RIM2D workflow:

1. **Data Preparation** ← *This guide*
   - Convert DEM to ASC
   - Apply building mask

2. **Model Setup**
   - Configure model definition file
   - Set up rainfall data
   - Define other input layers

3. **Simulation Execution**
   - Run RIM2D with processed DEM
   - Monitor GPU performance
   - Generate flood depth outputs

4. **Results Analysis**
   - Visualize flood depths
   - Extract flood statistics
   - Validate against observations

## Contact and Support

For technical questions about this processing workflow:
- Check script comments and error messages
- Verify input file formats and paths
- Review GDAL documentation for rasterization issues

For RIM2D modeling questions, refer to the main project documentation.
