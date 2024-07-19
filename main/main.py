import subprocess
import re
import time
import sqlite3
import json
from check_open_por import scan_ports
from illegal_conn import check_illegal
# from dictionary_attack import get_device



def get_connected_devices_windows():
    try:
        result = subprocess.check_output(["arp", "-a"], encoding='utf-8')
        all_ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', result)
        hotspot_subnet = "192.168.137."
        excluded_ips = {"192.168.137.1", "192.168.137.255"}
        connected_devices = [ip for ip in all_ips if ip.startswith(hotspot_subnet) and ip not in excluded_ips]
        return connected_devices
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
        return []
    

def update_device_status():
    connected_devices = get_connected_devices_windows()
    if not connected_devices:
        return
    
    conn = sqlite3.connect('new_devices.db')
    cursor = conn.cursor()

    try:
        # Fetch all MAC addresses from the database
        cursor.execute("SELECT mac_adress FROM new_devices")
        all_macs_in_db = cursor.fetchall()
        
        # Extract MAC addresses from the fetched records
        all_macs_in_db = [mac[0] for mac in all_macs_in_db]
        
        # Get the MAC addresses of currently connected devices
        connected_macs = [get_mac_address(ip) for ip in connected_devices]
        connected_macs = [mac for mac in connected_macs if mac]  # Filter out None values
        
        # Find MACs that are not in the connected devices list
        inactive_macs = set(all_macs_in_db) - set(connected_macs)
        
        # Update status to inactive for those MACs
        for mac in inactive_macs:
            cursor.execute("UPDATE new_devices SET status = 'inactive' WHERE mac_adress = ?", (mac,))
        
        # Update status to active for currently connected devices
        for mac in connected_macs:
            cursor.execute("UPDATE new_devices SET status = 'active' WHERE mac_adress = ?", (mac,))
        
        # Commit the changes
        conn.commit()
    except sqlite3.Error as e:
        print("Database error: ", e)
    finally:
        conn.close()

# Function to get the MAC address of a device
def get_mac_address(ip):
    try:
        result = subprocess.check_output(["arp", "-a", ip], encoding='utf-8')
        mac = re.search(r'(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))', result)
        if mac:
            mac_address = mac.group(0)
            # Replace hyphens with colons
            formatted_mac_address = mac_address.replace('-', ':')
            return formatted_mac_address
        return None
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
        return None
    
def save_new_device(ip_address, mac_address, device_name,status):
    conn = sqlite3.connect('new_devices.db')
    cursor = conn.cursor()

    cursor.execute("SELECT mac_adress FROM new_devices WHERE mac_adress = ?", (device_mac,))
    mac=cursor.fetchone()
    if mac:
        print("Device already exists in the database")
    else:
        # cursor('')
        cursor.execute("INSERT INTO new_devices (ip_address, mac_adress, device_name, status) VALUES (?, ?, ?,?)",
                    (ip_address, mac_address, device_name,status))
        conn.commit()
        conn.close()
        print("Device added to the database")


if __name__ == "__main__":
    interface_description = 'Local Area Connection* 10'
    previous_devices = set()
    print("Starting the hotspot monitoring server...")
    interval=10
    while True:
        update_device_status()
        current_devices = set(get_connected_devices_windows())
        new_devices = current_devices - previous_devices
        if new_devices:
            for device_ip in new_devices:
                print(f"New device connected: {device_ip}")
                device_mac=get_mac_address(device_ip)
                print(f"MAC of the new device :{device_mac}")
                save_new_device(device_ip,device_mac, '','active' )
                check_illegal(interface_description)
                print("----------------------------")
                scan_ports(device_ip) #checks both the ports and the dictionary attack

        previous_devices = current_devices
        time.sleep(interval)