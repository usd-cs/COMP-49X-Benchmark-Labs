# COMP-49X-Benchmark-Labs

A tool to calculate the Powdery Mildew Index (PMI) for apple trees based on location and date range.

## How to Run

1. Make sure you have Python 3 installed
2. Install required dependencies:
   ```bash
   pip install requests
   ```

3. Run the application:
   ```bash
   python ./PMI_Model/app.py
   ```

4. Follow the prompts to enter:
   - Latitude (between -90 and 90)
   - Longitude (between -180 and 180)
   - Start date (MM/DD/YYYY format)
   - End date (MM/DD/YYYY format)

## What You'll Get

The tool will return:
- A PMI score from 0-100, where:
  - 0-20: Low risk
  - 20-40: Moderate risk
  - 40-60: High risk
  - 60-80: Very high risk
  - 80-100: Extreme risk

You can then choose to see pesticide recommendations based on returned PMI score.

## Example Input For Testing:
PMI of Napa Valley, CA from 06/07/2024 to 06/14/2024
- latitude: 38.5025
- longitude: -122.2654
- start date: 06/07/2024
- end date: 06/14/2024