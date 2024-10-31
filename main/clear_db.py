# import sqlite3
# import json


# connected_device = ["58:97:1d:ca:62:2d",]
# json_conn_devices = json.dumps(connected_device)
# # Initialize the database connection
# conn = sqlite3.connect('new_devices.db')
# cursor = conn.cursor()

# cursor.execute('''
#     UPDATE new_devices
#     SET connected_devices = ?
#     WHERE ip_address = ?
# ''', (json_conn_devices, '192.168.28.85'))



# conn.commit()



import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('score_model.db')
cursor = conn.cursor()

# # Step 1: Add a new column to the table
# cursor.execute("ALTER TABLE new_devices ADD COLUMN connected_device_status INTEGER")

# # Step 2: Set all values in the new column to 0
# cursor.execute("UPDATE new_devices SET connected_device_status = 0")

cursor.execute('''
    ALTER TABLE trust_score ADD COLUMN check_status INTEGER DEFAULT 0;
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
