## Request for Input Folder Setting, File Selection, and Batch Processing

I would like to request a feature enhancement for the Video Scene Split Tool. Specifically, I want to add an option for setting an input folder, reading all the video files within that folder, and listing them for the user to select which file(s) to process, including a batch processing option.

### Proposed Steps:
1. **Input Folder Setting**: Allow the user to specify an input folder instead of a single input video file.
2. **Read Files**: Read all video files within the specified input folder.
3. **List Files**: Display the list of video files to the user.
4. **File Selection**: Allow the user to select specific files from the list for processing, with an option to select all files for batch processing.

### Example Implementation:

1. **Input Folder Setting**:
   - Add an option in the menu to set the input folder.
   - Validate the folder path.

2. **Read Files**:
   - Use a loop to read all video files (e.g., with extensions .mp4, .mov, .mkv) in the specified folder.

3. **List Files**:
   - Display the list of video files with a numbered menu for selection.

4. **File Selection**:
   - Allow the user to select one or more files by entering the corresponding numbers, or choose an option to process all files in the folder.

### Sample Code Snippet:


## Development Progress

### Completed Tasks:
1. Created main script `video_scene_detector.py` with:
   - ConfigManager for handling configuration
   - VideoProcessor for processing videos
   - MenuSystem for user interaction
2. Created configuration file `scenedetect.cfg`
3. Created requirements.txt
4. Enhanced video processing functionality:
   - Added progress tracking with visual indicators
   - Implemented file selection from folder
   - Added support for processing specific files
   - Improved error handling and user feedback
5. Added logging functionality:
   - File-based logging with timestamps
   - Console output mirroring
   - Comprehensive error tracking
   - Operation status logging
6. Implemented configuration editing:
   - Interactive configuration editor
   - Section-based settings management
   - Input validation
   - Real-time configuration updates
7. Added output directory management:
   - Configurable output directory
   - Optional subdirectory creation
   - Automatic directory creation
8. Implemented processing statistics:
   - Per-file statistics tracking
   - Processing time measurement
   - Success/failure tracking
   - JSON statistics export
   - Processing summary display
9. Optimized performance:
   - Added parallel processing support
   - Implemented thread-safe operations
   - Optimized memory usage
   - Added CPU core-aware processing
   - Improved thread synchronization
10. Added progress tracking:
    - Individual file progress bars
    - Scene detection progress
    - Video splitting progress
    - Thread-safe progress updates
    - Clear progress visualization

### Next Steps:
1. Add more features:
   - Add batch processing status summary
   - Add scene detection sensitivity adjustment

### Current Features:
1. File Processing Options:
   - Process single video file
   - Select specific files from a folder
   - Batch process all files in a folder
2. Progress Tracking:
   - Individual file progress bars
   - Scene detection progress
   - Video splitting progress
   - File count tracking
   - Success/failure indicators
3. Configuration:
   - Interactive configuration editor
   - Section-based settings management
   - Real-time updates
4. Logging:
   - Timestamped log files
   - Detailed operation tracking
   - Error logging with stack traces
   - Console output mirroring
5. Output Management:
   - Configurable output directory
   - Optional subdirectory creation
   - Automatic path handling
6. Statistics:
   - Processing time tracking
   - Scene count statistics
   - Success rate calculation
   - JSON statistics export
   - Summary reporting
7. Performance:
   - Parallel processing
   - Memory optimization
   - Thread-safe operations
   - CPU core utilization
   - Synchronized statistics

### Notes:
- The script uses PySceneDetect's adaptive detector with threshold 17
- Configuration file is stored in the same directory as the script
- Output files are saved in configurable output directory
- Supports .mp4, .avi, .mov, and .mkv formats
- Progress bars show both file and scene detection progress
- Logs are stored in the "logs" directory with timestamps
- Statistics are saved in JSON format in the output directory
- Parallel processing is limited to 4 workers by default
- Thread-safe operations for all shared resources
- Progress bars are synchronized across threads
