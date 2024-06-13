import pandas as pd
import re
from difflib import get_close_matches
from tqdm import tqdm
from functools import lru_cache

def normalize_location(location):
    location = re.sub(r'\s+', ' ', location.strip().lower())  # Normalize spaces and case
    parts = location.split(',')
    
    if len(parts) > 2 and parts[-1].strip() == parts[-2].strip():
        location = ','.join(parts[:-1]).strip()
    
    if len(parts) >= 2:
        city = parts[0].strip()
        country = parts[-1].strip()
        return f"{city}, {country}"
    else:
        return location
def load_world_locations(file_path):
    df = pd.read_csv(file_path)
    df['normalized_location'] = df.apply(lambda row: f"{row['locationName']}, {row['countryName']}".lower(), axis=1)
    location_dict = pd.Series(df['geonameID'].values, index=df['normalized_location']).to_dict()
    return location_dict

@lru_cache(maxsize=None)
def match_location(normalized_location, world_locations):
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

# Load world locations
world_locations = load_world_locations(world_locations_file)

# Load company data
company_df = pd.read_csv(input_file)

company_df['normalized_location'] = company_df.apply(lambda row: normalize_location(f"{row['locality']}, {row['country']}"), axis=1)

# Create columns for the location ID and name
company_df['location_id'] = company_df['normalized_location'].apply(lambda loc: match_location(loc, world_locations))
company_df['location_name'] = company_df['normalized_location']

# Replace unmatched locations with a default value or leave them as is
company_df.loc[company_df['location_id'].isna(), 'location_id'] = "N/A"

output_df = company_df[['name', 'location_id', 'location_name']]
output_df.columns = ['company_name', 'location_id', 'location_name']

output_df.to_csv(output_file, index=False)

print(f"CSV file '{output_file}' created successfully. File size: {os.path.getsize(output_file) / (1024 * 1024):.2f} MB.")
