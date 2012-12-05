#!/bin/bash


# install gc3pie
mkdir /root/install_gc3pie
cd /root/install_gc3pie
wget http://gc3pie.googlecode.com/svn/install.sh
sh ./install.sh --develop --yes

# switch to gc3pie virtual env 
. /root/gc3pie/bin/activate


# call evolution script
python /root/dif_evolution_forwardPremium.py > sample.txt

