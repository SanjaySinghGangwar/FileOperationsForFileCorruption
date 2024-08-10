import os
from datetime import datetime


def list_files_with_dates(directory):
    """List all files in the directory with creation and modification dates."""
    files = os.listdir(directory)
    for file in files:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            creation_time = os.path.getctime(file_path)
            modification_time = os.path.getmtime(file_path)
            creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
            modification_date = datetime.fromtimestamp(modification_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"File: {file}")
            print(f"Creation Date: {creation_date}")
            print(f"Modification Date: {modification_date}")
            print("-" * 50)


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"
list_files_with_dates(directory_path)
