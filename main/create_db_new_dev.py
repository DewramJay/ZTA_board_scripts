import sqlite3
import json

# Initialize the database connection
conn = sqlite3.connect('new_devices.db')
cursor = conn.cursor()

# # Create the table to store device information if it doesn't exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS new_devices (
#         ip_address TEXT ,
#         mac_adress TEXT,
#         device_name TEXT,
#         status STRING,
#         connected_devices TEXT     
#     )
# ''')
# conn.commit()

# # Example list of connected devices
# connected_devices_list = ['']

# # Convert the list of connected devices to a JSON string
# connected_devices_json = json.dumps(connected_devices_list)

# Update the connected_devices field in the database with the JSON string
# mac_address = 'ae:bc:da:7a:65:cb'
# cursor.execute(
#     "UPDATE new_devices SET connected_devices = ? WHERE mac_adress = ?", 
#     (connected_devices_json, mac_address)
# )

# Define the data you want to insert
# data = ('157.240.15.61', '36:2e:b7:14:cb:98', '', 'active', "")  # Example data: IP address, MAC address, device name, connected devices count

# Insert the data into the table
# cursor.execute('''
#     INSERT INTO new_devices (ip_address, mac_adress, device_name,status,  connected_devices)
#     VALUES (?, ?, ?, ?,?)
# ''', data)

# Create the table to store the information of the api usage
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS visited_url (
#         source_ip TEXT ,
#         source_mac TEXT ,
#         dest_ip TEXT,
#         dest_mac TEXT,
#         dns_name STRING    
#     )
# ''')

cursor.execute("DELETE FROM new_devices")


conn.commit()




# Close the database connection
conn.close()