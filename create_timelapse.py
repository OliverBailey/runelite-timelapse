import os
import subprocess
import re
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---

# Path to RuneLite screenshots directory
screenshots_dir = os.getenv('SCREENSHOTS_DIR')
if not screenshots_dir:
    raise ValueError("SCREENSHOTS_DIR must be set in .env file")
if not os.path.exists(screenshots_dir):
    raise ValueError(f"Screenshots directory does not exist: {screenshots_dir}")

# Video settings
framerate = int(os.getenv('FRAMERATE', '5'))
output_fps = int(os.getenv('OUTPUT_FPS', '30'))
output_video = os.getenv('OUTPUT_VIDEO', 'account_timelapse.mp4')
video_quality = os.getenv('VIDEO_QUALITY', '23')

# Music file (optional)
music_file = os.getenv('MUSIC_FILE', '')
if music_file == '':
    music_file = None
elif not os.path.exists(music_file):
    print(f"Warning: Music file '{music_file}' not found. Proceeding without music.")
    music_file = None

# Music playback mode
hold_last_frame = os.getenv('HOLD_LAST_FRAME', 'true').lower() == 'true'

# Chatbox blur settings
blur_enabled = os.getenv('BLUR_ENABLED', 'true').lower() == 'true'
if blur_enabled:
    blur_box = {
        'x': int(os.getenv('BLUR_X', '7')),
        'y': int(os.getenv('BLUR_Y', '740')),
        'w': int(os.getenv('BLUR_WIDTH', '512')),
        'h': int(os.getenv('BLUR_HEIGHT', '110'))
    }
    blur_amount = int(os.getenv('BLUR_AMOUNT', '15'))
else:
    blur_box = None
    blur_amount = 0

# --- End of Configuration ---

# Temporary file to hold the sorted list
list_filename = 'mylist.txt'

# Regex to find the timestamp in the filename
timestamp_regex = re.compile(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})')

