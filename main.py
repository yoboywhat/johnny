import csv
import re
import pandas as pd
from difflib import get_close_matches

def load_world_locations(file_path):
    locations = {}
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_name = f"{row['locationName']}, {row['countryName']}".lower()
            locations[location_name] = row['geonameID']
    return locations

def normalize_location(location):
    location = re.sub(r'\s+', ' ', location.strip().lower())
    parts = location.split(',')
    
    if len(parts) > 2 and parts[-1].strip() == parts[-2].strip():
        location = ','.join(parts[:-1]).strip()
    
    if len(parts) >= 2:
        city = parts[0].strip()
        country = parts[-1].strip()
        return f"{city}, {country}"
    else:
        return location

def match_location(location, world_locations):
    normalized_location = normalize_location(location)
    
    location_id = world_locations.get(normalized_location)
    
    if location_id:
        return location_id
    
    location_keys = list(world_locations.keys())
    close_matches = get_close_matches(normalized_location, location_keys, n=1, cutoff=0.8)  # Adjust the cutoff as needed
    
    if close_matches:
        return world_locations[close_matches[0]]
    
    return None

input_file = "/Users/johnnyrobert/Desktop/Jobs Bringer/Datasets/Companies Dataset/companies_sorted.csv"
world_locations_file = "/Users/johnnyrobert/Desktop/Jobs Bringer/Datasets/World Locations Dataset/WorldLocations.csv"
output_file = "/Users/johnnyrobert/Desktop/Jobs Bringer/Datasets/Companies Dataset/company_with_location_ids.csv"

world_locations = load_world_locations(world_locations_file)

start_time = time.time()
total_lines = sum(1 for _ in open(input_file, 'r'))

with open(input_file, "r") as file:
    reader = csv.DictReader(file)

    with open(output_file, "w") as output:
        writer = csv.writer(output)
        writer.writerow(["company_name", "location_id", "location_name"])

        unmatched_locations = []

        for row in reader:
            company_name = row["name"]

            words = re.findall(r"[\w']+", company_name)
            capitalized_words = [word.capitalize() if "'" not in word else word.split("'")[0].capitalize() + "'" + word.split("'")[1].lower() for word in words]
            capitalized_company_name = " ".join(capitalized_words)

            company_location = f"{row['locality']}, {row['country']}"
            normalized_location = normalize_location(company_location)

            location_id = match_location(normalized_location, world_locations)

            if location_id:
                writer.writerow([capitalized_company_name, location_id, normalized_location])
            else:
                writer.writerow([capitalized_company_name, "N/A", normalized_location])
                unmatched_locations.append(normalized_location)

    csv_file_size = os.path.getsize(output_file) / (1024 * 1024)  # size in MB
    print(f"CSV file '{output_file}' created successfully. CSV file size: {csv_file_size:.2f} MB.")

unmatched_file = "/Users/johnnyrobert/Desktop/Jobs Bringer/Datasets/Companies Dataset/unmatched_locations.txt"
with open(unmatched_file, "w") as file:
    file.write("\n".join(unmatched_locations))

print(f"Unmatched locations saved to: {unmatched_file}")

