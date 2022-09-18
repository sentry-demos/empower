#!/bin/bash

export SENDGRID_API_KEY='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'

#RECEPIENTS='[{"email":"kosty.maleyev@sentry.io","name":"Kosty Maleyev"}]'
#SUBJECT="test subject"
#CONTENT="test content"
#FROM='{"email":"kosty.maleyev@sentry.io"}'

#curl --request POST \
#--url https://api.sendgrid.com/v3/mail/send \
#--header "Authorization: Bearer $SENDGRID_API_KEY" \
#--header 'Content-Type: application/json' \
#--data '{"personalizations":[{"to":'"$RECEPIENTS"',"subject":'"$SUBJECT"'}],"content": [{"type": "text/plain", "value": '"$CONTENT"'}],"from":'"$FROM"'}'


curl --request POST \
  --url https://api.sendgrid.com/v3/mail/send \
  --header "Authorization: Bearer $SENDGRID_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"personalizations": [{"to": [{"email": "kosty.maleyev@sentry.io", "name": "Kosty Maleyev"}]}],"from": {"email": "kosty.maleyev@sentry.io"},"subject": "Sending with SendGrid is Fun","content": [{"type": "text/plain", "value": "and easy to do anywhere, even with cURL"}]}'

