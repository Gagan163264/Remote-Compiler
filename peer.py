import socket
import sys
import json
import os
from auth import encrypt,decrypt
import shutil

if(len(sys.argv)<=2):
    sys.exit("No target(s)/IP specified")

en = 0
filelist = []
count = 0
netw = 0
verboseall = 0
verboseni = 0

nc_dir_dict = {}
for arg in sys.argv:
    if (arg == '-a'):
        en = 1

    if count>=2 and netw == 0:
        filelist.append(arg)
    if netw == 1:
        if verboseall:print(arg)
        socket.inet_aton(arg)
        nc_dir_dict[arg]=0
    if arg == '-n':
        netw = 1
    if arg == '-v':
        verboseall = 1
        verboseni = 1
    if arg == '-vn':
        verboseall = 1
    count += 1

host_det = sys.argv[1]
host_ip, host_port = host_det.split(':',1)
socket.inet_aton(host_ip)
cli_ip = socket.gethostbyname(socket.gethostname()+ ".local")
if verboseall:
    print('Client',cli_ip,'online')
if verboseall:
    print('Connecting to ', host_det)


if netw == 1:
    nc_dir_dict[cli_ip]=0
    with open('network-list.ncf','w') as f:
        f.write(json.dumps(nc_dir_dict))
    filelist.append('network-list.ncf')

data = {}
for file in os.listdir(os.curdir):
    if en or file in filelist:
        if verboseall:
            print('Sending',file)
        with open(file,'r',encoding = 'utf-8') as f:
            data[file]=f.read()
data = encrypt(json.dumps(data))

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if verboseall:
        print ("Socket successfully created")
except socket.error as err:
    if verboseall:
        print ("socket creation failed with error %s" %(err))



port = int(host_port)

s.connect((host_ip, port))
s.send(data.encode())
s.send('END'.encode())

if netw==1:
    if verboseall:
        print('Waiting for network clients:')
    resp = s.recv(3).decode()
    if(resp!='ACK'):
        sys.exit('Other clients did not connect')
    if verboseall:
        print('All files recieved successfully by server')


if verboseall:
    print('Compiling')

while True:
    inc = s.recv(1024).decode('utf-8')
    data = inc
    while inc:
        inc = s.recv(1024).decode('utf-8')
        if inc.endswith('END'):
            data += inc[:-3]
            break
        data += inc
    s.close()
    break


response = json.loads(data)

for file in response.keys():
    if verboseall:
        print("Recieved ", file)
    name,ext = file.rsplit(".",1)
    if ext == 'exe' or ext == 'o' or ext == 'out':
        with open(file,'wb') as f:
            f.write(response[file].encode('latin-1'))
    else:
        with open(file,'w') as f:
            f.write(response[file])
        if file.endswith('output_linux_err.txt'):
            if verboseall or verboseni:
                print('\n',response[file])
