import os
import json
import requests
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class Regression:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_true_path = os.path.join(current_dir, '../INaturalist_Scraper/Data/true_observations.json') # remove .. if filepath isn't working
        json_false_path = os.path.join(current_dir, '../INaturalist_Scraper/Data/false_observations.json')

        with open(json_true_path, "r") as file:
            self.true_data = json.load(file)

        with open(json_false_path, "r") as file:
            self.false_data = json.load(file)

        self.true_lons = []
        self.true_lats = []
        self.true_years = []
        self.true_months = []
        self.true_days = []
        for point in self.true_data:
            self.true_lons.append(point['coordinates'][0])
            self.true_lats.append(point['coordinates'][1])
            self.true_years.append(point["date"]["year"])
            self.true_months.append(point["date"]["month"])
            self.true_days.append(point["date"]["day"])

        self.false_lons = []
        self.false_lats = []
        self.false_years = []
        self.false_months = []
        self.false_days = []
        for point in self.false_data:
            self.false_lons.append(point['coordinates'][0])
            self.false_lats.append(point['coordinates'][1])
            self.false_years.append(point["date"]["year"])
            self.false_months.append(point["date"]["month"])
            self.false_days.append(point["date"]["day"])
            
        self.regression_driver()

    def regression_driver(self):
        while(True):
            try:
                user_input = int(input("How many data points would you like to use to train? (up to 160): "))
                if user_input <= 160:
                    break
            except(ValueError):
                pass
        
        while (True):
            self.user_type = input("Enter T to use temperature, H to use humidity, and Y for time of year: ")
            if self.user_type in ["t", "T", "h", "H", "y", "Y"]:
                break
        
        self.results = []
        self.avg_temps = []
        self.avg_humidities = []
        self.time_of_years = []
        if self.user_type in ["t", "T"]: 
            for i in range(user_input):
                self.get_sample_temps(self.true_lons[i], self.true_lats[i], self.true_days[i], self.true_months[i], self.true_years[i])
                self.results.append(1) # true result so 1
                self.get_sample_temps(self.false_lons[i], self.false_lats[i], self.false_days[i], self.false_months[i], self.false_years[i])
                self.results.append(-1) # false result so -1 (bipolar) (could be 0 instead)
            self.plot_regression_temps()
        
        elif self.user_type in ["h", "H"]:
            for i in range(user_input):
                self.get_sample_humidity(self.true_lons[i], self.true_lats[i], self.true_days[i], self.true_months[i], self.true_years[i])
                self.results.append(1) # true result so 1
                self.get_sample_humidity(self.false_lons[i], self.false_lats[i], self.false_days[i], self.false_months[i], self.false_years[i])
                self.results.append(-1) # false result so -1 (bipolar) (could be 0 instead)
            self.plot_regression_humidity()
        
        else:
            for i in range(user_input):
                self.time_of_years.append([self.true_months[i]])
                self.results.append(1) # true result so 1
                self.time_of_years.append([self.false_months[i]])
                self.results.append(-1) # false result so -1 (bipolar) (could be 0 instead)
            self.plot_regression_time()
    
    def plot_regression_temps(self):
        model = LinearRegression()

        # Train the model on the training data
        model.fit(self.avg_temps, self.results)

        # Plot the data and the regression line
        plt.scatter(self.avg_temps, self.results, color='blue', label='Data points')
        plt.plot(self.avg_temps, model.predict(self.avg_temps), color='red', label='Regression line')
        plt.xlabel('Average Temp')
        plt.ylabel('Results 1 = Powdery Mildew -1 = No Powdery Mildew')
        plt.legend()
        plt.show()
    
    def plot_regression_humidity(self):
        model = LinearRegression()

        # Train the model on the training data
        model.fit(self.avg_humidities, self.results)

        # Plot the data and the regression line
        plt.scatter(self.avg_humidities, self.results, color='blue', label='Data points')
        plt.plot(self.avg_humidities, model.predict(self.avg_humidities), color='red', label='Regression line')
        plt.xlabel('Average Humidity')
        plt.ylabel('Results 1 = Powdery Mildew -1 = No Powdery Mildew')
        plt.legend()
        plt.show()
    
    def plot_regression_time(self):
        model = LinearRegression()

        # Train the model on the training data
        model.fit(self.time_of_years, self.results)

        # Plot the data and the regression line
        plt.scatter(self.time_of_years, self.results, color='blue', label='Data points')
        plt.plot(self.time_of_years, model.predict(self.time_of_years), color='red', label='Regression line')
        plt.xlabel('Month of year')
        plt.ylabel('Results 1 = Powdery Mildew -1 = No Powdery Mildew')
        plt.legend()
        plt.show()
        
    def get_sample_temps(self, lon, lat, day, month, year):
        url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
        
        month = str(month).zfill(2) # make sure is 2 length
        day = str(day).zfill(2) # same as above
        start_date = int(f"{year}{month}{day}")
        # end_date = int(f"{year}{month}{int(day)+1}")
        
        parameters = {
            # full list of parameters found here: https://power.larc.nasa.gov/api/pages/ 
            "parameters": "T2M",
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "start": start_date,
            "end": start_date,
            "format": "JSON"
        }

        response = requests.get(url, params=parameters)
        data = response.json()
        print("a")

        temperatures_total = 0
        for temperature in data['properties']['parameter']['T2M'].values():
            temperatures_total += (temperature * (9/5)) + 32 # convert to Fahrenheit
        temperature_avg = temperatures_total / 24
        self.avg_temps.append([temperature_avg])

    def get_sample_humidity(self, lon, lat, day, month, year):
        url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
        
        month = str(month).zfill(2) # make sure is 2 length
        day = str(day).zfill(2) # same as above
        start_date = int(f"{year}{month}{day}")
        # end_date = int(f"{year}{month}{int(day)+1}")
        
        parameters = {
            # full list of parameters found here: https://power.larc.nasa.gov/api/pages/ 
            "parameters": "RH2M",
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "start": start_date,
            "end": start_date,
            "format": "JSON"
        }

        response = requests.get(url, params=parameters)
        data = response.json()
        print("b")

        humidity_total = 0
        for humidity in data['properties']['parameter']['RH2M'].values():
            humidity_total += humidity
        humidity_avg = humidity_total / 24
        self.avg_humidities.append([humidity_avg])


if __name__ == "__main__":
    Regression()