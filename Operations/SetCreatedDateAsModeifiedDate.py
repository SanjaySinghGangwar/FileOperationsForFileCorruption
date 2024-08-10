import os
import subprocess
from datetime import datetime


def update_creation_date_to_modified(directory):
    """Update the creation date to match the modification date for all files in the directory."""
    files = os.listdir(directory)
    for file in files:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            # Get the modification time
            modification_time = os.path.getmtime(file_path)
            modification_date = datetime.fromtimestamp(modification_time)

            # Format the modification date to the required format for SetFile
            modification_date_str = modification_date.strftime('%m/%d/%Y %H:%M:%S')

            try:
                # Update the creation date to match the modification date using SetFile on macOS
                subprocess.run(['SetFile', '-d', modification_date_str, file_path], check=True)
                print(f"Updated creation date for {file} to {modification_date_str}")
            except Exception as e:
                print(f"Failed to update creation date for {file}: {e}")


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"
update_creation_date_to_modified(directory_path)
