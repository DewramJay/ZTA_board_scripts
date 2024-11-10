import requests

# Replace with the IP address of your Kali machine
# file_path = 'unibversal_remote_2.pcap'
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


def score_calculation(mac_address):
    accuracy  = 0.9599
    score = 1 - accuracy
    update_score(mac_address, ml=score)


def read_file(device_mac):
    # print("aaa")
    url = 'https://haxtreme.info/upload'
    file_path = f'./captured_pcap/packet_capture{device_mac}.pcap'

    with open(file_path, 'rb') as f:
        files = {'file.pcap': f}
        response = requests.post(url, files=files)

    # Check if the request was successful
    if response.status_code == 200:
        try:
            # Try to parse the JSON response
            json_response = response.json()
            print(json_response)
            anomalies = json_response.get('anomalies')    
            if anomalies > 100 :
                print(anomalies)
                score_calculation(device_mac)
            else : 
                update_score(device_mac, ml=1)

        except requests.exceptions.JSONDecodeError:
            # If the response isn't JSON, print the raw response
            print("Failed to parse JSON. Raw response content:")
            print(response.text)
    else:
        # If the request was not successful, print the status code and error
        print(f"Request failed with status code {response.status_code}")
        print("Response content:", response.text)


# read_file()