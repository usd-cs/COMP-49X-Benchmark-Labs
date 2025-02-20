from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import json

m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,\
            llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
m.drawcoastlines()
m.fillcontinents(color='coral',lake_color='aqua')

with open("observations.json", "r") as file:
    data = json.load(file)

lons = []
lats = []
for point in data:
    lons.append(point['coordinates'][0])
    lats.append(point['coordinates'][1])

# Convert latitude and longitude to x, y map coordinates
x, y = m(lons, lats)

# Plot the points on the map
m.scatter(x, y, color='yellow', marker='.') 

m.drawmapboundary(fill_color='aqua') 
plt.title("INaturalist Data Points")
plt.show()