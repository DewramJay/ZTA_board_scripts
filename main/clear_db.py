import sqlite3
import json


connected_device = ["58:97:1d:ca:62:2d",]
json_conn_devices = json.dumps(connected_device)
# Initialize the database connection
conn = sqlite3.connect('new_devices.db')
cursor = conn.cursor()

cursor.execute('''
    UPDATE new_devices
    SET connected_devices = ?
    WHERE ip_address = ?
''', (json_conn_devices, '192.168.28.85'))



conn.commit()