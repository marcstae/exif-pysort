#!/usr/bin/env python3
"""
Tests for the EXIF PySort script
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

# Import the main module
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from exif_pysort_improved import ExifProcessor


class TestExifProcessor(unittest.TestCase):
    """Test cases for ExifProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ExifProcessor(dry_run=True, verbose=False)
    
    def test_extract_year_from_name(self):
        """Test year extraction from folder names."""
        test_cases = [
            ("Photos 2023", 2023),
            ("2022-Summer-Vacation", 2022),
            ("Holiday_2021_Europe", 2021),
            ("2020", 2020),
            ("My Photos from 1999", 1999),
            ("Random Folder", None),
            ("Photos 1899", None),  # Too old
            ("Photos 2150", None),  # Too far in future
        ]
        
        for folder_name, expected_year in test_cases:
            with self.subTest(folder_name=folder_name):
                result = self.processor.extract_year_from_name(folder_name)
                self.assertEqual(result, expected_year)
    
    def test_generate_random_time(self):
        """Test random time generation."""
        time_str = self.processor.generate_random_time()
        self.assertRegex(time_str, r'^\d{2}:\d{2}:\d{2}$')
        
        # Test multiple generations are different
        times = [self.processor.generate_random_time() for _ in range(10)]
        self.assertTrue(len(set(times)) > 1)  # Should have some variety
    
    @patch('subprocess.run')
    def test_check_exiftool_available(self, mock_run):
        """Test exiftool availability check."""
        mock_run.return_value = MagicMock()
        result = self.processor.check_exiftool()
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_check_exiftool_not_available(self, mock_run):
        """Test exiftool not available."""
        mock_run.side_effect = FileNotFoundError()
        result = self.processor.check_exiftool()
        self.assertFalse(result)
    
    def test_get_image_files(self):
        """Test getting image files from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "image1.jpg").touch()
            (temp_path / "image2.jpeg").touch()
            (temp_path / "image3.png").touch()  # Not supported
            (temp_path / "document.txt").touch()  # Not an image
            
            image_files = self.processor.get_image_files(temp_path)
            
            # Should only include supported formats
            self.assertEqual(len(image_files), 2)
            self.assertTrue(all(f.suffix.lower() in ['.jpg', '.jpeg'] for f in image_files))


if __name__ == '__main__':
    unittest.main()
