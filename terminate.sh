#!/bin/bash

type -P "starcluster" &>/dev/null || { echo "Err: Command not found: starcluster"
    echo "Install starcluster with command: easy_install starcluster"; exit 1; }

USAGE="Usage: `basename $0` <path/to/starcluster/config> nameOfCluster"

# Parse command line options.
while getopts hv OPT; do
    case "$OPT" in
        h)
            echo $USAGE
            exit 0
            ;;
        v)
            echo "LSCI Project - Nicolas Bär - Fabian Christoffel, version 0.1"
            exit 0
            ;;
        \?)
            # getopts issues an error message
            echo $USAGE >&2
            exit 1
            ;;
    esac
done

# Remove the switches we parsed above.
shift `expr $OPTIND - 1`

# We want at least one non-option argument. 
# Remove this block if you don't need it.
if [ ! $# -eq 2 ]
then
    echo $USAGE >&2
    exit 1
fi

# Access additional arguments as usual through 
# variables $@, $*, $1, $2, etc. or using this loop:
config=$1
cluster=$2

result=./result

# delete old result file
if [ -f $result ]
then
	cp $result ./"result_old_`date +%H%M%S`"
    rm $result
fi

# fetch result file from master
starcluster -c $config get $cluster --node master /home/lsci/result_output $result

if [ -f $result ];
then
	cat $result
	echo "the result file is saved in ./results"
else
	while true; do
    	read -p "The program did not converge yet, do you want to terminate anyhow?" yn
    	case $yn in
        	[Yy]* ) break;;
        	[Nn]* ) exit;;
        	* ) echo "Please answer yes or no.";;
    	esac
	done
fi

echo "Terminating cluster ..."
# terminate cluster
starcluster -c $config terminate $cluster
echo "Cluster is down."
