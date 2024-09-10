from scapy.all import *

# Function to extract and print hostname from DHCP packets
def extract_hostname(packet):
    print("hhhh")
    if packet.haslayer(DHCP):
        options = packet[DHCP].options
        for option in options:
            if option[0] == 'hostname':  # DHCP Option 12
                print(f"Hostname: {option[1].decode()}")
                return option[1].decode()
                break

# Sniff DHCP packets
def sniff_dhcp_packets(interface):
    print(f"Sniffing on interface: {interface}")
    sniff(filter="udp and (port 67 or port 68)", prn=extract_hostname, iface=interface, store=0)

# Replace 'your_interface' with your actual network interface, e.g., 'wlan0' for Wi-Fi
sniff_dhcp_packets("wlan0")