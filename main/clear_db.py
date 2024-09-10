import sqlite3
import json

# Initialize the database connection
conn = sqlite3.connect('new_devices.db')
cursor = conn.cursor()

cursor.execute('''
    UPDATE new_devices
    SET connected_devices = ?
    WHERE ip_address = ?
''', ('192.168.28.85', '192.168.28.127'))



conn.commit()