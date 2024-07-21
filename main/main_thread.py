import subprocess
import re
import time
import threading
import sqlite3
from check_open_por import scan_ports
from illagel_and_api_2 import check_illegal
from check_vendor import get_vendor

def ping_device(ip):
    try:
        # Ping the device with a timeout of 1 second
        result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], capture_output=True, encoding='utf-8')
        return 'TTL=' in result.stdout
    except subprocess.CalledProcessError:
        return False
    
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

    cursor.execute("SELECT mac_adress FROM new_devices WHERE mac_adress = ?", (mac_address,))
    mac=cursor.fetchone()
    if mac:
        print("Device already exists in the database")
        cursor.execute("UPDATE new_devices SET ip_address =? WHERE mac_adress=?",(ip_address,mac_address))
        conn.commit()
    else:
        # cursor('')
        cursor.execute("INSERT INTO new_devices (ip_address, mac_adress, device_name, status) VALUES (?, ?, ?,?)",
                    (ip_address, mac_address, device_name,status))
        conn.commit()
        conn.close()
        print("Device added to the database")
    
def operations_on_device(device_ip,interface_description):
    device_mac=get_mac_address(device_ip)
    save_new_device(device_ip,device_mac, '','active' )
    check_illegal(interface_description,device_ip,device_mac)
    scan_ports(device_ip)
    get_vendor(device_mac)


def get_connected_devices_windows(stop_event):
    previous_devices = set()
    interface_description = "Local Area Connection* 10"
    while not stop_event.is_set():
        try:
            result = subprocess.check_output(["arp", "-a"], encoding='utf-8')
            all_ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', result)
            hotspot_subnet = "192.168.137."
            excluded_ips = {"192.168.137.1", "192.168.137.255"}
            connected_devices = {ip for ip in all_ips if ip.startswith(hotspot_subnet) and ip not in excluded_ips}

            # Confirm connection status by pinging each IP address
            
            active_devices = {ip for ip in connected_devices if ping_device(ip)}

            # Find new devices
            new_devices = active_devices - previous_devices
            print(f"new device = {new_devices}")

            for new_device in new_devices:
                print(f"New device connected---------------: {new_device}")
                operations_on_device_thread = threading.Thread(target=operations_on_device, args=(new_device,interface_description))
                operations_on_device_thread.start()

            # Update previous devices
            previous_devices = active_devices
            print(f"Active devices :{active_devices}")

            time.sleep(1)
        except subprocess.CalledProcessError as e:
            print("Error: ", e)

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
