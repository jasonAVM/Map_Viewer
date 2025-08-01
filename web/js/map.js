// Configuration - Auto-generated from ortho processing
const CONFIG = {
    initialView: {
        lat: 46.137960,
        lng: -122.989262,
        zoom: 15
    },
    
    zoomLevels: {
        min: 10,
        max: 22
    },
    
    orthoLayers: [
        {
            name: 'Ditch5',
            url: 'tiles/Ditch5/{z}/{x}/{y}.png',
            bounds: [[46.127990, -122.989713], [46.147684, -122.971028]]
        },
        {
            name: 'Ditch6',
            url: 'tiles/Ditch6/{z}/{x}/{y}.png',
            bounds: [[46.177256, -122.998390], [46.178681, -122.993338]]
        },
        {
            name: 'Ditch2',
            url: 'tiles/Ditch2/{z}/{x}/{y}.png',
            bounds: [[46.131986, -122.969520], [46.147200, -122.966346]]
        },
        {
            name: 'Ditch14',
            url: 'tiles/Ditch14/{z}/{x}/{y}.png',
            bounds: [[46.141751, -123.016294], [46.149016, -123.003420]]
        },
    ]
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
        tms: true,
        bounds: layerConfig.bounds,
        errorTileUrl: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' // Transparent 1x1 gif
    });
    layer.addTo(map);
});

// Set zoom limits
map.options.minZoom = CONFIG.zoomLevels.min;
map.options.maxZoom = CONFIG.zoomLevels.max;

// Add keyboard shortcut to show current position
document.addEventListener('keydown', function(e) {
    // Ctrl+Shift+P (or Cmd+Shift+P on Mac)
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        
        const center = map.getCenter();
        const zoom = map.getZoom();
        
        const message = `Current Map Position:\n\n` +
                       `Zoom: ${zoom}\n` +
                       `Center Lat: ${center.lat.toFixed(6)}\n` +
                       `Center Lng: ${center.lng.toFixed(6)}\n\n` +
                       `To update initial view, change these values in CONFIG:\n` +
                       `lat: ${center.lat.toFixed(6)}\n` +
                       `lng: ${center.lng.toFixed(6)}\n` +
                       `zoom: ${zoom}`;
        
        alert(message);
    }
});