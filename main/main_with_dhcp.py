import subprocess
import re
import time
import threading
import sqlite3
import requests
from check_open_por import scan_ports
from illagel_and_api_2 import check_illegal
from check_vendor import get_vendor
# from api_and_illegal import monitor_api, delete_alerts
from api_and_illegal_copy import monitor_api, delete_alerts
from encryption_methods import analyze_pcap
# from encryption_method_proto import analyze_pcap
from scapy.all import *
import socketio
from flask import Flask, request, jsonify  # Import Flask and request
import time

# Initialize Flask app
app = Flask(__name__)

#####################################################
# Standard Python
sio = socketio.Client()

@sio.event
def connect():
    print("Connection established with Flask server")

@sio.event
def disconnect():
    print("Disconnected from Flask server")

# Listening to the re_evaluate event from Flask backend
@sio.on('re_evaluate')
def handle_re_evaluate_event(data):
    device_ip = data['device_ip']
    device_mac = data['device_mac']
    hostname = data['hostname']
    interface_description = data['interface_description']
    print(f"Re-evaluating device with IP: {device_ip}, MAC: {device_mac}, hostname: {hostname}, interface: {interface_description}")
    
    if check_device_status(device_mac, device_ip):
        operations_on_device(device_ip, device_mac, hostname, interface_description)

# New endpoint to trigger operations on a device
# @app.route('/trigger_operations', methods=['POST'])
# def trigger_operations():
#     data = request.get_json()
#     device_ip = data.get('device_ip')
#     device_mac = data.get('device_mac')
#     hostname = data.get('hostname')
#     interface_description = data.get('interface_description')

#     # Call the operations_on_device function
#     operations_on_device(device_ip, device_mac, hostname, interface_description)
    
#     return jsonify({"message": "Operations triggered"}), 200

# Function to connect to the Flask Socket.IO server and keep listening for events
def start_socket_io():
    sio.connect('http://localhost:2000')
    sio.wait()

#####################################################

