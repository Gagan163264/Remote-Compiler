import socket
import json
from auth import encrypt,decrypt
import os
import shutil
from _thread import *
import subprocess

ThreadCount = 0

s = socket.socket()
print ("Socket successfully created")
port = 1800
s.bind(('',port))
print(socket.gethostbyname(socket.gethostname()+ ".local"))
print ("socket bound to %s" %(port))
s.listen(5)
print ("socket is listening")

def client_handle(c):
    inc = c.recv(1024)
    data = inc
    while inc:
        inc = c.recv(1024)
        data += inc
    data = json.loads(decrypt(str(data.decode())))
    client_path = os.path.join('shared',client_host)
    print(client_path)
    if os.path.exists(client_path):
        shutil.rmtree(client_path)
    os.makedirs(client_path)
    for file in data.keys():
        with open(os.path.join(client_path,file),'w',encoding = 'utf-8') as f:
            f.write(data[file])
        print('Recieved ', file)

    arg = 'gcc '
    respath = os.path.join(client_path,'out')
    if os.path.exists(respath):
        shutil.rmtree(respath)
    os.makedirs(respath)
    for file in os.listdir(client_path):
        if file != 'out':
            name,ext = file.rsplit(".",1)
            if(ext == 'c'):
                arg += os.path.join(client_path,file)+' '
                cmd = 'gcc -c '+os.path.join(client_path,file)+' -o '+ os.path.join(respath,file+'.o')
                print(cmd)
                os.system(cmd)
                result = subprocess.check_output('dir', shell=True)
                if result:
                    with open(os.path.join(respath,name+'_compile_res.txt'),'w',encoding='utf-8') as f:
                        f.write(result.decode())

    os.system(arg)
    print(arg)
    result = subprocess.check_output('dir', shell=True)
    if result:
        with open(os.path.join(respath,'output_linux_compile_res.txt'),'w', encoding = 'utf-8') as f:
            f.write(result.decode())

    os.system(arg+' -o '+ os.path.join(respath,file+'.exe'))
    result = subprocess.check_output('dir', shell=True)
    if result:
        with open(os.path.join(respath,'output_win_compile_res.txt'),'w', encoding = 'utf-8') as f:
            f.write(result.decode())

    response = {}
    for file in os.listdir(respath):
        with open(os.path.join(respath,file),'rb') as f:
            response[file]=f.read()
            print(file)
            name,ext = file.rsplit(".",1)
            if ext == 'exe' or ext == 'o':
                response[file]=response[file].decode('latin-1')
            else:
                response[file]=response[file].decode()
    response = encrypt(json.dumps(response))
    #c.send(response.encode())
    c.close()
    #if os.path.exists(client_path):
    #    shutil.rmtree(client_path)


while True:
    c, (client_host, client_port) = s.accept()
    print('Connected to: ' + str(client_host) + ':' + str(client_port))
    start_new_thread(client_handle, (c,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

s.close()
