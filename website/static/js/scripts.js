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
            
            // Create table for results
            var table = document.createElement('table');
            table.className = 'prediction-table';
            var headerRow = document.createElement('tr');
            
            // Add headers
            var timestampHeader = document.createElement('th');
            timestampHeader.textContent = 'Timestamp';
            var predictionHeader = document.createElement('th');
            predictionHeader.textContent = 'Prediction';
            var confidenceHeader = document.createElement('th');
            confidenceHeader.textContent = 'Confidence';
            
            headerRow.appendChild(timestampHeader);
            headerRow.appendChild(predictionHeader);
            headerRow.appendChild(confidenceHeader);
            table.appendChild(headerRow);

            // Add data rows
            data.forEach(result => {
                var row = document.createElement('tr');
                
                var timestampCell = document.createElement('td');
                timestampCell.textContent = result.timestamp;
                
                var predictionCell = document.createElement('td');
                predictionCell.textContent = result.prediction ? 'Positive' : 'Negative';
                predictionCell.className = result.prediction ? 'positive' : 'negative';
                
                var confidenceCell = document.createElement('td');
                // Format confidence as percentage
                var confidenceValue = (result.confidence * 100).toFixed(2) + '%';
                
                // Create confidence bar
                var confidenceBar = document.createElement('div');
                confidenceBar.className = 'confidence-bar';
                
                var confidenceFill = document.createElement('div');
                confidenceFill.className = 'confidence-fill';
                confidenceFill.style.width = (result.confidence * 100) + '%';
                confidenceFill.style.backgroundColor = result.prediction ? 
                    `rgba(0, 128, 0, ${result.confidence})` : 
                    `rgba(255, 0, 0, ${result.confidence})`;
                
                confidenceBar.appendChild(confidenceFill);
                
                confidenceCell.textContent = confidenceValue;
                confidenceCell.appendChild(confidenceBar);
                
                row.appendChild(timestampCell);
                row.appendChild(predictionCell);
                row.appendChild(confidenceCell);
                table.appendChild(row);
            });

            resultsDiv.appendChild(table);
            
            // Create visualization
            var chartContainer = document.createElement('div');
            chartContainer.className = 'chart-container';
            
            var canvas = document.createElement('canvas');
            canvas.id = 'predictionChart';
            chartContainer.appendChild(canvas);
            resultsDiv.appendChild(chartContainer);
            
            // Create chart with confidence metrics
            var ctx = canvas.getContext('2d');
            var timeLabels = data.map(item => item.timestamp);
            var confidenceData = data.map(item => item.confidence);
            var colors = data.map(item => item.prediction ? 
                `rgba(0, 128, 0, ${item.confidence})` : 
                `rgba(255, 0, 0, ${item.confidence})`);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeLabels,
                    datasets: [
                        {
                            label: 'Confidence',
                            data: confidenceData,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderWidth: 2,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            max: 1,
                            title: {
                                display: true,
                                text: 'Confidence'
                            }
                        }
                    }
                }
            });
        });
    });
});
