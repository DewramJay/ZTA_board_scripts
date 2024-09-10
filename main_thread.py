import subprocess
import re
import time
import threading
import sqlite3
import requests
from check_open_por import scan_ports
from illagel_and_api_2 import check_illegal
from check_vendor import get_vendor
from api_usage import monitor_api

def ping_device(ip):
    try:
        # Ping the device with a timeout of 1 second
        result = subprocess.run(["ping", "-c", "1", "-W", "4", ip], capture_output=True, encoding='utf-8')
        return 'ttl=' in result.stdout.lower()
    except subprocess.CalledProcessError:
        return False
    
# def get_mac_address(ip):
#     try:
#         result = subprocess.check_output(["arp", "-a", ip], encoding='utf-8')
#         mac = re.search(r'(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))', result)
#         if mac:
#             mac_address = mac.group(0)
#             # Replace hyphens with colons
#             formatted_mac_address = mac_address.replace('-', ':')
#             return formatted_mac_address
#         return None
#     except subprocess.CalledProcessError as e:
#         print("Error: ", e)
#         return None

def update_device_status(inactive_devices):
    try:
        conn = sqlite3.connect('new_devices.db')
        cursor = conn.cursor()
        for ip, mac in inactive_devices.items():
            if not ping_device(ip):
                print(f"999999{ping_device(ip)}")
                cursor.execute("UPDATE new_devices SET status = ? WHERE mac_adress = ?", ('inactive', mac))
                conn.commit()
                print("Status updated to inactive")
                return True
            else:
                print("Not actually inactive *****")
                return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()  
# def save_new_device(ip_address, mac_address, device_name,status):
#     conn = sqlite3.connect(r'C:\Users\User\Desktop\project\new_devices.db')
#     cursor = conn.cursor()

#     cursor.execute("SELECT mac_adress FROM new_devices WHERE mac_adress = ?", (mac_address,))
#     mac=cursor.fetchone()
#     if mac:
#         print("Device already exists in the database")
#         cursor.execute("UPDATE new_devices SET ip_address =? WHERE mac_adress=?",(ip_address,mac_address))
#         conn.commit()
#     else:
#         # cursor('')
#         cursor.execute("INSERT INTO new_devices (ip_address, mac_adress, device_name, status) VALUES (?, ?, ?,?)",
#                     (ip_address, mac_address, device_name,status))
#         conn.commit()
#         conn.close()
#         print("Device added to the database")

def save_new_device(ip_address, mac_address, device_name, status):
    payload = {
        "ip_address": ip_address,
        "mac_address": mac_address,
        "device_name": device_name,
        "status": status
    }
    
    # Check if the device exists
    check_response = requests.get(f"http://localhost:2000/api/get_device/{mac_address}")
    
    if check_response.status_code == 200:
        # Device exists, update the IP address
        print("Device already exists in the database. Updating the IP address.")
        update_payload = {
            "mac_address": mac_address,
            "ip_address": ip_address,
            "status":status
        }
        response_update = requests.post("http://localhost:2000/api/update_ip", json=update_payload)
        
        if response_update.status_code == 200:
            print("Device IP address updated in the database")
            return response_update.json()
        else:
            print(f"Failed to update device: {response_update.status_code}, {response_update.text}")
            return {"status": "error", "message": response_update.text}
    elif check_response.status_code == 404:
        # Device does not exist, add new device
        response = requests.post("http://localhost:2000/api/add_device", json=payload)
        
        if response.status_code == 200:
            print("Device added to the database")
            return response.json()
        else:
            print(f"Failed to add device: {response.status_code}, {response.text}")
            return {"status": "error", "message": response.text}
    else:
        print(f"Failed to check device existence: {check_response.status_code}, {check_response.text}")
        return {"status": "error", "message": check_response.text}

    
def operations_on_device(device_ip,device_mac,interface_description):
    # device_mac=get_mac_address(device_ip)
    vendor = get_vendor(device_mac)
    save_new_device(device_ip,device_mac, vendor,'active' )
    check_illegal(interface_description,device_ip,device_mac)
    scan_ports(device_ip, device_mac)
    time.sleep(3)
    monitor_api(interface_description,device_mac)


def get_connected_devices_windows(stop_event):
    previous_devices = {}
    interface_description = "wlan0"
    while not stop_event.is_set():
        try:
            result = subprocess.check_output(["sudo", "arp-scan", "-l", "-I", interface_description], encoding='utf-8')
            # print(result)  # Debug print
            ip_mac_pairs = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))', result)
            # print(ip_mac_pairs)  # Debug print to see what is matched
            hotspot_subnet = "192.168.28."
            excluded_ips = {"192.168.28.1", "192.168.28.255"}
            connected_devices = {ip for (ip, mac, *_) in ip_mac_pairs if ip.startswith(hotspot_subnet) and ip not in excluded_ips}

            # Confirm connection status by pinging each IP address
            active_devices = {ip for ip in connected_devices if ping_device(ip)}

            # Update dictionary with active devices and their MAC addresses
            active_device_dict = {ip: mac for ip, mac, *_ in ip_mac_pairs if ip in active_devices}

            # Find new devices
            new_devices = active_device_dict.keys() - previous_devices.keys()
            inactive_devices = {ip: previous_devices[ip] for ip in set(previous_devices.keys()) - set(active_device_dict.keys())}            
            # print(f"MAC addresses: {ip_mac_pairs}")
            print(f"New devices: {new_devices}")

            for new_device in new_devices:
                device_mac = active_device_dict[new_device]
                print(f"New device connected: ---------------------------  {new_device} with MAC {device_mac}")
                operations_on_device_thread = threading.Thread(target=operations_on_device, args=(new_device, device_mac, interface_description))
                operations_on_device_thread.start()

            # Update previous devices
            previous_devices = active_device_dict
            # print(f"Inactive devices :{inactive_devices}")
            # print(f"Active devices :{active_devices}")

            if inactive_devices:
                if not update_device_status(inactive_devices):
                    previous_devices.update(inactive_devices)

            time.sleep(1)
        except subprocess.CalledProcessError as e:
            print("Error: ", e)
            print(f"Command output: {e.output}")

if __name__ == "__main__":
    stop_event = threading.Event()
    get_connected_devices_thread = threading.Thread(target=get_connected_devices_windows, args=(stop_event,))
    get_connected_devices_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        get_connected_devices_thread.join()
