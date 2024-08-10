import os
import subprocess
from datetime import datetime


def get_file_modification_date(file_path):
    try:
        # Get file modification date using 'stat' command
        result = subprocess.run(['stat', '-f', '%Sm', '-t', '%Y-%m-%d %H:%M:%S', file_path], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error getting modification date for {file_path}: {e}")
    return None


def format_timestamp_for_touch(date_str):
    # Convert YYYY-MM-DD HH:MM:SS to MMDDHHMM.YY
    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%m%d%H%M.%S')


def update_modification_date(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            try:
                # Get modification date
                mod_date_str = get_file_modification_date(file_path)
                if mod_date_str:
                    # Convert modification date to the format required by touch
                    timestamp = format_timestamp_for_touch(mod_date_str)

                    # Use the 'touch' command to update the modification date
                    command = ['touch', '-t', timestamp, file_path]
                    print(f"Running command: {' '.join(command)}")
                    result = subprocess.run(command, check=False, capture_output=True)

                    if result.returncode == 0:
                        print(f"Updated modification date for {file}.")
                    else:
                        print(f"Failed to update {file}: {result.stderr.decode()}")
            except Exception as e:
                print(f"Failed to update {file}: {e}")


# Example usage:
directory_path = "/Volumes/WD 1.5/NAS_BACKUP/Samsung"

# Update modification date to match creation date
update_modification_date(directory_path)
