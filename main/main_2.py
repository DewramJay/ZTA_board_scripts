import subprocess
import re
import csv
import sqlite3
from scapy.all import sniff
import socket
from illegal_conn import check_illegal


def get_interface_ip(interface_description):
    try:
        # Run the ipconfig command
        result = subprocess.check_output(["ipconfig"], encoding='utf-8')
        # Split the output by lines
        lines = result.splitlines()
        # Search for the specific interface description
        interface_found = False
        for line in lines:
            if interface_description in line:
                interface_found = True
            # When the interface is found, look for its IPv4 address
            if interface_found and "IPv4 Address" in line:
                # Extract the IP address
                ip_address = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line).group(0)
                return ip_address
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
    return None

def get_connected_devices():
    conn = sqlite3.connect('new_devices.db')
    cursor  = conn.cursor()
    cursor.execute("SELECT ip_address FROM new_devices WHERE status =?",('active',))
    devices = cursor.fetchall()
    print(devices)
    return devices



if __name__ == "__main__":
    interface_description = 'Local Area Connection* 10'
    output_file = 'packet_capture.csv'
    connected_devices = get_connected_devices()
    if connected_devices:
        print("Connected devices:")
        for device in connected_devices:
            print(device)
            check_illegal(interface_description)

    else:
        print("No connected devices found.")