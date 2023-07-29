#!/bin/bash

# Function to print the script usage.
function show_usage() {
  echo "Usage: $0 --project <gcp_project_id> --max-inactive-time-hours <max_inactive_time_hours> [--flexible-only] [--dry-run] [--service-id-contains <substring>]"
}

# Default values for optional arguments.
DRY_RUN=false
FLEXIBLE_ONLY=false
services_deleted=0

# Parse the arguments using getopts.
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      GCP_PROJECT_ID="$2"
      shift 2
      ;;
    --max-inactive-time-hours)
      MAX_INACTIVE_TIME_HOURS="$2"
      shift 2
      ;;
    --flexible-only)
      FLEXIBLE_ONLY=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      dryrun_suffix=" (dry run)"
      shift
      ;;
    --service-id-contains)
      SERVICE_ID_CONTAINS="$2"
      shift 2
      ;;
    *)
      echo "Error: Invalid option '$1'"
      show_usage
      exit 1
      ;;
  esac
done

# Check if the required arguments are provided.
if [[ -z $GCP_PROJECT_ID || -z $MAX_INACTIVE_TIME_HOURS ]]; then
  echo "Error: Missing required arguments."
  show_usage
  exit 1
fi

# Convert MAX_INACTIVE_TIME_HOURS to seconds.
MAX_INACTIVE_TIME_SECONDS=$(( MAX_INACTIVE_TIME_HOURS * 3600 ))

# Function to convert a timestamp to Unix timestamp (epoch time).
function to_unix_timestamp() {
  TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "$1" "+%s"
}

# Function to truncate a string to fit within the given width.
function truncate_string() {
  local str="$1"
  local width=$2
  if [ "${#str}" -gt "$width" ]; then
    echo "${str:0:$((width - 3))}..."
  else
    echo "$str"
  fi
}

# Function to convert seconds to a human-readable format.
function format_duration() {
  local seconds=$1
  if (( seconds >= 86400 )); then
    echo "$(( seconds / 86400 )) days ago"
  elif (( seconds >= 3600 )); then
    echo "$(( seconds / 3600 )) hours ago"
  elif (( seconds >= 60 )); then
    echo "$(( seconds / 60 )) minutes ago"
  else
    echo "$seconds seconds ago"
  fi
}

# Function to print the tabular output for the header.
function print_table_header() {
  printf "%-40s %-13s %-17s %-17s %-23s %-16s\n" "Service ID" "Environment" "Last Request" "Last Deploy" "Deployer" "Action Taken"
}

# Function to print the tabular output for a row.
function print_table_row() {
  local service_id=$1
  local environment=$2
  local last_request_rel=$3
  local last_deploy_rel=$4
  local last_deployer=$5
  local action=$6
  if [[ $last_request_rel == -1 ]]; then
    last_request_rel_h="> "$(format_duration "$MAX_INACTIVE_TIME_SECONDS")
  else
    last_request_rel_h=$(format_duration "$last_request_rel")
  fi
  last_deploy_rel_h=$(format_duration "$last_deploy_rel")
  # Truncate the service ID if it exceeds the width.
  local truncated_service_id=$(truncate_string "$service_id" 40)
  printf "%-40s %-13s %-17s %-17s %-23s %-16s\n" "$truncated_service_id" "$environment" "$last_request_rel_h" "$last_deploy_rel_h" "$last_deployer" "$action"
}

# Print the header for the table using the print_table_header function.
print_table_header

# Get a list of all services in the GCP project.
services=$(gcloud app services list --project="${GCP_PROJECT_ID}" --format="value(id)")

# Loop through each service and check its last request time and last deployer.
for service in $services; do
  # Check if the service ID contains the specified substring (if provided).
  if [[ -n $SERVICE_ID_CONTAINS && ! $service =~ $SERVICE_ID_CONTAINS ]]; then
    continue
  fi

  # Get the environment for the service using "gcloud app versions list".
  environment=$(gcloud app versions list --service="${service}" --project="${GCP_PROJECT_ID}" --filter="traffic_split=1.0" --format="value(environment.name)" 2>/dev/null | tr '[:upper:]' '[:lower:]')

  if [ "$FLEXIBLE_ONLY" = true ] && [ "$environment" != "flex" ]; then
    continue
  fi

  # Get the last request time for the service by querying the logs.
  # For standard environment, use "appengine.googleapis.com%2Frequest_log" log name.
  # For flexible environment, use "appengine.googleapis.com%2Fnginx.request" log name.
  # First, check logs with freshness of 1 day.
  last_request_time=$(gcloud logging read "resource.type=gae_app AND resource.labels.module_id=${service} AND logName=\"projects/${GCP_PROJECT_ID}/logs/appengine.googleapis.com%2Frequest_log\" OR logName=\"projects/${GCP_PROJECT_ID}/logs/appengine.googleapis.com%2Fnginx.request\" AND NOT protoPayload.userAgent =~ \"bot\"" --project="${GCP_PROJECT_ID}" --format="value(timestamp)" --limit=1 --freshness="1d" 2>/dev/null)

  # If no results found for 1 day, query logs for the entire max inactivity period.
  if [[ -z $last_request_time ]]; then
    last_request_time=$(gcloud logging read "resource.type=gae_app AND resource.labels.module_id=${service} AND logName=\"projects/${GCP_PROJECT_ID}/logs/appengine.googleapis.com%2Frequest_log\" OR logName=\"projects/${GCP_PROJECT_ID}/logs/appengine.googleapis.com%2Fnginx.request\" AND NOT protoPayload.userAgent =~ \"bot\"" --project="${GCP_PROJECT_ID}" --format="value(timestamp)" --limit=1 --freshness="${MAX_INACTIVE_TIME_SECONDS}S" 2>/dev/null)
  fi

  # Calculate the duration of inactivity in seconds.
  if [[ -z $last_request_time ]]; then
    last_request_rel=-1
  else
    last_request_rel=$(( $(TZ=UTC date "+%s") - $(to_unix_timestamp "${last_request_time%.*}") ))
  fi
  
  # Get the last deployment time for the service using "gcloud app versions list".
  last_deploy_time=$(gcloud app versions list --service="${service}" --project="${GCP_PROJECT_ID}" --filter="traffic_split=1.0" --format="value(version.createTime)" 2>/dev/null)
  last_deploy_rel=$(( $(TZ=UTC date "+%s") - $(to_unix_timestamp "${last_deploy_time%Z}") ))


  # Get the last deployer for the service using "gcloud app versions list".
  last_deployer=$(gcloud app versions list --service="${service}" --project="${GCP_PROJECT_ID}" --filter="traffic_split=1.0" --format="value(version.createdBy)" 2>/dev/null)

  # Strip everything starting with "@" from the last deployer.
  last_deployer="${last_deployer%%@*}"

  # If the service has never received a request or is inactive for more than the specified time, take appropriate action.
  if [[ ( $last_request_rel -eq -1 || $last_request_rel -gt $MAX_INACTIVE_TIME_SECONDS ) && $last_deploy_rel -gt $MAX_INACTIVE_TIME_SECONDS ]]; then
    action="delete$dryrun_suffix"
    ((services_deleted++))
  else
    action="none"
  fi
  # Print the table row for the service.
  print_table_row "$service" "$environment" "$last_request_rel" "$last_deploy_rel" "$last_deployer" "$action"

  if [[ $action == "delete" ]]; then
      gcloud app services delete "$service" --project="${GCP_PROJECT_ID}" --quiet
  fi
done

# Output the total number of services that were (or would've been) shut down in both environments.
echo -e "\nTotal number of services deleted$dryrun_suffix: $services_deleted"
