#!/bin/bash
# 1. Create ProgressBar function
# 1.1 Input is currentState($1) and totalState($2)
function ProgressBar {
# Process data
    let _progress=(${1}*100/${2}*100)/100
    let _done=(${_progress}*4)/10
    let _left=40-$_done
# Build progressbar string lengths
    _fill=$(printf "%${_done}s")
    _empty=$(printf "%${_left}s")

# 1.2 Build progressbar strings and print the ProgressBar line
# 1.2.1 Output example:                           
# 1.2.1.1 Progress : [########################################] 100%
printf "\r${3} : [${_fill// /#}${_empty// /-}] ${_progress}%%  Until the end approximately : %02dh:%02dm:%02ds" $((${4}/3600)) $((${4}%3600/60)) $((${4}%60))
}

# Variables
_start=0
# This accounts as the "totalState" variable for the ProgressBar function
# 147
_end=21
# Butch size
_step=100

if [ -f ./models/logs/checker_log.csv ]; then
   count_file=$(find ./models/logs/checker_* -type f |wc -l)
   mv ./models/logs/checker_log.csv ./models/logs/checker_${count_file}_log.csv
fi

# Proof of concept
for number in $(seq ${_start} ${_end})
do
    let _offset=$number*${_step}
    start_time=`date +%s`
    # Put here your script
    nice -19 python3 ./model_checker_batch.py ${_offset} ${_step} > /dev/null 2>&1
    end_time=`date +%s`
    runtime=$((end_time-start_time))
    let common_time=(${_end}-$number)*$runtime
    let _position=${_offset}+${_step}
    ProgressBar ${number} ${_end} ${_position} ${common_time}
done
printf '\nFinished!\n'
