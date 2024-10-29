from scapy.all import *
import numpy as np
import requests

def analyze_packet(mac_address):

    pcap_file_path = f'./captured_pcap/packet_capture{mac_address}.pcap'
    # Read the packets from the pcap file
    packets = rdpcap(pcap_file_path)
    
    total_packets = len(packets)
    unencrypted_count = 0
    encrypted_count = 0

    # Analyze each packet
    for packet in packets:
        if Raw in packet:
            payload = packet[Raw].load

            try:
                # Try to decode the payload as ASCII
                payload.decode('ascii')
                unencrypted_count += 1
            except UnicodeDecodeError:
                # If a UnicodeDecodeError occurs, it means the payload is encrypted or binary
                encrypted_count += 1

    # Calculate fractions

    fraction_unencrypted = unencrypted_count / total_packets if total_packets > 0 else 0
    fraction_encrypted = encrypted_count / total_packets if total_packets > 0 else 0

    # Calculate score where higher encrypted count results in a score closer to 1
    score = fraction_encrypted  # directly using the fraction of encrypted packets as the score
    print("score")
    print(score)

    update_score(mac_address, st=score)


    return {
        'total_packets': total_packets,
        'unencrypted_count': unencrypted_count,
        'encrypted_count': encrypted_count,
        'fraction_unencrypted': fraction_unencrypted,
        'fraction_encrypted': fraction_encrypted
    } # Return the updated value



def delta(S_t):

    t = 0  # example time t
    delta_0 = 1.0  # example delta_0 value
    phi = 0.5  # example phi value

    delta_t = delta_0 * np.exp(-phi * S_t)
    update_weights(st_weight=delta_t)
    return delta_t

def update_weights(ml_weight=None, ea_weight=None, cr_weight=None, st_weight=None):
    # Define the API endpoint URL
    url = 'http://127.0.0.1:2000/api/update_weights'
    
    # Create the payload with the weights that you want to update
    payload = {}
    if ml_weight is not None:
        payload['ml_weight'] = ml_weight
    if ea_weight is not None:
        payload['ea_weight'] = ea_weight
    if cr_weight is not None:
        payload['cr_weight'] = cr_weight
    if st_weight is not None:
        payload['st_weight'] = st_weight
    

    
    # Send a PUT request to the Flask endpoint
    response = requests.put(url, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Weights updated successfully.")
    else:
        print(f"Failed to update weights. Status code: {response.status_code}")
        print(f"Response: {response.json()}")

def update_score(mac_address, ml=None, ea=None, cr=None, st=None):
    # Define the API endpoint URL
    url = 'http://127.0.0.1:2000/api/trust_score'
    
    # Create the payload with the weights that you want to update
    payload = {}
    payload['mac_address'] = mac_address
    if ml is not None:
        payload['ml'] = ml
    if ea is not None:
        payload['ea'] = ea
    if cr is not None:
        payload['cr'] = cr
    if st is not None:
        payload['st'] = st
    

    
    # Send a PUT request to the Flask endpoint
    response = requests.post(url, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Weights updated successfully.")
    else:
        print(f"Failed to update weights. Status code: {response.status_code}")
      


# # Example usage:
# t = 0  # example time t
# delta_0 = 1.0  # example delta_0 value
# phi = 0.5  # example phi value
# S_t = 2.0  # example S(t) value

# delta_value = delta(t, delta_0, phi, S_t)
# print(f"delta(t) = {delta_value}")