import requests
from datetime import datetime, timedelta

class Data: 
    def __init__(self, lat, lon, start_date, end_date):
        """
        Makes an API request and formats the temperature data into a dictionary

        Args:
        lat: latitude of location (int)
        long: longitude of location (int)
        start_date: day to start parsing in form of YYYYMMDD (int)
        end_date: day to end parsing in form of YYYYMMDD (int)
        """
        url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
        parameters = {
            # full list of parameters found here: https://power.larc.nasa.gov/api/pages/ 
            # T2M is temperature at 2m above ground
            "parameters": "T2M",

            # Community is type of data, AG is agriculutral
            "community": "AG",

            "latitude": lat,
            "longitude": lon,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }

        response = requests.get(url, params=parameters)
        data = response.json()

        temperatures = {}
        for date_time, temperature in data['properties']['parameter']['T2M'].items():
            temperatures[date_time] = (temperature * (9/5)) + 32 # convert to Fahrenheit
        # in the form of a dictionary, key is YYYYMMDDTT value is temperature in Fahrenheit
        self.temperature_data = temperatures

    def get_data(self):
        """
        Returns the temperature data from the Data object
        
        return: dictionary
        """
        return self.temperature_data

    def check_consecutive_temp(self, temperature_data, day):
        """
        Checks if temperature has 6 hours of temperatures between 70 and 85 degrees returns True if so, False if not
       
        Args:
        temperature_data: temperature data to use (dictionary)
        day: day to check (int)
        
        return: boolean
        """
        curr_string = f"{day}00"
        count = 0
         # 24 hours in a day
        for i in range(24):
            if i < 10:
                curr_string = f"{curr_string[:8]}0{i}"
            else:
                curr_string = f"{curr_string[:8]}{i}"
            if temperature_data[curr_string] >= 70 and temperature_data[curr_string] <= 85:
                count += 1
        if count >= 6:
            return True
        return False
    
    def get_start_day(self, temperature_data, start_day, end_day):
        """
        Find the first day of atleast 3 consecutive days of temps between 70 and 85 for a minimum of 6 hours.
        The first day is found starting from the end date, so it's closest to the end of the time frame.

        Args:
        temperature_data: temperature data to use (dictionary)
        start_day: day to start parsing in form of YYYYMMDD (int)
        end_day: day to end parsing in form of YYYYMMDD (int)

        return: int
        """
        curr_day = end_day
        continuous_days = 0
        while True:
            if self.check_consecutive_temp(temperature_data, curr_day):
                continuous_days += 1
            else: 
                if continuous_days >= 3:
                    date_obj = datetime.strptime(str(curr_day), "%Y%m%d")
                    previous_day = date_obj + timedelta(days=1)
                    return int(previous_day.strftime("%Y%m%d"))
                    
                else:
                    continuous_days = 0
                    
            if curr_day == int(start_day):
                if continuous_days >= 3:
                    return curr_day
                else:
                    return -1

            date_time = datetime.strptime(str(curr_day), "%Y%m%d")
            previous_day = date_time - timedelta(days=1)
            curr_day = int(previous_day.strftime("%Y%m%d")) # format to previous format


    def check_single_temp(self, temperature_data, day):
        """
        Checks if the temperature goes below 70 degrees or above 85 degrees for over 45 minutes during a specified day

        Args:
        temperature_data: temperature data to use (dictionary)
        day: day to check (int)
        
        return: boolean
        """
        # 24 hours in a day
        curr_string = f"{day}00"
        for i in range(24):
            if i < 10:
                curr_string = f"{curr_string[:8]}0{i}"
            else:
                curr_string = f"{curr_string[:8]}{i}"
                
            if temperature_data[curr_string] <= 70 or temperature_data[curr_string] >= 85:
                return True
        return False
    
    def check_high_temp(self, temperature_data, day):
        """
        Checks if the temperature went above 95 degrees for the given day
        
        Args:
        temperature_data: temperature data to use (dictionary)
        day: day to check (int)
        
        return: boolean
        """
        curr_string = f"{day}00"
        for i in range(24):
            if i < 10:
                curr_string = f"{curr_string[:8]}0{i}"
            else:
                curr_string = f"{curr_string[:8]}{i}"
            if temperature_data[curr_string] >= 95:
                return True
        return False
    
