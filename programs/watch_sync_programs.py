#!/usr/bin/env python3
import os, json, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import upsert_program
from config.config import config
from utils import util

def scan_directory_for_json_files(directory):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        # Check if the file ends with .json
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            util.logger.info(f"Processing file: {file_path}")
            
            # Open and read the JSON file
            with open(file_path, 'r') as file:
                try:
                    data = json.load(file)
                    # Print properties
                    upsert_program(data.get('program_name'), data.get('scopes'), data.get('ooscopes'), {})

                except json.JSONDecodeError as e:
                    util.logger.info(f"Error parsing JSON file {file_path}: {e}")

def scan_programs():
    directory_to_scan = os.path.join(config().get('WATCH_DIR'), 'programs')
    scan_directory_for_json_files(directory_to_scan)
    

if __name__ == "__main__":
    scan_programs()