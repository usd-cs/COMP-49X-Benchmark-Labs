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
            // create chart
            var resultsDiv = document.getElementById('results');
            resultsDiv.classList.remove('hidden');
            resultsDiv.innerHTML = '<h2>Prediction Results</h2>';
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

            var riskMap = {
                'Extremely Low': { value: 0, color: 'darkgreen' },
                'Very Low': { value: 15, color: 'green' },
                'Low': { value: 30, color: 'lightgreen' },
                'Medium': { value: 40, color: 'yellow' },
                'High': { value: 60, color: 'orange' },
                'Very High': { value: 80, color: 'red' },
                'Extremely High': { value: 100, color: 'darkred' }
            };
            var colors = [];
            var levels = [];

            data.forEach(result => {
                const risk = riskMap[result.category];
                if (risk) {
                    colors.push(risk.color);
                    levels.push(risk.value);
                } else {
                    // Handle unknown categories, if needed
                    colors.push('gray');
                    levels.push(0);
                }
            });

            // center and resize the chart
            chartContainer.style.width = '90%';
            chartContainer.style.height = '400px';
            canvas.width = chartContainer.clientWidth;
            canvas.height = chartContainer.clientHeight;

            
            // format labels to Day (Ex: Monday) and Time (Ex: 12:00 AM)
            timeLabels = timeLabels.map(label => {
                var date = new Date(label);
                var options = { weekday: 'long', hour: 'numeric', minute: 'numeric' };
                return date.toLocaleDateString('en-US', options);
            });


            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeLabels,
                    datasets: [{
                        label: 'Risk Level Over Time',
                        data: levels,
                        backgroundColor: colors,
                        borderColor: 'rgb(0, 0, 0)',
                        borderWidth: 1,
                        fill: false,
                        pointRadius: 6,
                        pointHoverRadius: 8 
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date and Time'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Risk Level'
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
