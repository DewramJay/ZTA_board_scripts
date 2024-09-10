import subprocess
import re
import time
import threading
import sqlite3
import requests
from check_open_por import scan_ports
from illagel_and_api_2 import check_illegal
from check_vendor import get_vendor
# from api_usage import monitor_api
from api_and_illegal import monitor_api
from scapy.all import *

#ping the devic and check if it is still available
#in the previous version (main_thread) it used ttl something, but here just pinging
def ping_device(ip_address):
    """Ping a device and return True if it's reachable."""
    response = os.system(f"ping -c 1 -w {4} {ip_address} > /dev/null 2>&1")
    return response == 0

def update_device_status(inactive_devices):
    try:
        conn = sqlite3.connect('new_devices.db')
        cursor = conn.cursor()
        for ip, mac in inactive_devices.items():
            if not ping_device(ip):
                print(f"999999{ping_device(ip)}")
                cursor.execute("UPDATE new_devices SET status = ? WHERE mac_adress = ?", ('inactive', mac))
                conn.commit()
                print("Status updated to inactive for MAC:", mac)
                return True
            else:
                print("Device is still active, not updating status for MAC:", mac)
                return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close() 

def extract_device_info(packet):
    """Extract and return device info (IP, MAC, Hostname) from DHCP packet."""
    if packet.haslayer(DHCP):
        mac_address = packet[Ether].src  # MAC address of the device
        ip_address = None
        hostname = None
        options = packet[DHCP].options
        for option in options:
            if option[0] == 'requested_addr':  # IP requested by the client
                ip_address = option[1]
            elif option[0] == 'hostname':  # DHCP Option 12 contains the hostname
                hostname = option[1].decode()
            elif option[0] == 'yiaddr':  # 'yiaddr' is the address being assigned to the client
                ip_address = packet[IP].dst  # This should be the correct IP

        return {'ip': ip_address, 'mac': mac_address, 'hostname': hostname}
    return None

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



def operations_on_device(device_ip, device_mac, hostname, interface_description):
    """Perform operations on the device."""
    print(f"Operating on device: IP {device_ip}, MAC {device_mac}, Hostname {hostname}")
    save_new_device(device_ip,device_mac, hostname,'active' )
    check_illegal(interface_description,device_ip,device_mac)
    scan_ports(device_ip, device_mac)
    time.sleep(3)
    monitor_api(interface_description,device_mac)

def sniff_dhcp_packets(interface, known_devices,stop_event):
    """Sniff DHCP packets to identify new devices."""
    
    while not stop_event.is_set():
        
        def process_packet(packet):
            device_info = extract_device_info(packet)
            if device_info and device_info['ip'] and device_info['mac'] != "0.0.0.0":
                mac_address = device_info['mac']

                if mac_address in inactive_devices:
                    # If the device is in the inactive list, move it back to known devices
                    print(f"Device reconnected: IP {device_info['ip']}, MAC {mac_address}, Hostname {device_info['hostname']}")
                    known_devices[mac_address] = inactive_devices.pop(mac_address)
                else:
                    # If the device is new, add it to the known devices list
                    known_devices[mac_address] = device_info
                    print(f"New device seen: IP {device_info['ip']}, MAC {device_info['mac']}, Hostname {device_info['hostname']}")
                
                # Display the current state of active and inactive devices
                print(f"\nActive devices: {known_devices}")
                print(f"Inactive devices: {inactive_devices}\n")
                
                # Perform operations on the device in a separate thread
                operations_on_device_thread = threading.Thread(target=operations_on_device, args=(device_info['ip'], device_info['mac'], device_info['hostname'], interface))
                operations_on_device_thread.start()

        print(f"Sniffing on interface: {interface}")
        sniff(filter="udp and (port 67 or port 68)", prn=process_packet, iface=interface, store=0)
        time.sleep(1)



def monitor_devices(known_devices,stop_event, inactive_devices):
    """Ping known devices periodically to check their connectivity."""
    while not stop_event.set():
        for mac_address, device_info in list(known_devices.items()):
            if not ping_device(device_info['ip']):
                print(f"Device disconnected: IP {device_info['ip']}, MAC {mac_address}, Hostname {device_info['hostname']}")
                # Add to inactive devices
                if update_device_status({device_info['ip']: mac_address}):
                    # If the device status was successfully updated to inactive
                    # Add to inactive devices
                    inactive_devices[mac_address] = device_info
                    # Remove from known devices
                    del known_devices[mac_address]

                print(f"\nActive devices: {known_devices}")
                print(f"inactive devices: {inactive_devices}\n")
        
        time.sleep(30)  # Wait before next round of pings



if __name__ == "__main__":
    known_devices = {}
    inactive_devices = {}
    interface = "wlan0"  # Replace with your actual interface name
    stop_event = threading.Event()

    sniff_thread = threading.Thread(target=sniff_dhcp_packets, args=(interface, known_devices,stop_event))
    sniff_thread.start()

    monitor_thread = threading.Thread(target=monitor_devices, args=(known_devices,stop_event,inactive_devices))
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping DHCP sniffing and device monitoring...")
        stop_event.set()
        sniff_thread.join()
        monitor_thread.join()
        print("Threads stopped.")