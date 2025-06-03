#!/usr/bin/env python3

import sys
import time
from doodle_sdk.doodle_radio import Doodle

def main():
    # Initialize Doodle connection
    doodle_radio = Doodle(ip="10.223.166.69", user="user", password="DoodleSmartRadio")
    
    # Connect to the radio (you'll need to provide IP, username, and password)
    # Example: doodle.connect(ip="192.168.1.100", user="user", password="DoodleSmartRadio")
    if not doodle_radio.connect():
        print("Failed to connect to the Doodle radio")
        sys.exit(1)
    
    print("Connected to Doodle radio successfully")
    
    # Enable link status logging
    print("Enabling link status log...")
    if doodle_radio.enable_link_status_log():
        print("Link status log enabled successfully")
    else:
        print("Failed to enable link status log")
        sys.exit(1)
    
    # Wait 10 seconds for logs to be generated
    print("Waiting 10 seconds for logs to be generated...")
    time.sleep(1)
    
    # Get the log file location
    print("Getting link status log file location...")
    log_location = doodle_radio.get_link_status_log_location()
    
    if log_location:
        print(f"Link status log file location: {log_location}")
    else:
        print("Failed to get link status log file location")
        sys.exit(1)
    
    # Download the log file
    print("Downloading link status log file...")
    download_folder = "./logs"  # You can change this to your preferred folder
    local_file_path = doodle_radio.download_link_status_log(log_location, download_folder)
    
    if local_file_path:
        print(f"Link status log downloaded successfully to: {local_file_path}")
    else:
        print("Failed to download link status log file")
        sys.exit(1)

if __name__ == "__main__":
    main()