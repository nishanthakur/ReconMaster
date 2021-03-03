#!/bin/bash

python3 /root/reconMaster/reconMaster/tools/dirsearch/dirsearch.py -u $1 -w $2 --json-report=$3 -e $4 -t $5 -e $4 --exclude-texts=Attack Detected,Please contact the system administr
ator
