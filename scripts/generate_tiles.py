#!/usr/bin/env python3
"""
GeoTIFF to Web Tiles Generator

This script processes GeoTIFF files and generates web map tiles,
automatically configuring zoom levels and map extents based on the input data.
"""

import os
import sys
import subprocess
import json
import math
from pathlib import Path

def get_geotiff_info(geotiff_path):
    """Get bounds and projection info from a GeoTIFF using gdalinfo"""
    try:
        result = subprocess.run(['gdalinfo', '-json', geotiff_path], 
                              capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        # Extract bounds in WGS84
        corners = info['cornerCoordinates']
        
        # Get bounds in lat/lon
        lower_left = corners['lowerLeft']
        upper_right = corners['upperRight']
        
        bounds = {
            'west': lower_left[0],
            'south': lower_left[1], 
            'east': upper_right[0],
            'north': upper_right[1]
        }
        
        # Get pixel dimensions for calculating appropriate zoom levels
        size = info['size']
        pixel_size = info['geoTransform'][1]  # pixel width in map units
        
        return bounds, size, pixel_size
        
    except subprocess.CalledProcessError as e:
        print(f"Error getting info for {geotiff_path}: {e}")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"Error parsing gdalinfo output for {geotiff_path}: {e}")
        return None, None, None

def calculate_zoom_levels(pixel_size, image_width):
    """Calculate appropriate min/max zoom levels based on pixel resolution"""
    # Rough calculation - adjust based on your needs
    # Web Mercator tile size is ~156543.03 meters per pixel at zoom 0
    meters_per_pixel_zoom0 = 156543.03392804097
    
    # Calculate what zoom level gives us roughly the original resolution
    optimal_zoom = math.log2(meters_per_pixel_zoom0 / abs(pixel_size))
    
    # Set reasonable bounds around the optimal zoom
    calculated_min = max(1, int(optimal_zoom) - 8)  # Allow zooming out 8 levels
    calculated_max = min(22, int(optimal_zoom) + 4)  # Allow zooming in 4 levels
    
    # Ensure min is always less than max
    min_zoom = min(calculated_min, calculated_max)
    max_zoom = max(calculated_min, calculated_max)
    
    # For very high resolution imagery, use reasonable defaults
    if min_zoom > 18:
        min_zoom = 10
        max_zoom = 22
    
    return min_zoom, max_zoom

