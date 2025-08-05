#!/usr/bin/env python3
"""
EXIF Photo Sorter

A simple Python script that updates EXIF data of JPEG/TIFF images based on folder names containing years.
Extracts year from folder names and sets EXIF dates to January 1st of that year with random times.

Usage:
    python3 exif_sort.py /path/to/photos
    python3 exif_sort.py /path/to/photos --dry-run
    python3 exif_sort.py /path/to/photos --verbose

Requirements:
    - Python 3.7+
    - exiftool installed on system

Author: GitHub Copilot
"""

import argparse
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, List
import random
from datetime import datetime


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def check_exiftool() -> bool:
    """Check if exiftool is available on the system."""
    try:
        subprocess.run(['exiftool', '-ver'], 
                     capture_output=True, check=True, timeout=10)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def extract_year_from_name(name: str) -> Optional[int]:
    """
    Extract year from folder or file name.
    
    Args:
        name: Folder or file name
        
    Returns:
        Year as integer if found, None otherwise
    """
    # Look for 4-digit year
    matches = re.findall(r'(19\d{2}|20\d{2})', name)
    if matches:
        for match in matches:
            year = int(match)
            # Sanity check for reasonable year range
            current_year = datetime.now().year
            if 1900 <= year <= current_year + 10:
                return year
    return None


def get_exif_year(file_path: Path, logger: logging.Logger) -> Optional[int]:
    """
    Extract the year from the 'DateTimeOriginal' EXIF tag.
    
    Args:
        file_path: Path to the image file
        logger: Logger instance
        
    Returns:
        Year as integer if found, None otherwise
    """
    try:
        result = subprocess.run(
            ['exiftool', '-DateTimeOriginal', '-s3', str(file_path)],
            capture_output=True, text=True, check=True, timeout=30
        )
        
        if result.stdout.strip():
            date_match = re.search(r'^(\d{4})', result.stdout.strip())
            if date_match:
                year = int(date_match.group(1))
                logger.debug(f"Found EXIF year {year} for {file_path}")
                return year
                
    except subprocess.CalledProcessError:
        logger.debug(f"No EXIF data found for {file_path}")
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout reading EXIF data for {file_path}")
    except ValueError as e:
        logger.warning(f"Invalid year format in EXIF data for {file_path}: {e}")
        
    return None


def generate_random_time() -> str:
    """Generate a random time in HH:MM:SS format."""
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def set_exif_date(file_path: Path, year: int, dry_run: bool, logger: logging.Logger) -> bool:
    """
    Set the EXIF data for a file to the specified date.
    
    Args:
        file_path: Path to the image file
        year: Year to set
        dry_run: If True, only simulate the operation
        logger: Logger instance
        
    Returns:
        True if successful, False otherwise
    """
    # Check if update is needed
    current_year = get_exif_year(file_path, logger)
    if current_year == year:
        logger.info(f"EXIF data for {file_path.name} is already correct (Year: {current_year})")
        return True
    
    # Generate random time to avoid duplicate timestamps
    time_str = generate_random_time()
    exif_date = f"{year:04d}:01:01 {time_str}"
    
    if dry_run:
        if current_year is None:
            logger.info(f"[DRY RUN] Would set EXIF date for {file_path.name} to {exif_date}")
        else:
            logger.info(f"[DRY RUN] Would update EXIF date for {file_path.name} from {current_year} to {year}")
        return True
    
    try:
        logger.debug(f"Setting EXIF date for {file_path.name} to {exif_date}")
        
        subprocess.run([
            'exiftool', '-overwrite_original',
            f'-AllDates={exif_date}',
            f'-DateTimeOriginal={exif_date}',
            f'-CreateDate={exif_date}',
            f'-ModifyDate={exif_date}',
            str(file_path)
        ], check=True, capture_output=True, timeout=60)
        
        if current_year is None:
            logger.info(f"Set EXIF date for {file_path.name} to {exif_date}")
        else:
            logger.info(f"Updated EXIF date for {file_path.name} from {current_year} to {year}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set EXIF data for {file_path}: {e}")
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout setting EXIF data for {file_path}")
        return False


