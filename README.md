# Video Scene Split Tool

A shell-based tool for automatically detecting and splitting video files into scenes using FFmpeg.

## Prerequisites

- FFmpeg (version 4.0 or higher)
- Bash (version 4.0 or higher)
- `bc` command (for mathematical calculations)

## Installation

1. Clone or download this repository
2. Make the script executable:
   ```bash
   chmod +x split_scenes.sh
   ```

## Basic Usage

```bash
./split_scenes.sh [input_video] [output_dir]
```

## Menu System Guide

The tool provides an interactive menu system with four main options:

### 1. Input Settings
- Configure input video file or folder
- Set output directory
- Switch between single file and batch processing
- Save settings for future use

#### Batch Processing
- Select an input folder containing video files
- Choose to process all files or select individual files
- Automatic video format detection
- Progress tracking across multiple files

### 2. Scene Detection Settings
- **Threshold** (0.0-1.0, default: 0.3)
  - Lower values: more scenes detected
  - Higher values: fewer scenes detected
- **Minimum Duration** (1-300 seconds, default: 2)
- **Detection Method**
  - `content`: Based on content changes
  - `luminance`: Based on brightness changes

### 3. Output Configuration
- **Format**: mp4/mov/mkv
- **Codec Options**:
  - `copy`: Fastest, no quality loss
  - `h264`: Good compression, widely compatible
  - `h265`: Better compression, newer devices
- **Scene Prefix**: Customize output file names

### 4. Start Processing
- Begins the scene detection and splitting process
- Shows progress bar and status

## Usage Examples

### Single File Processing
```bash
# Create output directory
mkdir output_scenes

# Run with direct arguments
./split_scenes.sh movie.mp4 output_scenes/
```

### Batch Processing
```bash
# Start the tool
./split_scenes.sh

# Then follow these steps:
# 1. Select Option 1 -> Input Settings
# 2. Switch to Batch Processing mode
# 3. Enter the folder path containing videos
# 4. Choose to process all files or select specific ones
# 5. Configure output settings
# 6. Start processing
```

## Output Format

The tool creates files named according to the pattern:
```
scene_1_000000.mp4  (First scene starting at 0 seconds)
scene_2_000145.mp4  (Second scene starting at 145 seconds)
...
```

## Tips for Best Results

### 1. Scene Detection
- Start with default threshold (0.3)
- Adjust based on results:
  - Too many scenes? Increase threshold
  - Too few scenes? Decrease threshold
  - Scenes too short? Increase minimum duration

### 2. Performance
- For fastest processing:
  - Use `copy` codec
  - Keep minimum duration ≥ 2 seconds
  - Use mp4 format

### 3. Quality vs Size
- Best balance:
  - Use `h264` codec
  - Default quality settings
- Maximum compression:
  - Use `h265` codec
  - Note: Longer processing time

### 4. Storage Requirements
- Ensure at least 2x input video size is available
- Additional temporary space needed during processing

## Error Handling

The tool includes comprehensive error checking for:
- Input file validation
- Disk space verification
- FFmpeg compatibility
- Output directory permissions

## Settings Persistence

- Settings can be saved for future use
- Stored in `config/settings.conf`
- Automatically loaded on startup

## License

This tool is provided as-is under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests! 

## Batch Processing Features

### Supported Video Formats
- MP4 (.mp4)
- QuickTime (.mov)
- Matroska (.mkv)
- AVI (.avi)
- Windows Media (.wmv)

### Batch Mode Options
- Process all videos in a folder
- Select specific videos to process
- Automatic format detection
- Progress tracking for multiple files
- Individual file progress bars

### Storage Management
- Automatic disk space verification
- Space requirement calculation for largest file
- Temporary file cleanup between processing 