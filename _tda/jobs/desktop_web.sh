#!/bin/bash

DAY_TRACKING_FILE="/tmp/tda_loop_prev_day"

current_day=$(date +%j)
prev_day=""
if [ -f "$DAY_TRACKING_FILE" ]; then
    prev_day=$(cat "$DAY_TRACKING_FILE" 2>/dev/null || echo "")
fi
if [ -z "$prev_day" ] || [ "$current_day" != "$prev_day" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [loop.sh] Day changed from '$prev_day' to '$current_day', setting IS_FIRST_RUN_OF_THE_DAY=1"
    echo "$current_day" > "$DAY_TRACKING_FILE" 2>/dev/null
    IS_FIRST_RUN_OF_THE_DAY=1 BATCH_SIZE=1 pytest --timeout=900 -s desktop_web/test_cexp_checkout.py &
fi

# timeout is per-test, test_checkout is batch so can potentially take quite long
BATCH_SIZE=random_5_15 pytest --timeout=900 -s -n 7 --ignore-glob='*_vue.py' desktop_web

