#!/usr/bin/env python3
"""
Examine building footprint GeoJSON file structure and properties
"""
import json

def examine_geojson(filepath):
    """Examine GeoJSON file structure"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        print(f"=== GeoJSON File Analysis: {filepath} ===")
        print(f"Feature count: {len(data['features'])}")

        if len(data['features']) > 0:
            first_feature = data['features'][0]
            print(f"Feature type: {first_feature['geometry']['type']}")
            print(f"Properties keys: {list(first_feature['properties'].keys())}")

            # Check coordinate bounds from first few features
            if 'coordinates' in first_feature['geometry']:
                coords = first_feature['geometry']['coordinates']
                if first_feature['geometry']['type'] == 'Polygon':
                    # Get exterior ring coordinates
                    exterior_coords = coords[0]
                    lons = [coord[0] for coord in exterior_coords]
                    lats = [coord[1] for coord in exterior_coords]
                    print(f"Sample bounds - Lon: {min(lons):.6f} to {max(lons):.6f}")
                    print(f"Sample bounds - Lat: {min(lats):.6f} to {max(lats):.6f}")

        print(f"CRS: {data.get('crs', 'Not specified (assuming WGS84)')}")

        # Estimate file complexity
        file_size_mb = len(json.dumps(data)) / (1024 * 1024)
        print(f"Estimated memory usage: {file_size_mb:.1f} MB")

        return data

    except Exception as e:
        print(f"Error examining GeoJSON: {e}")
        return None

if __name__ == "__main__":
    examine_geojson("nbo.geojson")