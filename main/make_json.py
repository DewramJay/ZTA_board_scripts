import sqlite3
import json

def update_database():
    conn = sqlite3.connect('new_devices.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT mac_adress, connected_devices FROM new_devices")
        rows = cursor.fetchall()

        for row in rows:
            mac_adress, connected_devices = row

            # Ensure the connected_devices is a JSON string
            if isinstance(connected_devices, int):
                new_value = json.dumps([connected_devices])  # Convert integer to JSON string
                cursor.execute("UPDATE new_devices SET connected_devices=? WHERE mac_adress=?", (new_value, mac_adress))
            elif isinstance(connected_devices, str):
                try:
                    json.loads(connected_devices)  # Check if it is a valid JSON string
                except json.JSONDecodeError:
                    # If it's not valid JSON, convert it appropriately
                    new_value = json.dumps([connected_devices])
                    cursor.execute("UPDATE new_devices SET connected_devices=? WHERE mac_adress=?", (new_value, mac_adress))

        conn.commit()
        print("Database updated successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

update_database()