# Converts the training data from an Excel file to a more readable format

import pandas as pd
from datetime import timedelta, datetime

# Function to correct the 'Pace per km' format
def correct_pace_format(pace):
    try:
        # Handle NaN or None values by returning None
        if pd.isna(pace):
            return None

        # Ensure pace is in the 'HH:MM:SS' or 'MM:SS' format
        parts = pace.strip().split(':')
        
        # If it's in HH:MM:SS format, discard the hour part
        if len(parts) == 3:
            # Discard the hours part (e.g., '06:03:00' -> '06:03')
            hours, minutes, seconds = parts
            return f"{minutes}:{seconds:02d}"
        elif len(parts) == 2:
            # It's already in 'MM:SS' format
            minutes, seconds = parts
            return f"{minutes}:{seconds:02d}"
        else:
            print(f"Unexpected format: {pace}")
            return None
        
    except ValueError:
        # Handle invalid formats
        print(f"Invalid pace format: {pace}")
        return None


# Function to convert pace from 'MM:SS' format to total seconds
def pace_to_seconds(pace):
    try:
        # Ensure that the pace is treated as a string
        pace_str = str(pace)
        
        # Split the pace into minutes and seconds
        parts = pace_str.strip().split(':')
        
        if len(parts) == 2:  # Handle 'M:SS' and 'MM:SS' formats
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            print(f"Unexpected format: {pace_str}")
            return None
    except ValueError:
        # Handle cases where the format is not correct
        print(f"Invalid pace format: {pace}")
        return None

# Function to convert seconds back to 'MM:SS' format
def seconds_to_pace(seconds):
    minutes = seconds // 60
    remaining_seconds = int(seconds % 60)
    return f"{int(minutes):02d}:{remaining_seconds:02d}"

# Load the Excel sheet
json_file_path = '' # File path to an Excel file called 'masterdata.xlsx'
df = pd.read_excel(json_file_path)

# Ensure proper date formatting
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

# Ensure 'Pace per km' is treated as a string and correct the format
df['Pace per km'] = df['Pace per km'].astype(str).apply(correct_pace_format)

# Convert the 'Pace per km' to seconds for easier calculations
df['Pace (seconds per km)'] = df['Pace per km'].apply(pace_to_seconds)

# Calculate total distance
total_distance = df['Total Distance'].sum()

# Calculate total time (sum of (distance * pace in seconds))
total_time_seconds = (df['Total Distance'] * df['Pace (seconds per km)']).sum()
total_time = timedelta(seconds=int(total_time_seconds))

# Calculate average pace
average_pace_seconds_per_km = total_time_seconds / total_distance
average_pace = seconds_to_pace(average_pace_seconds_per_km)

# Group by weeks and calculate total distance per week
df['Week'] = df['Date'].dt.isocalendar().week
weekly_distances = df.groupby('Week')['Total Distance'].sum()

# Define the first run date for calculating the start day of each week
first_run_date = datetime(2023, 12, 17)  # Adjust this to match your actual first run date

# Function to calculate the start day for each week
def get_start_day(week_num):
    days_offset = (week_num - 1) * 7
    return first_run_date + timedelta(days=days_offset)

# Create a new column 'Start Day' based on the week number
weekly_distances_df = pd.DataFrame(weekly_distances).reset_index()
weekly_distances_df.columns = ['Week', 'Total Distance (km)']
weekly_distances_df['Start Day'] = weekly_distances_df['Week'].apply(get_start_day)

# Function to generate all 7 days of the week based on the start day
def generate_week_days(start_day):
    return [start_day + timedelta(days=i) for i in range(7)]

# Add a new column 'Week Days' containing a list of each day of the week
weekly_distances_df['Week Days'] = weekly_distances_df['Start Day'].apply(generate_week_days)

# Add a 'Month' column to the original dataframe for monthly calculations
df['Month'] = df['Date'].dt.to_period('M')

# Group by month and calculate total distance per month
monthly_distances = df.groupby('Month')['Total Distance'].sum()

# Write results to a new Excel file using xlsxwriter
output_path = '' # File path to save the Excel file

with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
    # Write the original dataframe with calculations
    df.to_excel(writer, sheet_name='Run Data', index=False)

    # Create a new sheet for summary statistics
    workbook = writer.book
    summary_sheet = workbook.add_worksheet('Summary')

    # Write summary statistics
    summary_sheet.write('A1', 'Total Distance (km)')
    summary_sheet.write('B1', f"{total_distance:.2f}")

    summary_sheet.write('A2', 'Total Time Running')
    summary_sheet.write('B2', str(total_time))

    summary_sheet.write('A3', 'Average Pace (per km)')
    summary_sheet.write('B3', average_pace)

    # Create a new sheet for weekly distance progression
    weekly_distances_df.to_excel(writer, sheet_name='Weekly Progression', index=False)

    # Create a new sheet for monthly distance progression
    monthly_distances_df = pd.DataFrame(monthly_distances).reset_index()
    monthly_distances_df.columns = ['Month', 'Total Distance (km)']
    monthly_distances_df.to_excel(writer, sheet_name='Monthly Progression', index=False)

print(f"Results saved to {output_path}")