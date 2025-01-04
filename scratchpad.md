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

### Next Steps:
1. Add more features:
   - Implement configuration editing interface
   - Add detailed logging functionality
   - Add output directory configuration
   - Add scene detection sensitivity adjustment
2. Testing:
   - Test with various video formats
   - Test batch processing with large folders
   - Test error handling scenarios

### Current Features:
1. File Processing Options:
   - Process single video file
   - Select specific files from a folder
   - Batch process all files in a folder
2. Progress Tracking:
   - Visual progress bar
   - File count tracking
   - Success/failure indicators
3. Configuration:
   - Adaptive detector with threshold 17
   - Support for multiple video formats
   - Configurable processing parameters

### Notes:
- The script uses PySceneDetect's adaptive detector with threshold 17
- Configuration file is stored in the same directory as the script
- Output files are saved with "-scene" suffix in the same directory as input
- Supports .mp4, .avi, .mov, and .mkv formats
- Added visual progress tracking for better user experience
