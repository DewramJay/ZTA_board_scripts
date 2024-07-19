
#this is the code to chech the illgela connection by the users.
# first get the packets from the interface of the laptop's hotspot. here it is local area connection 10
# then get the src abd sst of each aclet
# then check whether that src and dst is in the databse new_devices
# if it is in the database check the allowed devices of that device from the same database
# then check if thta is a illegal connection or not

from scapy.all import sniff
import sqlite3
import json
from scapy.layers.l2 import Ether

def get_allowed_devices(device_mac):
    conn = sqlite3.connect('new_devices.db')
    cursor = conn.cursor()

    try:
        # Query to get the connected devices for the given MAC address
        cursor.execute("SELECT connected_devices FROM new_devices WHERE mac_adress=?", (device_mac,))
        row = cursor.fetchone()

        if row and row[0]:
            # Load the allowed devices from JSON string
            allowed_devices = json.loads(row[0])
            return set(allowed_devices)  # Return as a set for easy comparison

        return set()  # Return an empty set if no devices are found

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return set()
    except Exception as e:
        print(f"Exception in get_allowed_devices: {e}")
        return set()
    finally:
        conn.close()

def is_mac_in_database(mac_address):
    conn = sqlite3.connect('new_devices.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM new_devices WHERE mac_adress=?", (mac_address,))
        row = cursor.fetchone()

        if row:
            return True
        else:
            return False

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Exception in is_mac_in_database: {e}")
        return False
    finally:
        conn.close()
    

def packet_callback(packet):
    flag = 0
    if packet.haslayer(Ether):
        eth_layer = packet.getlayer(Ether)
        src_mac = eth_layer.src
        dst_mac = eth_layer.dst
        # print(f'Source: {src_mac} -> Destination: {dst_mac}')
        # print(f"yyyyyy{is_mac_in_database(src_mac)} and {is_mac_in_database(dst_mac)}")

        if is_mac_in_database(src_mac) and is_mac_in_database(dst_mac):
            # Get allowed devices for the source IP
            allowed_devices = get_allowed_devices(src_mac)
            # print(f'Allowed devices for {src_mac}: {allowed_devices}')
            
            # Check if the destination IP is in the allowed list
            if dst_mac not in allowed_devices:
                print(f"Illegal connection detected: Source {src_mac} -> Destination: {dst_mac}")
            # else:
                # print("allowed")
    

def check_illegal(interface):
    # Replace 'Local Area Connection 10' with the actual interface name
    # interface = 'Local Area Connection* 10'
    print(f"Starting packet capture hhhhhhhhhhhhhhhhhh on {interface}...")
    # Start sniffing on the specified interface
    sniff(iface=interface, prn=packet_callback, store=0 , timeout=10)
