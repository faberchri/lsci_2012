#!/bin/bash
# 1. arg: EX
# 2. arg: sigmaX
# 3. arg: cycle count
# 4. arg: job id
# 5. -i arg [OPTIONAL]: input ROOT directory
# 5. -o arg [OPTIONAL]: output ROOT directory
# 6. -w arg [OPTIONAL]: working directory
# outputs are stored in <output-ROOT-directory>/<cycle-count>/<job-id>

outRootDir="/home/results" # default
workingDir="/root" # default
inputDir="/home/worker" # default

USAGE="Usage: `basename $0` [-hv] [-i <Input/Dir>] [-o <Output/Dir>] [-w <Working/Dir>] EX sigmaX cycleCount jobId"

# Parse command line options.
while getopts hvo:w:i: OPT; do
    case "$OPT" in
        h)
            echo $USAGE
            exit 0
            ;;
        v)
            echo "`basename $0` version 0.1"
            exit 0
            ;;
        o)
            outRootDir=$OPTARG
            ;;
        w)
            workingDir=$OPTARG
            ;;
        i)
            inputDir=$OPTARG
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
if [ $# -lt 4 ]
then
    echo $USAGE >&2
    exit 1
fi

# Access additional arguments as usual through 
# variables $@, $*, $1, $2, etc. or using this loop:
eX=$1
sigmaX=$2
cycleCount=$3
jobId=$4

echo "EX: "$eX
echo "sigmaX: "$sigmaX
echo "cycle count: "$cycleCount
echo "job id: "$jobId
echo "root input dir: "$inputDir
echo "root output directory: "$outRootDir
echo "working directory: "$workingDir

if [ ! -d $inputDir ]
then
	echo "Err: Input directory does not exist. "
	echo $USAGE >&2
	exit 1
fi

if [ ! -d $outRootDir ]
then
	echo "output root directory does not exist. "
	echo "output root directory is created: "$outRootDir
	mkdir $outRootDir
fi

# create outputDir string
outputDir=$outRootDir"/"$cycleCount"/"$jobId

if [ -d $outputDir ]
then
	echo "output directory does already exist. "
	echo "output directory is deleted: "$outputDir
	sudo -s rm -R $outputDir
fi
echo "create output directory: "$outputDir
mkdir -p $outputDir

if [ ! -d $workingDir ]
then
	echo "working directory does not exist. "
	echo "working directory is created: "$workingDir
	mkdir $workingDir
fi

######## set up working dir ##########
# delete old bin output directory
if [ -d $workingDir"/output" ]
then
	echo "old bin output directory is deleted: "$workingDir"/output"
	sudo -s rm -R $workingDir"/output"
fi
# copy binary if not available
if [ ! -f $workingDir"/forwardPremiumOut" ]
then
	echo "copy binary from "$inputDir" to "$workingDir
	cp $inputDir"/forwardPremiumOut" $workingDir"/."
fi
# copy constant input files if not available
if [ ! -d $workingDir"/input" ]
then
	echo "copy constant input files from "$inputDir" to "$workingDir
	cp -R $inputDir"/input" $workingDir"/."
fi

# remove a possibly present parameters.in file from working directory
parametersFile=$workingDir"/input/parameters.in"
if [ -f $parametersFile ]
then
	echo "Deleting old parameters.in file: "$parametersFile
	sudo -s rm $parametersFile
fi

# create new parameters.in file
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
echo "hbit    |       EA                                              |       $eX" >> $parametersFile
echo "hbit    |       EB                                              |       $eX" >> $parametersFile
echo "hbit    |       sigmaA                                          |       $sigmaX" >> $parametersFile
echo "hbit    |       sigmaB                                          |       $sigmaX" >> $parametersFile
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

echo "****** starting forwardPremiumOut... (job id: "$jobId", cycle: "$cycleCount", location: "$workingDir") *******"
cd $workingDir
./forwardPremiumOut

# ................................. 
# ... forwardPremiumOut running ...
# .................................

# extract FF-Beta from output if simulation.out present
if [ -f $workingDir"/output/simulation.out" ]
then
	grep "FamaFrenchBeta" $workingDir"/output/simulation.out" > $outputDir"/FF-beta.out"
	sed 's/FamaFrenchBeta//' $outputDir"/FF-beta.out" > $outputDir"/FF-beta.out"
fi

# move bin output dir to outputDir
mv $workingDir"/output" $outputDir
