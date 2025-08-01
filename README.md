# Ortho Map Viewer

A web application for displaying GeoTIFF orthoimages on an OpenStreetMap background, designed for AWS S3 static hosting.

## Features

- **OpenStreetMap Background**: 50% transparency to show orthos clearly
- **Auto-Configuration**: Automatically determines optimal zoom levels and map extents
- **GDAL Integration**: Built-in tile generation from GeoTIFF files
- **AWS S3 Ready**: Optimized for static website hosting
- **No API Keys**: Uses free OpenStreetMap tiles

## Quick Start

1. **Install GDAL**:
   ```bash
   sudo apt-get install gdal-bin  # Ubuntu/Debian
   brew install gdal              # macOS
   ```

2. **Add your GeoTIFF files** to the `orthos/` directory

3. **Generate web tiles**:
   ```bash
   python3 scripts/generate_tiles.py
   ```

4. **Deploy to S3**:
   ```bash
   ./deploy.sh
   ```

## Project Structure

```
map_display/
├── orthos/                # Place your GeoTIFF files here
├── tiles/                 # Generated tiles (auto-created)
├── web/
│   ├── index.html         # Main map viewer
│   ├── css/style.css      # Styling
│   └── js/map.js          # Map configuration (auto-updated)
├── scripts/
│   └── generate_tiles.py  # GDAL tile generation tool
└── deploy.sh              # AWS S3 deployment script
```

## Usage

### 1. Generate Tiles

The tile generation script automatically:
- Processes all GeoTIFF files in `orthos/`
- Calculates optimal zoom levels based on image resolution
- Generates XYZ web map tiles
- Updates JavaScript configuration with calculated bounds and zoom levels

```bash
python3 scripts/generate_tiles.py
```

### 2. Deploy to AWS S3

Configure AWS CLI first:
```bash
aws configure
```

Update the bucket name in `deploy.sh`, then deploy:
```bash
./deploy.sh
```

## Configuration

After tile generation, you can manually adjust settings in `web/js/map.js`:

- `initialView`: Center coordinates and initial zoom
- `zoomLevels`: Min/max zoom limits  
- `orthoLayers`: Individual ortho bounds and URLs

## Requirements

- Python 3.x
- GDAL tools (`gdal2tiles.py`, `gdalinfo`)
- AWS CLI (for deployment)

## License

MIT License