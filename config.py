# EXIF PySort Configuration
# This file demonstrates how you could extend the script with configuration options

# Supported file extensions (case-insensitive)
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.tiff', '.tif']

# Directories to exclude from processing
EXCLUDED_DIRECTORIES = ['@eaDir', '.DS_Store', 'Thumbs.db', '.thumbnails']

# Year range validation
MIN_YEAR = 1900
MAX_YEAR = 2030

# Default date components when setting EXIF data
DEFAULT_MONTH = 1
DEFAULT_DAY = 1

# ExifTool timeout settings (seconds)
EXIFTOOL_READ_TIMEOUT = 30
EXIFTOOL_WRITE_TIMEOUT = 60

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
