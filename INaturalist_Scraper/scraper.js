var request = require('request');
var fs = require('fs');

// Get all powdery mildew metadata from INaturalist
var options = {
  'method': 'GET',
  'url': 'https://api.inaturalist.org/v1/observations?taxon_id=408176&order_by=votes&quality_grade=research&photos=true&page=&per_page=159',
  'headers': {
  }
};

request(options, function (error, response) {
    if (error) throw new Error(error);
    
    // Parse body for dates and locations
    const data = JSON.parse(response.body);
    const processedData = data.results.map(observation => ({
        id: observation.id,
        date: {
            day: observation.observed_on_details.day,
            month: observation.observed_on_details.month,
            year: observation.observed_on_details.year
        },
        coordinates: observation.geojson.coordinates
    }));

    // Save parsed data to file
    fs.writeFileSync(__dirname + '/observations.json', JSON.stringify(processedData, null, 2));
    console.log('Data saved to observations.json');
});
