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
result=./result

# fetch result file from master
starcluster -c $config get $cluster --node master /root/result $result

if [ -f $result ];
then
	cat $result
	echo "the result file is saved in ./results"
else
	echo "The program did not converge yet, do you want to terminate anyhow?"
	select yn in "Yes" "No"; do
	    case $yn in
	        Yes ) break;;
	        No ) exit;;
	    esac
	done
fi


# terminate cluster
#starcluster -c $config terminate $cluster
echo "terminating"
