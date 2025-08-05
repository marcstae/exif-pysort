# EXIF PySort

A simple Python script that automatically updates EXIF data of JPEG/TIFF images based on folder names containing years.

## Features

- ✅ **Smart Year Detection**: Automatically extracts years (1900-2099) from folder names
- ✅ **Batch Processing**: Processes entire directory trees recursively  
- ✅ **Dry Run Mode**: Preview changes before applying them
- ✅ **Single File**: Everything you need in one Python script
- ✅ **Command Line Interface**: Easy to use with flexible options
- ✅ **Safe Operation**: Checks existing EXIF data to avoid unnecessary changes

## Requirements

- Python 3.7+ (uses only standard library)
- [ExifTool](https://exiftool.org/) installed on your system

### Installing ExifTool

**Ubuntu/Debian:**
```bash
sudo apt-get install exiftool
```

**macOS (with Homebrew):**
```bash
brew install exiftool
```

**Windows:**
Download from [https://exiftool.org/](https://exiftool.org/)

## Quick Start

1. **Download the script**:
   ```bash
   # Download directly
   curl -O https://raw.githubusercontent.com/marcstae/exif-pysort/main/exif_sort.py
   
   # OR clone the repository
   git clone https://github.com/marcstae/exif-pysort.git
   cd exif-pysort
   ```

2. **Make it executable** (optional):
   ```bash
   chmod +x exif_sort.py
   ```

3. **Run it**:
   ```bash
   python3 exif_sort.py /path/to/your/photo/directory
   ```

## Usage

### Basic Usage

Process all subdirectories recursively:
```bash
python3 exif_sort.py /path/to/your/photos
```

### Options

**Preview changes** (dry run - recommended first):
```bash
python3 exif_sort.py /path/to/photos --dry-run
```

**Verbose output** for detailed logging:
```bash
python3 exif_sort.py /path/to/photos --verbose
```

**Process only immediate subdirectories** (not recursive):
```bash
python3 exif_sort.py /path/to/photos --no-recursive
```

**Combine options**:
```bash
python3 exif_sort.py /path/to/photos --dry-run --verbose
```

### Help

```bash
python3 exif_sort.py --help
```

## How It Works

1. **Scans** the specified directory for folders containing years (1900-2099)
2. **Extracts** the year from folder names using smart pattern matching
3. **Finds** all JPEG/TIFF images in each folder
4. **Checks** existing EXIF data to avoid unnecessary updates
5. **Sets** EXIF date to January 1st of the detected year with a random time
6. **Logs** detailed feedback on all operations

## Example

```bash
# Your folder structure
Photos/
├── Summer_2020/
│   ├── IMG_001.jpg
│   └── IMG_002.jpg
├── Vacation 2021/
│   ├── photo1.jpg
│   └── photo2.jpg
└── Random Folder/    # Skipped (no year)
    └── image.jpg

# Run the script
python3 exif_sort.py Photos/ --dry-run

# Output shows what will happen:
# 2025-08-05 16:00:01 - INFO - Processing folder: Photos/Summer_2020 (Year: 2020)
# 2025-08-05 16:00:01 - INFO - [DRY RUN] Would set EXIF date for IMG_001.jpg to 2020:01:01 14:23:15
# 2025-08-05 16:00:01 - INFO - [DRY RUN] Would set EXIF date for IMG_002.jpg to 2020:01:01 09:41:52
# ...
```

## Supported File Formats

- JPEG (.jpg, .jpeg)
- TIFF (.tiff, .tif)

## Troubleshooting

### Common Issues

1. **"exiftool not found"**: Install ExifTool using the instructions above
2. **Permission errors**: Make sure you have read/write access to the photo directories
3. **No changes made**: Use `--verbose` to see what's happening
4. **Script doesn't find years**: Folder names must contain 4-digit years (1900-2099)

### Getting Help

- Always test with `--dry-run` first
- Use `--verbose` for detailed logs
- Check that ExifTool is installed: `exiftool -ver`

## What's Different from the Original?

This improved version includes:

- ✅ **Command-line interface** instead of interactive prompts
- ✅ **Dry run mode** to preview changes safely
- ✅ **Better error handling** and logging
- ✅ **Type hints** for better code quality
- ✅ **Timeout protection** to prevent hanging
- ✅ **TIFF support** in addition to JPEG
- ✅ **Everything in one file** for simplicity

## License

This project is open source. Feel free to use and modify as needed.
