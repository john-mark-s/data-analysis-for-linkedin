# Reads and analyzes marathon data from a JSON file and creates and excel and visualisations

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# Load JSON data
json_file_path = '' # File path to the JSOn file with fitness data
with open(json_file_path, 'r') as f:
    data = json.load(f)

# Parse data into a DataFrame
records = []
for entry in data:
    if 'timestamp' in entry:
        record = {
            'timestamp': entry['timestamp'],
            'heart_rate': entry.get('heart_rate'),
            'cadence': entry.get('cadence'),
            'speed': entry.get('speed'),
            'distance': entry.get('distance'),
            'position_lat': entry.get('position_lat'),
            'position_long': entry.get('position_long')
        }
        records.append(record)

df = pd.DataFrame(records)

# Convert the timestamp to datetime and ensure it's timezone-unaware
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)

# Drop rows with missing values in position
df = df.dropna(subset=['position_lat', 'position_long'])

# Convert semicircles to degrees (latitude and longitude)
def semicircles_to_degrees(semicircles):
    return (semicircles / 2**31) * 180

df['latitude'] = df['position_lat'].apply(semicircles_to_degrees)
df['longitude'] = df['position_long'].apply(semicircles_to_degrees)

# Define the folder to save graphics
graphics_folder = os.path.dirname(json_file_path)

# --- Visualization 1: Time Series Line Graphs ---
# Heart Rate over Time
plt.figure(figsize=(10, 6))
plt.plot(df['timestamp'], df['heart_rate'], label='Heart Rate', color='red')
plt.title('Heart Rate over Time')
plt.xlabel('Time')
plt.ylabel('Heart Rate (bpm)')
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(graphics_folder, 'heart_rate_over_time.png'))
plt.close()

# Convert speed from m/s to minutes per kilometer
df['speed_km_h'] = df['speed'] * 3.6  # Convert speed to km/h
df['minutes_per_km'] = 60 / df['speed_km_h']  # Convert speed to min/km

# Average minutes per kilometer every 3 minutes
df.set_index('timestamp', inplace=True)  # Set timestamp as the index
avg_minutes_per_km_per_minute = df['minutes_per_km'].resample('8min').mean().reset_index()  # Resample to 3-minute intervals

# Plotting Average Minutes per Kilometer over Time
plt.figure(figsize=(10, 6))
plt.plot(avg_minutes_per_km_per_minute['timestamp'], avg_minutes_per_km_per_minute['minutes_per_km'], label='Average Pace (min/km)', color='orange')
plt.title('Average Pace (min/km) over Time')
plt.xlabel('Time')
plt.ylabel('Pace (min/km)')
plt.grid(True)

# Formatting the x-axis to display only hour and minute
plt.xticks(rotation=45)
ax = plt.gca()  # Get current axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Format x-axis to display hours and minutes

# Set x-ticks to show every 30 minutes
plt.xticks(avg_minutes_per_km_per_minute['timestamp'][::30], rotation=45)  # Adjust this slice based on your data frequency
plt.legend()
plt.savefig(os.path.join(graphics_folder, 'average_pace_over_time.png'))
plt.close()

# --- Visualization 2: Heart Rate vs Distance ---
plt.figure(figsize=(10, 6))
plt.plot(df['distance'], df['heart_rate'], label='Heart Rate', color='green')
plt.title('Heart Rate vs Distance')
plt.xlabel('Distance (m)')
plt.ylabel('Heart Rate (bpm)')
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(graphics_folder, 'heart_rate_vs_distance.png'))
plt.close()

# --- Visualization 3: Average Speed (km/min) vs Distance ---
# Convert speed from m/s to km/h
df['speed_km_h'] = df['speed'] * 3.6  # Convert speed to km/h
print(df['speed_km_h'])

# Calculate pace in minutes per kilometer
df['minutes_per_km'] = 60 / df['speed_km_h']  # Convert speed to min/km
print(df['minutes_per_km'])

# Calculate the average speed in km/min
# Average pace is already in minutes per km; now calculate average speed
# You can also resample based on distance here if needed

# Resample by distance to get average pace for each distance point
avg_speed_per_distance = df[['distance', 'minutes_per_km']].groupby('distance').mean().reset_index()

# Calculate Average Speed in km/min
avg_speed_per_distance['Average Speed (km/min)'] = 1 / avg_speed_per_distance['minutes_per_km']

# Rename the column
avg_speed_per_distance = avg_speed_per_distance[['distance', 'Average Speed (km/min)']]




# --- Visualization 5: Heart Rate Zones Histogram ---
# Define non-overlapping heart rate zones based on your MHR
heart_rate_zones = [95, 115, 134, 153, 172, 191]  # Adjusted to be exclusive
zone_labels = ['Low', 'Moderate', 'High', 'Very High', 'Max Effort']

# Use pd.cut to categorize heart rates into zones
df['hr_zone'] = pd.cut(df['heart_rate'], bins=heart_rate_zones, labels=zone_labels, right=False)

# Calculate the time spent in each zone in seconds
time_spent_in_zones = df['hr_zone'].value_counts().sort_index() * (1/60)  # Counts to minutes
time_spent_in_zones_hours = time_spent_in_zones / 60  # Convert minutes to hours

# Prepare DataFrame for visualization
time_spent_in_zones_df = time_spent_in_zones_hours.reset_index()
time_spent_in_zones_df.columns = ['Heart Rate Zone', 'Time Spent (hours)']

# Plotting the Time Spent in Heart Rate Zones
plt.figure(figsize=(10, 6))
time_spent_in_zones_df.plot(kind='bar', x='Heart Rate Zone', y='Time Spent (hours)', color=['blue', 'green', 'orange', 'red'])
plt.title('Heart Rate Zones Distribution')
plt.xlabel('Heart Rate Zones (bpm)')
plt.ylabel('Time Spent in Zone (hours)')
plt.xticks(ticks=range(len(time_spent_in_zones_df)), labels=[f'{heart_rate_zones[i]}-{heart_rate_zones[i + 1]}' for i in range(len(heart_rate_zones) - 1)], rotation=0)
plt.grid(True)
plt.savefig(os.path.join(graphics_folder, 'heart_rate_zones_distribution.png'))
plt.close()


# Define the path for the Excel file
excel_file_path = os.path.join(graphics_folder, 'aggregated_data_8min.xlsx')

# Create a new Excel writer object using xlsxwriter
with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
    # Write Heart Rate Zones Data
    time_spent_in_zones_df.to_excel(writer, sheet_name='Heart Rate Zones', index=False)

    # Write Average Pace Data
    avg_pace_df = avg_minutes_per_km_per_minute.rename(columns={'minutes_per_km': 'Average Pace (min/km)'})
    avg_pace_df.to_excel(writer, sheet_name='Average Pace', index=False)
    
    # Write Average Speed Data
    avg_speed_df = avg_speed_per_distance.rename(columns={'speed_km_min': 'Average Speed (km/min)'})
    avg_speed_df.to_excel(writer, sheet_name='Average Speed', index=False)

print(f"Excel file saved at: {excel_file_path}")