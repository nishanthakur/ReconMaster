#!/bin/bash

#This script performs all the subdomain discovery using tools assetfinder, subfinder and sublist3r.
#Here, $1 = threads, $2 = domain, $3 = output_directory

for i in "$@" ; do
    if [[ $i == "sublist3r" ]] ; then
        python3 /app/tools/Sublist3r/sublist3r.py -d $2 -t $1 -o $3/from_sublist3r.txt
    fi
    if [[ $i == "assetfinder" ]] ; then
        assetfinder --subs-only $2>$3/from_asssetfinder.txt
    fi
    if [[ $i == "subfinder" ]] ; then
        subfinder -d $2 -t $1 > $3/from_subfinder.txt
    fi

done

cat $3/*.txt > $3/subdomain_collection.txt
rm -rf $3/from*
sort -u $3/subdomain_collection.txt -o $3/sorted_subdomain_collection.txt

rm -rf $3/subdomain*