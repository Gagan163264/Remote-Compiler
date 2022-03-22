# [Remote-Compiler](https://github.com/Gagan163264/Remote-Compiler.git)

C compiler for LAN multi-client applications, where each client has parts of all files to create an executable
## Setup
Download all files using 

`git clone https://github.com/Gagan163264/Remote-Compiler.git`

To install client, run

`./installer.sh`

## Usage
To run server navigate to directory and run it in terminal

`python3 serv.py`

Client can be run using `ncc .....`

If installer is not used `python3 peer.py ........` with peer.py file in the active directory is required

First argument is always server IP and is compulsory

## Flags for client
Flags:
- -a : sends all files in active directory to server
- -n : All arguments after this flag (except other flags) are taken as IP addresses of other peers. All peers should have the IPs of all other peers for successful compilation
- -v : Verbose
- -vn : Disable all print statements to stdout ( not using both -v and -vn will print compile errors(if any))

## Peer Connection
Run client with server IP, file names and peer IPs(optional) as arguments

`ncc <server_ip> <file_1> <file_2>... -n <peer_ip1> <peer_ip2>...`

if peer IP is given, the program will wait for 120 seconds for all clients to connect to the server before it times out and exits

alternatively -a flag can be used to select all files 

`ncc <server_ip> -a `

## Output
Output will include:
- Object files for each C file from all peers(.o)
- Error files for each object file compilation(if any) and error for compile+link of all files(if any)(.txt)
- Output as a.exe and a.out if no errors

These files will be written into the active directory 

## Uninstall
To remove ncc command run
`./uninstall.sh`
