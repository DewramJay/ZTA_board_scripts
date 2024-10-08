from scapy.all import sniff
import sqlite3
import json
from scapy.layers.l2 import Ether
import subprocess
import re
import socket

illegal_connections =[]

def resolve_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None
    

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

def store_dns_name_in_db(source_ip, src_mac, collected_data):
    conn = sqlite3.connect('new_devices.db')
    cursor = conn.cursor()

    dns_names = ','.join(set([data['dns_name'] for data in collected_data if data['dns_name']]))
    dest_ips = ','.join(set([data['dest_ip'] for data in collected_data]))
    dest_macs = ','.join(set([data['dest_mac'] for data in collected_data]))

    cursor.execute('SELECT dns_name, dest_ip, dest_mac FROM visited_url WHERE source_ip = ?', (source_ip,))
    row = cursor.fetchone()

    if row:
        # Update the existing row
        existing_dns_names = set(row[0].split(',')) if row[0] else set()
        existing_dest_ips = set(row[1].split(',')) if row[1] else set()
        existing_dest_macs = set(row[2].split(',')) if row[2] else set()

        new_dns_names = ','.join(existing_dns_names.union(set(dns_names.split(','))))
        new_dest_ips = ','.join(existing_dest_ips.union(set(dest_ips.split(','))))
        new_dest_macs = ','.join(existing_dest_macs.union(set(dest_macs.split(','))))

        cursor.execute('''
            UPDATE visited_url
            SET dns_name = ?, dest_ip = ?, dest_mac = ?
            WHERE source_ip = ?
        ''', (new_dns_names, new_dest_ips, new_dest_macs, source_ip))
    else:
        # Insert a new row
        cursor.execute('''
            INSERT INTO visited_url (source_ip, source_mac, dns_name, dest_ip, dest_mac)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_ip, src_mac, dns_names, dest_ips, dest_macs))


    conn.commit()
    conn.close()

def update_connected_devices(device_mac, new_connections):
    conn = sqlite3.connect('new_devices.db')
    cursor = conn.cursor()

    def fetch_connected_devices(mac):
        cursor.execute("SELECT connected_devices FROM new_devices WHERE mac_adress=?", (mac,))
        row = cursor.fetchone()
        if row is not None and row[0] is not None:
            return json.loads(row[0])
        return []

    def update_device(mac, connections):
        current_connections = fetch_connected_devices(mac)
        updated_connections = list(set(current_connections + connections))
        cursor.execute("UPDATE new_devices SET connected_devices=? WHERE mac_adress=?", (json.dumps(updated_connections), mac))

    try:
        # Update the connecting devices for the main device
        update_device(device_mac, new_connections)

        # Update the connecting devices for each new connection to include the main device
        for connection in new_connections:
            update_device(connection, [device_mac])

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Exception in update_connected_devices: {e}")
        return False
    finally:
        conn.close()


def process_packet(packet,target_ip, collected_data,connecting_devices):
    global illegal_connections
    
    if 'IP' in packet:

        source_ip = packet['IP'].src
        dest_ip = packet['IP'].dst
        if source_ip == target_ip or dest_ip == target_ip:

            protocol = packet.sprintf("%IP.proto%")
            dns_name = resolve_dns(dest_ip) if dest_ip != target_ip else resolve_dns(source_ip)
            
            src_mac = packet[Ether].src if Ether in packet else 'N/A'
            dst_mac = packet[Ether].dst if Ether in packet else 'N/A'

            # collected_data.append({'dns_name': dns_name, 'dest_ip': dest_ip, 'dest_mac': dst_mac})

            #---------------illegal connections part----------
            if is_mac_in_database(src_mac) and is_mac_in_database(dst_mac):

            # Get allowed devices for the source IP
                if source_ip == target_ip and dst_mac not in connecting_devices:
                    connecting_devices.append(dst_mac)
                elif dest_ip == target_ip and src_mac not in connecting_devices:
                    connecting_devices.append(src_mac)
                
                # print(f"Updated connecting devices: {connecting_devices}")
            
            # Store in database
            collected_data.append({'dns_name': dns_name, 'dest_ip': dest_ip, 'dest_mac': dst_mac})


def check_illegal(interface,device_ip,device_mac):
    connecting_devices = []
    collected_data =[]
    print(f"Starting packet capture {device_mac}  {interface}...")
    # Start sniffing on the specified interface
    sniff(iface=interface, prn=lambda x: process_packet(x, device_ip, collected_data,connecting_devices), store=0 , timeout=10)
    if collected_data:
        store_dns_name_in_db(device_ip, device_mac, collected_data)
        print("\nThe urls are stored to the database")

    if connecting_devices:
        update_connected_devices(device_mac,connecting_devices)
        print("\nThe connecting devices are stored to the database")
