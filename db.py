import sqlite3
import json

# Initialize the database connection
conn = sqlite3.connect('new_devices.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS new_devices (
    mac_adress TEXT PRIMARY KEY,
    ip_address TEXT,
    device_name TEXT,
    status TEXT,
    connected_devices TEXT
)
''')



conn.commit()





cursor = conn.cursor()

# SQL command to create the 'evaluation' table
create_table_query = '''
CREATE TABLE IF NOT EXISTS evaluation (
    mac_address TEXT PRIMARY KEY,
    ip_address INTEGER NOT NULL,
    open_ports TEXT,
    password_status TEXT 
);
'''

# Execute the SQL command to create the table
cursor.execute(create_table_query)

# Commit the transaction
conn.commit()

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS url_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address TEXT,
    blacklist_mac TEXT
)
''')



conn.commit()


cursor = conn.cursor()

# Step 1: Create a new table with the desired schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS visited_url (
        source_mac TEXT PRIMARY KEY,
               source_ip TEXT,
               dest_ip  TEXT,
               dest_mac TEXT,
               dns_name TEXT   
    )
''')

# Commit the changes
conn.commit()

# Close the connection
conn.close()