def get_image_files(folder_path: Path, logger: logging.Logger) -> List[Path]:
    """
    Get all supported image files in a folder.
    
    Args:
        folder_path: Path to the folder
        logger: Logger instance
        
    Returns:
        List of image file paths
    """
    supported_extensions = ('.jpg', '.jpeg', '.tiff', '.tif')
    image_files = []
    
    try:
        for file_path in folder_path.iterdir():
            if (file_path.is_file() and 
                file_path.suffix.lower() in supported_extensions):
                image_files.append(file_path)
    except PermissionError:
        logger.warning(f"Permission denied accessing {folder_path}")
    
    return sorted(image_files)


def process_folder(folder_path: Path, year: int, dry_run: bool, logger: logging.Logger) -> tuple:
    """
    Process all images in a folder.
    
    Args:
        folder_path: Path to the folder
        year: Year to set in EXIF data
        dry_run: If True, only simulate operations
        logger: Logger instance
        
    Returns:
        Tuple of (processed_count, error_count)
    """
    logger.info(f"Processing folder: {folder_path} (Year: {year})")
    
    image_files = get_image_files(folder_path, logger)
    if not image_files:
        logger.info(f"No supported image files found in {folder_path}")
        return 0, 0
    
    processed_count = 0
    error_count = 0
    
    for file_path in image_files:
        if set_exif_date(file_path, year, dry_run, logger):
            processed_count += 1
        else:
            error_count += 1
    
    logger.info(f"Completed folder {folder_path}: {processed_count} processed, {error_count} errors")
    return processed_count, error_count


def process_directory_tree(base_path: Path, recursive: bool, dry_run: bool, logger: logging.Logger):
    """
    Process directory tree for EXIF updates.
    
    Args:
        base_path: Root directory to process
        recursive: Whether to process subdirectories recursively
        dry_run: If True, only simulate operations
        logger: Logger instance
    """
    if not base_path.exists():
        logger.error(f"Directory does not exist: {base_path}")
        return
    
    if not base_path.is_dir():
        logger.error(f"Path is not a directory: {base_path}")
        return
    
    logger.info(f"Starting processing of {base_path}")
    total_processed = 0
    total_errors = 0
    excluded_dirs = ('@eaDir', '.DS_Store', 'Thumbs.db', '.thumbnails')
    
    try:
        if recursive:
            # Process all subdirectories
            for root in base_path.rglob('*'):
                if (root.is_dir() and 
                    not any(excluded in root.name for excluded in excluded_dirs)):
                    
                    year = extract_year_from_name(root.name)
                    if year:
                        processed, errors = process_folder(root, year, dry_run, logger)
                        total_processed += processed
                        total_errors += errors
                    else:
                        logger.debug(f"No year found in folder name: {root}")
        else:
            # Process only immediate subdirectories
            for item in base_path.iterdir():
                if (item.is_dir() and 
                    not any(excluded in item.name for excluded in excluded_dirs)):
                    
                    year = extract_year_from_name(item.name)
                    if year:
                        processed, errors = process_folder(item, year, dry_run, logger)
                        total_processed += processed
                        total_errors += errors
                    else:
                        logger.debug(f"No year found in folder name: {item}")
    
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    
    logger.info(f"Processing complete: {total_processed} files processed, {total_errors} errors")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Update EXIF data of images based on folder names containing years",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/photos
  %(prog)s /path/to/photos --dry-run
  %(prog)s /path/to/photos --verbose --no-recursive

Supported formats: JPEG (.jpg, .jpeg), TIFF (.tiff, .tif)
Requires: exiftool installed on system
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
    
    # Set up logging
    logger = setup_logging(args.verbose)
    
    # Check for exiftool
    if not check_exiftool():
        print("Error: exiftool is required but not found.")
        print("Install instructions:")
        print("  Ubuntu/Debian: sudo apt-get install exiftool")
        print("  macOS: brew install exiftool") 
        print("  Windows: Download from https://exiftool.org/")
        sys.exit(1)
    
    # Process directory
    base_path = Path(args.directory).resolve()
    process_directory_tree(base_path, not args.no_recursive, args.dry_run, logger)


if __name__ == "__main__":
    main()
