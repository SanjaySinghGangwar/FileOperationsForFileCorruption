import os
import re
import subprocess
from datetime import datetime


def get_file_creation_date(file_path):
    try:
        # Get file creation date using 'stat' command (Unix-based systems)
        result = subprocess.run(['stat', '-c', '%W', file_path], capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
    except Exception as e:
        print(f"Error getting creation date for {file_path}: {e}")
    return None


def format_timestamp_for_touch(date_str, time_str):
    # Ensure the format: YYYYMMDDhhmm.ss
    if len(time_str) >= 6:
        formatted_time = f'{time_str[:2]}{time_str[2:4]}{time_str[4:6]}'
        if len(time_str) > 6:
            formatted_time += f'.{time_str[6:8]}'  # Limit to 2 decimal places for seconds
        else:
            formatted_time += '.00'  # Add default seconds if not present
    else:
        formatted_time = f'{time_str[:2]}{time_str[2:4]}{time_str[4:]}'
        formatted_time += '.00'  # Add default seconds if not present
    return f'{date_str}{formatted_time}'


def get_timestamp_from_filename(file, pattern):
    match = pattern.match(file)
    if match:
        date_str = match.group(1).replace('-', '')
        time_str = match.group(2).replace('.', '')
        millis_str = match.group(3) if len(match.groups()) > 2 else ''

        return format_timestamp_for_touch(date_str, time_str)
    return None


def update_dates_from_filename(directory):
    # Regular expressions for different filename formats
    patterns = {
        'YYYYMMDD_HHMMSS': re.compile(r'^(\d{8})_(\d{6})\.\w+$'),
        'YYYY-MM-DD HH.MM.SS': re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})\.\w+$'),
        'YYYY-MM-DD HH.MM.SS-x': re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})-(\d+)\.\w+$'),
        'YYYYMMDD_HHMMSS(x)': re.compile(r'^(\d{8})_(\d{6})\(\d+\)\.\w+$'),
        'YYYYMMDD_HHMMSS-x': re.compile(r'^(\d{8})_(\d{6})-(\d+)\.\w+$'),
        'IMG_YYYYMMDD_HHMMSS': re.compile(r'^IMG_(\d{8})_(\d{6})\.\w+$'),
        'IMG_YYYYMMDD_HHMMSSsss': re.compile(r'^IMG_(\d{8})_(\d{6})(\d{3})\.\w+$'),
        'YYYYMMDD_HHMMSS_milliseconds': re.compile(r'^(\d{8})_(\d{6})_(\d+)\.\w+$'),
        'IMG_YYYYMMDD_HHMMSS_milliseconds': re.compile(r'^IMG_(\d{8})_(\d{6})_(\d{4})\.\w+$'),
        'YYYYMMDD_HHMMSS_milliseconds_001': re.compile(r'^(\d{8})_(\d{6})_(\d{3})\.\w+$'),
        'IMG-YYYYMMDD-WA####': re.compile(r'^IMG-(\d{8})-WA\d{4}\.\w+$'),
        'IMG_YYYYMMDD_HHMMSS_001': re.compile(r'^IMG_(\d{8})_(\d{6})_(\d{3})\.\w+$'),
        'YYYYMMDD_HHMM_001': re.compile(r'^(\d{8})_(\d{4})\.\w+$'),
        'YYYY-MM-DD_HH-MM-SS': re.compile(r'^(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})\.\w+$'),
        'YYYY-MM-DD_HH-MM-SS-x': re.compile(r'^(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d+)\.\w+$'),
        'YYYYMMDD_HHMM': re.compile(r'^(\d{8})_(\d{4})\.\w+$'),
        'YYYY-MM-DD': re.compile(r'^(\d{4}-\d{2}-\d{2})\.\w+$'),
        'YYYYMMDD': re.compile(r'^(\d{8})\.\w+$'),
    }

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            for format_name, pattern in patterns.items():
                timestamp = get_timestamp_from_filename(file, pattern)
                if timestamp:
                    try:
                        # Get existing creation date
                        current_creation_date = get_file_creation_date(file_path)

                        if current_creation_date:
                            # Convert current creation date to YYYYMMDDhhmm.ss format
                            current_timestamp = datetime.fromtimestamp(current_creation_date).strftime('%Y%m%d%H%M.%S')

                            if timestamp == current_timestamp:
                                print(f"Skipping {file}, creation date is already correct.")
                                continue

                        # Use the 'touch' command to update both creation and modification date
                        command = ['touch', '-t', timestamp, file_path]
                        print(f"Running command: {' '.join(command)}")
                        result = subprocess.run(command, check=False, capture_output=True)

                        if result.returncode == 0:
                            print(f"Updated creation and modification date for {file} to {timestamp}")
                        else:
                            print(f"Failed to update {file}: {result.stderr.decode()}")

                    except Exception as e:
                        print(f"Failed to update {file}: {e}")
                    break  # Stop after the first match


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"

# Update creation and modification date based on filename
update_dates_from_filename(directory_path)
