#!/bin/bash

HOST=empower-tda-and-crons.us-central1-a.sales-engineering-sf
DIR=/home/kosty/empower-tda

function cleanup {
  echo "NOTE: if ssh check hangs, re-run 'gcloud compute config-ssh; ssh $HOST exit' to fix"
}
trap cleanup EXIT

echo "Checking ssh connection can be established..."
ssh -o StrictHostKeyChecking=accept-new $HOST exit
if [ $? != "0" ]; then
  echo "[ERROR] Can't ssh into destination host. Please run 'gcloud compute config-ssh; ssh $HOST exit' to fix"
  exit 5 
fi

trap - EXIT

reqs_changed=0
env_nonempty=0
echo "Checking state of current deployment..."
diff -q requirements.txt <(ssh $HOST 'cat '$DIR'/requirements.txt')
if [ $? == 1 ]; then # files differ or failed to compare
  reqs_changed=1
fi
if ssh $HOST '[[ -d '"$DIR/env"' ]] && [[ ! -z `ls -A '"$DIR/env"'` ]]'; then
  env_nonempty=1
fi

echo "Copying code to remote directory..."
# for whatever reason can't delete or chmod __pycache__ directories
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
ssh $HOST 'sudo cp '$DIR'/logrotate.d/tda /etc/logrotate.d/tda && sudo sed -i "s/create 0640 replace_with_user replace_with_user/create 0640 $USER $USER/" /etc/logrotate.d/tda'
if [ $? != 0 ]; then
  echo "[ERROR] Failed to copy logrotate configuration to remote host."
  exit 1
fi
echo "Logrotate configuration copied."

echo "Testing logrotate configuration..."
ssh $HOST 'sudo logrotate -d /etc/logrotate.d/tda'
if [ $? != 0 ]; then
  echo "[ERROR] Logrotate configuration test failed."
  exit 1
fi
echo "Logrotate configuration test passed."

echo "Setting up log directory permissions..."
ssh $HOST 'sudo mkdir -p /var/log && for job in '$DIR'/jobs/*.sh; do job_name=$(basename $job .sh); sudo touch /var/log/tda-$job_name.log; done && sudo chown $USER:$USER /var/log/tda*.log'
if [ $? != 0 ]; then
  echo "[ERROR] Failed to set up log directory permissions."
  exit 1
fi
echo "Log directory permissions set up."

# setting permissions with rscync doesn't work, leaves 775 instead of 777 (umask?)
ssh $HOST 'find '$DIR' ! -path "*/__pycache__/*" ! -path "*/empower-tda/env/*" ! -path "*/canary.*" -exec sudo chmod 777 {} \;'

if [[ $reqs_changed == "1" || $env_nonempty == "0" ]]; then
  echo "re-installing requirements (because requirements.txt changed OR 'env' directory does not exist or is empty)..."
  # Host must have python3.8 and virtualenv installed
  ssh $HOST 'cd '$DIR' && ./build.sh'
  if [ $? != 0 ]; then
    echo "[ERROR] failed to install requirements on destination host"
    exit 1
  fi
else
  echo "No need to install requirements, because no changes to requirements.txt, env exists on remote host and is not empty."
fi

set -e
# TODO: before killing anything first run canaries, that way we don't end up with
#       a situation where nothing is running
# Side effect would be that then ./stop.sh would stop canaries as well - we don't want that
echo Killing any currently running TDA processes...
ssh $HOST 'cd '$DIR' && ./stop.sh'

echo "Starting TDA..."
ssh $HOST 'cd '$DIR' && ./run.sh'
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
