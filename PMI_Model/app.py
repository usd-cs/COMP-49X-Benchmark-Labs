from model import Model
from datetime import datetime, timedelta

# Get input coordinates from the user
def get_valid_coordinates():
    while True:
        try:
            lat = float(input("Enter latitude: "))
            long = float(input("Enter longitude: "))
            if -90 <= lat <= 90 and -180 <= long <= 180:
                return lat, long
            else:
                print("Invalid coordinates")
        except ValueError:
            print("Please enter valid numbers for coordinates.")

# Get input start and end dates from the user
def get_valid_date(prompt):
    while True:
        try:
            date_str = input(prompt + " (MM/DD/YYYY): ")
            date = datetime.strptime(date_str, "%m/%d/%Y")
            return date
        except ValueError:
            print("Please enter a valid date in the format MM/DD/YYYY")

def main():
    print("Welcome to the Powdery Mildew Index Calculator!")
    print("Please enter your location coordinates:")
    
    # Get coordinates from the user
    lat, long = get_valid_coordinates()
    
    # Get date range from user
    print("\nEnter the date range for PMI calculation:")
    start_date = get_valid_date("Start date")
    end_date = get_valid_date("End date")
    
    # Ensure end date is after start date
    if end_date <= start_date:
        print("End date must be after start date")
        return
    
    # Convert dates to required format (YYYYMMDD)
    start_day = int(start_date.strftime("%Y%m%d"))
    end_day = int(end_date.strftime("%Y%m%d"))
    
    # Create model and calculate risk index
    model = Model(lat, long, start_day, end_day)
    risk_index = model.get_risk_index()
    
    if risk_index == -1:
        print("\nUnable to calculate PMI for your location. Please try different coordinates or dates.")
        return
    
    print(f"\nYour Powdery Mildew Index (PMI) is: {risk_index}")
    
    # Ask about recommendations
    while True:
        see_recommendations = input("\nWould you like to see pesticide recommendations? (yes/no): ").lower()
        if see_recommendations in ['yes', 'no', 'y', 'n']:
            break
        print("Please enter 'yes' or 'no'")
    
    if see_recommendations.startswith('y'):
        print("\nPesticide Recommendations:")
        print("-" * 50)
        print(model.get_pesticide_recommendation())

if __name__ == "__main__":
    main()
