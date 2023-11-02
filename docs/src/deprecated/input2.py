import js
from src.input import fetch_arrest_records

if __name__ == "__main__":
    # Fetch location data and pass it into the javscript map
    locations = fetch_arrest_records("aloha")
    # Call javascript from python code
    js.generate_new_map(str(locations))
