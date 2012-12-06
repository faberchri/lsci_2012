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

# start cluster
starcluster -c $config start $cluster

# clear master and client folders
starcluster -c $config sshmaster $cluster 'rm -rf /home/lsci && mkdir /home/lsci'


### upload files to cluster
# master files
starcluster -c $config put $cluster --node master master /home/lsci/master
# worker files
starcluster -c $config put $cluster worker /home/lsci/worker



# execute master script
echo "--------------------------------------------------------"
echo "Starting distributed experiment now! Check back later :)"
# to see the whole output:
#starcluster -c $config sshmaster $cluster 'chmod +x /home/lsci/master/master.sh && chmod +x /home/worker/worker.sh && /home/lsci/master/master.sh'
starcluster -c $config sshmaster $cluster 'chmod +x /home/lsci/master/master.sh && chmod +x /home/worker/worker.sh && sh -c "nohup /home/lsci/master/master.sh > /dev/null 2>&1 &"'