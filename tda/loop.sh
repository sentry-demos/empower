#!/bin/bash

# Execute command in a loop infinitely, whether it fails or succeeds

# usage: ./loop.sh command arg1 arg2 ...

LOG_FILE=/var/log/tda.log

# Signal handling function
log_signal() {
    local signal_name=$1
    local signal_num=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local script_pid=$$
    local parent_pid=$PPID
    local user=$(whoami)
    local hostname=$(hostname)
    local pwd=$(pwd)
    local cmd_line=$(ps -p $$ -o args= 2>/dev/null || echo "unknown")
    local parent_cmd_line=$(ps -p $PPID -o args= 2>/dev/null || echo "unknown")
    
    {
        echo "[$timestamp] SIGNAL RECEIVED: $signal_name ($signal_num)"
        echo "[$timestamp] Script PID: $script_pid"
        echo "[$timestamp] Parent PID: $parent_pid"
        echo "[$timestamp] User: $user"
        echo "[$timestamp] Working directory: $pwd"
        echo "[$timestamp] Command line: $cmd_line"
        echo "[$timestamp] Parent command line: $parent_cmd_line"
        echo "[$timestamp] exiting..."
        echo "----------------------------------------"
    } >> $LOG_FILE 2>/dev/null || true
    
    exit 1
}

# Set up signal handlers for common signals
trap 'log_signal "SIGHUP" 1' HUP
trap 'log_signal "SIGINT" 2' INT
trap 'log_signal "SIGQUIT" 3' QUIT
trap 'log_signal "SIGTERM" 15' TERM
trap 'log_signal "SIGUSR1" 10' USR1
trap 'log_signal "SIGUSR2" 12' USR2
trap 'log_signal "SIGALRM" 14' ALRM
trap 'log_signal "SIGPIPE" 13' PIPE
trap 'log_signal "SIGXCPU" 24' XCPU
trap 'log_signal "SIGXFSZ" 25' XFSZ
trap 'log_signal "SIGVTALRM" 26' VTALRM
trap 'log_signal "SIGPROF" 27' PROF
trap 'log_signal "SIGWINCH" 28' WINCH
trap 'log_signal "SIGIO" 29' IO
trap 'log_signal "SIGPWR" 30' PWR
trap 'log_signal "SIGSYS" 31' SYS

# Log script start
echo "[$(date '+%Y-%m-%d %H:%M:%S')] loop.sh started with PID $$, command: $*"

while true; do 
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [loop.sh] running: $@"
  
  # sets IS_FIRST_RUN_OF_THE_DAY accordingly
  check_is_first_run_of_the_day
  
  "$@"
done
