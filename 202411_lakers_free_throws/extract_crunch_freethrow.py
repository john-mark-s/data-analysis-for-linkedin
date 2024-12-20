# Extracts free throw data from all games from several seasons, but limited to 'chrunch time'

import os
import pandas as pd

# Specify the folder containing the CSV files
folder_path = "" # add folder path
output_excel = os.path.join(folder_path, "Filtered_Free_Throws.xlsx")

# Initialize a list to store data from all games
all_games_data = []

# Loop through all CSV files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".csv"):
        file_path = os.path.join(folder_path, file_name)
        
        # Extract the desired section from the file name
        game_identifier = file_name.split('_')[0]  # Extract '202110190LAL'

        # Read the CSV file with no headers initially
        df = pd.read_csv(file_path, header=None)

        # Use the second row as the header
        df.columns = df.iloc[1]
        df = df[2:].reset_index(drop=True)

        # Identify the start of the 4th quarter
        fourth_quarter_index = df[df.iloc[:, 0].str.contains("4th Q", na=False)].index[0]

        # Filter rows starting from the 4th quarter
        df_4th_quarter = df.iloc[fourth_quarter_index + 1:].copy()

        # Extract time and filter for the last 3 minutes (<= 3:00.0)
        df_4th_quarter['Time'] = df_4th_quarter.iloc[:, 0]
        df_4th_quarter = df_4th_quarter[df_4th_quarter['Time'].str.match(r'^[0-3]:\d{2}\.\d$', na=False)]

        # Filter for 'makes free throw' and 'misses free throw' in any column
        search_terms = 'makes free throw|misses free throw'
        filtered_df = df_4th_quarter[
            df_4th_quarter.apply(lambda row: row.astype(str).str.contains(search_terms, na=False).any(), axis=1)
        ]

        # Drop rows where 'LA Lakers' column is NaN
        filtered_df = filtered_df.dropna(subset=['LA Lakers'])

        # Add a column for the game identifier
        filtered_df['Game'] = game_identifier

        # Keep only the desired columns
        columns_to_keep = ['Time', 'Score', 'LA Lakers', 'Game'] + [col for col in filtered_df.columns if pd.isna(col)]
        filtered_df = filtered_df[columns_to_keep]

        # Add to list of all games data
        all_games_data.append(filtered_df)

# Combine all games data into a single DataFrame
final_df = pd.concat(all_games_data, ignore_index=True)

# Combine the last two columns of final_df into one, applying the condition
final_df['Free throws made'] = final_df.iloc[:, -2:].apply(
    lambda row: 1 if row.notna().any() else pd.NA, axis=1
)

# Drop the two original columns after combining them
# final_df = final_df.drop(columns=final_df.columns[-2:])

# Reorder the columns if necessary, placing 'Free throws made' in the correct position
columns_to_keep = ['Time', 'Score', 'LA Lakers', 'Game', 'Free throws made']
final_df = final_df[columns_to_keep]


# Replace 'makes free throw' and 'misses free throw' with the prefix '_'
final_df['LA Lakers'] = final_df['LA Lakers'].apply(lambda x: x.replace('makes free throw', '_makes free throw') if 'makes free throw' in x else x)
final_df['LA Lakers'] = final_df['LA Lakers'].apply(lambda x: x.replace('misses free throw', '_misses free throw') if 'misses free throw' in x else x)

# Split the 'LA Lakers' column at the first underscore ('_') into 'Player' and 'Action'
final_df[['Player', 'Action']] = final_df['LA Lakers'].str.split('_', n=1, expand=True)

# Optional: Drop the original 'LA Lakers' column if no longer needed
final_df = final_df.drop(columns=['LA Lakers'])

columns_to_keep = ['Game', 'Time', 'Player', 'Free throws made', 'Score', 'Action']
final_df = final_df[columns_to_keep]


# Save the final DataFrame to an Excel file
final_df.to_excel(output_excel, index=False)

print(f"Filtered data saved to {output_excel}")