document.addEventListener('DOMContentLoaded', function () {
    var map = L.map('map').setView([39.8283, -98.5795], 4);  // Default to center of the US

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var marker;
    var resultsDiv = document.getElementById('results'); // Get the results div
    var loadingDiv = document.getElementById('loading'); // Get the loading div

    // Function to set marker at given location
    function setMarker(lat, lng) {
        if (marker) {
            map.removeLayer(marker);
        }
        marker = L.marker([lat, lng], { draggable: true }).addTo(map);
        map.setView([lat, lng], 13); // Zoom to the user's location
    }

    // Try to get the user's current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            setMarker(position.coords.latitude, position.coords.longitude);
        }, function () {
            console.error('Geolocation failed or permission denied.');
        });
    } else {
        console.error('Geolocation is not supported by this browser.');
    }

    map.on('click', function (e) {
        setMarker(e.latlng.lat, e.latlng.lng);
    });

    document.getElementById('requestPMI').addEventListener('click', function () {
        if (!marker) {
            alert('Please select a location on the map.');
            return;
        }

        // Hide previous results
        resultsDiv.classList.add('hidden');
        // Show loading icon
        loadingDiv.classList.remove('hidden');

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
            // Hide loading icon
            loadingDiv.classList.add('hidden');
            // create chart
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
                        label: 'Risk Level Prediction',
                        data: levels,
                        backgroundColor: colors,
                        borderColor: 'rgb(0, 0, 0)',
                        borderWidth: 1,
                        fill: false,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointStyle: 'circle',
                        hoverBackgroundColor: colors,
                        hoverBorderColor: 'rgb(0, 0, 0)',
                        hoverBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const index = context.dataIndex;
                                    const category = data[index].category;
                                    const value = context.raw;
                                    return `Risk Level: ${value}, Category: ${category}`;
                                }
                            }
                        }
                    },
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

        // Hide modal and finish card
        modal.style.display = 'none';
        finishCard.classList.add('hidden');

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
            // Show finish card
            finishCard.classList.remove('hidden');
            alert('Report submitted successfully.');
        })
        .catch(error => {
            console.error('Error submitting report:', error);
            alert('Error submitting report: ' + error.message);
        });
    });
});
