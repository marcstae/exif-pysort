import os
import re
import subprocess
import random

def get_exif_year(file_path):
    """Extracts the year from the 'DateTimeOriginal' EXIF tag."""
    try:
        result = subprocess.run(
            ['exiftool', '-DateTimeOriginal', file_path],
            capture_output=True, text=True, check=True
        )
        output = result.stdout
        print(f"EXIF output for {file_path}: {output}")  # Debug output
        match = re.search(r'Date/Time Original\s*:\s*(\d{4}):', output)
        if match:
            return int(match.group(1))  # Return the extracted year
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving EXIF data: {e}")
    return None  # Return None if EXIF data is not found or error occurs

def set_exif_date(file_path, year, time_str):
    """Sets the EXIF data for a file to the specified year and time if needed."""
    current_year = get_exif_year(file_path)
    if current_year is not None and current_year == year:
        print(f"EXIF data for {file_path} is already correct (Year: {current_year}). No update needed.")
        return
    elif current_year is None:
        print(f"No valid EXIF data found, updating: {file_path}")
    else:
        print(f"Updating EXIF data from Year {current_year} to {year} for {file_path}")

    exif_date = f"{year}:{time_str}"
    subprocess.run(
        [
            'exiftool', '-overwrite_original',
            f'-AllDates={exif_date}',
            f'-DateTimeOriginal={exif_date}',
            f'-CreateDate={exif_date}',
            f'-ModifyDate={exif_date}',
            file_path
        ],
        check=True
    )
    print(f"EXIF data for {file_path} set to {exif_date}.")

def generate_random_time():
    """Generates a random time in the format HH:MM:SS."""
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"

def process_folder(folder_path, year):
    """Processes all images in the specified folder to set EXIF data if required."""
    print(f"Processing folder: {folder_path}, Year detected: {year}")
    random_time_str = f"01:01 {generate_random_time()}"
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith('@eaDir')]
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                set_exif_date(file_path, year, random_time_str)

def main():
    base_path = input("Enter the path to the root directory: ")
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('@eaDir')]
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            year = extract_year_from_name(dir_name)
            if year:
                process_folder(folder_path, year)
            else:
                print(f"No year found in folder name: {folder_path}")

def extract_year_from_name(name):
    """Extracts the year from the folder name. Returns None if no year is found."""
    match = re.search(r'\b(\d{4})\b', name)
    return int(match.group(1)) if match else None

if __name__ == "__main__":
    main()