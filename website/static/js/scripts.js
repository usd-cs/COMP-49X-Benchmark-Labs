document.addEventListener('DOMContentLoaded', function () {
    var map = L.map('map').setView([39.8283, -98.5795], 4);  // Centered on the US

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var marker;

    map.on('click', function (e) {
        if (marker) {
            map.removeLayer(marker);
        }
        marker = L.marker(e.latlng).addTo(map);
    });

    document.getElementById('requestPMI').addEventListener('click', function () {
        if (!marker) {
            alert('Please select a location on the map.');
            return;
        }

        var latlng = marker.getLatLng();
        var timestamp = new Date().toISOString().split('T')[0];

        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude: latlng.lat,
                longitude: latlng.lng,
                timestamp: timestamp
            })
        })
        .then(response => response.json())
        .then(data => {
            var resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<h2>Prediction Results</h2>';
            var table = document.createElement('table');
            var headerRow = document.createElement('tr');
            var timestampHeader = document.createElement('th');
            timestampHeader.textContent = 'Timestamp';
            var confidenceHeader = document.createElement('th');
            confidenceHeader.textContent = 'Confidence Interval';
            headerRow.appendChild(timestampHeader);
            headerRow.appendChild(confidenceHeader);
            table.appendChild(headerRow);

            data.forEach(result => {
                var row = document.createElement('tr');
                var timestampCell = document.createElement('td');
                timestampCell.textContent = result.timestamp;
                var confidenceCell = document.createElement('td');
                confidenceCell.textContent = result.confidence_interval;
                row.appendChild(timestampCell);
                row.appendChild(confidenceCell);
                table.appendChild(row);
            });

            resultsDiv.appendChild(table);
        });
    });
});
