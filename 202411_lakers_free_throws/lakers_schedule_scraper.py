# Webscraper to extract the 2022 schedule of the Los Angeles Lakers from basketball-reference.com

import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the website
url = 'https://www.basketball-reference.com/teams/LAL/2022_games.html'

# Send a GET request to the website
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table with the specified class
table = soup.find('table', {'id': 'games'})

# Extract the table headers
header_row = table.find('thead').find_all('th')  # Only fetch headers from the table's header section
headers = []
for th in header_row:
    if th.getText() == "Notes":  # Stop at "Notes"
        headers.append(th.getText())
        break
    headers.append(th.getText())

# Add a new column header for the box score URL
headers.append("Box Score URL")


# Extract the table rows
rows = table.find_all('tr')[1:]  # Skip the header row

# Extract the data from each row
data = []
for row in rows:
    th = row.find('th')  # Extract the row header (if any)
    cells = row.find_all('td')
    if cells:
        row_data = [th.getText()] if th else []  # Include the row header
        for cell in cells:
            # Check if the cell contains a link
            link = cell.find('a')
            if link and cell.get('data-stat') == 'box_score_text':
                # If a link exists, append the full URL
                row_data.append("https://www.basketball-reference.com" + link['href'])
            else:
                # Otherwise, append the cell text
                row_data.append(cell.getText())
        data.append(row_data)


# Create a DataFrame from the extracted data
df = pd.DataFrame(data, columns=headers[1:])  # Skip the first header which is empty

# Save the DataFrame to a CSV file
df.to_csv('LAL_2022_games.csv', index=False)

print(df)