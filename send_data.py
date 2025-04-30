import csv
import http.client
import json
import urllib.parse

low_income_crimes = 0
high_income_crimes = 0

# Separate wards into bottom and top 50% by median income
low_income_community_areas = []
high_income_community_areas = []

# Community areas in .csv file are sorted from lowest to highest median income
community_areas_low_to_high = []
with open('median_income.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Skip header if exists
    column_index = header.index("AREA_NUM")
    
    for row in reader:
        community_areas_low_to_high.append(row[column_index])

# Separate neighborhoods into lower and upper 50th percentile by median income
for i in range(38):
    low_income_community_areas.append(community_areas_low_to_high[i])

for i in range(39, 77):
    high_income_community_areas.append(community_areas_low_to_high[i])


# Prints the lists containing the ordered community area data for testing purposes
print(high_income_community_areas)
print(low_income_community_areas)

# Replace with actual port
#Arduino is COM4
# port = 'COM4'

# Match rate with Arduino sketch
baud_rate = 9600

# ser = serial.Serial(port, baud_rate)


# Make request to Chicago Data Portal
conn = http.client.HTTPSConnection("data.cityofchicago.org")
headers = { 
     "Content-Type": "application/json"    
}
conn.request("GET", "/resource/ijzp-q8t2.json", None, headers)
res = conn.getresponse()
data = res.read()

# Store data
parsed_data = json.loads(data)
area_data = []

current_date = ''

# Stores community area data for every crime committed on the last day the database was updated
flags = True
for obj in parsed_data:
    if(flags):
        current_date = obj["date"][:10]
        print("Checking for Crimes committed on " + str(current_date) + "(Latest Update from Crime Database)")
        flags = False

    if(obj["date"][:10] == current_date):
        area_data.append(obj["community_area"])

# Checks if a crime was committed in a neighborhood in the bottom 50% by median income
def checkLowIncomeArea(curr_community_area):
    global low_income_crimes
    for i in low_income_community_areas:
        if(curr_community_area == i):
            low_income_crimes += 1
            return True
    return False

# Checks if a crime was committed in a neighbordhood in the top 50% by median income
def checkHighIncomeArea(curr_community_area):
    global high_income_crimes
    for i in high_income_community_areas:
        if(curr_community_area == i):
            high_income_crimes += 1
            break

# Counts number of crimes committed in each neighborhood category
for curr_community_area in area_data:
    flags = checkLowIncomeArea(curr_community_area)
    if(not flags):
       checkHighIncomeArea(curr_community_area)
    
# Prints data to console for testing purposes
print(f"Crimes in High Income Areas(Upper 50th Percentile by Median Income): %d" % high_income_crimes)
print(f"Crimes in Low Income Areas(Lower 50th Percentile by Median Income): %d" % low_income_crimes)

# Make Request to Particle 
conn = http.client.HTTPSConnection("api.particle.io")
headers = { 
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": "Bearer 0bc4afe21c459b013f67dd0335eaf917bf75144c"    
}
arg_value = '{"low_income_area_crime": "' + str(low_income_crimes) + '", "high_income_area_crime": "' + str(high_income_crimes) +'"}'
body = urllib.parse.urlencode({"arg": arg_value})
print(arg_value)

conn.request("POST", "/v1/devices/0a10aced202194944a0556d4/getData/", body, headers)
res = conn.getresponse()
data = res.read()

# Check format for testing purposes
# ser.print('[{"low_income_area_crime": "%d"}, {"high_income_area_crime": "%d"}]' % low_income_crimes, high_income_crimes)
