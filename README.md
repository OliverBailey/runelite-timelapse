# RuneLite Timelapse Creator

Create awesome timelapse videos from your RuneLite screenshots! This tool automatically finds all your OSRS screenshots, sorts them by timestamp, and compiles them into a video with optional music and chatbox blurring.

## Features

- 📸 Automatically finds and sorts all screenshots from any RuneLite character directory
- 🎵 Optional background music support
- 🔒 Chatbox blurring to protect privacy
- ⚙️ Highly customizable framerate and video settings
- 🎬 Two modes: hold last frame to match music length, or loop music to match video length

## Prerequisites

- Python 3.6 or higher
- FFmpeg and FFprobe (for video processing)

### Installing FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

**macOS:**
```bash
brew install ffmpeg
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/OliverBailey/runelite-timelapse.git
cd runelite-timelapse
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create your configuration file:
```bash
cp .env.sample .env
```

4. Edit `.env` with your settings (see Configuration section below)

## Configuration

Open the `.env` file and configure the following settings:

### Required Settings

- **SCREENSHOTS_DIR**: Path to your RuneLite screenshots directory
  - Windows: `C:/Users/YourName/.runelite/screenshots/YourCharacterName`
  - Linux: `/home/username/.runelite/screenshots/YourCharacterName`
  - WSL: `/mnt/c/Users/YourName/.runelite/screenshots/YourCharacterName`

### Optional Settings

- **FRAMERATE**: Frames per second (default: 5)
  - Controls how fast screenshots advance (pacing)
  - Lower = slower video, more detail per screenshot
  - Recommended: 5-10
  
- **OUTPUT_FPS**: Output video framerate (default: 30)
  - Controls playback smoothness
  - Higher = smoother video playback
  - Recommended: 25-60
  - This is independent of FRAMERATE - you can have slow-paced screenshots (5 fps) with smooth playback (30 fps)

- **OUTPUT_WIDTH** / **OUTPUT_HEIGHT**: Output video resolution (default: 1920x1080)
  - All screenshots will be scaled to this resolution
  - Maintains aspect ratio with black padding if needed
  - Common options: 1920x1080 (Full HD), 2560x1440 (2K), 3840x2160 (4K)
  
- **MUSIC_FILE**: Audio file to add as background music
  - Place the audio file in the same directory as the script
  - Leave empty or comment out for no music
  
- **OUTPUT_VIDEO**: Name of the output video file (default: account_timelapse.mp4)

- **VIDEO_ENCODER**: Video encoding method (default: auto)
  - `auto`: Automatically detect and use GPU if available, fallback to CPU
  - `nvidia`: Force NVIDIA GPU encoding (h264_nvenc) - 5-10x faster
  - `amd`: Force AMD GPU encoding (h264_amf) - 5-10x faster
  - `intel`: Force Intel GPU encoding (h264_qsv) - 5-10x faster
  - `cpu`: Force CPU encoding (libx264) - slower but most compatible

- **VIDEO_QUALITY**: Video quality/bitrate (default: 23)
  - Range: 0-51 (lower = better quality, larger file)
  - Recommended: 20-28 for good balance
  - 18 = very high quality, very large file
  - 23 = high quality, good file size (recommended)
  - 28 = medium quality, smaller file

### Blur Settings

To protect your privacy by blurring the chatbox:

- **BLUR_ENABLED**: Set to `true` to enable chatbox blurring (default: true)
- **BLUR_X**, **BLUR_Y**, **BLUR_WIDTH**, **BLUR_HEIGHT**: Position and size of blur box
  - Coordinates are based on RuneLite fixed mode (765x503) 
  - **Automatically scaled** to match your OUTPUT_WIDTH and OUTPUT_HEIGHT
  - Default values work for standard chatbox position
- **BLUR_AMOUNT**: Blur intensity (default: 15)

### Advanced Settings

- **HOLD_LAST_FRAME**: 
  - `true`: Music plays once, video holds last frame to match music length
  - `false`: Music loops and gets cut to match video length

## Usage

Once you've configured your `.env` file, simply run:

```bash
python create_timelapse.py
```

The script will:
1. Scan all subdirectories in your screenshots folder
2. Find all PNG files with RuneLite timestamps
3. Sort them chronologically
4. Create a timelapse video with your settings

## Example

Here's a sample `.env` configuration:

```bash
SCREENSHOTS_DIR=/mnt/c/Users/YourUsername/.runelite/screenshots/MyIronman
FRAMERATE=8
OUTPUT_FPS=30
OUTPUT_WIDTH=1920
OUTPUT_HEIGHT=1080
MUSIC_FILE=Sea_Shanty_2.mp3
OUTPUT_VIDEO=my_osrs_journey.mp4
VIDEO_ENCODER=auto
VIDEO_QUALITY=23
BLUR_ENABLED=true
BLUR_X=0
BLUR_Y=325
BLUR_WIDTH=315
BLUR_HEIGHT=70
BLUR_AMOUNT=15
HOLD_LAST_FRAME=true
```

This will create a video where screenshots advance at 8 per second with smooth 30fps playback, Sea Shanty 2 playing in the background, and the chatbox blurred out. GPU encoding will be used automatically if available.

## Troubleshooting

### "SCREENSHOTS_DIR must be set in .env file"
Make sure you've created a `.env` file (copy from `.env.sample`) and set the `SCREENSHOTS_DIR` variable.

### "No .png files with valid RuneLite timestamps found"
Check that your `SCREENSHOTS_DIR` path is correct and contains RuneLite screenshots with timestamps in the format `YYYY-MM-DD_HH-MM-SS`.

### FFmpeg errors
Ensure FFmpeg is installed and accessible from the command line:
```bash
ffmpeg -version
ffprobe -version
```

## License

MIT License - Feel free to use and modify!

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Acknowledgments

- Created for the OSRS/RuneLite community
- Inspired by the nostalgia of looking back at your gaming journey
