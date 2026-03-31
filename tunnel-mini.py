import getpass
import socket
import socketio
import uuid
import json
import time
import threading
import os
import requests
import sys

sio = socketio.Client()

if len(sys.argv) < 2:
    print("Usage: python client.py <remote_port> <remote_host>")
    sys.exit(1)

REMOTE_PORT = int(sys.argv[1])
REMOTE_HOST = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"

TCP_SOCKET = None

def get_hostname():
    hostname = socket.gethostname()
    machine_id = hex(uuid.getnode())[2:]
    full_hostname = f"{hostname}-{machine_id[:6]}"
    if not full_hostname:
        full_hostname = getpass.getuser()
    return full_hostname
 
hostname = get_hostname()

def connect_remote_server():
    global TCP_SOCKET

    while True:
        try:
            TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            TCP_SOCKET.connect((REMOTE_HOST, REMOTE_PORT))
            while True:
                data = TCP_SOCKET.recv(4096)
                if not data:
                    raise Exception("Remote socket closed")
                sio.emit("client_to_manager", data, namespace='/client')
        except Exception as e:
            time.sleep(1)
        finally:
            try:
                TCP_SOCKET.close()
            except:
                pass
        
@sio.on("manager_to_client", namespace='/client')
def on_manager_to_client(data):
    global TCP_SOCKET
    if TCP_SOCKET:
        TCP_SOCKET.sendall(data)

@sio.event(namespace='/client')
def connect():
    sio.emit('exec_result', f'Connected : {hostname}', namespace='/client')
    sio.emit('set_client_info', {'username': hostname}, namespace='/client')
    threading.Thread(target=connect_remote_server, daemon=True).start()

# sio.connect('http://localhost:8111', namespaces=['/client'])
sio.connect('https://tunnel.hellokrypto.com/', socketio_path='/socket.io', namespaces=['/client'], transports=['websocket'])
sio.wait()
