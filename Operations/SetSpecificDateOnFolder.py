import os
import subprocess
from datetime import datetime


def set_file_dates_with_touch(directory, specific_date):
    """
    Set the modified and access dates for all files in a directory to a specific date using the `touch` command.
    """
    # Format the specific date for 'touch' command (YYYYMMDDHHMM.SS)
    touch_timestamp = specific_date.strftime('%Y%m%d%H%M.%S')

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            try:
                # Use the 'touch' command to update modification and access dates
                subprocess.run(['touch', '-t', touch_timestamp, file_path], check=True)
                print(f"Updated modification and access date for {filename} to {touch_timestamp}")

            except subprocess.CalledProcessError as e:
                print(f"Failed to update {filename}: {e}")


# Example usage
directory_path = '/path/to/your/directory'  # Replace with your directory path
specific_date = datetime(2001, 12, 21, 0, 0, 0)  # Date set to 2001-12-21 at midnight

# Set file dates
set_file_dates_with_touch(directory_path, specific_date)
