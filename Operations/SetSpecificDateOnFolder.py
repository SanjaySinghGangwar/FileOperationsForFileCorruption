import os
import subprocess
from datetime import datetime


def set_file_dates_with_touch(directory, specific_date):
    """
    Set the modified and access dates for all files in a directory and its subdirectories
    to a specific date using the `touch` command.
    """
    # Format the specific date for 'touch' command (YYYYMMDDHHMM.SS)
    touch_timestamp = specific_date.strftime('%Y%m%d%H%M.%S')

    # Recursively walk through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)

            if os.path.isfile(file_path):
                try:
                    # Use the 'touch' command to update modification and access dates
                    subprocess.run(['touch', '-t', touch_timestamp, file_path], check=True)
                    print(f"Updated modification and access date for {file_path} to {touch_timestamp}")

                except subprocess.CalledProcessError as e:
                    print(f"Failed to update {file_path}: {e}")


# Example usage
directory_path = '//path'  # Replace with your directory path
specific_date = datetime(2001, 12, 21, 0, 0, 0)  # Date set to 2001-12-21 at midnight

# Set file dates
set_file_dates_with_touch(directory_path, specific_date)
