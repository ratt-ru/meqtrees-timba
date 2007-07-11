LOG="pipeline_`date|sed 's/ /_/g'`.log"
python runpipeline_again.py -run > $LOG 2>&1
#
#python runpipeline.py -run -dmeqserver=3
