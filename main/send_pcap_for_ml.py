import requests

# Replace with the IP address of your Kali machine
# file_path = 'unibversal_remote_2.pcap'

def read_file():
    url = 'http://192.168.243.128:5000/upload'
    file_path = 'laptop_traffic.pcap'

    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)

    # Check if the request was successful
    if response.status_code == 200:
        try:
            # Try to parse the JSON response
            json_response = response.json()
            print(json_response)
        except requests.exceptions.JSONDecodeError:
            # If the response isn't JSON, print the raw response
            print("Failed to parse JSON. Raw response content:")
            print(response.text)
    else:
        # If the request was not successful, print the status code and error
        print(f"Request failed with status code {response.status_code}")
        print("Response content:", response.text)

read_file()