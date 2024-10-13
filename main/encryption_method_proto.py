from scapy.all import rdpcap
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.ipsec import ESP
from scapy.layers.dns import DNS

# Initialize counters for different protocols
tls_count = 0
tcp_count = 0
udp_count = 0
dns_count = 0
ipsec_esp_count = 0

# Function to analyze packets and count protocol types
def analyze_packet(packet):
    global tls_count, tcp_count, udp_count, dns_count, ipsec_esp_count

    # Check if the packet has an IP layer
    if IP in packet:
        ip_layer = packet[IP]
        
        # Check for TCP protocol
        if TCP in packet:
            tcp_layer = packet[TCP]
            if tcp_layer.dport == 443 or tcp_layer.sport == 443:
                tls_count += 1  # Count TLS/SSL packets
            else:
                tcp_count += 1  # Count other TCP packets

        # Check for UDP protocol
        elif UDP in packet:
            udp_layer = packet[UDP]
            if packet.haslayer(DNS):
                dns_count += 1  # Count DNS packets
            else:
                udp_count += 1  # Count other UDP packets

        # Check for IPSec ESP protocol
        elif ESP in packet:
            ipsec_esp_count += 1  # Count IPSec ESP packets

# Function to read and analyze packets from a PCAP file
def analyze_pcap():
    file_path = 'packet_capture.pcap'
    print(f"[*] Reading packets from {file_path}...")
    packets = rdpcap(file_path)
    
    # Analyze each packet in the file
    for packet in packets:
        analyze_packet(packet)
    
    # Print the summary of counts
    print("\n[*] Summary of Protocols:")
    print(f"TLS/SSL (HTTPS) Packets: {tls_count}")
    print(f"TCP Packets (non-TLS): {tcp_count}")
    print(f"UDP Packets: {udp_count}")
    print(f"DNS Packets: {dns_count}")
    print(f"IPSec ESP Packets: {ipsec_esp_count}")



