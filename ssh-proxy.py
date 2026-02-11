import getpass
import socket
import socketio
import uuid
import json
import paramiko

sio = socketio.Client()
ssh_client = None

def connect_ssh(config):
    global ssh_client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=config["host"],
        port=config.get("port", 22),
        username=config.get("username"),
        password=config.get("password"),
        key_filename=config.get("privateKey"),
        timeout=config.get("timeout", 10)
    )
    return "SSH connection established."

def exec_command(command, use_bashrc=False):
    global ssh_client
    if ssh_client is None:
        raise Exception("SSH not connected")
    if use_bashrc:
        command = f'bash -ic "{command}"'
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if exit_code == 0:
            return out
        else:
            raise Exception(err or f"Command exited with code {exit_code}")
    except Exception as e:
        raise e
    
def close_ssh():
    global ssh_client
    if ssh_client:
        ssh_client.close()
        ssh_client = None

def get_hostname():
    hostname = socket.gethostname()
    machine_id = hex(uuid.getnode())[2:]
    full_hostname = f"{hostname}-{machine_id[:6]}"
    if not full_hostname:
        full_hostname = getpass.getuser()
    return full_hostname
 
hostname = get_hostname()

@sio.event(namespace='/client')
def connect():
    sio.emit('exec_result', f'Connected : {hostname}', namespace='/client')
    sio.emit('set_client_info', {'username': hostname}, namespace='/client')

@sio.on('client_event_ssh_connect', namespace='/client')
def on_ssh_connect(connectConfig):
    try:
        res = connect_ssh(connectConfig)
        sio.emit('exec_result', res, namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'SSH connection error: {str(e)}', namespace='/client')

@sio.on('client_event_ssh_disconnect', namespace='/client')
def on_ssh_disconnect():
    try:
        close_ssh()
        sio.emit('exec_result', 'SSH connection ended.', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'SSH connection error: {str(e)}', namespace='/client')

@sio.on('client_event_cmd_exec', namespace='/client')
def on_cmd_exec(instruction):
    try:
        res = exec_command(instruction)
        sio.emit('exec_result', res, namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f"Command execution error: {str(e)}", namespace='/client')

# sio.connect('http://localhost:8111', namespaces=['/client'])
sio.connect('https://ssh.hellokrypto.com/', socketio_path='/socket.io', namespaces=['/client'])
sio.wait()