# Video Scene Split Tool

A Python-based tool for automatically detecting and splitting video files into scenes using PySceneDetect.

[中文版](README.zh-TW.md)




## Features

- **Processing Options**:
  - Single video file processing
  - Batch processing of multiple files
  - Folder-based video selection
  - Progress tracking with visual indicators

- **Scene Detection**:
  - Adaptive detection with configurable threshold
  - Support for multiple video formats (mp4, mov, mkv, avi, wmv)
  - Minimum scene duration control
  - Real-time progress visualization

## Prerequisites

- Python 3.x
- PySceneDetect library
- FFmpeg (version 4.0 or higher)

## Configuration

The tool uses a configuration file (`scenedetect.cfg`) with the following key settings:

- Scene detection threshold: 17 (default)
- Minimum scene length: 0.6s
- Output directory configuration
- Processing parameters

## Usage

### Single File Processing
```bash
python video_scene_detector.py -f video.mp4
```

### Batch Processing
```bash
python video_scene_detector.py -d /path/to/videos
```

## Output Format

Files are saved with the following naming convention:
```
original_name-scene-01.mp4
original_name-scene-02.mp4
...
```

## Performance Features

- Parallel processing support
- Memory-optimized operations
- CPU core-aware processing
- Thread-safe operations

## Error Handling

- Comprehensive error checking
- Detailed logging system
- Operation status tracking
- Recovery options for failed operations

## License

This tool is provided under the MIT License.