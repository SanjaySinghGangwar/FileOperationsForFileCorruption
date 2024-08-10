import os
import re
import subprocess
from datetime import datetime


def list_files_in_directory(directory):
    """List all files in the given directory."""
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def format_timestamp(date_str, time_str):
    """Format timestamp for touch command (YYYYMMDDHHMM.SS)"""
    # Ensure the time_str is always in HHMMSS format and seconds part is correctly formatted
    time_str = time_str.ljust(6, '0')  # Pad time_str with zeros if it's shorter than 6 digits
    seconds = time_str[4:]
    return f'{date_str}{time_str[:2]}{time_str[2:4]}.{seconds}'


def extract_date_from_filename(format_name, match):
    """Extract date from filename based on format"""
    if format_name in {'YYYYMMDD_HHMMSS', 'IMG_YYYYMMDD_HHMMSS'}:
        date_str = match.group(1)  # YYYYMMDD part
        time_str = match.group(2)  # HHMMSS part
    elif format_name in {'YYYY-MM-DD HH.MM.SS', 'YYYY-MM-DD HH.MM.SS-x'}:
        date_str = match.group(1).replace("-", "")  # YYYYMMDD part
        time_str = match.group(2) + match.group(3)  # HHMMSS part
    elif format_name in {'YYYYMMDD_HHMMSS(x)', 'YYYYMMDD_HHMMSS-x', 'IMG_YYYYMMDD_HHMMSSsss',
                         'IMG_YYYYMMDD_HHMMSS_milliseconds', 'YYYYMMDD_HHMMSS_milliseconds',
                         'YYYYMMDD_HHMMSS_milliseconds_001', 'YYYY-MM-DD HH.MM.SS.jpg',
                         'YYYY-MM-DD HH.MM.SS-x.jpg'}:
        date_str = match.group(1).replace("-", "")  # YYYYMMDD part
        time_str = match.group(2) + match.group(3)  # HHMMSS part
    elif format_name == 'IMG_YYYYMMDD_HHMMSS_extra':
        date_str = match.group(1)  # YYYYMMDD part
        time_str = match.group(2) + match.group(3).rjust(6, '0')  # HHMMSS part with extra digits
    return date_str, time_str


def update_creation_and_modified_date_from_filename(directory, files):
    # Regular expressions for different filename formats
    patterns = {
        'YYYYMMDD_HHMMSS': re.compile(r'^(\d{8})_(\d{6})\.\w+$'),
        'YYYY-MM-DD HH.MM.SS': re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})\.\w+$'),
        'YYYY-MM-DD HH.MM.SS-x': re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})-(\d+)\.\w+$'),
        'YYYYMMDD_HHMMSS(x)': re.compile(r'^(\d{8})_(\d{6})\(\d+\)\.\w+$'),
        'YYYYMMDD_HHMMSS-x': re.compile(r'^(\d{8})_(\d{6})-(\d+)\.\w+$'),
        'IMG_YYYYMMDD_HHMMSS': re.compile(r'^IMG_(\d{8})_(\d{6})\.\w+$'),
        'IMG_YYYYMMDD_HHMMSSsss': re.compile(r'^IMG_(\d{8})_(\d{6})(\d{3})\.\w+$'),
        'IMG_YYYYMMDD_HHMMSS_milliseconds': re.compile(r'^IMG_(\d{8})_(\d{6})_(\d+)\.\w+$'),
        'YYYYMMDD_HHMMSS_milliseconds': re.compile(r'^(\d{8})_(\d{6})_(\d+)\.\w+$'),
        'YYYYMMDD_HHMMSS_milliseconds_001': re.compile(r'^(\d{8})_(\d{6})_(\d{3})\.\w+$'),
        'YYYY-MM-DD HH.MM.SS.jpg': re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})\.jpg$'),
        'YYYY-MM-DD HH.MM.SS-x.jpg': re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})-(\d+)\.jpg$'),
        'IMG_YYYYMMDD_HHMMSS_extra': re.compile(r'^IMG_(\d{8})_(\d{6})_(\d{1,6})\.\w+$')  # Updated pattern
    }

    for file in files:
        file_path = os.path.join(directory, file)
        creation_time = os.path.getctime(file_path)
        modified_time = os.path.getmtime(file_path)
        creation_date_obj = datetime.fromtimestamp(creation_time)
        modified_date_obj = datetime.fromtimestamp(modified_time)

        for format_name, pattern in patterns.items():
            match = pattern.match(file)
            if match:
                try:
                    date_str, time_str = extract_date_from_filename(format_name, match)
                    timestamp = format_timestamp(date_str, time_str)

                    # Check if timestamp is correctly formatted
                    if len(timestamp) < 15 or len(timestamp) > 16:
                        print(f"SANJAY :: Invalid timestamp format for {file}: {timestamp}")
                        break

                    # Convert extracted date and time to a datetime object
                    file_date = datetime.strptime(date_str + time_str[:6], '%Y%m%d%H%M%S')

                    # Check if both creation and modified dates already match the extracted date and time
                    if (creation_date_obj.date() == file_date.date() and creation_date_obj.time() == file_date.time() and
                            modified_date_obj.date() == file_date.date() and modified_date_obj.time() == file_date.time()):
                        print(f"{file} creation and modified dates already match the filename.")
                        break

                    # Use the 'touch' command to update the creation and modified date and time
                    command = ['touch', '-t', timestamp, '-m', file_path]
                    result = subprocess.run(command, check=True, capture_output=True)

                    if result.returncode == 0:
                        print(f"Updated creation and modified dates for {file} to {timestamp}")
                    else:
                        print(f"SANJAY :: Failed to update {file}: {result.stderr.decode()}")

                except Exception as e:
                    print(f"SANJAY :: Failed to update {file}: {e}")
                break  # Stop after the first match


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"

# List all files in the directory
files_to_update = list_files_in_directory(directory_path)

# Update creation and modified dates based on filename
update_creation_and_modified_date_from_filename(directory_path, files_to_update)
