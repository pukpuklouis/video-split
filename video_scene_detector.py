#!/usr/bin/env python3

import os
import sys
import configparser
import logging
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import concurrent.futures
import threading
from queue import Queue
from tqdm import tqdm
from datetime import datetime
from scenedetect import detect, ContentDetector, AdaptiveDetector, split_video_ffmpeg, FrameTimecode

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"video_scene_detector_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = Path(os.path.dirname(os.path.abspath(__file__))) / 'scenedetect.cfg'
        self.logger = logging.getLogger(__name__)
        self.load_config()

    def load_config(self) -> None:
        """Load configuration with fallback to defaults if file missing."""
        if self.config_path.exists():
            self.logger.info(f"Loading configuration from {self.config_path}")
            self.config.read(self.config_path)
        else:
            self.logger.warning("Configuration file not found, creating default configuration")
            self._create_default_config()

    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self.config['global'] = {
            'default-detector': 'detect-adaptive',
            'output_directory': './output',
            'verbosity': 'info',
            'min-scene-len': '0.6',
            'create_subdirs': 'no'
        }
        self.config['detect-adaptive'] = {
            'adaptive_threshold': '17',
            'min-content-val': '15',
            'frame-window': '2',
            'weights': '1.0, 1.0, 1.0, 0.0',
            'luma-only': 'no',
            'kernel-size': '-1'
        }
        self.config['statistics'] = {
            'save_stats': 'no',
            'stats_file': 'processing_stats.json'
        }
        self.save_config()

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")

    def edit_setting(self, section: str, key: str, value: str) -> bool:
        """Edit a specific configuration setting."""
        try:
            if section not in self.config:
                self.logger.error(f"Section {section} not found in configuration")
                return False
            if key not in self.config[section]:
                self.logger.error(f"Key {key} not found in section {section}")
                return False
            
            self.config[section][key] = value
            self.save_config()
            self.logger.info(f"Updated configuration: [{section}] {key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating configuration: {str(e)}")
            return False

    def get_sections(self) -> List[str]:
        """Get all configuration sections."""
        return self.config.sections()

    def get_settings(self, section: str) -> dict:
        """Get all settings in a section."""
        return dict(self.config[section])

