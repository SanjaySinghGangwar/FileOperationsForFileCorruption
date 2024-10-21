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


def process_videos(input_directory, output_directory):
    """
    Processes all video files in the input directory.
    Converts videos with resolution greater than 720p and saves them in the output directory.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    video_files = [f for f in os.listdir(input_directory) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]

    # Use tqdm to create a progress bar for video file processing
    for filename in tqdm(video_files, desc="Processing videos", unit="file"):
        video_path = os.path.join(input_directory, filename)
        width, height = get_video_resolution(video_path)

        if width is None or height is None:
            logging.warning(f'Skipping {filename} due to an error reading resolution.')
            continue

        if height > 720:
            output_path = os.path.join(output_directory, f"{filename}")
            convert_to_480p(video_path, output_path)
        else:
            logging.info(f'{filename} is already 720p or lower. Skipping conversion.')


if __name__ == "__main__":
    input_directory = "/input_Folder"  # Change to your input directory containing videos
    output_directory = "/output_Folder"  # Directory where you want to store converted videos
    process_videos(input_directory, output_directory)
