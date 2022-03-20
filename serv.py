import socket
import json
from auth import encrypt,decrypt
import os
import shutil
from _thread import *
import subprocess
import datetime
from waiting import wait

def is_something_ready(something, dict):
    if something in dict.keys():
        return False
    return True

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

ThreadCount = 0
client_list = {}
job_list = {}

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
    netw = 0
    for file in data.keys():
        with open(os.path.join(client_path,file),'w',encoding = 'utf-8') as f:
            f.write(data[file])
        name,ext = file.rsplit(".",1)
        if ext == 'ncf':
            netw = 1
        if ext != 'ncf':
            print('Recieved ', file)
        dump.write('[{0}]Recieved {3} from {1}:{2}\n'.format(str(datetime.datetime.now()),client_host,client_port,file))

    contin = 1
    nc_dir_dict = {}
    nc_dir_path = ''
    if (netw == 1):
        contin = 0
        with open(os.path.join(client_path,'network-list.ncf'),'r') as f:
            nc_dir_dict = json.loads(f.read())
        val = 1
        arg_li = []
        for cli in nc_dir_dict.keys():
            arg_li.append(cli)
        arg_li.sort()
        for cli in arg_li:
            nc_dir_path += cli+'+'
        nc_dir_path=nc_dir_path[:-1]
        nc_dir_path = os.path.join('shared',nc_dir_path)

        if nc_dir_path in client_list.keys():
            client_list[nc_dir_path]+=1
        else:
            client_list[nc_dir_path]=1

        if nc_dir_path in job_list.keys():
            nc_dir_dict=job_list[nc_dir_path]
        else:
            if os.path.exists(nc_dir_path):
                shutil.rmtree(nc_dir_path)
            os.makedirs(nc_dir_path)

        nc_dir_dict[client_host]=1
        job_list[nc_dir_path]=nc_dir_dict

        for cli in nc_dir_dict.keys():
            val *= nc_dir_dict[cli]
        copytree(client_path,nc_dir_path)
        shutil.rmtree(client_path)

        if val==1:
            contin = 1
        else:
            contin = 0
            try:
                print(client_host,' waiting for clients')
                wait(lambda: is_something_ready(nc_dir_path, job_list), timeout_seconds = 120)
            except:
                print(client_host, 'timed out')
                dump.write('[{0}]Timeout {1}:{2} thread closed\n'.format(str(datetime.datetime.now()),client_host,client_port,file))
                c.send('NCK'.encode())
                return

        c.send('ACK'.encode())
        client_path=nc_dir_path

    respath = os.path.join(client_path,'out')
    if contin==1:
        arg = ''
        if os.path.exists(respath):
            shutil.rmtree(respath)
        os.makedirs(respath)
        for file in os.listdir(client_path):
            if file != 'out':
                name,ext = file.rsplit(".",1)
                if(ext == 'c'):
                    arg += os.path.join(client_path,file)+' '
                    cmd = 'gcc -c '+os.path.join(client_path,file)+' -o '+ os.path.join(respath,name+'.o')+' 2> '+ os.path.join(respath,name+'_compile_err.txt')
                    print(cmd)
                    os.system(cmd)

        cmd = 'gcc '+arg+' -o '+ os.path.join(respath,'a'+'.out')+' 2> '+os.path.join(respath,'output_linux_err.txt')
        os.system(cmd)

        cmd = 'i686-w64-mingw32-gcc '+arg+' -o '+ os.path.join(respath,'a'+'.exe')+' 2> '+os.path.join(respath,'output_win_err.txt')
        os.system(cmd)

    if netw == 1:
        if nc_dir_path in job_list.keys():
            job_list.pop(nc_dir_path)

    response = {}
    for file in os.listdir(respath):
        name,ext = file.rsplit(".",1)
        if ext == 'exe' or ext == 'o' or ext == 'out':
            with open(os.path.join(respath,file),'rb') as f:
                response[file]=f.read().decode('latin-1')
        else:
            with open(os.path.join(respath,file),'r') as f:
                fileout = f.read()
                if fileout:
                    response[file]=fileout
        dump.write('[{0}]Sent {3} to {1}:{2}\n'.format(str(datetime.datetime.now()),client_host,client_port,file))
        print('Sending ',file)
    
    response = json.dumps(response).encode('utf-8')
    c.send(response)
    c.send('END'.encode('utf-8'))
    c.close()
    if netw == 1:
        client_list[nc_dir_path]-=1
        if(client_list[nc_dir_path]==0):
            if os.path.exists(nc_dir_path):
                shutil.rmtree(nc_dir_path)
            client_list.pop(nc_dir_path)
    else:
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
