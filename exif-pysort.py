import os
import re
import exiftool

def set_exif_date(file_path, year):
    """Setzt die EXIF-Daten für eine Datei auf das angegebene Jahr."""
    with exiftool.ExifTool() as et:
        # Set the EXIF creation year manually
        exif_date = f"{year}:01:01 00:00:00"
        et.execute(
            b"-overwrite_original",
            b"-AllDates=" + exif_date.encode('utf-8'),
            b"-DateTimeOriginal=" + exif_date.encode('utf-8'),
            b"-CreateDate=" + exif_date.encode('utf-8'),
            b"-ModifyDate=" + exif_date.encode('utf-8'),
            file_path.encode('utf-8')
        )

def process_folder(folder_path, year):
    """Durchläuft alle Bilder im angegebenen Ordner und setzt die EXIF-Daten."""
    print(f"Bearbeite Ordner: {folder_path}, Jahr erkannt: {year}")
    for root, dirs, files in os.walk(folder_path):
        # Ignoriere @eaDir Verzeichnisse
        dirs[:] = [d for d in dirs if not d.startswith('@eaDir')]
        for file in files:
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                file_path = os.path.join(root, file)
                try:
                    set_exif_date(file_path, year)
                    print(f"EXIF-Daten für {file_path} gesetzt.")
                except Exception as e:
                    print(f"Fehler beim Bearbeiten von {file_path}: {e}")

def extract_year_from_name(name):
    """Extrahiert das Jahr aus dem Ordnernamen. Gibt None zurück, wenn kein Jahr gefunden wird."""
    # Suche nach einer vierstelligen Jahreszahl
    match = re.search(r'\b(\d{4})\b', name)
    return int(match.group(1)) if match else None

def main():
    """Hauptfunktion zur Verarbeitung aller Bildordner."""
    base_path = input("Geben Sie den Pfad zum Stammverzeichnis ein: ")
    for root, dirs, files in os.walk(base_path):
        # Ignoriere @eaDir Verzeichnisse
        dirs[:] = [d for d in dirs if not d.startswith('@eaDir')]
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            try:
                # Jahr aus dem Ordnernamen extrahieren
                year = extract_year_from_name(dir_name)
                if year:
                    process_folder(folder_path, year)
                else:
                    print(f"Kein Jahr im Ordnernamen gefunden: {folder_path}")
            except Exception as e:
                print(f"Fehler beim Bearbeiten von {folder_path}: {e}")

if __name__ == "__main__":
    main()