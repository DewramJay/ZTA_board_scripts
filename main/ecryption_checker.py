from scapy.all import *

def analyze_packet(packet, unencrypted_data):

    if Raw in packet:
        payload = packet[Raw].load  

        try:
            # print("\n")
            payload.decode('ascii')
            print("Unencrypted payload:", payload)
            unencrypted_data += 1
        except UnicodeDecodeError:
            pass
            # print("Encrypted or binary payload:")

    return unencrypted_data  # Return the updated value