#!/bin/sh
echo "python3 ${PWD}/peer.py \$@" > ncc.sh
chmod +x ncc.sh
sudo cp ncc.sh /usr/local/bin/ncc
rm ncc.sh
