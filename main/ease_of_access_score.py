import numpy as np
import requests

def EA_score(mac_address, port_score, password_score):
    print("open port score calculation")
    print(port_score)
    print(password_score)
    # illegal_connection = 1
    no_illegal_connection = get_illegal_connection_count(mac_address)
    print(f"noofillegal{no_illegal_connection}")
    x = no_illegal_connection
    n = 1
    illegal_connection = np.exp(-n * x)
    print("illegal_connection")
    print(illegal_connection)

    score = 0.56 * port_score + 0.33 * password_score + 0.11 * illegal_connection
    update_score(mac_address, ea=score)
    return beta(mac_address, score)




# def update_weights(ml_weight=None, ea_weight=None, cr_weight=None, st_weight=None):
#     # Define the API endpoint URL
#     url = 'http://127.0.0.1:2000/api/update_weights'
    
#     # Create the payload with the weights that you want to update
#     payload = {}
#     if ml_weight is not None:
#         payload['ml_weight'] = ml_weight
#     if ea_weight is not None:
#         payload['ea_weight'] = ea_weight
#     if cr_weight is not None:
#         payload['cr_weight'] = cr_weight
#     if st_weight is not None:
#         payload['st_weight'] = st_weight
    

    
#     # Send a PUT request to the Flask endpoint
#     response = requests.put(url, json=payload)
    
#     # Check if the request was successful
#     if response.status_code == 200:
#         print("Weights updated successfully.")
#     else:
#         print(f"Failed to update weights. Status code: {response.status_code}")
#         print(f"Response: {response.json()}")

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
        # print(f"Response: {response.json()}")


def beta(mac_address, E_t):
    
    t = 0  # example time t
    k_val = 1.0  # example kappa value
    theta_E = 0.5  # example theta_E value
    
    beta_t = 1 / (1 + np.exp(-k_val * (E_t - theta_E)))
    print("beta_t")
    # update_score(mac_address, ea=beta_t)
    print(beta_t)

    return beta_t

# def get_illegal_connection_count():
#     try:
#         # Replace with the actual URL where your Flask app is running
#         url = "http://127.0.0.1:2000/api/get_illegal_connection_count"
        
#         # Make the GET request
#         response = requests.get(url)
        
#         # Check if the request was successful
#         if response.status_code == 200:
#             # Parse the JSON response
#             data = response.json()
#             illegal_connection_count = data['illegal_connection_count']
#             print(f"illegal_connection_count: {data['illegal_connection_count']}")
#             return illegal_connection_count
#         else:
#             print(f"Failed to get data. Status code: {response.status_code}")
#             return 0
    
#     except requests.exceptions.RequestException as e:
#         print(f"Error occurred: {e}")


def get_illegal_connection_count(mac_address):
    if check_connected_device_status(mac_address):
        payload = {
            "mac_address": mac_address
        }
        try:
            # Replace with the actual URL where your Flask app is running
            url = "http://127.0.0.1:2000/api/get_related_mac_count"
            
            # Make the GET request
            response = requests.get(url, json=payload)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                related_mac_count = data['related_mac_count']
                print(f"related_mac_count: {data['related_mac_count']}")
                return related_mac_count
            else:
                print(f"Failed to get data. Status code: {response.status_code}")
                return 0
        
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
    else:
        print("no status----------------------------")
        return 0


def check_connected_device_status(mac_address):
    # Define the Flask API endpoint URL
    url = 'http://localhost:2000/api/check_connected_device_status' 

    # Set up the parameters with the MAC address
    params = {'mac_address': mac_address}

    try:
        # Send a GET request to the Flask API
        response = requests.get(url, json=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            return data['status']
        else:
            print(f"Error: Unable to contact the API. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# beta_value = EA_score(0.2, 0.1)
# print(f"beta(t) = {beta_value}")