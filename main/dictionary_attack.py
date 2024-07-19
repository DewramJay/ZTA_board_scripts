import csv
import threading
import time
import logging
from logging import NullHandler
from paramiko import SSHClient, AutoAddPolicy, AuthenticationException, ssh_exception
# from score_dictionary import score_calculation_weakPassword

# This function is responsible for the SSH client connecting.
def ssh_connect(host, username, password, result, lock):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh_client.connect(host, port=22, username=username, password=password, banner_timeout=300)
        with lock:
            if not result['found']:
                result['found'] = True
                result['username'] = username
                result['password'] = password
        print(f"Username - {username} and Password - {password} found.")
    except AuthenticationException:
        print(f"Username - {username} and Password - {password} is Incorrect.")
    except ssh_exception.SSHException:
        print("**** Attempting to connect - Rate limiting on server ****")
    finally:
        ssh_client.close()

def get_device(device):
    logging.getLogger('paramiko.transport').addHandler(NullHandler())
    list_file = "passwords.csv"

    with open(list_file) as fh:
        csv_reader = csv.reader(fh, delimiter=",")
        headers = next(csv_reader, None)  # Skip header row
        
        result = {'found': False}
        lock = threading.Lock()
        threads = []

        for row in csv_reader:
            if len(row) < 2:
                continue  # Skip incomplete rows
            username, password = row
            t = threading.Thread(target=ssh_connect, args=(device, username, password, result, lock))
            threads.append(t)
            t.start()
            time.sleep(0.2)  # Small delay between starting new connection threads

        for t in threads:
            t.join()
        
        if result['found']:
            return "The credentials of this device are weak"
    
        else:
            return "The credentials of this device are not weak"
    
# if __name__ == '__main__':
#     device = '192.168.137.148'  # Replace with the target IP address
#     result=get_device(device)
#     print(result)