def generate_tiles(geotiff_path, output_dir, folder_name):
    """Generate web tiles from GeoTIFF using gdal2tiles.py"""
    
    print(f"Processing {folder_name}...")
    
    # Get GeoTIFF information
    bounds, size, pixel_size = get_geotiff_info(geotiff_path)
    if bounds is None:
        print(f"Failed to get info for {geotiff_path}")
        return None, None, None
    
    # Calculate appropriate zoom levels
    min_zoom, max_zoom = calculate_zoom_levels(pixel_size, size[0])
    
    print(f"  Bounds: {bounds}")
    print(f"  Suggested zoom levels: {min_zoom}-{max_zoom}")
    
    # Create output directory using the folder name
    tile_output_dir = os.path.join(output_dir, folder_name)
    os.makedirs(tile_output_dir, exist_ok=True)
    
    # Generate tiles using gdal2tiles.py
    cmd = [
        'gdal2tiles.py',
        '-z', f"{min_zoom}-{max_zoom}",
        '-w', 'none',  # No web viewer
        '--processes=4',  # Use 4 processes for faster processing
        geotiff_path,
        tile_output_dir
    ]
    
    print(f"  Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"  ✓ Tiles generated successfully for {folder_name}")
        return bounds, min_zoom, max_zoom
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error generating tiles for {folder_name}: {e}")
        return None, None, None

def update_map_config(ortho_configs, output_dir):
    """Update the JavaScript map configuration with calculated values"""
    
    # Calculate overall bounds for all orthos
    all_bounds = [config['bounds'] for config in ortho_configs.values() if config['bounds']]
    
    if not all_bounds:
        print("No valid ortho bounds found")
        return
    
    # Calculate center point and zoom level to show all orthos
    min_west = min(b['west'] for b in all_bounds)
    max_east = max(b['east'] for b in all_bounds)
    min_south = min(b['south'] for b in all_bounds)
    max_north = max(b['north'] for b in all_bounds)
    
    center_lat = (min_south + max_north) / 2
    center_lng = (min_west + max_east) / 2
    
    # Calculate zoom to fit all orthos (rough approximation)
    lat_range = max_north - min_south
    lng_range = max_east - min_west
    max_range = max(lat_range, lng_range)
    
    # Rough zoom calculation - may need adjustment
    initial_zoom = max(1, int(10 - math.log2(max_range * 10)))
    
    # Get overall zoom range
    all_min_zooms = [config['min_zoom'] for config in ortho_configs.values() if config['min_zoom']]
    all_max_zooms = [config['max_zoom'] for config in ortho_configs.values() if config['max_zoom']]
    
    overall_min_zoom = min(all_min_zooms) if all_min_zooms else 5
    overall_max_zoom = max(all_max_zooms) if all_max_zooms else 18
    
    # Generate updated JavaScript config
    js_config = f"""// Configuration - Auto-generated from ortho processing
const CONFIG = {{
    initialView: {{
        lat: {center_lat:.6f},
        lng: {center_lng:.6f},
        zoom: {initial_zoom}
    }},
    
    zoomLevels: {{
        min: {overall_min_zoom},
        max: {overall_max_zoom}
    }},
    
    orthoLayers: [
"""
    
    # Generate layer configs dynamically
    for ortho_name, config in ortho_configs.items():
        if config['bounds']:
            bounds = config['bounds']
            js_config += f"""        {{
            name: '{ortho_name}',
            url: '../tiles/{ortho_name}/{{z}}/{{x}}/{{y}}.png',
            bounds: [[{bounds['south']:.6f}, {bounds['west']:.6f}], [{bounds['north']:.6f}, {bounds['east']:.6f}]]
        }},
"""
        else:
            js_config += f"""        {{
            name: '{ortho_name}',
            url: '../tiles/{ortho_name}/{{z}}/{{x}}/{{y}}.png',
            bounds: null
        }},
"""
    
    js_config += """    ]
};

// Initialize the map
const map = L.map('map').setView([CONFIG.initialView.lat, CONFIG.initialView.lng], CONFIG.initialView.zoom);

// Add OpenStreetMap base layer with 50% transparency
const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    opacity: 0.5,
    maxZoom: 19
});
osmLayer.addTo(map);

// Dynamically add ortho tile layers
CONFIG.orthoLayers.forEach(layerConfig => {
    const layer = L.tileLayer(layerConfig.url, {
        attribution: layerConfig.name,
        maxZoom: CONFIG.zoomLevels.max,
        tms: false,
        bounds: layerConfig.bounds
    });
    layer.addTo(map);
});

// Set zoom limits
map.options.minZoom = CONFIG.zoomLevels.min;
map.options.maxZoom = CONFIG.zoomLevels.max;"""
    
    # Write updated config
    js_file = os.path.join(output_dir, 'web', 'js', 'map.js')
    with open(js_file, 'w') as f:
        f.write(js_config)
    
    print(f"Updated map configuration:")
    print(f"  Center: {center_lat:.6f}, {center_lng:.6f}")
    print(f"  Initial zoom: {initial_zoom}")
    print(f"  Zoom range: {overall_min_zoom}-{overall_max_zoom}")

def main():
    # Define paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    geotiff_dir = project_dir / 'orthos'
    tiles_dir = project_dir / 'tiles'
    
    print("GeoTIFF to Web Tiles Generator")
    print("=" * 40)
    
    # Check if GDAL is available
    try:
        subprocess.run(['gdalinfo', '--version'], capture_output=True, check=True)
        subprocess.run(['gdal2tiles.py', '--help'], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Error: GDAL tools not found. Please install GDAL:")
        print("  Ubuntu/Debian: sudo apt-get install gdal-bin")
        print("  macOS: brew install gdal")
        print("  Windows: Install OSGeo4W or use conda")
        sys.exit(1)
    
    # Find GeoTIFF files
    geotiff_files = list(geotiff_dir.glob('*.tif')) + list(geotiff_dir.glob('*.tiff'))
    
    if not geotiff_files:
        print(f"No GeoTIFF files found in {geotiff_dir}")
        print("Please place your .tif or .tiff files in the orthos/ directory")
        sys.exit(1)
    
    # Process all GeoTIFF files found (removed 4-file limit)
    
    print(f"Found {len(geotiff_files)} GeoTIFF files to process:")
    for i, f in enumerate(geotiff_files, 1):
        print(f"  {i}. {f.name}")
    
    # Process each GeoTIFF
    ortho_configs = {}
    
    for geotiff_file in geotiff_files:
        # Use filename without extension as folder name
        folder_name = geotiff_file.stem  # Gets filename without extension
        bounds, min_zoom, max_zoom = generate_tiles(str(geotiff_file), str(tiles_dir), folder_name)
        
        ortho_configs[folder_name] = {
            'bounds': bounds,
            'min_zoom': min_zoom,
            'max_zoom': max_zoom,
            'source_file': geotiff_file.name
        }
    
    # Update map configuration
    print("\nUpdating map configuration...")
    update_map_config(ortho_configs, str(project_dir))
    
    print("\n✓ Tile generation complete!")
    print(f"✓ Generated tiles in: {tiles_dir}")
    print(f"✓ Updated map configuration")
    print(f"\nTo view your map:")
    print(f"1. Upload the 'web' and 'tiles' directories to your S3 bucket")
    print(f"2. Enable static website hosting on the S3 bucket")
    print(f"3. Set index.html as the index document")

if __name__ == '__main__':
    main()