class VideoProcessor:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv']
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'total_files_processed': 0,
            'total_scenes_detected': 0,
            'failed_files': 0,
            'processing_times': [],
            'files_processed': []
        }
        self.stats_lock = threading.Lock()
        self.print_lock = threading.Lock()
        self.progress_bars = {}
        self.progress_lock = threading.Lock()
        self._setup_output_directory()

    def _update_stats(self, stats_update: Dict) -> None:
        """Thread-safe statistics update."""
        with self.stats_lock:
            if 'total_scenes_detected' in stats_update:
                self.stats['total_scenes_detected'] += stats_update['total_scenes_detected']
            if 'failed_files' in stats_update:
                self.stats['failed_files'] += stats_update['failed_files']
            if 'processing_time' in stats_update:
                self.stats['processing_times'].append(stats_update['processing_time'])
            if 'file_stats' in stats_update:
                self.stats['files_processed'].append(stats_update['file_stats'])
            self.stats['total_files_processed'] += 1

    def _thread_safe_print(self, *args, **kwargs) -> None:
        """Thread-safe printing."""
        with self.print_lock:
            print(*args, **kwargs)

    def _create_progress_bar(self, desc: str, total: int, position: int) -> tqdm:
        """Create a thread-safe progress bar."""
        with self.progress_lock:
            progress_bar = tqdm(
                total=total,
                desc=desc,
                position=position,
                leave=True,
                ncols=80,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            )
            return progress_bar

    def _update_progress(self, progress_bar: tqdm, n: int = 1) -> None:
        """Update progress bar in a thread-safe manner."""
        with self.progress_lock:
            progress_bar.update(n)

    def process_video(self, video_path: Path, total_files: int = 1, current_file: int = 1) -> Dict:
        """Process a single video file with progress tracking."""
        start_time = datetime.now()
        file_stats = {
            'filename': video_path.name,
            'start_time': start_time.isoformat(),
            'scenes_detected': 0,
            'status': 'failed',
            'error': None
        }

        # Create progress bars for this file
        file_desc = f"File {current_file}/{total_files}: {video_path.name}"
        file_progress = self._create_progress_bar(file_desc, 100, current_file * 2 - 2)

        try:
            self.logger.info(f"Starting to process file {current_file}/{total_files}: {video_path.name}")
            file_progress.update(10)  # Started processing
            
            # Process video in chunks to optimize memory usage
            scenes = self._detect_scenes_optimized(video_path, None, None)
            file_progress.update(40)  # Scene detection complete
            
            # Split video into scenes
            if scenes:
                output_path = self._get_output_path(video_path)
                num_scenes = len(scenes)
                self.logger.info(f"Found {num_scenes} scenes in {video_path.name}")
                
                # Split video with progress tracking
                self._split_video_with_progress(video_path, scenes, output_path, file_progress)
                
                self.logger.info(f"Successfully split {video_path.name} into {num_scenes} scenes")
                
                # Update statistics
                file_stats.update({
                    'scenes_detected': num_scenes,
                    'status': 'success',
                    'error': None
                })
            else:
                self.logger.warning(f"No scenes detected in {video_path.name}")
                file_progress.update(90)  # Almost complete
                
                file_stats.update({
                    'status': 'warning',
                    'error': 'No scenes detected'
                })
                
        except Exception as e:
            self.logger.error(f"Error processing {video_path.name}: {str(e)}")
            
            file_stats.update({
                'status': 'error',
                'error': str(e)
            })
            return {'failed_files': 1, 'file_stats': file_stats}
        finally:
            # Ensure progress bars are completed and closed
            file_progress.update(100 - file_progress.n)  # Complete the progress
            file_progress.close()
        
        # Finalize statistics
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        file_stats['end_time'] = end_time.isoformat()
        file_stats['processing_time'] = processing_time
        
        return {
            'total_scenes_detected': file_stats['scenes_detected'],
            'processing_time': processing_time,
            'file_stats': file_stats
        }

    def _detect_scenes_optimized(self, video_path: Path, progress_bar: tqdm, scene_progress: tqdm) -> List:
        """Detect scenes with memory optimization and progress tracking."""
        try:
            # Use PySceneDetect's detect function with memory optimization
            detector = AdaptiveDetector()
            scenes = detect(str(video_path), detector)  # Convert Path to string
            return scenes
        except Exception as e:
            self.logger.error(f"Error in scene detection: {str(e)}")
            raise

    def _split_video_with_progress(self, video_path: Path, scenes: List, output_path: Path, progress_bar: tqdm) -> None:
        """Split video into scenes with progress tracking."""
        try:
            total_scenes = len(scenes)
            progress_per_scene = 40 / total_scenes  # 40% of progress bar for splitting
            
            for i, (start, end) in enumerate(zip(scenes[:-1], scenes[1:]), 1):
                # Update progress before processing each scene
                self._update_progress(progress_bar, progress_per_scene)
                
            # Final progress update
            self._update_progress(progress_bar, 40 - (progress_per_scene * (total_scenes - 1)))
            
            # Actually split the video
            split_video_ffmpeg(video_path, scenes, output_path)
            
        except Exception as e:
            self.logger.error(f"Error splitting video: {str(e)}")
            raise

    def process_folder(self, folder_path: Path, selected_indices: List[int] = None) -> None:
        """Process selected video files in a folder using parallel processing."""
        video_files = self.get_video_files(folder_path)
        if not video_files:
            self.logger.warning(f"No video files found in folder: {folder_path}")
            print("No video files found in the specified folder.")
            return

        if selected_indices:
            video_files = [video_files[i] for i in selected_indices if 0 <= i < len(video_files)]

        total_files = len(video_files)
        self.logger.info(f"Processing {total_files} files from {folder_path}")

        # Clear screen for progress bars
        print("\033[2J\033[H")  # Clear screen and move cursor to top
        print(f"Processing {total_files} files from {folder_path}\n")

        # Determine optimal number of workers based on CPU cores and available memory
        max_workers = min(os.cpu_count() or 1, 4)  # Limit to 4 workers to prevent memory issues
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all files for processing
                future_to_file = {
                    executor.submit(
                        self.process_video, 
                        video_file, 
                        total_files, 
                        idx + 1
                    ): video_file 
                    for idx, video_file in enumerate(video_files)
                }

                # Process completed tasks and update statistics
                for future in concurrent.futures.as_completed(future_to_file):
                    video_file = future_to_file[future]
                    try:
                        stats_update = future.result()
                        self._update_stats(stats_update)
                    except Exception as e:
                        self.logger.error(f"Error processing {video_file}: {str(e)}")
                        self._update_stats({
                            'failed_files': 1,
                            'file_stats': {
                                'filename': video_file.name,
                                'status': 'error',
                                'error': str(e)
                            }
                        })

        except Exception as e:
            self.logger.error(f"Error in parallel processing: {str(e)}")
            print(f"Error during parallel processing: {str(e)}")
        finally:
            # Move cursor below all progress bars
            print("\n" * (total_files * 2 + 1))

        # Print processing summary
        self._print_processing_summary()
        
        # Save statistics if enabled
        if self.config_manager.config['statistics'].getboolean('save_stats', fallback=False):
            self._save_statistics()

    def _setup_output_directory(self) -> None:
        """Setup output directory based on configuration."""
        output_dir = Path(self.config_manager.config['global']['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory set to: {output_dir}")

    def _get_output_path(self, input_path: Path) -> Path:
        """Get output path for a video file based on configuration."""
        base_output = Path(self.config_manager.config['global']['output_directory'])
        
        if self.config_manager.config['global'].getboolean('create_subdirs', fallback=False):
            # Create a subdirectory using the input filename
            output_dir = base_output / input_path.stem
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir / f"{input_path.stem}-scene"
        else:
            return base_output / f"{input_path.stem}-scene"

    def _print_processing_summary(self) -> None:
        """Print processing statistics summary."""
        total_files = self.stats['total_files_processed']
        total_scenes = self.stats['total_scenes_detected']
        failed_files = self.stats['failed_files']
        avg_time = sum(self.stats['processing_times']) / len(self.stats['processing_times']) if self.stats['processing_times'] else 0
        
        print("\n=== Processing Summary ===")
        print(f"Total files processed: {total_files}")
        print(f"Total scenes detected: {total_scenes}")
        print(f"Failed files: {failed_files}")
        print(f"Average processing time: {avg_time:.2f} seconds")
        print(f"Success rate: {((total_files - failed_files) / total_files * 100):.1f}%")

    def _save_statistics(self) -> None:
        """Save processing statistics to file."""
        try:
            output_dir = Path(self.config_manager.config['global']['output_directory'])
            stats_file = output_dir / self.config_manager.config['statistics']['stats_file']
            
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
            self.logger.info(f"Statistics saved to {stats_file}")
        except Exception as e:
            self.logger.error(f"Error saving statistics: {str(e)}")

    def get_video_files(self, folder_path: Path) -> List[Path]:
        """Get all video files from a folder."""
        return [f for f in folder_path.iterdir() if f.suffix.lower() in self.supported_formats]

    def display_video_files(self, folder_path: Path) -> List[Path]:
        """Display available video files in the folder."""
        video_files = self.get_video_files(folder_path)
        if not video_files:
            print("No video files found in the specified folder.")
            return []

        print("\nAvailable video files:")
        for idx, file in enumerate(video_files):
            print(f"{idx + 1}. {file.name}")
        return video_files

class MenuSystem:
    def __init__(self, video_processor: VideoProcessor):
        self.video_processor = video_processor
        self.logger = logging.getLogger(__name__)

    def display_menu(self) -> None:
        """Display the main menu and handle user input."""
        while True:
            print("\nVideo Scene Detector Menu:")
            print("1. Process single video file")
            print("2. Process all videos in a folder")
            print("3. Select specific videos from a folder")
            print("4. Edit configuration")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                self._process_single_file()
            elif choice == '2':
                self._process_folder()
            elif choice == '3':
                self._process_selected_files()
            elif choice == '4':
                self._edit_configuration()
            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def _process_single_file(self) -> None:
        """Handle processing a single video file."""
        file_path = input("\nEnter the path to the video file: ").strip()
        if not file_path:
            print("No file path provided.")
            return

        file_path = Path(file_path)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        if file_path.suffix.lower() not in self.video_processor.supported_formats:
            print(f"Unsupported file format. Supported formats: {', '.join(self.video_processor.supported_formats)}")
            return

        self.video_processor.process_video(file_path)

    def _process_folder(self) -> None:
        """Handle processing all videos in a folder."""
        folder_path = input("\nEnter the path to the folder: ").strip()
        if not folder_path:
            print("No folder path provided.")
            return

        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            print(f"Invalid folder path: {folder_path}")
            return

        self.video_processor.process_folder(folder_path)

    def _process_selected_files(self) -> None:
        """Handle processing selected videos from a folder."""
        folder_path = input("\nEnter the path to the folder: ").strip()
        if not folder_path:
            print("No folder path provided.")
            return

        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            print(f"Invalid folder path: {folder_path}")
            return

        video_files = self.video_processor.get_video_files(folder_path)
        if not video_files:
            print("No video files found in the specified folder.")
            return

        print("\nAvailable video files:")
        for i, file in enumerate(video_files, 1):
            print(f"{i}. {file.name}")

        selection = input("\nEnter the numbers of files to process (comma-separated, e.g., 1,3,4): ").strip()
        if not selection:
            print("No files selected.")
            return

        try:
            selected_indices = [int(x.strip()) - 1 for x in selection.split(',')]
            self.video_processor.process_folder(folder_path, selected_indices)
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")

    def _edit_configuration(self) -> None:
        """Handle editing the configuration."""
        config = self.video_processor.config_manager.config
        
        while True:
            print("\nConfiguration Editor:")
            print("1. Edit Scene Detection Settings")
            print("2. Edit Output Settings")
            print("3. Edit Statistics Settings")
            print("4. Save and Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                self._edit_scene_detection_settings(config)
            elif choice == '2':
                self._edit_output_settings(config)
            elif choice == '3':
                self._edit_statistics_settings(config)
            elif choice == '4':
                self.video_processor.config_manager.save_config()
                print("Configuration saved.")
                break
            else:
                print("Invalid choice. Please try again.")

    def _edit_scene_detection_settings(self, config: configparser.ConfigParser) -> None:
        """Edit scene detection settings."""
        print("\nScene Detection Settings:")
        threshold = input(f"Enter threshold value (current: {config['detect-adaptive']['adaptive_threshold']}): ").strip()
        if threshold.isdigit():
            config['detect-adaptive']['adaptive_threshold'] = threshold
        else:
            print("Invalid threshold value. Keeping current value.")

    def _edit_output_settings(self, config: configparser.ConfigParser) -> None:
        """Edit output settings."""
        print("\nOutput Settings:")
        output_dir = input(f"Enter output directory (current: {config['global']['output_directory']}): ").strip()
        if output_dir:
            config['global']['output_directory'] = output_dir

        create_subdirs = input(f"Create subdirectories for each file? (y/n, current: {config['global']['create_subdirs']}): ").strip().lower()
        if create_subdirs in ['y', 'n']:
            config['global']['create_subdirs'] = str(create_subdirs == 'y')

    def _edit_statistics_settings(self, config: configparser.ConfigParser) -> None:
        """Edit statistics settings."""
        print("\nStatistics Settings:")
        save_stats = input(f"Save statistics? (y/n, current: {config['statistics']['save_stats']}): ").strip().lower()
        if save_stats in ['y', 'n']:
            config['statistics']['save_stats'] = str(save_stats == 'y')

        if save_stats == 'y':
            stats_file = input(f"Enter statistics file path (current: {config['statistics']['stats_file']}): ").strip()
            if stats_file:
                config['statistics']['stats_file'] = stats_file

def main():
    try:
        logger = setup_logging()
        config_manager = ConfigManager()
        video_processor = VideoProcessor(config_manager)
        menu_system = MenuSystem(video_processor)
        menu_system.display_menu()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
