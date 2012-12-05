#!/bin/bash
# first argument is EX,
# second argument is sigmaX,
# third argument is session id,
# fourth argument is root directory
# outputs are stored in <root directory>/<session-id>/output

echo "EX: "$1
echo "sigmaX: "$2
echo "session id: "$3
echo "root directory: "$4

rootDir=$4
if [ ! -d $rootDir ]
then
	echo "root directory does not exist. "
	echo "root directory is created: "$rootDir
	mkdir $rootDir
fi

sessionLocation=$rootDir"/"$3

if [ -d $sessionLocation ]
then
	echo "old session directory is deleted: "$sessionLocation
	sudo -s rm -R $sessionLocation
fi

echo "new session directory is created: "$sessionLocation
mkdir $sessionLocation

# copy the unchanged inputs to create session input
echo "copy constant input files from /opt/ifi/input to "$sessionLocation
cp -R /opt/ifi/input $sessionLocation"/."

# copy binary
echo "copy binary from /apps/ifi/forwardPremiumOut to "$sessionLocation
cp /apps/ifi/forwardPremiumOut $sessionLocation"/forwardPremiumOut"


sessionInputLocation=$sessionLocation"/input/"

parametersFile=$sessionInputLocation"parameters.in"
if [ -f $parametersFile ]
then
	echo "The old parameters.in file "$parametersFile" is deleted.
	sudo -s rm $parametersFile
fi
touch $parametersFile


echo "group   |       name                                            |       value" >> $parametersFile
echo "algo    |       T                                               |       100" >> $parametersFile
echo "algo    |       convCrit                                        |       1e-6" >> $parametersFile
echo "algo    |       newPolicyFlag                                   |       1" >> $parametersFile
echo "algo    |       storeStartingPoints                             |       0" >> $parametersFile
echo "algo    |       nSimulations                                    |       1e6" >> $parametersFile
echo "sspa    |       wGridSize                                       |       11" >> $parametersFile
echo "econ    |       gamma                                           |       2" >> $parametersFile
echo "econ    |       beta                                            |       0.99" >> $parametersFile
echo "econ    |       alphaA                                          |       0.5" >> $parametersFile
echo "econ    |       alphaB                                          |       0.5" >> $parametersFile
echo "econ    |       b1Abar                                          |       -1" >> $parametersFile
echo "econ    |       b2Abar                                          |       -1" >> $parametersFile
echo "econ    |       b1Bbar                                          |       -1" >> $parametersFile
echo "econ    |       b2Bbar                                          |       -1" >> $parametersFile
echo "econ    |       wBar                                            |       -0.100" >> $parametersFile
echo "econ    |       wGridBar                                        |       -0.100" >> $parametersFile
echo "hbit    |       EA                                              |       $1" >> $parametersFile
echo "hbit    |       EB                                              |       $1" >> $parametersFile
echo "hbit    |       sigmaA                                          |       $2" >> $parametersFile
echo "hbit    |       sigmaB                                          |       $2" >> $parametersFile
echo "hbit    |       gridScaleA                                      |       1" >> $parametersFile
echo "hbit    |       gridScaleB                                      |       1" >> $parametersFile
echo "hbit    |       gridSizeA                                       |       3" >> $parametersFile
echo "hbit    |       gridSizeB                                       |       3" >> $parametersFile
echo "algo    |       simulOnly                                       |       0" >> $parametersFile
echo "algo    |       policPlot                                       |       0" >> $parametersFile
echo "algo    |       simulPlot                                       |       0" >> $parametersFile
echo "algo    |       makeSav                                         |       0" >> $parametersFile
echo "algo    |       simulWealth0                                    |       0" >> $parametersFile

echo "----------- The parameters.in file --------------"
cat $parametersFile
echo "-------------------------------------------------"

echo "****** starting forwardPremiumOut (session: "$3", location: "$sessionLocation"/forwardPremiumOut)... *******"
cd $sessionLocation
./forwardPremiumOut







#replacementStringEX='s/EX/'$1'/'
#sed $replacementStringEX /opt/ifi/parameter_template.in > /opt/ifi/input/tmp.in
#
#replacementStringSigmaX='s/sigmaX/'$2'/'
#sed $replacementStringSigmaX /opt/ifi/input/tmp.in > /opt/ifi/input/parameters.in
#
#rm /opt/ifi/input/tmp.in
#
#if [ ! -f /opt/ifi/forwardPremiumOut ]
#then
#	cp /apps/ifi/forwardPremiumOut /opt/ifi/forwardPremiumOut
#fi
#
#cat /opt/ifi/input/parameters.in
#
#/opt/ifi/forwardPremiumOut
#


#cd /opt/ifi/input
#
#echo "now run the fucking shit"
#/apps/ifi/forwardPremiumOut