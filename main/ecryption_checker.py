from scapy.all import *
import numpy as np
import requests

def analyze_packet(packet, unencrypted_data,device_mac):

    if Raw in packet:
        payload = packet[Raw].load  

        try:
            # print("\n")
            payload.decode('ascii')
            # print(f"Device: ({device_mac}) :Unencrypted payload:", payload)
            unencrypted_data += 1
            # delta(0)
        except UnicodeDecodeError:
            # delta(1)
            pass
            # print("Encrypted or binary payload:")

    return unencrypted_data  # Return the updated value



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
    if ml_weight is not None:
        payload['ml'] = ml_weight
    if ea_weight is not None:
        payload['ea'] = ea_weight
    if cr_weight is not None:
        payload['cr'] = cr_weight
    if st_weight is not None:
        payload['st'] = st_weight
    

    
    # Send a PUT request to the Flask endpoint
    response = requests.put(url, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Weights updated successfully.")
    else:
        print(f"Failed to update weights. Status code: {response.status_code}")
        print(f"Response: {response.json()}")
      


# # Example usage:
# t = 0  # example time t
# delta_0 = 1.0  # example delta_0 value
# phi = 0.5  # example phi value
# S_t = 2.0  # example S(t) value

# delta_value = delta(t, delta_0, phi, S_t)
# print(f"delta(t) = {delta_value}")