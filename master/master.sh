#!/bin/bash


# install gc3pie
mkdir /root/install_gc3pie
cd /root/install_gc3pie
wget http://gc3pie.googlecode.com/svn/install.sh
sh ./install.sh --develop --yes

# switch to gc3pie virtual env 
. /root/gc3pie/bin/activate


# call evolution script
cd /home/lsci/master
python /home/lsci/master/dif_evolution_forwardPremium.py # enable log: > /root/evolution.log

