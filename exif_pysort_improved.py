#!/usr/bin/env python3
"""
EXIF Photo Sorter - Improved Version

A Python script that updates EXIF data of JPEG images based on folder names.
Extracts year from folder names and sets EXIF dates accordingly.
"""

import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import random
from datetime import datetime


class ExifProcessor:
    """Handles EXIF data processing for photo files."""
    
    SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.tiff', '.tif')
    EXCLUDED_DIRS = ('@eaDir', '.DS_Store', 'Thumbs.db')
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """
        Initialize the EXIF processor.
        
        Args:
            dry_run: If True, simulate operations without making changes
            verbose: Enable verbose logging
        """
        self.dry_run = dry_run
        self.setup_logging(verbose)
        self.processed_count = 0
        self.error_count = 0
        
    def setup_logging(self, verbose: bool) -> None:
        """Set up logging configuration."""
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def check_exiftool(self) -> bool:
        """
        Check if exiftool is available on the system.
        
        Returns:
            True if exiftool is available, False otherwise
        """
        try:
            subprocess.run(['exiftool', '-ver'], 
                         capture_output=True, check=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.logger.error("exiftool is not installed or not accessible")
            return False
    
    def get_exif_year(self, file_path: Path) -> Optional[int]:
        """
        Extract the year from the 'DateTimeOriginal' EXIF tag.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Year as integer if found, None otherwise
        """
        try:
            result = subprocess.run(
                ['exiftool', '-DateTimeOriginal', '-s3', str(file_path)],
                capture_output=True, text=True, check=True, timeout=30
            )
            
            if result.stdout.strip():
                # Try to parse the date string
                date_match = re.search(r'^(\d{4})', result.stdout.strip())
                if date_match:
                    year = int(date_match.group(1))
                    self.logger.debug(f"Found EXIF year {year} for {file_path}")
                    return year
                    
        except subprocess.CalledProcessError as e:
            self.logger.debug(f"No EXIF data found for {file_path}: {e}")
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout reading EXIF data for {file_path}")
        except ValueError as e:
            self.logger.warning(f"Invalid year format in EXIF data for {file_path}: {e}")
            
        return None
    
    def set_exif_date(self, file_path: Path, year: int, 
                     month: int = 1, day: int = 1) -> bool:
        """
        Set the EXIF data for a file to the specified date.
        
        Args:
            file_path: Path to the image file
            year: Year to set
            month: Month to set (default: 1)
            day: Day to set (default: 1)
            
        Returns:
            True if successful, False otherwise
        """
        # Check if update is needed
        current_year = self.get_exif_year(file_path)
        if current_year == year:
            self.logger.info(f"EXIF data for {file_path.name} is already correct (Year: {current_year})")
            return True
        
        # Generate random time to avoid duplicate timestamps
        time_str = self.generate_random_time()
        exif_date = f"{year:04d}:{month:02d}:{day:02d} {time_str}"
        
        if self.dry_run:
            if current_year is None:
                self.logger.info(f"[DRY RUN] Would set EXIF date for {file_path.name} to {exif_date}")
            else:
                self.logger.info(f"[DRY RUN] Would update EXIF date for {file_path.name} from {current_year} to {year}")
            return True
        
        try:
            # Create backup if file is valuable
            self.logger.debug(f"Setting EXIF date for {file_path.name} to {exif_date}")
            
            subprocess.run([
                'exiftool', '-overwrite_original',
                f'-AllDates={exif_date}',
                f'-DateTimeOriginal={exif_date}',
                f'-CreateDate={exif_date}',
                f'-ModifyDate={exif_date}',
                str(file_path)
            ], check=True, capture_output=True, timeout=60)
            
            if current_year is None:
                self.logger.info(f"Set EXIF date for {file_path.name} to {exif_date}")
            else:
                self.logger.info(f"Updated EXIF date for {file_path.name} from {current_year} to {year}")
            
            self.processed_count += 1
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to set EXIF data for {file_path}: {e}")
            self.error_count += 1
            return False
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout setting EXIF data for {file_path}")
            self.error_count += 1
            return False
    
    @staticmethod
    def generate_random_time() -> str:
        """
        Generate a random time in HH:MM:SS format.
        
        Returns:
            Random time string
        """
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    
    def extract_year_from_name(self, name: str) -> Optional[int]:
        """
        Extract year from folder or file name.
        
        Args:
            name: Folder or file name
            
        Returns:
            Year as integer if found, None otherwise
        """
        # Look for 4-digit year - more flexible pattern
        matches = re.findall(r'(19\d{2}|20\d{2})', name)
        if matches:
            # Take the first valid year found
            for match in matches:
                year = int(match)
                # Sanity check for reasonable year range
                current_year = datetime.now().year
                if 1900 <= year <= current_year + 10:
                    return year
        return None
    
    def get_image_files(self, folder_path: Path) -> List[Path]:
        """
        Get all supported image files in a folder.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            List of image file paths
        """
        image_files = []
        try:
            for file_path in folder_path.iterdir():
                if (file_path.is_file() and 
                    file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS):
                    image_files.append(file_path)
        except PermissionError:
            self.logger.warning(f"Permission denied accessing {folder_path}")
        
        return sorted(image_files)
    
    def process_folder(self, folder_path: Path, year: int) -> Tuple[int, int]:
        """
        Process all images in a folder.
        
        Args:
            folder_path: Path to the folder
            year: Year to set in EXIF data
            
        Returns:
            Tuple of (processed_count, error_count)
        """
        self.logger.info(f"Processing folder: {folder_path} (Year: {year})")
        
        image_files = self.get_image_files(folder_path)
        if not image_files:
            self.logger.info(f"No supported image files found in {folder_path}")
            return 0, 0
        
        folder_processed = 0
        folder_errors = 0
        
        for file_path in image_files:
            if self.set_exif_date(file_path, year):
                folder_processed += 1
            else:
                folder_errors += 1
        
        self.logger.info(f"Completed folder {folder_path}: {folder_processed} processed, {folder_errors} errors")
        return folder_processed, folder_errors
    
    def process_directory_tree(self, base_path: Path, recursive: bool = True) -> None:
        """
        Process directory tree for EXIF updates.
        
        Args:
            base_path: Root directory to process
            recursive: Whether to process subdirectories
        """
        if not base_path.exists():
            self.logger.error(f"Directory does not exist: {base_path}")
            return
        
        if not base_path.is_dir():
            self.logger.error(f"Path is not a directory: {base_path}")
            return
        
        self.logger.info(f"Starting processing of {base_path}")
        total_processed = 0
        total_errors = 0
        
        try:
            if recursive:
                # Process all subdirectories
                for root in base_path.rglob('*'):
                    if (root.is_dir() and 
                        not any(excluded in root.name for excluded in self.EXCLUDED_DIRS)):
                        
                        year = self.extract_year_from_name(root.name)
                        if year:
                            processed, errors = self.process_folder(root, year)
                            total_processed += processed
                            total_errors += errors
                        else:
                            self.logger.debug(f"No year found in folder name: {root}")
            else:
                # Process only immediate subdirectories
                for item in base_path.iterdir():
                    if (item.is_dir() and 
                        not any(excluded in item.name for excluded in self.EXCLUDED_DIRS)):
                        
                        year = self.extract_year_from_name(item.name)
                        if year:
                            processed, errors = self.process_folder(item, year)
                            total_processed += processed
                            total_errors += errors
                        else:
                            self.logger.debug(f"No year found in folder name: {item}")
        
        except KeyboardInterrupt:
            self.logger.info("Processing interrupted by user")
        
        self.logger.info(f"Processing complete: {total_processed} files processed, {total_errors} errors")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Update EXIF data of images based on folder names",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/photos
  %(prog)s /path/to/photos --dry-run
  %(prog)s /path/to/photos --verbose --no-recursive
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='Root directory containing photo folders'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Process only immediate subdirectories'
    )
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = ExifProcessor(dry_run=args.dry_run, verbose=args.verbose)
    
    # Check for exiftool
    if not processor.check_exiftool():
        print("Error: exiftool is required but not found.")
        print("Please install exiftool: https://exiftool.org/")
        sys.exit(1)
    
    # Process directory
    base_path = Path(args.directory).resolve()
    processor.process_directory_tree(base_path, recursive=not args.no_recursive)


if __name__ == "__main__":
    main()
