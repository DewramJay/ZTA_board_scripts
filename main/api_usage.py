import subprocess
import re
import csv
import sqlite3
from scapy.all import sniff
import socket

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

def store_dns_name_in_db(source_ip, dest_ip, protocol, dns_name):
    conn = sqlite3.connect('visited_url.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO visited_urls_2 (source_ip, dest_ip, protocol, dns_name)
        VALUES (?, ?, ?, ?)
    ''', (source_ip, dest_ip, protocol, dns_name))
    conn.commit()
    conn.close()

def packet_sniffer(interface, output_file, target_ip, count=100):
    # Open the CSV file for writing
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Source IP', 'Destination IP', 'Protocol', 'DNS Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()

        # Packet sniffing function
        def process_packet(packet):
            if 'IP' in packet:
                source_ip = packet['IP'].src
                dest_ip = packet['IP'].dst
                if source_ip == target_ip or dest_ip == target_ip:
                    protocol = packet.sprintf("%IP.proto%")
                    dns_name = resolve_dns(dest_ip) if dest_ip != target_ip else resolve_dns(source_ip)

                    writer.writerow({
                        'Source IP': source_ip,
                        'Destination IP': dest_ip,
                        'Protocol': protocol,
                        'DNS Name': dns_name if dns_name else 'N/A'
                    })

                    # Store in database
                    store_dns_name_in_db(source_ip, dest_ip, protocol, dns_name if dns_name else 'N/A')

        # Sniff packets on the specified interface
        sniff(iface=interface, prn=process_packet, count=count)

if __name__ == "__main__":
    interface_description = 'Local Area Connection* 10'
    output_file = 'packet_capture.csv'
    connected_devices = get_connected_devices(interface_description)
    if connected_devices:
        print("Connected devices:")
        for device in connected_devices:
            packet_sniffer(interface_description, output_file, device, count=1000)  # Capture 1000 packets and save to CSV
            print(device)
    else:
        print("No connected devices found.")