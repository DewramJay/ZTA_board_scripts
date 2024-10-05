import numpy as np
import requests

def score_calculation_openPorts(ports):
    # ports = []
    if ports:
        score_openPorts = 10

        critical_ports = [23,22]
        high_ports = [80, 8080, 443, 8443, 137, 139, 445]
        medium_ports = [161, 1883, 502, 1433, 1434, 3306]
        low_ports = [1900]
        critical_flag = True
        high_flag = True
        medium_flag = True
        low_flag = True

        for port in ports:
            for critical_port in critical_ports:
                if port == critical_port and critical_flag == True:
                    score_openPorts -= 4
                    critical_flag = False
                    break
            for high_port in high_ports:
                if port == high_port and high_flag == True:
                    score_openPorts -= 3
                    high_flag = False
                    break
            for medium_port in medium_ports:
                if port == medium_port and medium_flag == True:
                    score_openPorts -= 2
                    medium_flag = False
                    break
            for low_port in low_ports:
                if port == low_port and low_flag == True:
                    score_openPorts -= 1
                    low_flag = False
                    break
        score_openPorts=score_openPorts/10            
        print(score_openPorts)
        return score_openPorts
    else:
        return 0


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



def beta(t, E_t, k_val, theta_E):
    
    beta_t = 1 / (1 + np.exp(-k_val * (E_t - theta_E)))
    update_weights(ea_weight=beta_t)

    return beta_t

# Example usage:
t = 0  # example time t
E_t = 2.5  # example E(t) value
k_val = 1.0  # example kappa value
theta_E = 0.5  # example theta_E value

beta_value = beta(t, E_t, k_val, theta_E)
print(f"beta(t) = {beta_value}")






# if __name__ == "__main__":
#     score_calculation_openPorts()