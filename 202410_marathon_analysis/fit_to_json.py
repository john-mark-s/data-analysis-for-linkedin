# Converts a file in fit format, from a fitness watch, to a JSON file

import fitdecode
import json
from datetime import datetime


# Path to your .fit file
fit_file_path = '' # Path for a Fit File
# Path to save the output JSON file
json_file_path = '' # Path to save output JSON file

# Create a list to hold the records
records = []

# Open and parse the .fit file
with fitdecode.FitReader(fit_file_path) as fit:
    # Iterate over all records in the .fit file
    for frame in fit:
        if isinstance(frame, fitdecode.FitDataMessage):
            record_data = {}
            for field in frame.fields:
                # Convert datetime objects to strings
                if isinstance(field.value, datetime):
                    record_data[field.name] = field.value.isoformat()  # Convert to ISO format
                else:
                    record_data[field.name] = field.value
            records.append(record_data)

# Write the records to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(records, json_file, indent=4)

print(f"Data successfully converted to JSON and saved at {json_file_path}")