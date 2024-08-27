# Photo EXIF PySort

## Description
The Photo EXIF PySorter is a Python script designed to update the EXIF data of JPEG images in a directory based on the year extracted from the folder names. It sets the 'Date/Time Original' EXIF field to January 1st of the year mentioned in the folder name, alongside a randomly generated time, ensuring all images within the same folder share the same timestamp.

## Functions

### `get_exif_year(file_path)`
Extracts the year from the 'Date/Time Original' field in the EXIF data of the image.
- **Parameters**:
  - `file_path`: The full path to the image file.
- **Returns**:
  - The year as an integer if found, `None` otherwise.

### `set_exif_date(file_path, year, time_str)`
Sets the EXIF date of an image to the specified year and a randomly generated time if the current EXIF year is different or missing.
- **Parameters**:
  - `file_path`: The full path to the image file.
  - `year`: The year to set in the EXIF data.
  - `time_str`: The time string (HH:MM:SS) to use in the EXIF data.
  
### `generate_random_time()`
Generates a random time string in the format HH:MM:SS.
- **Returns**:
  - A string representing the time.

### `process_folder(folder_path, year)`
Processes all JPEG images in the specified folder, updating their EXIF data if necessary.
- **Parameters**:
  - `folder_path`: The path to the directory containing images.
  - `year`: The year to set in the EXIF data based on the folder name.

### `extract_year_from_name(name)`
Extracts the year from a folder name.
- **Parameters**:
  - `name`: The folder name.
- **Returns**:
  - The year as an integer if found, `None` otherwise.

### `main()`
The main function that prompts the user for the root directory path and processes each folder.

## How to Use
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/marcstae/exif-pysort.git
   cd exif-pysort
