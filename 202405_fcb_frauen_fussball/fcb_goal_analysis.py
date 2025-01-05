'''Generates a text file with an analysis of the goals, including: Home vs Away goals, In Favor vs Against, First half vs Second half goals, 
Number of set-piece goals and stoppage time goals, top 10 goalscorers, and split by types of goals'''

import pandas as pd

# Path to the Excel file and the results file
file_path = "./FcBayernWomenGoals.xlsx"
results_file_path = "./FcBayernTeamGoalStats.txt"

# Read the data from the Excel file
data = pd.read_excel(file_path)

# 1. Total goals this season (only 'IN_FAVOR' = TRUE)
total_goals = data[data['IN_FAVOR'] == True].shape[0]

# 2. Total goals at home vs away
home_goals = data[(data['HOME'] == True) & (data['IN_FAVOR'] == True)].shape[0]
away_goals = data[(data['HOME'] == False) & (data['IN_FAVOR'] == True)].shape[0]

# 3. Total goals in the 1st half vs the 2nd half
first_half_goals = data[(data['IN_FAVOR'] == True) & (data['MINUTE'] <= 45)].shape[0]
second_half_goals = data[(data['IN_FAVOR'] == True) & (data['MINUTE'] > 45) & (data['MINUTE'] <= 90)].shape[0]

# 4. Total goals in stoppage time (rows with non-empty 'STOPPAGE_TIME')
stoppage_time_goals = data[(data['IN_FAVOR'] == True) & data['STOPPAGE_TIME'].notna()].shape[0]

# 4b. Total goals from a Set Piece
set_piece_goals = data[(data['ORIGIN'] != 'In Game Action') & (data['IN_FAVOR'] == True)]

# 4c. Header Goals from a set piece
header_set_piece_goals = set_piece_goals['TYPE'].value_counts()

# 5. Goal type statistics with count and percentage
goal_type_count = data[data['IN_FAVOR'] == True]['TYPE'].value_counts()
goal_type_percentage = (goal_type_count / total_goals * 100).round(1)
goal_type_stats = goal_type_count.astype(str) + " (" + goal_type_percentage.astype(str) + "%)"

# 5b. Goals per Origina with count and percentage
goal_origin_count = data[data['IN_FAVOR'] == True]['ORIGIN'].value_counts()
goal_origin_percentage = (goal_origin_count / total_goals * 100).round(1)
goal_origin_stats = goal_origin_count.astype(str) + " (" + goal_origin_percentage.astype(str) + "%)"

# 6. Top 3 goalscorers in the team
top_goalscorers = data[data['IN_FAVOR'] == True]['GOALSCORER'].value_counts().head(10)

# 7. Top header goal scorer with number of header goals
header_goals = data[(data['TYPE'] == 'Header') & (data['IN_FAVOR'] == True)]
top_header_scorer = header_goals['GOALSCORER'].value_counts().head(1)

# 8. Total goals against
goals_against = data[data['IN_FAVOR'] == False].shape[0]

# Output the results to a text file
results_text = f"""Goal Statistics for FC Bayern Women

Total Goals This Season: {total_goals}
Total Goals Against: {goals_against}

Home Goals: {home_goals}
Away Goals: {away_goals}

First Half Goals: {first_half_goals}
Second Half Goals: {second_half_goals}

Stoppage Time Goals: {stoppage_time_goals}
Set Piece Goals: {set_piece_goals.shape[0]}


Top 10 Goalscorers:
{top_goalscorers.to_string()}

Top Header Goal Scorer:
{top_header_scorer.to_string()}


Goal Stats by Type:
{goal_type_stats.to_string()}

Goal Stats by Origin:
{goal_origin_stats.to_string()}

Set Piece Goals sorted by Result:
{header_set_piece_goals.to_string()}
"""

# Save the results to a text file
with open(results_file_path, 'w') as file:
    file.write(results_text)