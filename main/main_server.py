from flask import Flask, jsonify, Request, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
cors = CORS(app, origins='*')
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/api/users", methods=["GET"])
def get_users():
    try:
        database_path = r'D:\D\fyp_main\main\new_devices.db'
        conn = sqlite3.connect(database_path)
        # conn = sqlite3.connect('new_devices.db')
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_adress, device_name FROM new_devices')
        devices = [{"ip_address": row[0], "mac_address": row[1], "device_name": row[2]} for row in c.fetchall()]
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

    return jsonify(devices)

def notify_clients():
    try:
        database_path = r'C:\Users\User\Desktop\project\evaluation\ZTA_main_2\main\new_devices.db'
        conn = sqlite3.connect(database_path)
        # conn = sqlite3.connect('new_devices.db')
        c = conn.cursor()
        c.execute('SELECT ip_address, mac_adress, device_name FROM new_devices')
        devices = [{"ip_address": row[0], "mac_address": row[1], "device_name": row[2]} for row in c.fetchall()]
        socketio.emit('update', devices)
    except sqlite3.Error as e:
        print("Error fetching data:", e)
    finally:
        if conn:
            conn.close()

@app.route("/api/add_device", methods=["POST"])
def add_device():
    data = request.get_json()
    ip_address = data.get('ip_address')
    mac_address = data.get('mac_address')
    device_name = data.get('device_name')
    try:
        database_path = r'D:\D\fyp_main\main\new_devices.db'
        
        conn = sqlite3.connect(database_path)
        # conn = sqlite3.connect('new_devices.db')
        c = conn.cursor()
        c.execute('INSERT INTO new_devices (ip_address, mac_adress, device_name) VALUES (?, ?, ?)', 
                  (ip_address, mac_address, device_name))
        conn.commit()
        notify_clients()  # Notify clients after inserting new data
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)