# Webscrape the play-by-play data for each game for a specific season from Basketball Reference

import os
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Read the existing CSV
df = pd.read_csv('LAL_2022_games.csv')

# Ensure output directory exists
output_dir = "LAL_2022_season" # 2022
os.makedirs(output_dir, exist_ok=True)

# List of headers to randomize from
headers_list = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
]

# Set the testing limit (set to None or remove the check when ready)
processed_count = 0  # Counter to track processed games
request_count = 0  # Tracks the number of requests in the current minute

# Loop through the Box Score URLs
for index, row in df.iterrows():
    # if request_count == 20:  # Stop after processing one game
    #     print(f"Test limit reached. Stopping.")
    #     break
    
    box_score_url = row[4]  # Extract the Box Score URL
    print(box_score_url)
    
    # Skip rows with missing or invalid Box Score URLs
    if pd.isna(box_score_url) or not isinstance(box_score_url, str):
        print(f"Skipping row {index}: Invalid Box Score URL")
        continue
    
    # Modify the URL to include /pbp/
    pbp_url = box_score_url.replace('/boxscores/', '/boxscores/pbp/')
    
    # Extract the unique identifier from the URL for the file name
    game_id = pbp_url.split('/')[-1].replace('.html', '')  # Get "202110190LAL"
    output_file = f"{output_dir}/{game_id}_Play_by_Play.csv"  # Create a unique file name
    
    print(f"Scraping Play-by-Play data from: {pbp_url}")
    
    # Randomly select headers for this request
    headers = random.choice(headers_list)
    
    # Send a GET request to the modified URL with random headers
    response = requests.get(pbp_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {pbp_url}: HTTP {response.status_code}")
        processed_count += 1  # Increment the counter even if fetch fails
        request_count += 1
        time.sleep(5)  # Adjust the delay as needed
        continue

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the Play-by-Play table
    pbp_table = soup.find('table', {'id': 'pbp'})
    
    # Find the Play-by-Play table
    pbp_table = soup.find('table', {'id': 'pbp'})
    if not pbp_table:
        print(f"No play-by-play table found for {pbp_url}")
        request_count += 1
        processed_count += 1
        time.sleep(5)  # Adjust the delay as needed
        continue

    # Extract rows, accounting for cases where <tbody> may not exist
    rows = pbp_table.find_all('tr')  # Find all <tr> elements directly

    # Extract data from each row
    pbp_data = []
    for row in rows:
        cells = row.find_all(['td', 'th'])  # Get all <td> and <th> elements
        row_data = [cell.get_text(strip=True) for cell in cells]  # Extract and clean text
        pbp_data.append(row_data)

    # Check if any rows were extracted
    if not pbp_data:
        print(f"No data rows found in the table for {pbp_url}")
        request_count += 1
        processed_count += 1
        time.sleep(5)  # Adjust the delay as needed
        continue

    # Save the Play-by-Play data to a CSV file
    pbp_df = pd.DataFrame(pbp_data)
    pbp_df.to_csv(output_file, index=False, header=False)
    print(f"Play-by-Play data saved to '{output_file}'")

    
    # Increment the counters
    processed_count += 1
    request_count += 1

    # Respect rate limit: Pause if 20 requests have been made
    if request_count >= 19:
        print(f"Rate limit reached. Pausing for 60 seconds.")
        time.sleep(60)  # Pause for 60 seconds
        request_count = 0  # Reset the request counter

    # Short delay between requests to reduce server load
    time.sleep(5)  # Adjust the delay as needed