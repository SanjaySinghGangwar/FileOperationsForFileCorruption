import logging
import os
import ffmpeg
from tqdm import tqdm  # Import tqdm for progress bar

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_video_resolution(video_path):
    """
    Returns the resolution (width, height) of the video.
    """
    try:
        probe = ffmpeg.probe(video_path)
        video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        return width, height
    except ffmpeg.Error as e:
        logging.error(f"Error probing {video_path}: {e}")
        return None, None


def convert_to_480p(video_path, output_path):
    """
    Converts the given video to 480p resolution using ffmpeg.
    """
    try:
        ffmpeg.input(video_path).output(output_path, vf='scale=-2:480').run(overwrite_output=True)
        logging.info(f'Converted {video_path} to {output_path}')
    except ffmpeg.Error as e:
        logging.error(f"Error converting {video_path}: {e}")


def process_videos(watch_directory):
    """
    Processes all video files in the watch directory.
    Converts videos with resolution greater than 480p and replaces the original files.
    """
    video_files = [f for f in os.listdir(watch_directory) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]

    # Use tqdm to create a progress bar for video file processing
    for filename in tqdm(video_files, desc="Processing videos", unit="file"):
        video_path = os.path.join(watch_directory, filename)
        width, height = get_video_resolution(video_path)

        if width is None or height is None:
            logging.warning(f'Skipping {filename} due to an error reading resolution.')
            continue

        if height > 480:
            temp_output_path = os.path.join(watch_directory, f"temp_{filename}")
            convert_to_480p(video_path, temp_output_path)

            # Replace the original file with the converted one
            os.remove(video_path)
            os.rename(temp_output_path, video_path)
            logging.info(f'Replaced original {filename} with 480p version.')
        else:
            logging.info(f'{filename} is already 480p or lower. Skipping conversion.')


if __name__ == "__main__":
    watch_directory = "/Volumes/2 TB/Personal/Creative/ContentCreations/Raw/"  # Change to your watch directory
    process_videos(watch_directory)
