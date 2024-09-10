import socket
from scapy.all import sniff, wrpcap
from scapy.layers.l2 import Ether
import sqlite3
import json
import requests
from score_api import score_illegal_conn

def resolve_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None
    
# def store_in_db(device_mac, blacklist_mac):
#     conn = sqlite3.connect(r'C:\Users\User\Desktop\project\new_devices.db')
#     cursor = conn.cursor()

#     try:
#         cursor.execute("INSERT INTO url_alerts (mac_address, blacklist_mac) VALUES (?, ?)", (device_mac, blacklist_mac))
#         conn.commit()
#         print("saved into database")

#     except sqlite3.Error as e:
#         print(f"Database error: {e}")
#         return set()
#     except Exception as e:
#         print(f"Exception in get_allowed_devices: {e}")
#         return set()
#     finally:
#         conn.close()

def store_in_db(device_mac, blacklist_mac):
    payload = {
            "mac_address": device_mac,
            "blacklist_mac": blacklist_mac
        }
    response = requests.post("http://localhost:2000/api/add_url_alert", json=payload)
    if response.status_code == 200:
        print("Device added to the database")
        return response.json()
    else:
        print(f"Failed to add device: {response.status_code}, {response.text}")
        return {"status": "error", "message": response.text}


def process_packet(packet, target_mac, collected_packets, blacklisted_macs,illegal_connections):
    # def process_packet(packet,target_ip, collected_data,connecting_devices):
    
    if 'IP' in packet:
        source_ip = packet['IP'].src
        dest_ip = packet['IP'].dst
        src_mac = packet[Ether].src if Ether in packet else 'N/A'
        dst_mac = packet[Ether].dst if Ether in packet else 'N/A'

        if src_mac == target_mac or dst_mac == target_mac:
            protocol = packet.sprintf("%IP.proto%")
            dns_name = resolve_dns(dest_ip) if dst_mac != target_mac else resolve_dns(source_ip)
            # print(dns_name)
            # Check if dst_mac is in the blacklisted MAC addresses
            if dst_mac in blacklisted_macs:
                print(f"Blacklisted MAC address detected: {dst_mac}")
                if dst_mac not in illegal_connections:
                    illegal_connections.append(dst_mac)
                    # print("hhhhh")
                    store_in_db(target_mac, dst_mac)
        
            # Store the packet
            collected_packets.append(packet)

def delete_alerts():
    response = requests.delete("http://localhost:2000/api/delete_all_alert")
    if response.status_code == 200:
        print("deleted all alert")
        return response.json()
    else:
        print(f"Failed to delete alerts: {response.status_code}, {response.text}")
        return {"status": "error", "message": response.text}


def monitor_api(interface_description,device_mac):
    illegal_connections = []
    # interface_description = 'Local Area Connection* 10'
    # device_mac = '42:56:21:fc:c9:36'
    # output_file = 'packet_capture.pcap'
    collected_packets = []
    
    # Define the list of blacklisted MAC addresses
    blacklisted_macs = [
        '5a:96:1d:ca:62:2d','c6:2d:c5:0d:36:16',
        '00:1a:2b:3c:4d:5e','b8:27:eb:88:13:e7','ba:8a:d5:8e:53:30'
        # Add more MAC addresses as needed
    ]

    delete_alerts()
    
    
    sniff(iface=interface_description, prn=lambda x: process_packet(x, device_mac, collected_packets, blacklisted_macs,illegal_connections), timeout=20, store=0)
    if illegal_connections:
        # print(f"no of illegal conections : {len(illegal_connections)}")
        print(f"The score for illegal connections {score_illegal_conn(len(illegal_connections))} *******************")

