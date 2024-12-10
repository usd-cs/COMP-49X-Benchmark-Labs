from data import Data
from datetime import datetime, timedelta
from recommendation import Recommendation, InvalidPMI

class Model:
    """

    https://power.larc.nasa.gov/data-access-viewer/ 

    https://ipm.ucanr.edu/DISEASE/DATABASE/grapepowderymildew.html#:~:text=26-,Conidial%20stage,reset%20the%20index%20to%20zero 

    Input variables
    Environmental: Hourly average temperature, daily maximum temperature

    Calculated: Daily average temperature; daily value of number of hours 
    that 70<=T<=85 F, amount of time that temperature is above 95 F.

    Model: 
    1. The start of the conidial stage of the model is triggered early in the growing season by 
    three consecutive days with six consecutive hours of temperatures between 70 and 85 F; for 
    each of these three days, the model assigns 20 points to the disease risk index.

    2. The conidial infection index increases by 20 points on each subsequent day where at least 
    six continuous hours of temperatures between 70 and 85 F occur.

    3. If there are less than six consecutive hours of temperatures between 70 and 85 F, 10 points
    are subtracted from the index. This is the case if the temperature falls below 70 or goes above 
    85 for more than 45 minutes, since this amount of time is considered to break the accumulation 
    of conducive temperature hours.

    4. If the temperature is 95 F or higher for at least 15 minutes, 10 points are subtracted from 
    the index for the day.

    5. If on the same day with 6 continuous hours between 70-85 F the temperature exceeds 95 F for 
    15 minutes or more, then the model adds 20 points for the six hours but subtracts 10 points due 
    to the high temperature. Thus, for that day the model adds 10 points.

    6. If after subtracting a day's points the index is less than zero, reset the index to zero. If 
    after adding a day's points the index is greater than 100, reset the index to 100.

    7. On any one day the index should not decline by more than 10 points or increase by more than 20 points.

    8. After treatment, the index is reset to zero.
    """

    def __init__(self, lat, long, start_day, end_day, temperature_data = None):
        """
        Sets up the temperature data
        Args:
        lat: latitude of location (int)
        long: longitude of location (int)
        start_day: day to start parsing in form of YYYYMMDD (int)
        end_day: day to end parsing in form of YYYYMMDD (int)
        temperature_data: optional argument to give predetermined data
        """
        self.start_day = start_day
        self.end_day = end_day
        self.lat = lat
        self.long = long
        self.data_obj = Data(lat, long, start_day, end_day)
        if temperature_data != None:
            self.temperature_data = temperature_data
        else:
            self.temperature_data = self.data_obj.get_data()
            
        self.risk_index = None

    def get_risk_index(self):
        """
        Calculates the risk index based on the initialized dataset or location given

        return: int
        """
        start_day = self.data_obj.get_start_day(self.temperature_data, self.start_day, self.end_day)
        if start_day == -1:
            self.risk_index = -1
            return -1
        curr_day = self.start_day
        index = 0
        while True:
            change = 0

            if self.data_obj.check_consecutive_temp(self.temperature_data, curr_day):
                change += 20
            else: 
                change -= 10
            
            if self.data_obj.check_single_temp(self.temperature_data, curr_day):
                change -= 10

            if self.data_obj.check_high_temp(self.temperature_data, curr_day):
                change -= 10

            if change > 20:
                change = 20
            if change < -10:
                change = -10
            index += change
            if index > 100:
                index = 100
            if index < 0:
                index = 0 

            if curr_day == int(self.end_day):
                self.risk_index = index
                return index

            date_time = datetime.strptime(str(curr_day), "%Y%m%d")
            previous_day = date_time + timedelta(days=1)
            curr_day = int(previous_day.strftime("%Y%m%d")) # format to previous format
            
    def get_pesticide_recommendation(self):
        """
        Returns the pesticide recommendation based on the risk index
        """
        
        # If risk index is not calculated, calculate it
        if self.risk_index == None:
            try:
                self.get_risk_index()
            except:
                return "Unable to calculate risk index, please check your input data"
        
        # If risk index is still -1, return error message
        if self.risk_index == -1:
            return "Unable to calculate risk index, please check your input data"
        
        # Return the full recommendation info
        return Recommendation(self.risk_index).get_full_info()
