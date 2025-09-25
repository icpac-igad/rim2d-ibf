# STAC API DEM Download for Nairobi Region

This document describes how to download Digital Elevation Model (DEM) data from STAC APIs for the Nairobi region using Python and the pystac-client library.

## Overview

STAC (SpatioTemporal Asset Catalog) APIs provide a standardized way to search and access geospatial datasets. For this project, we use the Copernicus Dataspace STAC API to download 30-meter resolution DEM data covering the Nairobi study area.

## Study Area

- **Region**: Nairobi, Kenya
- **Coordinates**:
  - Latitude: -1.402004 to -1.098036
  - Longitude: 36.6 to 37.1
- **Bounding Box**: [36.6, -1.402004, 37.1, -1.098036] (lon_min, lat_min, lon_max, lat_max)

## Data Source

- **STAC API**: https://catalogue.dataspace.copernicus.eu/stac
- **Collection**: `cop-dem-glo-30-dged-cog` (Copernicus DEM 30m Global)
- **Data Type**: Cloud Optimized GeoTIFF (COG)
- **Resolution**: 30 meters
- **Vertical Datum**: EGM2008 geoid

## Dependencies

Install required Python packages:

```bash
pip install pystac-client rasterio
```

## Usage

### 1. Run the Download Script

```bash
python download_stac_dem.py
```

### 2. Script Workflow

The script performs the following steps:

1. **Search STAC API**: Queries the Copernicus Dataspace STAC API for DEM tiles covering the Nairobi extent
2. **Filter Results**: Identifies DEM assets (GeoTIFF files) from the returned STAC items
3. **Download Tiles**: Downloads individual DEM tiles as Cloud Optimized GeoTIFFs
4. **Crop to AOI**: Clips each tile to the area of interest to reduce file size
5. **Merge Tiles**: Combines multiple tiles into a single mosaic if needed
6. **Save Output**: Writes the final DEM as `nairobi_dem_30m.tif`

### 3. Key Functions

- `search_dem_tiles()`: Searches STAC API for DEM data within bounding box
- `download_and_merge_dem()`: Downloads, crops, and merges DEM tiles
- `main()`: Orchestrates the entire download process

## Output

The script generates:
- **File**: `nairobi_dem_30m.tif`
- **Format**: GeoTIFF with LZW compression
- **Coordinate System**: Same as source data (typically EPSG:4326 or UTM)
- **Coverage**: Nairobi study area

## STAC API Details

### Copernicus DEM Collection

The Copernicus DEM is derived from the WorldDEM™ and provides global coverage at multiple resolutions. Key characteristics:

- **Horizontal Resolution**: 30 meters (1 arc-second)
- **Vertical Accuracy**: Better than 4 meters RMSE
- **Coverage**: Near-global (between 85°N and 56°S)
- **Update Frequency**: Static dataset
- **Data Format**: Cloud Optimized GeoTIFF

### STAC Search Parameters

```python
search = catalog.search(
    collections=["cop-dem-glo-30-dged-cog"],
    bbox=[lon_min, lat_min, lon_max, lat_max]
)
```

Parameters:
- `collections`: List of STAC collection IDs to search
- `bbox`: Bounding box as [west, south, east, north] in WGS84

## Error Handling

The script includes error handling for:
- STAC API connection issues
- Missing or invalid DEM assets
- Rasterio read/write errors
- Temporary file cleanup

## Troubleshooting

### Common Issues

1. **No tiles found**: Verify bounding box coordinates are in correct order (lon_min, lat_min, lon_max, lat_max)
2. **Download failures**: Check internet connection and STAC API availability
3. **Large file sizes**: Consider reducing the bounding box area for testing

### Verification

After download, verify the DEM using:

```python
import rasterio

with rasterio.open("nairobi_dem_30m.tif") as src:
    print(f"Shape: {src.shape}")
    print(f"CRS: {src.crs}")
    print(f"Bounds: {src.bounds}")
    print(f"Resolution: {src.res}")

    # Check elevation statistics
    data = src.read(1)
    print(f"Elevation range: {data.min():.1f} to {data.max():.1f} meters")
```

## Alternative STAC APIs

Other STAC APIs that may have DEM data:
- Microsoft Planetary Computer: https://planetarycomputer.microsoft.com/api/stac/v1
- Element84 Earth Search: https://earth-search.aws.element84.com/v1
- USGS STAC API: https://landsatlook.usgs.gov/stac-server

## Integration with RIM2D

The downloaded DEM can be used directly with the RIM2D flood model:
1. Ensure the DEM covers the entire model domain
2. Convert to ASCII grid format if required by RIM2D
3. Update model definition file with DEM path
4. Verify coordinate system compatibility

## References

- [STAC Specification](https://stacspec.org/)
- [pystac-client Documentation](https://pystac-client.readthedocs.io/)
- [Copernicus DEM Documentation](https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model)
- [Rasterio Documentation](https://rasterio.readthedocs.io/)