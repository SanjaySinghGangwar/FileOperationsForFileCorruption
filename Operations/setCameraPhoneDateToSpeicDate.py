import os
import re
import subprocess
from datetime import datetime

# Specify the target dates and times here
TARGET_DATE_1 = '2016-08-22'  # Target date for DSC00002 to DSC00150 (YYYY-MM-DD)
TARGET_DATE_2 = '2016-09-27'  # Target date for DSC00190 to DSC00250 (YYYY-MM-DD)
TARGET_DATE_3 = '2015-01-20'  # Target date for DSC01608 to DSC01815 (YYYY-MM-DD)
TARGET_DATE_4 = '2021-07-19'  # Target date for DSC02222 to DSC02360 (YYYY-MM-DD) and files starting with 5000
TARGET_DATE_5 = '2021-09-20'  # Target date for DSC02361 to DSC02514 (YYYY-MM-DD)
TARGET_DATE_6 = '2022-10-20'  # Target date for DSC04966 to DSC05037 (YYYY-MM-DD)
TARGET_DATE_8 = '2015-01-20'  # Target date for DSC_0205 to DSC_0436 (YYYY-MM-DD)
TARGET_DATE_9 = '2012-10-27'  # Target date for files starting with 13523 (YYYY-MM-DD)
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
        # Set the appropriate target date based on file number
        file_number = int(match.group(1))
        if 2 <= file_number <= 150:
            date_str = TARGET_DATE_1.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        elif 190 <= file_number <= 250:
            date_str = TARGET_DATE_2.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        elif 1608 <= file_number <= 1815:
            date_str = TARGET_DATE_3.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        elif 2222 <= file_number <= 2360:
            date_str = TARGET_DATE_4.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        elif 2361 <= file_number <= 2514:
            date_str = TARGET_DATE_5.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        elif 4966 <= file_number <= 5037:
            date_str = TARGET_DATE_6.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        elif 205 <= file_number <= 436:
            date_str = TARGET_DATE_8.replace('-', '')  # Convert YYYY-MM-DD to YYYYMMDD
        else:
            return None, None
    elif format_name == '500':
        # Use TARGET_DATE_4 for files starting with 5000
        date_str = TARGET_DATE_4.replace('-', '')
    elif format_name == '13523':
        # Use TARGET_DATE_9 for files starting with 13523
        date_str = TARGET_DATE_9.replace('-', '')
    return date_str, TARGET_TIME


def update_creation_and_modified_date_from_filename(directory, files):
    patterns = {
        'DSC': re.compile(r'^DSC_(\d{4,5})\.\w+$'),  # Pattern for DSC00002 to DSC05037 and DSC_0205 to DSC_0436
        '500': re.compile(r'^500\d{9}_\d+\.\w*$'),  # Pattern for files like 500158300625_204620
        '13523': re.compile(r'^13523\d+\.\w+$'),  # Pattern for files starting with 13523
    }

    for file in files:
        file_path = os.path.join(directory, file)
        for format_name, pattern in patterns.items():
            match = pattern.match(file)
            if match:
                creation_time = os.path.getctime(file_path)
                modified_time = os.path.getmtime(file_path)
                creation_date_obj = datetime.fromtimestamp(creation_time)
                modified_date_obj = datetime.fromtimestamp(modified_time)

                try:
                    date_str, time_str = extract_date_from_filename(format_name, match)
                    if date_str is None:
                        continue  # Skip files not in the target ranges

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
                break  # Stop after the first match


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"

# List all files in the directory
files_to_update = list_files_in_directory(directory_path)

# Update creation and modified date based on filename
update_creation_and_modified_date_from_filename(directory_path, files_to_update)
