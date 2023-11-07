#!/bin/bash

if [ ! -f .env ]; then
  >&2 echo "[ERROR] Missing .env file. Project deploy scripts are not supposed to be run \
directly, run the following command instead (from parent dir): ./deploy.sh --env=production crons-python"
  exit 1
fi
source .env

HOST="$CRONSPYTHON_DEPLOY_HOST"
DIR="$CRONSPYTHON_DEPLOY_DIR"
CRONTAB_USER=$CRONSPYTHON_CRONTAB_USER

function cleanup {
  echo "NOTE: if ssh check hangs, re-run 'gcloud compute config-ssh; ssh $HOST exit' to fix"
}
trap cleanup EXIT

echo "Checking ssh connection can be established..."
ssh $HOST exit
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
rsync -rz --exclude env * .env $HOST:$DIR/
if [ $? != 0 ]; then
  echo "[ERROR] Failed to rsync code to remote directory."
  exit 1
fi
echo "Code copied."

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

# handle case when crontab is empty
echo "EXISTING crontab:"
ssh $HOST 'sudo crontab -u '$CRONTAB_USER' -l'
if [ $? != 0 ]; then
  ssh $HOST 'echo "" | crontab -'
fi
echo "---"

# set up cron job if not set up already
# NOTE: this will overwrite any existing cron jobs from same project directory
ssh $HOST '(sudo crontab -u '$CRONTAB_USER' -l | grep -v '"$DIR"'; cat '$DIR'/crontab) | sort - | uniq - | sudo crontab -u '$CRONTAB_USER' -'

echo "UPDATED crontab:"
ssh $HOST 'sudo crontab -u '$CRONTAB_USER' -l'
echo "---"

echo "Done. New code should be picked up when cron job runs next time."
echo "If not working, ssh into the host ($HOST) and check the logs in $DIR/crons-python.log"
