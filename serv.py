import socket
import json
from auth import encrypt,decrypt
import os
import shutil
from _thread import *
import subprocess
import datetime

ThreadCount = 0

dump = open('dump.txt','a')
print("Starting")
s = socket.socket()
port = 1984
s.bind(('',port))
serv_ip = socket.gethostbyname(socket.gethostname()+ ".local")
print('Listening on:{0}:{1}'.format(serv_ip,port))
s.listen(5)
dump.write('\n[{0}]Server started on {1}:{2}\n'.format(str(datetime.datetime.now()),serv_ip,port))

def client_handle(c):
    inc = c.recv(1024).decode()
    data = inc
    while inc:
        inc = c.recv(1024).decode()
        if inc.endswith('END'):
            data += inc[:-3]
            break
        data += inc
    data = json.loads(decrypt(str(data)))
    client_path = os.path.join('shared',client_host)
    print(client_path)
    if os.path.exists(client_path):
        shutil.rmtree(client_path)
    os.makedirs(client_path)
    for file in data.keys():
        with open(os.path.join(client_path,file),'w',encoding = 'utf-8') as f:
            f.write(data[file])
        print('Recieved ', file)
        dump.write('[{0}]Recieved {3} from {1}:{2}\n'.format(str(datetime.datetime.now()),client_host,client_port,file))



    arg = ''
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

    os.system('gcc '+arg+' -o '+ os.path.join(respath,'a'+'.out'))
    result = subprocess.check_output('dir', shell=True)
    if result:
        with open(os.path.join(respath,'output_linux_compile_res.txt'),'w', encoding = 'utf-8') as f:
            f.write(result.decode())

    os.system('i686-w64-mingw32-gcc '+arg+' -o '+ os.path.join(respath,'a'+'.exe'))
    result = subprocess.check_output('dir', shell=True)
    if result:
        with open(os.path.join(respath,'output_win_compile_res.txt'),'w', encoding = 'utf-8') as f:
            f.write(result.decode())

    response = {}
    for file in os.listdir(respath):
        name,ext = file.rsplit(".",1)
        if ext == 'exe' or ext == 'o' or ext == 'out':
            with open(os.path.join(respath,file),'rb') as f:
                response[file]=f.read().decode('latin-1')
        else:
            with open(os.path.join(respath,file),'r') as f:
                response[file]=f.read()
        dump.write('[{0}]Sent {3} to {1}:{2}\n'.format(str(datetime.datetime.now()),client_host,client_port,file))
        print('Sending ',file)

    response = json.dumps(response).encode('utf-8')
    c.send(response)
    c.send('END'.encode('utf-8'))
    c.close()
    if os.path.exists(client_path):
        shutil.rmtree(client_path)


while True:
    c, (client_host, client_port) = s.accept()
    print('Connected to: ' + str(client_host) + ':' + str(client_port))
    dump.write('[{0}]Connected to {1}:{2}\n'.format(str(datetime.datetime.now()),client_host,client_port))
    start_new_thread(client_handle, (c,))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

s.close()
dump.close()
