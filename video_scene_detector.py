#!/usr/bin/env python3

import os
import sys
import configparser
from pathlib import Path
from typing import List, Optional, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox
from scenedetect import detect, ContentDetector, AdaptiveDetector, split_video_ffmpeg

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = Path(os.path.dirname(os.path.abspath(__file__))) / 'scenedetect.cfg'
        self.load_config()

    def load_config(self) -> None:
        """Load configuration with fallback to defaults if file missing."""
        if self.config_path.exists():
            self.config.read(self.config_path)
        else:
            self._create_default_config()

    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self.config['global'] = {
            'default-detector': 'detect-adaptive',
            'output': './output',
            'verbosity': 'info',
            'min-scene-len': '0.6'
        }
        self.config['detect-adaptive'] = {
            'threshold': '17',
            'min-content-val': '15',
            'frame-window': '2',
            'weights': '1.0, 1.0, 1.0, 0.0',
            'luma-only': 'no',
            'kernel-size': '-1'
        }
        self.save_config()

    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

class VideoProcessor:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv']

    def process_video(self, video_path: Path, total_files: int = 1, current_file: int = 1) -> None:
        """Process a single video file with progress tracking."""
        try:
            print(f"\nProcessing file {current_file}/{total_files}: {video_path.name}")
            print("[", end="", flush=True)
            
            # Get scene list using detect function
            scenes = detect(video_path, AdaptiveDetector(
                threshold=int(self.config_manager.config['detect-adaptive']['threshold'])
            ))
            print("=====", end="", flush=True)
            
            # Split video into scenes
            if scenes:
                output_path = video_path.parent / f"{video_path.stem}-scene"
                split_video_ffmpeg(video_path, scenes, output_path)
                print("=====]")
                print(f"✓ Successfully processed {video_path.name}")
                print(f"  Found {len(scenes)} scenes")
            else:
                print("=====]")
                print(f"! No scenes detected in {video_path.name}")
                
        except Exception as e:
            print("=====]")
            print(f"✗ Error processing {video_path.name}: {str(e)}")

    def process_folder(self, folder_path: Path, selected_indices: List[int] = None) -> None:
        """Process selected video files in a folder."""
        video_files = self.get_video_files(folder_path)
        if not video_files:
            print("No video files found in the specified folder.")
            return

        if selected_indices:
            # Process only selected files
            selected_files = [video_files[i] for i in selected_indices if 0 <= i < len(video_files)]
            total_files = len(selected_files)
            for idx, video_file in enumerate(selected_files, 1):
                self.process_video(video_file, total_files, idx)
        else:
            # Process all files
            total_files = len(video_files)
            for idx, video_file in enumerate(video_files, 1):
                self.process_video(video_file, total_files, idx)

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
    def __init__(self, config_manager: ConfigManager, video_processor: VideoProcessor):
        self.config_manager = config_manager
        self.video_processor = video_processor
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

    def display_menu(self) -> None:
        """Display main menu with options."""
        print("\n=== PySceneDetect Control Panel ===")
        print("1. Process a single video file")
        print("2. Select specific files from a folder")
        print("3. Batch process all files in a folder")
        print("4. View/Edit Configuration")
        print("5. Preview Current Settings")
        print("6. Exit")

    def run(self) -> None:
        """Main menu loop."""
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self._process_single_file()
            elif choice == "2":
                self._process_selected_files()
            elif choice == "3":
                self._process_folder()
            elif choice == "4":
                self._edit_config()
            elif choice == "5":
                self._preview_settings()
            elif choice == "6":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")

    def _process_single_file(self) -> None:
        """Handle single file processing."""
        file_path = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.video_processor.process_video(Path(file_path))

    def _process_selected_files(self) -> None:
        """Handle processing of selected files from a folder."""
        folder_path = filedialog.askdirectory(title="Select folder containing videos")
        if not folder_path:
            return

        folder_path = Path(folder_path)
        video_files = self.video_processor.display_video_files(folder_path)
        if not video_files:
            return

        print("\nEnter the numbers of files to process (comma-separated, e.g., 1,3,4)")
        print("Or enter 'all' to process all files")
        selection = input("Selection: ").strip().lower()

        if selection == 'all':
            self.video_processor.process_folder(folder_path)
        else:
            try:
                # Convert 1-based user input to 0-based indices
                indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                self.video_processor.process_folder(folder_path, indices)
            except ValueError:
                print("Invalid selection format. Please use comma-separated numbers.")

    def _process_folder(self) -> None:
        """Handle folder processing."""
        folder_path = filedialog.askdirectory(title="Select folder containing videos")
        if folder_path:
            self.video_processor.process_folder(Path(folder_path))

    def _edit_config(self) -> None:
        """Edit configuration settings."""
        print("\nCurrent Configuration:")
        for section in self.config_manager.config.sections():
            print(f"\n[{section}]")
            for key, value in self.config_manager.config[section].items():
                print(f"{key} = {value}")
        
        print("\nNote: Manual configuration editing is currently not implemented.")
        input("Press Enter to continue...")

    def _preview_settings(self) -> None:
        """Preview current settings."""
        print("\nCurrent Settings:")
        for section in self.config_manager.config.sections():
            print(f"\n[{section}]")
            for key, value in self.config_manager.config[section].items():
                print(f"{key} = {value}")
        input("\nPress Enter to continue...")

def main():
    try:
        config_manager = ConfigManager()
        video_processor = VideoProcessor(config_manager)
        menu_system = MenuSystem(config_manager, video_processor)
        menu_system.run()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
