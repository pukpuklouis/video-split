### Requirements and Planning Document (RPD) for PySceneDetect Python Execution File

#### 1. **Objective**
The goal is to create a Python script that uses the `pyscenedetect` library to detect scenes in video files. The script should allow the user to choose between processing a single file or batch processing all files in a folder. The configuration file will be located in the same directory as the Python script. The output files will be saved in the same directory as the input files, with the scene number appended to the original file name.

#### 2. **Functional Requirements**
- **User Input**: The script should provide a menu for the user to choose between:
  - Processing a single video file.
  - Batch processing all video files in a folder.
- **Configuration File**: The script should read settings from a configuration file located in the same directory as the script.
- **Scene Detection**: The script should use the `detect-adaptive` method with a threshold of 17 (`-t 17`).
- **Output**: 
  - The output files should be saved in the same directory as the input files.
  - The output file names should be the same as the original file names, with `-scene-##` appended (e.g., `video.mp4` → `video-scene-01.mp4`).

#### 3. **Non-Functional Requirements**
- **User Interface**: The script should have a simple text-based menu for user interaction.
- **Error Handling**: The script should handle errors gracefully, such as invalid file paths or unsupported file formats.
- **Performance**: The script should efficiently process video files, especially in batch mode.

#### 4. **Technical Specifications**
- **Programming Language**: Python
- **Libraries**: 
  - `pyscenedetect` for scene detection.
  - `os` and `argparse` for file and directory handling.
  - `configparser` for reading the configuration file.
- **Input**: 
  - Single video file or folder containing video files.
  - Configuration file (`config.ini`) in the same directory as the script.
- **Output**: 
  - Video files with detected scenes, saved in the same directory as the input files.

#### 5. **Design and Architecture**
- **Main Script**: 
  - The script will start by displaying a menu to the user.
  - Based on the user's choice, it will either process a single file or all files in a folder.
  - The script will read the configuration file for any necessary settings.
  - It will use the `pyscenedetect` library to detect scenes using the `detect-adaptive` method with a threshold of 17.
  - The output files will be saved with the appropriate naming convention.

- **Configuration File**:
  - The configuration file (`scenedetect.cfg`) will contain global settings and detector-specific parameters.
  - Configuration Management:
    - Default location: User's home directory
    - Fallback to default values if file is missing
    - Auto-creation of config file with defaults on first run
  - Example `scenedetect.cfg`:
    ```
    [global]
    # Default detector to use (options: detect-adaptive, detect-content, detect-threshold)
    default-detector = detect-adaptive
    # Output directory for written files (absolute path or relative to working directory)
    output = ./output
    # Verbosity of console output (options: debug, info, warning, error)
    verbosity = info
    # Minimum length of any scene (format: {number}s, range: 0.1-10.0)
    min-scene-len = 0.6s

    [detect-adaptive]
    # Frame score threshold for adaptive detection (range: 1-100)
    threshold = 17
    # Minimum threshold for content_val metric (range: 1-100)
    min-content-val = 15
    # Window size for rolling average (range: 1-10 frames)
    frame-window = 2
    # Weights for RGB and motion components (format: r,g,b,motion)
    weights = 1.0, 1.0, 1.0, 0.0
    # Use only luma channel for detection (yes/no)
    luma-only = no
    # Kernel size for expanding detected edges (-1 for auto)
    kernel-size = -1
    ```

- **Menu System**:
  - The script will display an interactive text-based menu:
    ```
    === PySceneDetect Control Panel ===
    1. Process a single video file
    2. Batch process all video files in a folder
    3. View/Edit Configuration
    4. Preview Current Settings
    5. Exit
    ```
  - Features:
    - Real-time progress indication
    - Cancellable operations (Ctrl+C)
    - Error recovery and retry options
    - Configuration validation before processing
    - Processing status and completion reports

#### 6. **Code Snippets**
- **Reading Configuration File**:
  ```python
  import configparser
  import os
  from pathlib import Path
  from typing import Dict, List, Union

  class ConfigManager:
      def __init__(self):
          self.config = configparser.ConfigParser()
          self.config_path = Path.home() / 'scenedetect.cfg'
          self.load_config()

      def load_config(self) -> None:
          """Load configuration with fallback to defaults if file missing."""
          if self.config_path.exists():
              self.config.read(self.config_path)
          else:
              self._create_default_config()

      def get_setting(self, section: str, key: str) -> Union[str, int, float, List[float]]:
          """Get setting with type conversion and validation."""
          try:
              value = self.config[section][key]
              return self._convert_and_validate(key, value)
          except KeyError:
              raise ValueError(f"Missing configuration: {section}.{key}")

      def _create_default_config(self) -> None:
          """Create default configuration file."""
          # Default configuration initialization
          self.config['global'] = {
              'default-detector': 'detect-adaptive',
              'output': './output',
              'verbosity': 'info',
              'min-scene-len': '0.6s'
          }
          # Save default configuration
          self.save_config()

      def save_config(self) -> None:
          """Save current configuration to file."""
          with open(self.config_path, 'w') as configfile:
              self.config.write(configfile)
  ```

