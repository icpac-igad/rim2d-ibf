#!/usr/bin/env python3
"""
Check available collections in the Copernicus STAC API.
"""

import pystac_client
from pystac_client import Client

# STAC API endpoint for Copernicus Dataspace
STAC_API_URL = "https://catalogue.dataspace.copernicus.eu/stac"

def list_collections():
    """List all available collections in the STAC catalog."""
    try:
        catalog = Client.open(STAC_API_URL)
        print(f"Connected to STAC API: {STAC_API_URL}")

        collections = list(catalog.get_collections())
        print(f"\nFound {len(collections)} collections:")
        print("-" * 80)

        for collection in collections:
            print(f"ID: {collection.id}")
            print(f"Title: {collection.title}")
            if collection.description:
                desc = collection.description[:100] + "..." if len(collection.description) > 100 else collection.description
                print(f"Description: {desc}")
            print("-" * 80)

        # Look for DEM-related collections
        dem_collections = [c for c in collections if 'dem' in c.id.lower() or 'elevation' in c.id.lower()]
        if dem_collections:
            print(f"\nFound {len(dem_collections)} DEM-related collections:")
            for c in dem_collections:
                print(f"- {c.id}: {c.title}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_collections()