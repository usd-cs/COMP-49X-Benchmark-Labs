import json

class InvalidPMI(Exception):
    pass

class Recommendation:
    def __init__(self, pmi_index):
        self.pmi = pmi_index
        f = open('recommendations.json', 'r')
        self.json_data = self.create_recommendations(f)

    def create_recommendations(self, json_file):
        data = json.load(json_file)
        if self.pmi >= 0 and self.pmi < 20:
            return data[0]
        elif self.pmi >= 20 and self.pmi < 40:
            return data[1]
        elif self.pmi >= 40 and self.pmi < 60:
            return data[2]
        elif self.pmi >= 60 and self.pmi < 80:
            return data[3]
        elif self.pmi >= 80 and self.pmi <= 100:
            return data[4]
        else:
            raise InvalidPMI(f"Invalid PMI Index: {self.pmi}")
    
    def get_range(self):
        return self.json_data["PMI Value"]
    
    def get_risk_level(self):
        return self.json_data["Risk Level"]

    def get_strategy(self):
        return self.json_data["Fungicide Strategy"]
    
    def get_name(self):
        return self.json_data["Generic Name"]

    def get_application_rate(self):
        return self.json_data["Application Rate"]
    
    def get_frequency(self):
        return self.json_data["Spray Frequency/Stage"]

    def get_additional_notes(self):
        return self.json_data["Additional Notes"]

    def get_full_info(self):
        data = ""
        for key, value in self.json_data.items():
            if isinstance(value, list):
                data += f"{key}:\n"
                for item in value:
                    data += f"{item}\n"
            else:
                data += f"{key}: \n{value}\n\n"

        return data

x = Recommendation(20)
print(x.get_full_info())