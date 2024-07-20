import nmap
import time

def scan_network(interface_ip, subnet='24'):
    # Initialize the nmap object
    nm = nmap.PortScanner()

    # Define the target IP range or subnet (e.g., '192.168.1.0/24')
    target = f"{interface_ip}/{subnet}"

    try:
        # Perform the scan
        print(f"Scanning network: {target}")
        nm.scan(hosts=target, arguments='-sn')  # '-sn' performs a ping scan (no port scan)

        # Retrieve and print the scan results
        hosts = nm.all_hosts()
        if hosts:
            print("Devices found:")
            for host in hosts:
                print(f"IP Address: {host}, Hostname: {nm[host].hostname()}")
        else:
            print("No devices found.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace with your network interface IP address and subnet
interface_ip = '192.168.137.1'
subnet = '24'  # You can adjust the subnet mask as needed

scan_network(interface_ip, subnet)
