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
        marker = L.marker(e.latlng, { draggable: true }).addTo(map);
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
            resultsDiv.classList.remove('hidden');
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
            var categoryHeader = document.createElement('th');
            categoryHeader.textContent = 'Risk Level';
            
            headerRow.appendChild(timestampHeader);
            headerRow.appendChild(predictionHeader);
            headerRow.appendChild(confidenceHeader);
            headerRow.appendChild(categoryHeader);
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
                    `rgba(255, 0, 0, ${result.confidence})` : 
                    `rgba(0, 128, 0, ${result.confidence})`;
                
                confidenceBar.appendChild(confidenceFill);
                
                confidenceCell.textContent = confidenceValue;
                confidenceCell.appendChild(confidenceBar);

                var categoryCell = document.createElement('td');
                categoryCell.textContent = result.category;
                var categoryColor = '';
                switch (result.category) {
                    case 'Extremely Low':
                        categoryColor = 'lightblue';
                        categoryCell.textContent += ' (1 - 10)';
                        break;
                    case 'Very Low':
                        categoryColor = 'lightgreen';
                        categoryCell.textContent += ' (11 - 20)';
                        break;
                    case 'Low':
                        categoryColor = 'green';
                        categoryCell.textContent += ' (21 - 30)';
                        break;
                    case 'Medium':
                        categoryColor = 'yellow';
                        categoryCell.textContent += ' (31 - 50)';
                        break;
                    case 'High':
                        categoryColor = 'red';
                        categoryCell.textContent += ' (51 - 70)';
                        break;
                    case 'Very High':
                        categoryColor = 'darkred';
                        categoryCell.textContent += ' (71 - 90)';
                        break;
                    case 'Extremely High':
                        categoryColor = 'purple';
                        categoryCell.textContent += ' (90 - 100)';
                        break;
                    default:
                        categoryColor = 'gray';
                }
                categoryCell.style.color = categoryColor;
                
                row.appendChild(timestampCell);
                row.appendChild(predictionCell);
                row.appendChild(confidenceCell);
                row.appendChild(categoryCell);
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
            
            // Create chart
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
                    datasets: [{
                        label: 'Confidence Over Time',
                        data: confidenceData,
                        backgroundColor: colors,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false
                    }]
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

    var modal = document.getElementById('dateModal');
    var span = document.getElementsByClassName('close')[0];
    var submitDateButton = document.getElementById('submitDate');
    var observationDateInput = document.getElementById('observationDate');
    var finishCard = document.getElementById('finishCard');

    document.getElementById('reportMildew').addEventListener('click', function () {
        if (!marker) {
            alert('Please select a location on the map.');
            return;
        }

        // Set the default date to today
        var today = new Date().toISOString().split('T')[0];
        observationDateInput.value = today;

        // Show the modal
        modal.style.display = 'block';
    });

    span.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    submitDateButton.addEventListener('click', function () {
        var latlng = marker.getLatLng();
        var timestamp = observationDateInput.value;

        fetch('/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                coordinates: [latlng.lat, latlng.lng],
                timestamp: timestamp
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Report submitted successfully.');
            modal.style.display = 'none';
            finishCard.classList.remove('hidden');
        })
        .catch(error => {
            alert('Error submitting report: ' + error.message);
        });
    });
});
