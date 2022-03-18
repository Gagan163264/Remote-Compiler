import socket
import sys
import json
import os
from auth import encrypt,decrypt
import shutil


if(len(sys.argv)<=2):
    sys.exit("No filename(s)/IP specified")

host_ip = sys.argv[1]
socket.inet_aton(host_ip)
print(host_ip)
print('Connecting to ', host_ip)

en = 0
if (sys.argv[2] == '-a'):
    en = 1

data = {}
for file in os.listdir(os.curdir):
    if en or file in sys.argv:
        print('Sending',file)
        with open(file,'r',encoding = 'utf-8') as f:
            data[file]=f.read()
data = encrypt(json.dumps(data))

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket successfully created")
except socket.error as err:
    print ("socket creation failed with error %s" %(err))



port = 1984

s.connect((host_ip, port))
s.send(data.encode())
s.send('END'.encode())
print('Compiling')


while True:
    inc = s.recv(1024)
    data = inc
    while inc:
        inc = s.recv(1024)
        data += inc
    s.close()
    break

response = json.loads(data.decode('utf-8'))

for file in response.keys():
    print("Recieved ", file)
    name,ext = file.rsplit(".",1)
    if ext == 'exe' or ext == 'o' or ext == 'out':
        with open(file,'wb') as f:
            f.write(response[file].encode('latin-1'))
    else:
        with open(file,'w') as f:
            f.write(response[file])

print('Completed')
