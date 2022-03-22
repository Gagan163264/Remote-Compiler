#!/bin/sh
sudo apt-get install mingw-w64
pip install waiting
echo "python3 ${PWD}/peer.py \$@" > ncc.sh
chmod +x ncc.sh
sudo cp ncc.sh /usr/local/bin/ncc
rm ncc.sh
