#!/bin/bash

#this command checks for the possibility of subdomain takeover in discovered subdomains.
subjack -w $1/sorted_subdomain_collection.txt -t $2 -a -o $1/takeover_result.json --ssl -c /root/go/src/github.com/haccer/subjack/fingerprints.json -v