def check_device_status(mac_address, ip_address):
    payload = {
        "mac_address": mac_address,
        "ip_address": ip_address
    }
    
    try:
        response_update = requests.get("http://localhost:2000/api/check_device_status", json=payload)

        if response_update.status_code == 200:
            result = response_update.json()
            
            # Check if the device status is 'active'
            if result.get("device_status") == "active":
                print("Device is active.")
                return True
            elif result.get("device_status") == "inactive":
                print("Device is inactive.")
                return False
            else:
                print(f"Unexpected status: {result.get('device_status')}")
                return False

        else:
            print(f"Failed to retrieve device status: {response_update.status_code}, {response_update.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False


# Ping the device and check if it is still available
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
                update_status(mac, 'inactive')
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

# Update device status
def update_status(mac_address, status):
    payload = {
        "mac_address": mac_address,
        "status": status
    }
    response_update = requests.post("http://localhost:2000/api/update_device_status", json=payload)
        
    if response_update.status_code == 200:
        print("Device status updated in the database")
        return response_update.json()
    else:
        print(f"Failed to update device status: {response_update.status_code}, {response_update.text}")
        return {"status": "error", "message": response_update.text}

####################################

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

def re_evaluate(device_ip, device_mac, hostname, interface_description):
    payload = {
            "ip_address": device_ip,
            "mac_address": device_mac,
            "hostname" : hostname,
            "interface_description" : interface_description
        }
    
    # Check if the device exists
    check_response = requests.post(f"http://localhost:2000/api/re_evaluate", json=payload)
    
    if check_response.status_code == 200:
        # Device exists, update the IP address
        print("Re-evaluation is scheduled.")

    else:
        print("Error in re-evaluation.")

def operations_on_device(device_ip, device_mac, hostname, interface_description):
    # start_time = time.time()
    """Perform operations on the device."""
    print(f"Operating on device: IP {device_ip}, MAC {device_mac}, Hostname {hostname}")
    save_new_device(device_ip, device_mac, hostname, 'active')
    # check the connections within first 30 seconds.
    # check_illegal(interface_description, device_ip, device_mac)
    scan_ports(device_ip, device_mac)
    time.sleep(3)
    re_evaluate(device_ip, device_mac, hostname, interface_description)
    monitor_api(interface_description, device_mac)
    analyze_pcap()
    # end_time = time.time()
    # duration = end_time - start_time
    # print(f"Total time taken: {duration}")
    # Call re-evaluation endpoint

def sniff_dhcp_packets(interface, known_devices, stop_event):
    """Sniff DHCP packets to identify new devices."""
    operations_ongoing_devics = {}
    while not stop_event.is_set():
        
        def process_packet(packet):
            device_info = extract_device_info(packet)
            if device_info and device_info['ip'] and device_info['mac'] != "0.0.0.0":
                mac_address = device_info['mac']

                if mac_address in inactive_devices:
                    # If the device is in the inactive list, move it back to known devices
                    print(f"Device reconnected: IP {device_info['ip']}, MAC {mac_address}, Hostname {device_info['hostname']}")
                    known_devices[mac_address] = inactive_devices.pop(mac_address)
                    
                elif mac_address not in known_devices:
                    # print("))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))")
                    # If the device is new, add it to the known devices list
                    known_devices[mac_address] = device_info
                    print(f"New device seen: IP {device_info['ip']}, MAC {device_info['mac']}, Hostname {device_info['hostname']}")
                    # Perform operations on the device in a separate thread
                    operations_on_device_thread = threading.Thread(target=operations_on_device, args=(device_info['ip'], device_info['mac'], device_info['hostname'], interface))
                    operations_on_device_thread.start()
                
                # Display the current state of active and inactive devices
                print(f"\nActive devices: {known_devices}")
                print(f"Inactive devices: {inactive_devices}\n")
                
                


        print(f"Sniffing on interface: {interface}")
        sniff(filter="udp and (port 67 or port 68)", prn=process_packet, iface=interface, store=0)
        time.sleep(1)

def monitor_devices(known_devices, stop_event, inactive_devices):
    """Ping known devices periodically to check their connectivity."""
    while not stop_event.is_set():
        for mac_address, device_info in list(known_devices.items()):
            ip_address = device_info['ip']
            if not ping_device(ip_address):
                print(f"Device {mac_address} {ping_device(ip_address)}is inactive")
                inactive_devices[device_info['ip']] = mac_address  # Move to inactive devices
                del known_devices[mac_address]  # Remove from known devices
                update_status(mac_address, 'inactive')


            time.sleep(2)


def update_all_devices_to_inactive():
    # Sending POST request to update the status of all devices to 'inactive'
    response = requests.post(f"http://localhost:2000/api/update_all_devices_status")
    
    if response.status_code == 200:
        # Status update successful
        print("All devices updated to inactive successfully.")
    else:
        # There was an error in updating the status
        print(f"Error updating devices: {response.json().get('error', 'Unknown error')}")

def delete_illegal_connections_alert():
    response = requests.delete("http://localhost:2000/api/delete_illegal_connections")
    if response.status_code == 200:
        print("deleted all illegal connection alert")
        return response.json()
    else:
        print(f"Failed to delete illegal connection alerts: {response.status_code}, {response.text}")
        return {"status": "error", "message": response.text}


if __name__ == '__main__':
    interface = "wlan0"  # Replace with your network interface
    known_devices = {}
    inactive_devices = {}
    stop_event = threading.Event()
    update_all_devices_to_inactive()
    delete_alerts()
    delete_illegal_connections_alert()

    # Start the Socket.IO connection in a separate thread
    socket_io_thread = threading.Thread(target=start_socket_io)
    socket_io_thread.start()

    # Start sniffing for DHCP packets
    sniff_thread = threading.Thread(target=sniff_dhcp_packets, args=(interface, known_devices, stop_event))
    sniff_thread.start()

    # Start monitoring devices
    monitor_thread = threading.Thread(target=monitor_devices, args=(known_devices, stop_event, inactive_devices))
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        stop_event.set()
        socket_io_thread.join()
        sniff_thread.join()
        monitor_thread.join()
