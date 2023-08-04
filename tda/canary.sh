#!/bin/bash

# Run given job script in background with IS_CANARY=1 and return 0 if it doesn't
# quit prematurely and doesn't print any errors to stderr within first CANARY_TIMEOUT
# seconds. Otherwise, return 1.

job="$1"
CANARY_TIMEOUT=15

job_display=$(echo $job | sed 's/\//_/g') # replace / with _
OUT=canary.$job_display.stdout
ERR=canary.$job_display.stderr
rm -f $OUT $ERR # delete old ones from previous run
# Canary run
# We instruct conftest.py to set batch size to 1 regardless of what BATCH_SIZE $job has
# passed in. This is necessary because if we ran it in a loop from the get go, it would
# not be possible to redirect stderr to /dev/null after we've examined it for errors 
# (deleting a file to which a background process is redirecting output seems to results
# in some kind of system buffer using up all the disk space). 
echo "Running canary for $job ..."
IS_CANARY=1 ./$job >$OUT 2>$ERR &
canary_pid=$!
echo " . pid: $canary_pid"
echo " . sleeping for $CANARY_TIMEOUT seconds..."
sleep $CANARY_TIMEOUT
# the '=' in '-o pid=' is to avoid printing the header
if [ -z "$(ps -p $canary_pid -o pid=)" ]; then
  echo "[ERROR] Process exited prematurely."
  err=1
elif [ -s $ERR ]; then
  echo "[ERROR] Canary process still running but STDERR is not empty. Assuming failure."
  err=1
else
  echo "[OK] Seems to be running fine."
  echo " . canaries are let to run their course, so process may linger for a few minutes."
 fi
# Let canary run its course to avoid any own errors resulting from abnormal termination
# kill -s 9 $!

if [ "$err" == "1" ]; then 
  echo "$OUT (last 10 lines):"
  tail -10 $OUT 2>/dev/null
  echo "$ERR (last 10 lines):"
  tail -10 $ERR 2>/dev/null
  exit 1
fi

exit 0