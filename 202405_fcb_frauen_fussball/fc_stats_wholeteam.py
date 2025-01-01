# Generates one on the field visualization for the whole team showing where most the goals are scored from.

import matplotlib.pyplot as plt  
import pandas as pd  
import os  
  
# Define soccer field dimensions  
field_length = 105  # Length of the field in meters (between 100 and 110 meters)  
field_width = 68    # Width of the field in meters (between 64 and 75 meters)  
  
# Path of the Excel file  
file_path = ""  # File path to an excel with the goals throughout the season
  
# Read the data from the Excel file  
data = pd.read_excel(file_path)  
  
# Calculate the scaled x and y coordinates  
x = data['X'] * field_length / 100  
y = data['Y'] * field_width / 100  
  
# Load and display the image of the field as a background  
img = plt.imread("")  # File path to an SVG file of a soccer field 
  
# Create the visualization with the field image as background  
plt.figure(figsize=(12, 8))  
plt.imshow(img, extent=[0, field_length, 0, field_width], alpha=0.8)  # Adjust alpha for a denser blue color  
  
# Plot the points on the field  
plt.scatter(x, y, c='red')  # Change color as needed  
  
plt.title('Goal Locations')  
plt.xlabel('X Coordinate (m)')  
plt.ylabel('Y Coordinate (m)')  
  
# Add soccer field lines  
plt.axhline(y=0, color='black', linewidth=2)  # Bottom line of the field  
plt.axhline(y=field_width, color='black', linewidth=2)  # Top line of the field  
  
# Save the figure as an SVG in the same directory as the Excel file  
output_path = os.path.join(os.path.dirname(file_path), "goal_locations.svg")  
plt.savefig(output_path, format='svg')  
  
plt.show()