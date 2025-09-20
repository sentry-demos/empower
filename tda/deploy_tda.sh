#!/bin/bash

HOST=empower-tda-and-crons
HOST_ZONE=us-central1-a
DIR=/home/kosty/empower-tda
GCP_PROJECT=sales-engineering-sf

export CLOUDSDK_CORE_PROJECT=$GCP_PROJECT
export CLOUDSDK_COMPUTE_ZONE=$HOST_ZONE

function ssh_cmd() {
    local host=$1
    shift
    gcloud compute ssh --tunnel-through-iap $host -- "$@"
}

function cleanup {
  echo "NOTE: if ssh check hangs, re-run 'gcloud compute config-ssh; gcloud compute ssh --tunnel-through-iap $HOST -- exit' to fix"
}
trap cleanup EXIT

echo "[DEBUG] System information:"
ssh -V
ps aux | grep ssh-agent | grep -v grep > /dev/null && echo "ssh-agent is running" || echo "ssh-agent is NOT running"
rsync --version | head -1
gcloud --version

echo "Checking ssh connection can be established..."
gcloud compute ssh --tunnel-through-iap $HOST -- -o StrictHostKeyChecking=accept-new exit
if [ $? != "0" ]; then
  echo "[ERROR] Can't ssh into destination host. Please run 'gcloud compute config-ssh; gcloud compute ssh --tunnel-through-iap $HOST -- exit' to fix"
  exit 5 
fi

trap - EXIT

echo "Copying code to remote directory..."
# for whatever reason can't delete or chmod __pycache__ directories
export RSYNC_RSH='ssh -o "ProxyCommand gcloud compute start-iap-tunnel '$HOST' %p --listen-on-stdin --project='$GCP_PROJECT' --zone='$HOST_ZONE' --verbosity=warning" -o "StrictHostKeyChecking=accept-new"'
rsync -rz --delete --force-delete --exclude env/ --exclude __pycache__ --exclude .pytest_cache * .sauce_credentials $HOST:$DIR/
ret="$?"

echo "Re-attempting with --delete instead of --force-delete..."
if [ $ret == 1 ]; then # some versions of rsync don't recognize --force-delete option
  rsync -rz --delete --force --exclude env/ --exclude __pycache__ --exclude .pytest_cache * .sauce_credentials $HOST:$DIR/
  ret="$?"
fi
if [ $ret != 0 ]; then
  echo "[ERROR] Failed to rsync code to remote directory."
  exit 1
fi
echo "Code copied."

echo "Copying logrotate configuration..."
ssh_cmd $HOST 'sudo cp '$DIR'/logrotate.d/tda /etc/logrotate.d/tda && sudo sed -i "s/create 0640 replace_with_user replace_with_user/create 0640 $USER $USER/" /etc/logrotate.d/tda && sudo sed -i "s/su replace_with_user replace_with_user/su $USER $USER/" /etc/logrotate.d/tda'
if [ $? != 0 ]; then
  echo "[ERROR] Failed to copy logrotate configuration to remote host."
  exit 1
fi
echo "Logrotate configuration copied."

echo "Testing logrotate configuration..."
ssh_cmd $HOST 'sudo logrotate -d /etc/logrotate.d/tda'
if [ $? != 0 ]; then
  echo "[ERROR] Logrotate configuration test failed."
  exit 1
fi
echo "Logrotate configuration test passed."

echo "Setting up log directory permissions..."
ssh_cmd $HOST 'sudo mkdir -p /var/log && sudo touch /var/log/tda.log && sudo chown $USER:$USER /var/log/tda.log'
ssh_cmd $HOST 'sudo chown $USER:$USER /var/log/tda.log*'
if [ $? != 0 ]; then
  echo "[ERROR] Failed to set up log directory permissions."
  exit 1
fi
echo "Log directory permissions set up."

# setting permissions with rscync doesn't work, leaves 775 instead of 777 (umask?)
ssh_cmd $HOST 'find '$DIR' ! -path "*/__pycache__/*" ! -path "*/empower-tda/env/*" ! -path "*/canary.*" -exec sudo chmod 777 {} \;'

echo "Cleaning up old virtual environment..."
ssh_cmd $HOST 'sudo rm -rf '$DIR'/env'
if [ $? != 0 ]; then
  echo "[ERROR] Failed to clean up old virtual environment."
  exit 1
fi
echo "Old virtual environment cleaned up."

echo "Installing requirements..."
# Host must have python3.12 and virtualenv installed
ssh_cmd $HOST 'cd '$DIR' && ./build.sh'
if [ $? != 0 ]; then
  echo "[ERROR] failed to install requirements on destination host"
  exit 1
fi

set -e
# TODO: before killing anything first run canaries, that way we don't end up with
#       a situation where nothing is running
# Side effect would be that then ./stop.sh would stop canaries as well - we don't want that
echo Killing any currently running TDA processes...
ssh_cmd $HOST 'cd '$DIR' && ./stop.sh'

echo "Starting TDA..."
ssh_cmd $HOST 'cd '$DIR' && ./run.sh'
if [ $? != 0 ]; then
  echo "[ERROR] failed to start TDA"
  exit 1
fi

echo "________________________________________________________"
echo "[OK] TDA started!"
echo "Please verify manually:"
echo " . Own errors: https://demo.sentry.io/discover/results/?end={end}&field=title&field=se&field=sauceLabsUrl&field=cexp&field=timestamp&project={project}&query=se:prod-tda-direct-*%2A&queryDataset=error-events&sort=-timestamp&start={start}&yAxis=count%28%29"
echo " . Generated events: https://demo.sentry.io/discover/homepage/?display=top5&field=project&field=count%28%29&field=se&interval=10s&name=All+Events&project=-1&query=&sort=-count&statsPeriod=1h&yAxis=count%28%29"
echo " . Troubleshooting: canary.*.stderr and canary.*.stdout on the host."
