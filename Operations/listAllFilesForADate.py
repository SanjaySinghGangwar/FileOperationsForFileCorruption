import os
from datetime import datetime


def list_files_by_date(directory, target_date):
    """List all files in the given directory that match the specified date."""
    target_date = datetime.strptime(target_date, '%Y-%m-%d')
    matching_files = []

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        # Get the file's creation and modification times
        creation_time = os.path.getctime(file_path)
        modified_time = os.path.getmtime(file_path)

        # Convert to datetime objects
        creation_date = datetime.fromtimestamp(creation_time).date()
        modified_date = datetime.fromtimestamp(modified_time).date()

        # Check if either the creation or modification date matches the target date
        if creation_date == target_date.date() or modified_date == target_date.date():
            matching_files.append(file)

    return matching_files


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"
date_to_search = "2024-06-02"  # Specify the target date in YYYY-MM-DD format

# Get the list of files that match the target date
files_on_date = list_files_by_date(directory_path, date_to_search)

# Print the files found
if files_on_date:
    print(f"Files found on {date_to_search}:")
    for file in files_on_date:
        print(file)
else:
    print(f"No files found on {date_to_search}.")
