RELEASE=`../release.sh`
## TODO try source env/bin/activate in here
## source env/bin/activate
FLASK_ENV=test RELEASE=$RELEASE python3 main.py
