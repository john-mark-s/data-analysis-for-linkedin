'''Generates a text field using the location of each goal scored to categorize the team's goals inside the goal area, in the penalty area or outside the area'''

import pandas as pd

# Function to calculate goal distribution based on defined areas and categorize by origin
def get_goal_distribution(data, in_favor, total_goals):
    # Helper function to determine area
    def determine_area(x, y):
        if (
            ((x >= 0) & (x <= 5) & (y >= 37) & (y <= 64))
            or ((x >= 95) & (x <= 100) & (y >= 37) & (y <= 64))
        ):
            return "Inside Goal Area"
        elif (
            ((x >= 0) & (x <= 15) & (((y >= 22) & (y <= 36)) | ((y >= 65) & (y >= 79)) | ((y >= 37) & (y <= 64) & (x >= 6))))
            or ((x >= 85) & (x <= 100) & (((y >= 22) & (y <= 36)) | ((y >= 65) & (y >= 79))))
            or ((x >= 85) & (x <= 94) & ((y >= 37) & (y <= 64)))
        ):
            return "In Penalty Area"
        else:
            return "Outside Area"
    
    # Add new 'Area' column based on X and Y coordinates
    data["Area"] = data.apply(lambda row: determine_area(row["X"], row["Y"]), axis=1)

    # Get count of goals for each area
    areas = ["Inside Goal Area", "In Penalty Area", "Outside Area"]
    goal_distribution = {}

    for area in areas:
        area_data = data[(data["IN_FAVOR"] == in_favor) & (data["Area"] == area)]
        
        # Calculate total goals and distribution percentages
        total_area_goals = area_data.shape[0]
        area_percentage = (total_area_goals / total_goals) * 100
        
        # Get counts for set pieces and in-game actions
        set_pieces = area_data[area_data["ORIGIN"] != "In Game Action"].shape[0]
        in_game_actions = total_area_goals - set_pieces
        
        # Record data
        goal_distribution[area] = {
            "Total Goals": f"{total_area_goals} ({area_percentage:.1f}%)",
            "Set Pieces": f"{set_pieces} ({(set_pieces / total_area_goals) * 100:.1f}%)",
            "In-Game Actions": f"{in_game_actions} ({(in_game_actions / total_area_goals) * 100:.1f}%)",
        }
    
    return goal_distribution

# Read the data from the Excel file
file_path = "./FcBayernWomenGoals.xlsx"
results_file_path = "./FcBayernGoalDistribution.txt"
data = pd.read_excel(file_path)

# Total goals
total_goals_in_favor = 50
total_goals_against = 6

# Get goal distribution for FC Bayern (Goals In Favor)
goal_distribution_in_favor = get_goal_distribution(data, True, total_goals_in_favor)

# Get goal distribution for goals against
goal_distribution_against = get_goal_distribution(data, False, total_goals_against)

# Write the results to a text file
results_text = f"""
Goal Distribution Stats for FC Bayern Women

Goal Distribution - Goals Scored:
{goal_distribution_in_favor}

Goal Distribution - Goals Against:
{goal_distribution_against}
"""

with open(results_file_path, 'w') as file:
    file.write(results_text)