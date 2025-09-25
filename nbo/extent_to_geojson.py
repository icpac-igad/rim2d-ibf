#!/usr/bin/env python3
"""
Convert extent coordinates to GeoJSON polygon using Shapely box method.
"""

import json
from shapely.geometry import box
from shapely import to_geojson

# Define extent coordinates
lat_min = -1.402004
lon_min = 36.6
lat_max = -1.098036
lon_max = 37.1

# Create polygon using Shapely box (lon_min, lat_min, lon_max, lat_max)
polygon = box(lon_min, lat_min, lon_max, lat_max)

# Convert to GeoJSON
geojson_str = to_geojson(polygon)
geojson_dict = json.loads(geojson_str)

# Create feature collection
feature_collection = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Study Area Extent",
                "lat_min": lat_min,
                "lon_min": lon_min,
                "lat_max": lat_max,
                "lon_max": lon_max
            },
            "geometry": geojson_dict
        }
    ]
}

# Write to file
output_file = "extent_polygon.geojson"
with open(output_file, 'w') as f:
    json.dump(feature_collection, f, indent=2)

print(f"GeoJSON file created: {output_file}")
print(f"Extent: lat({lat_min}, {lat_max}), lon({lon_min}, {lon_max})")