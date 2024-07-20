import subprocess
import re
import csv
import sqlite3
from scapy.all import sniff
import socket
from scapy.layers.l2 import Ether



def resolve_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

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

def get_connected_devices(interface_description):
    interface_ip = get_interface_ip(interface_description)
    if not interface_ip:
        print(f"No IP address found for interface: {interface_description}")
        return []

    try:
        # Run the arp command
        result = subprocess.check_output(["arp", "-a"], encoding='utf-8')
        # Extract the IP addresses
        all_ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', result)
        # Extract the subnet from the interface IP (e.g., 192.168.1.1 -> 192.168.1.)
        subnet = ".".join(interface_ip.split('.')[:-1]) + "."
        # Filter for the subnet and exclude .1 (interface itself) and .255 (broadcast)
        excluded_ips = {interface_ip, subnet + "255"}
        connected_devices = [ip for ip in all_ips if ip.startswith(subnet) and ip not in excluded_ips]
        return connected_devices
    except subprocess.CalledProcessError as e:
        print("Error: ", e)
        return []

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


def process_packet(packet,target_ip, collected_data):
    
    if 'IP' in packet:
        source_ip = packet['IP'].src
        dest_ip = packet['IP'].dst
        if source_ip == target_ip or dest_ip == target_ip:
            protocol = packet.sprintf("%IP.proto%")
            dns_name = resolve_dns(dest_ip) if dest_ip != target_ip else resolve_dns(source_ip)
            
            dst_mac = packet[Ether].dst if Ether in packet else 'N/A'


            # Store in database
            collected_data.append({'dns_name': dns_name, 'dest_ip': dest_ip, 'dest_mac': dst_mac})


if __name__ == '__main__':
    interface_description = 'Local Area Connection* 10'
    device_ip = '192.168.137.86'
    device_mac = 'ae:bc:da:7a:65:cb'
    output_file = 'packet_capture.csv'
    sniff(iface=interface_description, prn=lambda x: process_packet(x, device_ip, collected_data), store=0 , timeout=10)
    if collected_data:
        store_dns_name_in_db(device_ip, device_mac, collected_data)



