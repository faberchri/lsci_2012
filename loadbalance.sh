#!/bin/bash

type -P "starcluster" &>/dev/null || { echo "Err: Command not found: starcluster"
    echo "Install starcluster with command: easy_install starcluster"; exit 1; }

USAGE="Usage: `basename $0` <path/to/starcluster/config> nameOfCluster minClusterSize maxClusterSize"

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
if [ ! $# -eq 4 ]
then
    echo $USAGE >&2
    exit 1
fi

# Access additional arguments as usual through 
# variables $@, $*, $1, $2, etc. or using this loop:
config=$1
cluster=$2
minClusterSize=$3
maxClusterSize=$4
clusterGrowthRate=5 # set to a high value, since all jobs are done at the same time
statisticsFile=./statistics/statistic
killTime=20 # Minutes after which a node can be killed - set to a high value, since we don't want nodes to shutdown during cycle pause 

# start cluster
echo "This command is blocking, so whenever you shutdown this machine, the loadbalancer will stop. So think twice about it :)"
starcluster -c $config loadbalance -m $maxClusterSize -n $minClusterSize -a $clusterGrowthRate -d -D $statisticsFile -k $killTime $cluster
