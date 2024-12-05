// Initialize leaflet map
let map = L.map('map', {minZoom: 3, maxBounds: [[-90,-180],   [90,180]]}).setView([25, 0], 1);

// Add openstreetmap API to leaflet map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);
// Add gpx files to map
for (let i = 0; i < gpxFiles.length; i++) {
    let points = []; // Array to store coordinates for LineString features
    
    // Custom options for popup styling
    var customOptions =
    {
        'maxWidth': '500',
        'width': '100',
        'className' : 'custom-popup'
    }

    // Create a custom GeoJSON layer
    let customLayer = L.geoJson(null, {
        onEachFeature: function (feature, layer) {
            if (feature.geometry.type === 'Point') {
                // For Point features, create marker and bind popup
                let coords = feature.geometry.coordinates;
                pointMarker = L.marker(L.latLng(coords[1], coords[0])).addTo(map);
                pointMarker.bindPopup("Type: Location Marker" + "<br>Uploaded by: " + gpxFiles[i][2] +  "<br>Description: " + gpxFiles[i][3] +  "<br>Date Uploaded: " + gpxFiles[i][1], customOptions)
            } else if (feature.geometry.type === 'LineString') {
                // For LineString features, collect coordinates
                feature.geometry.coordinates.forEach(c => points.push(L.latLng(c[1], c[0])));
            }
        },
    });

    // Parse GPX file and add to custom layer
    let runLayer = omnivore.gpx(gpxFiles[i][0], null, customLayer)
        .on('ready', function () {
            if (points.length > 0){
                // If there are collected points (LineString), process them
                
                // Retrieve first and last points
                let firstPoint = points[0];
                let lastPoint = points[points.length - 1];

                // Create markers for first and last points
                let firstMarker = L.marker(firstPoint, {
                    icon: L.divIcon({
                        className: 'first-marker'
                    })
                }).addTo(map); // Add first point as a marker

                let lastMarker = L.marker(lastPoint, {
                    icon: L.divIcon({
                        className: 'last-marker'
                    })
                }).addTo(map); // Add last point as a marker

                // Bind popups to markers
                firstMarker.bindPopup("Starting point", customOptions);
                lastMarker.bindPopup("Destination", customOptions);

                // Create a polyline using all points
                let polyline = L.polyline(points, {
                    color: 'blue', // Set line color
                    weight: 6, // Adjust line weight
                }).addTo(map);

                // Bind popup to polyline
                polyline.bindPopup("Type: Route" + "<br>Uploaded by: " + gpxFiles[i][2] +  "<br>Description: " + gpxFiles[i][3] + "<br>Date Uploaded: " + gpxFiles[i][1], customOptions)

                points = [] // Clear points array
            }
        })
        .on('error', function (e) {
            console.error('Error loading GPX file:', e);
        });
}

// Listens for changes in friend selection
document.addEventListener('DOMContentLoaded', function() {
    elements = document.getElementsByClassName('form-check-input');
    for(let i = 0; i < elements.length; i++){
        elements[i].addEventListener('change', function() {
            
            // Array to store selected friends
            let selectedFriends = [];
            let checkboxes = document.querySelectorAll('.form-check-input:checked');
            checkboxes.forEach(function(checkbox) {
                selectedFriends.push(checkbox.value);
            });

            // Send selected friends to /map and update map using update function
            fetch('/map', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ friends: selectedFriends }),
            })
            .then(response => response.json())
            .then(data => {
                updateMapWithGPXData(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});

// Update function for when friends are selected
function updateMapWithGPXData(data) {
    if (data && data.success) {
        // Get new gpx files
        let gpxFiles = data.gpx_files;

        // Clear existing layers
        map.eachLayer(function (layer) {
            map.removeLayer(layer);
        });

        // Add OpenStreetMap tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 20,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Iterate over new gpx files
        for (let i = 0; i < gpxFiles.length; i++) {
            let points = [];
            let customLayer = L.geoJson(null, {
                onEachFeature: function (feature, layer) {
                    if (feature.geometry.type === 'Point') {
                        // For Point features, create marker and bind popup
                        let coords = feature.geometry.coordinates;
                        pointMarker = L.marker(L.latLng(coords[1], coords[0])).addTo(map);
                        pointMarker.bindPopup("Type: Location Marker" + "<br>Uploaded by: " + gpxFiles[i][2] +  "<br>Description: " + gpxFiles[i][3] +  "<br>Date Uploaded: " + gpxFiles[i][1], customOptions)
                    } else if (feature.geometry.type === 'LineString') {
                        // For LineString features, collect coordinates
                        feature.geometry.coordinates.forEach(c => points.push(L.latLng(c[1], c[0])));
                    }
                },
            });
            
            // Parse GPX file and add to custom layer
            let runLayer = omnivore.gpx(gpxFiles[i][0], null, customLayer)
                .on('ready', function () {
                    if (points.length > 0){
                        // If there are collected points (LineString), process them
                        
                        // Retrieve first and last points
                        let firstPoint = points[0];
                        let lastPoint = points[points.length - 1];

                        // Create markers for first and last points
                        let firstMarker = L.marker(firstPoint, {
                            icon: L.divIcon({
                                className: 'first-marker'
                            })
                        }).addTo(map); // Add first point as a marker

                        let lastMarker = L.marker(lastPoint, {
                            icon: L.divIcon({
                                className: 'last-marker'
                            })
                        }).addTo(map); // Add last point as a marker

                        // Bind popups to markers
                        firstMarker.bindPopup("Starting point", customOptions);
                        lastMarker.bindPopup("Destination", customOptions);

                        // Create a polyline using all points
                        let polyline = L.polyline(points, {
                            color: 'blue', // Set line color
                            weight: 6, // Adjust line weight
                        }).addTo(map);

                        // Bind popup to polyline
                        polyline.bindPopup("Type: Route" + "<br>Uploaded by: " + gpxFiles[i][2] +  "<br>Description: " + gpxFiles[i][3] + "<br>Date Uploaded: " + gpxFiles[i][1], customOptions)

                        points = [] // Clear points array
                        
                    }
                    
                })
                .on('error', function (e) {
                    console.error('Error loading GPX file:', e);
                });
        }
    } else {
        console.error('Error updating map with GPX files: Invalid data or success flag not set');
    }
}


