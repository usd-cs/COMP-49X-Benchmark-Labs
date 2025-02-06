"""
File to be used by the dockerfile to be tested
"""

from model import Model

latitude = 37.7749    
longitude = -122.4194 
start_date = "20231001" 
end_date = "20231008"  

model = Model(latitude, longitude, start_date, end_date)
risk_index = model.get_risk_index()

print(f"Your Powdery Mildew Index (PMI) is: {risk_index}")