
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

illegal_connections = []



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
    

def process_packet(packet,target_ip,connecting_devices):
    
    if 'IP' in packet:
        source_ip = packet['IP'].src
        dest_ip = packet['IP'].dst
        if source_ip == target_ip or dest_ip == target_ip:
            protocol = packet.sprintf("%IP.proto%")
            
            src_mac = packet[Ether].src if Ether in packet else 'N/A'
            dst_mac = packet[Ether].dst if Ether in packet else 'N/A'
            print(f"{src_mac} -- {dst_mac}")
            #---------------illegal connections part----------
            if is_mac_in_database(src_mac) and is_mac_in_database(dst_mac):
            # Get allowed devices for the source IP
                
                connecting_devices.append({'dst_ip':dest_ip ,'dst_mac':dst_mac})
                print(connecting_devices)
            
                

if __name__ == '__main__':
    connecting_devices = []
    device_ip = '192.168.137.204'
    interface = 'Local Area Connection* 10'
    print(f"Starting packet capture  on {interface}...")
    # Start sniffing on the specified interface
    sniff(iface=interface, prn=lambda x: process_packet(x, device_ip,connecting_devices), store=0 , timeout=10)
    