- **Enhanced Menu System**:
  ```python
  from typing import Tuple, Optional
  import tkinter as tk
  from tkinter import filedialog, messagebox
  from pathlib import Path

  class MenuSystem:
      def __init__(self, config_manager: ConfigManager):
          self.config_manager = config_manager
          self.root = tk.Tk()
          self.root.withdraw()  # Hide main window

      def display_menu(self) -> None:
          """Display main menu with options."""
          print("\n=== PySceneDetect Control Panel ===")
          print("1. Process a single video file")
          print("2. Batch process all video files in a folder")
          print("3. View/Edit Configuration")
          print("4. Preview Current Settings")
          print("5. Exit")

      def get_user_choice(self) -> Tuple[str, Optional[Path]]:
          """Get and validate user input."""
          while True:
              try:
                  choice = input("\nEnter your choice (1-5): ").strip()
                  if choice not in ['1', '2', '3', '4', '5']:
                      print("Invalid choice. Please enter a number between 1 and 5.")
                      continue

                  if choice in ['1', '2']:
                      path = self._get_file_or_folder(choice)
                      if not path:
                          continue
                      return choice, path
                  
                  return choice, None

              except Exception as e:
                  print(f"Error: {e}")
                  print("Please try again.")

      def _get_file_or_folder(self, choice: str) -> Optional[Path]:
          """Get file or folder path based on user choice."""
          try:
              if choice == "1":
                  file_path = filedialog.askopenfilename(
                      title="Select video file",
                      filetypes=[
                          ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                          ("All files", "*.*")
                      ]
                  )
                  if not file_path:
                      print("No file selected.")
                      return None
                  return Path(file_path)
              else:
                  folder_path = filedialog.askdirectory(
                      title="Select folder containing videos"
                  )
                  if not folder_path:
                      print("No folder selected.")
                      return None
                  return Path(folder_path)
          except Exception as e:
              print(f"Error selecting path: {e}")
              return None
  ```

- **Processing a Single File**:
  ```python
  from scenedetect import VideoManager, SceneManager, open_video
  from scenedetect.detectors import AdaptiveDetector
  from scenedetect.video_splitter import split_video_ffmpeg

  def process_single_file(file_path, threshold):
      video_manager = VideoManager([file_path])
      scene_manager = SceneManager()
      scene_manager.add_detector(AdaptiveDetector(threshold=threshold))

      video_manager.set_downscale_factor()
      video_manager.start()
      scene_manager.detect_scenes(frame_source=video_manager)
      scene_list = scene_manager.get_scene_list()
      video_manager.release()

      split_video_ffmpeg(file_path, scene_list, output_file_template=f"{file_path}-scene-$SCENE_NUMBER.mp4")
  ```

- **Batch Processing Files in a Folder**:
  ```python
  import os

  def batch_process_folder(folder_path, threshold):
      for filename in os.listdir(folder_path):
          if filename.endswith(".mp4") or filename.endswith(".avi"):  # Add more formats if needed
              file_path = os.path.join(folder_path, filename)
              process_single_file(file_path, threshold)
  ```

#### 7. **Error Handling and Logging**
- **Error Messages**:
  ```
  ERROR_CODES = {
      'CONFIG_001': 'Configuration file not found or invalid',
      'CONFIG_002': 'Invalid parameter value',
      'VIDEO_001': 'Unsupported video format',
      'VIDEO_002': 'Corrupted video file',
      'PROCESS_001': 'Insufficient system resources',
      'PROCESS_002': 'Operation timeout'
  }
  ```

- **Logging Levels**:
  - DEBUG: Detailed information for debugging
  - INFO: General operational messages
  - WARNING: Issues that don't stop processing
  - ERROR: Critical issues that halt operations

#### 8. **System Requirements**
- **Minimum Requirements**:
  - Python 3.8+
  - 4GB RAM
  - 1GB free disk space
  - OpenCV compatible GPU (optional)

- **Performance Expectations**:
  - Processing speed: ~30fps on CPU, ~90fps with GPU
  - Maximum supported video resolution: 4K
  - Typical processing time: 1 minute per 3 minutes of video

#### 9. **Configuration Management**
- **Version Control**:
  ```python
  [metadata]
  version = 1.0
  last_modified = 2024-01-04
  compatibility = ">=1.0,<2.0"
  ```

- **Environment Variables**:
  ```
  PYSCENEDETECT_CONFIG=/path/to/config
  PYSCENEDETECT_OUTPUT_DIR=/path/to/output
  PYSCENEDETECT_LOG_LEVEL=INFO
  ```

- **Configuration Precedence**:
  1. Command-line arguments
  2. Environment variables
  3. User configuration file
  4. System-wide configuration
  5. Default values

#### 10. **Common Use Cases**
- **Basic Scene Detection**:
  ```python
  # Example: Simple content-aware detection
  detector = SceneDetector(
      threshold=30,
      min_scene_len=0.5
  )
  detector.process_video("input.mp4")
  ```

- **Advanced Processing**:
  ```python
  # Example: Custom detection with filters
  detector = SceneDetector(
      threshold=25,
      min_scene_len=1.0,
      filters=[
          NoiseReduction(strength=0.5),
          MotionCompensation(enabled=True)
      ]
  )
  detector.process_video(
      "input.mp4",
      output_format="json"
  )
  ```

#### 11. **Testing Plan**
- **Unit Testing**: 
  - Test the `process_single_file` function with different video files.
  - Test the `batch_process_folder` function with a folder containing multiple video files.
- **Integration Testing**:
  - Test the entire script with both single file and batch processing options.
- **User Acceptance Testing**:
  - Ensure the menu system is intuitive and the output files are correctly named and saved.

#### 12. **Future Enhancements**
- **Additional Detectors**: Allow the user to choose different scene detection methods (e.g., `detect-content`, `detect-threshold`).
- **Custom Output Directory**: Allow the user to specify a different output directory.
- **GUI**: Develop a graphical user interface for easier interaction.

#### 13. **Documentation**
- **User Guide**: Provide instructions on how to use the script, including how to set up the configuration file.
- **Code Comments**: Ensure the code is well-commented for future maintenance.

---

This RPD outlines the requirements, design, and implementation plan for the Python script using `pyscenedetect`. The next step would be to start coding based on this document.