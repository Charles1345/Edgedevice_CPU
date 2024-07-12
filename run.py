import os
import subprocess

# Folder to be copied
source_folder = r"C:\Users\13462\Downloads\HW2"
# Destination base path on the remote devices
destination_base = "/home/student"
# Remote username
username = "student"
# List of device numbers to exclude
excluded_devices = {32}

# SCP function to copy the folder
def scp_to_device(device_str, source_folder, destination_path):
    scp_command = ["scp", "-r", source_folder, destination_path]
    try:
        result = subprocess.run(scp_command, check=True, text=True, capture_output=True)
        print(f"Successfully copied to {device_str}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy to {device_str}: {e.stderr}")

for device_num in range(1, 36):
    if device_num in excluded_devices:
        continue
    # Format device number to two digits
    device_str = f"{device_num:02}"
    # Construct the remote device address and destination path
    remote_device = f"sld-mc1-{device_str}.ece.utexas.edu"
    destination_path = f"{username}@{remote_device}:{destination_base}"
    
    # Copy the folder to the remote device
    scp_to_device(remote_device, source_folder, destination_path)

print("All operations completed.")
