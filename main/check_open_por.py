import nmap
import sqlite3
from dictionary_attack import get_device
from score_open_ports import score_calculation_openPorts

def scan_ports(target_ip):
    # target_ip = '192.168.137.202'
    print('Checking for open ports..')
    nm = nmap.PortScanner()
    nm.scan(hosts=target_ip, arguments='-p 1-7700 -T4')  # Scan all ports
    result=''
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
                        print(f"resyult{result}")
                        print(result)
                    else:
                        print("port 22 is not open")
                else:
                    print("no open ports")
                        
    print(f"Open ports :{open_ports}")
    score_ports=score_calculation_openPorts(open_ports)
    # score_dicti=
    # print(score_ports)
    return open_ports,result,score_ports


# def get_device_ip(device_name):
#     conn = sqlite3.connect('new_devices.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT ip_address FROM new_devices WHERE device_name =?',(device_name,))
#     result=cursor.fetchone()
#     # print(result[0])
#     open_ports=scan_ports(result[0])
#     print(open_ports)
#     conn.close()
#     return open_ports



