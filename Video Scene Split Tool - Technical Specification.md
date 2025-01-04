# Video Scene Split Tool - Technical Specification

## Overview
Shell-based tool with menu interface for video scene detection and splitting using FFmpeg.

## Command Structure
```bash
split_scenes [input_video] [output_dir]
```

## Menu System
1. Input Settings
   - Video path validation
   - Output directory creation/validation
   - Settings persistence option

2. Scene Detection Settings
   - Threshold (0.0-1.0, steps of 0.1)
   - Minimum duration (1-300 seconds)
   - Detection method:
     - Content-based
     - Luminance-based

3. Output Configuration
   - Formats: mp4/mov/mkv
   - Naming: scene_{number}_{timestamp}
   - Codecs: copy/h264/h265

## Technical Requirements
- FFmpeg ≥ 4.0
- Bash ≥ 4.0
- Minimum disk space = 2x input file size

## Error Handling
- Input validation
- Directory permissions
- Disk space verification
- FFmpeg execution monitoring

## User Interface
- Clear screen between menus
- Progress bar during processing
- Error messages in red
- Success messages in green

## Parameter Constraints
- Threshold: 0.0-1.0 (default: 0.3)
- Duration: 1-300s (default: 2s)
- File prefix: alphanumeric + underscore
- Disk space: Minimum 2x source size