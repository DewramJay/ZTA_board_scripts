import nmap
import sqlite3
import json
from dictionary_attack import get_device
from score_open_ports import score_calculation_openPorts

def scan_ports(target_ip, device_mac):
    # target_ip = '192.168.137.202'
    print('Checking for open ports..')
    nm = nmap.PortScanner()
    nm.scan(hosts=target_ip, arguments='-p 1-7700 -T4')  # Scan all ports
    result='strong'
    open_ports = []

    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            port_info = nm[host][proto].items()
            for port, port_data in port_info:
                if port_data['state'] == 'open':
                    # print(f"open port detected:{port}")
                    open_ports.append(port)
                    if port == 22:
                        result=get_device(host)
                        print(f"result{result}")
                        print(f"The score for weak credentials {result} *******************")

                        print(result)
                    else:
                        result="strong"
                        print("port 22 is not open")
                else:
                    print("no open ports")
                    result="strong"
                        
    print(f"Open ports :{open_ports}")
    score_ports=score_calculation_openPorts(open_ports)
    print(f"The score for open ports {score_ports} *******************")

    conn = sqlite3.connect('/home/kali/Desktop/project/eval/ZTA_main_2/main/new_devices.db')
    cursor = conn.cursor()

    cursor.execute("SELECT mac_address FROM evaluation WHERE mac_address = ?", (device_mac,))
    mac=cursor.fetchone()
    if mac:
        # print("Device already exists in the database")
        cursor.execute("UPDATE evaluation SET open_ports = ?, password_status = ? WHERE mac_address = ?",(json.dumps(open_ports), result ,device_mac))
        conn.commit()
        print(result)
    else:
        # cursor('')
        cursor.execute("INSERT INTO evaluation (ip_address, mac_address, open_ports, password_status) VALUES (?, ?, ?,?)",
                    (target_ip, device_mac, json.dumps(open_ports), result))
        conn.commit()
        conn.close()
        print("Data added to the database")
    
 
    return open_ports,result,score_ports


# def get_device_ip(device_name):
#     conn = sqlite3.connect(r'C:\Users\User\Desktop\project\new_devices.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT ip_address FROM new_devices WHERE device_name =?',(device_name,))
#     result=cursor.fetchone()
#     # print(result[0])
#     open_ports=scan_ports(result[0])
#     print(open_ports)
#     conn.close()
#     return open_ports



