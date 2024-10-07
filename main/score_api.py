import requests
import math

def score_illegal_conn(number):

    A_t = get_anomaly_count()
    print(A_t)

    print(calculate_gamma(A_t))


    if (number < 5):
        score = 0 
    else:
        score = 1
    
    return score

def get_anomaly_count():
    try:
        # Replace with the actual URL where your Flask app is running
        url = "http://127.0.0.1:2000/api/get_blacklist_mac_count"
        
        # Make the GET request
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            anomaly_count = data['anomaly_count']
            print(f"anomaly count: {data['anomaly_count']}")
            return anomaly_count
        else:
            print(f"Failed to get data. Status code: {response.status_code}")
            return 0
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")

def calculate_gamma(A_t):
    gamma_0 = 2.0  # initial gamma value
    eta = 0.5  # eta constant

    # gamma(t) = gamma_0 + eta * log(1 + A_i(t))
    gamma_t = gamma_0 + eta * math.log(1 + A_t)

    update_weights(cr_weight=gamma_t)
    return gamma_t

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

        


# # Calculate gamma(t)
# gamma_t = calculate_gamma(gamma_0, eta, A_t)
# print(f"Gamma(t): {gamma_t}")
# score_illegal_conn(6)






