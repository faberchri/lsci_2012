#!/bin/bash

type -P "starcluster" &>/dev/null || { echo "Err: Command not found: starcluster"
    echo "Install starcluster with command: easy_install starcluster"; exit 1; }

if [ $# -eq 0 ]
  then
    echo "No arguments supplied. Please pass the path to your starcluster config as first parameter"
	exit 1
fi

config=$1
cluster="supercluster"

# start cluster
starcluster -c $config start $cluster

# clear master and client folders
starcluster -c $config sshmaster $cluster 'rm -rf /home/lsci && mkdir /home/lsci'


### upload files to cluster
# master files
starcluster -c $config put $cluster --node master master /home/lsci/master
# worker files
starcluster -c $config put $cluster worker /home/worker



# execute master script
echo "--------------------------------------------------------"
echo "Starting distributed experiment now! Check back later :)"
# to see the whole output:
#starcluster -c $config sshmaster $cluster 'chmod +x /home/lsci/master/master.sh && chmod +x /home/worker/worker.sh && /home/lsci/master/master.sh'
starcluster -c $config sshmaster $cluster 'chmod +x /home/lsci/master/master.sh && chmod +x /home/worker/worker.sh && sh -c "nohup /home/lsci/master/master.sh > /dev/null 2>&1 &"'