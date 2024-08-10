import os
import re
import subprocess
from datetime import datetime

# Specify the target dates and times here
TARGET_DATE_1 = '2016-08-22'
TARGET_DATE_2 = '2016-09-27'
TARGET_DATE_3 = '2015-01-20'
TARGET_DATE_4 = '2021-07-19'
TARGET_DATE_5 = '2021-09-20'
TARGET_DATE_6 = '2022-10-20'
TARGET_DATE_8 = '2015-01-20'
TARGET_DATE_9 = '2012-10-27'
TARGET_DATE_10 = '2023-09-03'
TARGET_DATE_11 = '2023-09-17'
TARGET_DATE_12 = '2020-12-20'
TARGET_DATE_13 = '2023-05-23'
TARGET_DATE_14 = '2022-10-20'  # For IMG_0284 to IMG_0337
TARGET_DATE_15 = '2021-03-20'  # For IMG_5132 to IMG_5187
TARGET_DATE_16 = '2017-01-26'  # New target date for IMG_5529 to IMG_6582
TARGET_TIME = '120000'


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
        file_number = int(match.group(1))
        if 2 <= file_number <= 150:
            date_str = TARGET_DATE_1.replace('-', '')
        elif 190 <= file_number <= 250:
            date_str = TARGET_DATE_2.replace('-', '')
        elif 1608 <= file_number <= 1815:
            date_str = TARGET_DATE_3.replace('-', '')
        elif 2222 <= file_number <= 2360:
            date_str = TARGET_DATE_4.replace('-', '')
        elif 2361 <= file_number <= 2514:
            date_str = TARGET_DATE_5.replace('-', '')
        elif 4966 <= file_number <= 5037:
            date_str = TARGET_DATE_6.replace('-', '')
        elif 205 <= file_number <= 436:
            date_str = TARGET_DATE_8.replace('-', '')
        else:
            return None, None
    elif format_name == '500':
        date_str = TARGET_DATE_4.replace('-', '')
    elif format_name == '1352':
        date_str = TARGET_DATE_9.replace('-', '')
    elif format_name == 'Photo':
        file_number = int(match.group(1))
        if 1918 <= file_number <= 2050:
            date_str = TARGET_DATE_9.replace('-', '')
        else:
            return None, None
    elif format_name == 'IMG':
        file_number = int(match.group(1))
        if 2748 <= file_number <= 2889:
            date_str = TARGET_DATE_10.replace('-', '')
        elif 3048 <= file_number <= 3180:
            date_str = TARGET_DATE_11.replace('-', '')
        elif 1862 <= file_number <= 1963:
            date_str = TARGET_DATE_13.replace('-', '')
        elif 284 <= file_number <= 337:
            date_str = TARGET_DATE_14.replace('-', '')
        elif 5132 <= file_number <= 5187:
            date_str = TARGET_DATE_15.replace('-', '')
        elif 5529 <= file_number <= 6582:  # New range
            date_str = TARGET_DATE_16.replace('-', '')
        else:
            return None, None
    elif format_name == 'DJI':
        file_number = int(match.group(1))
        if 936 <= file_number <= 943:
            date_str = TARGET_DATE_12.replace('-', '')
        else:
            return None, None
    return date_str, TARGET_TIME


def update_creation_and_modified_date_from_filename(directory, files):
    patterns = {
        'DSC': re.compile(r'^DSC_(\d{4,5})\.\w+$'),
        '500': re.compile(r'^500\d{9}_\d+\.\w*$'),
        '1352': re.compile(r'^1352\d+\.\w+$'),
        'Photo': re.compile(r'^Photo-(\d{4})\.\w+$'),
        'IMG': re.compile(r'^IMG_(\d{4})\.\w+$'),
        'DJI': re.compile(r'^DJI_(\d{4})\.\w+$'),
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
                        continue

                    timestamp = format_timestamp(date_str, time_str)

                    if len(timestamp) < 15 or len(timestamp) > 16:
                        print(f"Invalid timestamp format for {file}: {timestamp}")
                        continue

                    file_date = datetime.strptime(date_str + time_str[:6], '%Y%m%d%H%M%S')

                    if (creation_date_obj.date() == file_date.date() and creation_date_obj.time() == file_date.time() and
                            modified_date_obj.date() == file_date.date() and modified_date_obj.time() == file_date.time()):
                        print(f"{file} creation and modification dates already match the filename.")
                        continue

                    command = ['touch', '-t', timestamp, file_path]
                    result = subprocess.run(command, check=True, capture_output=True)

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

files_to_update = list_files_in_directory(directory_path)

update_creation_and_modified_date_from_filename(directory_path, files_to_update)
