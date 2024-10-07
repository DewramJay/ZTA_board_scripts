import numpy as np
import requests

def EA_score(port_score, password_score):
    print("open port score calculation")
    print(password_score)
    illegal_connection = 1

    score = 0.56 * port_score + 0.33 * password_score + 0.11 * illegal_connection
    return beta(score)


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



def beta(E_t):
    
    t = 0  # example time t
    k_val = 1.0  # example kappa value
    theta_E = 0.5  # example theta_E value
    
    beta_t = 1 / (1 + np.exp(-k_val * (E_t - theta_E)))
    update_weights(ea_weight=beta_t)

    return beta_t



# beta_value = EA_score(0.2, 0.1)
# print(f"beta(t) = {beta_value}")