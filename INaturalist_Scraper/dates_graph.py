import matplotlib.pyplot as plt
import json
from collections import Counter

with open("./Data/true_observations.json", "r") as file:
    data = json.load(file)

years = []
for point in data:
    years.append(point["date"]["year"])

year_counts = Counter(years)

plt.bar(year_counts.keys(), year_counts.values(), color='blue')

plt.xlabel('Year')
plt.ylabel('Number of Photos')
plt.title('Number of Photos by Year')

plt.show()