def check_encoder_available(encoder_name):
    """Check if a specific FFmpeg encoder is available."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-hide_banner', '-encoders'],
            capture_output=True,
            text=True,
            check=True
        )
        return encoder_name in result.stdout
    except Exception:
        return False

def get_video_encoder():
    """Determine the best video encoder to use based on user preference and availability."""
    encoder_preference = os.getenv('VIDEO_ENCODER', 'auto').lower()
    
    encoder_map = {
        'nvidia': ('h264_nvenc', 'NVIDIA GPU'),
        'amd': ('h264_amf', 'AMD GPU'),
        'intel': ('h264_qsv', 'Intel GPU'),
        'cpu': ('libx264', 'CPU')
    }
    
    # If user specified a specific encoder
    if encoder_preference in encoder_map:
        codec, name = encoder_map[encoder_preference]
        if encoder_preference == 'cpu' or check_encoder_available(codec):
            print(f"Using {name} encoding ({codec})")
            return codec
        else:
            print(f"Warning: {name} encoder ({codec}) not available.")
    
    # Auto-detect or fallback
    if encoder_preference == 'auto' or encoder_preference not in ['cpu'] + list(encoder_map.keys()):
        print("Auto-detecting GPU encoder...")
        for key in ['nvidia', 'amd', 'intel']:
            codec, name = encoder_map[key]
            if check_encoder_available(codec):
                print(f"GPU detected! Using {name} encoding ({codec})")
                return codec
    
    # Fallback to CPU
    print("GPU encoding not available. Falling back to CPU encoding (libx264)")
    return 'libx264'

def get_audio_duration(filepath):
    """Uses ffprobe to get the duration of an audio file."""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        filepath
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"Warning: Could not get duration of {filepath}. {e}")
        print("Install ffprobe (usually with ffmpeg) to use 'hold_last_frame' correctly.")
        return 0

def create_timelapse():
    print("Finding and sorting all screenshots in all subfolders...")
    
    # Determine video encoder
    video_codec = get_video_encoder()
    
    files_with_times = []
    
    for root, dirs, files in os.walk(screenshots_dir):
        for filename in files:
            if filename.endswith('.png'):
                match = timestamp_regex.search(filename)
                
                if match:
                    timestamp_str = match.group(1)
                    try:
                        timestamp_obj = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')
                        filepath = os.path.join(root, filename)
                        files_with_times.append((filepath, timestamp_obj))
                    except ValueError:
                        print(f"Skipping file with weird date: {filename}")

    files_with_times.sort(key=lambda x: x[1])

    if not files_with_times:
        print("Error: No .png files with valid RuneLite timestamps found.")
        return
        
    total_images = len(files_with_times)
    video_duration = total_images / framerate
    padding_duration = 0
    has_music = music_file and os.path.exists(music_file)
    
    print(f"Found {total_images} total images, for a video duration of {video_duration:.2f}s.")

    # Check audio duration if holding frame
    if has_music and hold_last_frame:
        print("Checking music duration for 'hold_last_frame'...")
        music_duration = get_audio_duration(music_file)
        if music_duration > video_duration:
            padding_duration = music_duration - video_duration
            print(f"Music is {music_duration:.2f}s. Adding {padding_duration:.2f}s of padding to video.")
        else:
            print(f"Music is {music_duration:.2f}s. No padding needed.")

    with open(list_filename, 'w', encoding='utf-8') as f:
        for filepath, timestamp_obj in files_with_times:
            escaped_path = filepath.replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    print("File list created. Starting FFmpeg to build video...")

    # Base command with video input
    ffmpeg_command = [
        'ffmpeg',
        '-r', str(framerate),
        '-f', 'concat',
        '-safe', '0',
        '-i', list_filename,
    ]

    # Add music & duration logic
    if has_music:
        if hold_last_frame:
            print("Adding music (single play) and holding last frame.")
            ffmpeg_command.extend(['-i', music_file])
        else:
            print("Adding music (looping) and cutting to video length.")
            ffmpeg_command.extend(['-t', str(video_duration)])
            ffmpeg_command.extend(['-stream_loop', '-1', '-i', music_file])
    else:
        print("No music file found. Setting video duration.")
        ffmpeg_command.extend(['-t', str(video_duration)])

    # Build the filter chain
    filter_chain = []
    video_stream_in = "[0:v]"
    
    if blur_box:
        print(f"Applying blur to box: {blur_box}")
        b = blur_box
        filter_chain.append(
            f"{video_stream_in}split[main][to_blur]; "
            f"[to_blur]crop={b['w']}:{b['h']}:{b['x']}:{b['y']},"
            f"gblur=sigma={blur_amount}[blurred_box]; "
            f"[main][blurred_box]overlay={b['x']}:{b['y']}[v_blurred]"
        )
        video_stream_in = "[v_blurred]"
    
    # Define the output name for the crop filter
    crop_output = "[v_out]" if padding_duration == 0 else "[v_cropped]"
    filter_chain.append(f"{video_stream_in}crop=floor(iw/2)*2:floor(ih/2)*2,fps={output_fps}{crop_output}")

    # Add padding filter if needed
    if padding_duration > 0:
        filter_chain.append(f"[v_cropped]tpad=stop_mode=clone:stop_duration={padding_duration}[v_out]")

    ffmpeg_command.extend(['-filter_complex', ";".join(filter_chain)])

    # Map final streams
    ffmpeg_command.extend(['-map', '[v_out]'])
    if has_music:
        ffmpeg_command.extend(['-map', '1:a:0'])
        ffmpeg_command.extend(['-c:a', 'aac'])
        if not hold_last_frame:
            ffmpeg_command.append('-shortest')
    # Add final output settings
    ffmpeg_command.extend(['-c:v', video_codec])
    
    # Add quality settings based on encoder type
    if video_codec == 'libx264':
        # CPU encoder uses CRF (Constant Rate Factor)
        ffmpeg_command.extend(['-crf', video_quality])
    elif video_codec in ['h264_nvenc', 'h264_amf', 'h264_qsv']:
        # GPU encoders use CQ (Constant Quality) 
        ffmpeg_command.extend(['-cq', video_quality])
    
    ffmpeg_command.extend([
        '-pix_fmt', 'yuv420p',
        '-y',
        output_video
    ])
    
    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"\nSuccess! Timelapse created: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"\nError: FFmpeg failed with exit code {e.returncode}")
    except FileNotFoundError as e:
        print(f"\nError: Command not found. Is FFmpeg/FFprobe installed? {e}")
    finally:
        if os.path.exists(list_filename):
            os.remove(list_filename)
            print(f"Cleaned up {list_filename}.")

if __name__ == "__main__":
    print("=" * 60)
    print("RuneLite Timelapse Creator")
    print("=" * 60)
    create_timelapse()
