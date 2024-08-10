import os
import re
import subprocess
from datetime import datetime

# Specify the target date and time here
TARGET_DATE = '2016-12-22'  # Example date (YYYY-MM-DD)
TARGET_TIME = '120000'  # Example time (HHMMSS)


def list_files_in_directory(directory):
    """List all files in the given directory."""
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def format_timestamp(date_str, time_str):
    """Format timestamp for touch command (YYYYMMDDHHMM.SS)"""
    time_str = time_str.ljust(6, '0')  # Pad time_str with zeros if it's shorter than 6 digits
    seconds = time_str[4:]
    return f'{date_str}{time_str[:2]}{time_str[2:4]}.{seconds}'


def extract_date_from_filename(format_name, match):
    """Extract date from filename based on format"""
    if format_name == 'DSC':
        date_str = TARGET_DATE.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        time_str = TARGET_TIME  # Use the specific time
    return date_str, time_str


def update_creation_and_modified_date_from_filename(directory, files):
    patterns = {
        'DSC': re.compile(r'^DSC(\d{5})\.\w+$'),  # Pattern for DSC00002 to DSC00150
    }

    for file in files:
        file_path = os.path.join(directory, file)
        if not patterns['DSC'].match(file):
            continue

        file_number = int(patterns['DSC'].match(file).group(1))
        if 2 <= file_number <= 150:
            creation_time = os.path.getctime(file_path)
            modified_time = os.path.getmtime(file_path)
            creation_date_obj = datetime.fromtimestamp(creation_time)
            modified_date_obj = datetime.fromtimestamp(modified_time)

            try:
                date_str, time_str = extract_date_from_filename('DSC', None)
                timestamp = format_timestamp(date_str, time_str)

                # Check if timestamp is correctly formatted
                if len(timestamp) < 15 or len(timestamp) > 16:
                    print(f"Invalid timestamp format for {file}: {timestamp}")
                    continue

                # Convert extracted date and time to a datetime object
                file_date = datetime.strptime(date_str + time_str[:6], '%Y%m%d%H%M%S')

                # Check if both creation and modification dates already match
                if (creation_date_obj.date() == file_date.date() and creation_date_obj.time() == file_date.time() and
                        modified_date_obj.date() == file_date.date() and modified_date_obj.time() == file_date.time()):
                    print(f"{file} creation and modification dates already match the filename.")
                    continue

                # Update the modification date
                command = ['touch', '-t', timestamp, file_path]
                result = subprocess.run(command, check=True, capture_output=True)

                # Update the creation date on macOS using SetFile
                creation_command = ['SetFile', '-d', datetime.strftime(file_date, '%m/%d/%Y %H:%M:%S'), file_path]
                result_creation = subprocess.run(creation_command, check=True, capture_output=True)

                if result.returncode == 0 and result_creation.returncode == 0:
                    print(f"Updated creation and modification date for {file} to {timestamp}")
                else:
                    print(f"Failed to update {file}: {result.stderr.decode()}")

            except Exception as e:
                print(f"Failed to update {file}: {e}")


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"

# List all files in the directory
files_to_update = list_files_in_directory(directory_path)

# Update creation and modified date based on filename
update_creation_and_modified_date_from_filename(directory_path, files_to_update)
