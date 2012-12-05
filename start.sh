#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied. Please pass the path to your starcluster config as first parameter"
	exit 1
fi

config=$1
cluster="supercluster"

# start cluster
starcluster -c $config start $cluster

### upload files to cluster
# master files
starcluster -c $config put $cluster --node master master/master.sh /root/master.sh
starcluster -c $config put $cluster --node master master/dif_evolution_forwardPremium.py /root/dif_evolution_forwardPremium.py

# worker files
starcluster -c $config put $cluster worker /home/worker



# execute master script
echo "--------------------------------------------------------"
echo "Starting distributed experiment now! Check back later :)"
starcluster -c $config sshmaster $cluster 'chmod +x /root/master.sh && sh -c "nohup /root/master.sh > /dev/null 2>&1 &"'