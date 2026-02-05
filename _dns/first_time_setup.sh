#!/bin/bash
#
# ONE-TIME SETUP: Creates the base Load Balancer infrastructure.
# Run this script ONCE before using deploy_project.sh for the first time.
#
# This script creates service-agnostic infrastructure:
#   1. Reserved global static IP address
#   2. Empty URL map with default backend
#   3. Target HTTPS proxy (with placeholder cert, replaced by deploy_project.sh)
#   4. Forwarding rule
#
# Service-specific resources (SSL certificates, NEGs, backend services) are created
# dynamically by deploy_project.sh based on config.yaml.
#
# After running this script:
#   1. Note the static IP address printed at the end
#   2. Deploy services: ./deploy --env=production _dns
#   3. Update DNS for each domain as you add them to config.yaml
#
# Usage: ./first_time_setup.sh [--dry-run]

set -e

# Configuration - matches config.yaml
REGION="${GCP_REGION}"
LB_NAME="empower-lb"
URL_MAP_NAME="empower-url-map"
TARGET_PROXY_NAME="empower-https-proxy"
FORWARDING_RULE_NAME="empower-forwarding-rule"
STATIC_IP_NAME="empower-lb-ip"

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[DRY-RUN] Commands will be printed but not executed"
fi

run_cmd() {
  echo "+ $*"
  if [[ "$DRY_RUN" == "false" ]]; then
    eval "$@"
  fi
}

echo "=== Empower Plant Load Balancer Infrastructure Setup ==="

# Set project
run_cmd "gcloud config set project ${GCP_PROJECT}"

echo ""
echo "=== Step 1: Reserve Global Static IP Address ==="
if gcloud compute addresses describe $STATIC_IP_NAME --global &>/dev/null; then
  echo "Static IP '$STATIC_IP_NAME' already exists."
else
  run_cmd "gcloud compute addresses create $STATIC_IP_NAME --global --ip-version=IPV4"
fi

# Get the IP address
STATIC_IP=$(gcloud compute addresses describe $STATIC_IP_NAME --global --format='get(address)' 2>/dev/null || echo "PENDING")
echo "Static IP: $STATIC_IP"

echo ""
echo "=== Step 2: Create Default Backend Service ==="
DEFAULT_BACKEND_NAME="${LB_NAME}-default-backend"

if gcloud compute backend-services describe $DEFAULT_BACKEND_NAME --global &>/dev/null; then
  echo "Default backend service '$DEFAULT_BACKEND_NAME' already exists."
else
  run_cmd "gcloud compute backend-services create $DEFAULT_BACKEND_NAME \
    --global \
    --load-balancing-scheme=EXTERNAL_MANAGED \
    --protocol=HTTPS"
fi

echo ""
echo "=== Step 3: Create URL Map ==="
if gcloud compute url-maps describe $URL_MAP_NAME --global &>/dev/null; then
  echo "URL map '$URL_MAP_NAME' already exists."
else
  run_cmd "gcloud compute url-maps create $URL_MAP_NAME \
    --global \
    --default-service=$DEFAULT_BACKEND_NAME"
fi

# This is needed because target-https-proxy requires a certificate at creation time.
# It will be replaced by deploy_project.sh with a Google-managed certificate.
echo ""
echo "=== Step 4: Create Placeholder Certificate ==="
PLACEHOLDER_CERT_NAME="${LB_NAME}-placeholder-cert"

if gcloud compute ssl-certificates describe $PLACEHOLDER_CERT_NAME --global &>/dev/null; then
  echo "Placeholder certificate '$PLACEHOLDER_CERT_NAME' already exists."
else
  # Create a temporary self-signed cert just to bootstrap the proxy
  TEMP_DIR=$(mktemp -d)
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$TEMP_DIR/key.pem" \
    -out "$TEMP_DIR/cert.pem" \
    -subj "/CN=placeholder.empower-plant.com" 2>/dev/null
  
  run_cmd "gcloud compute ssl-certificates create $PLACEHOLDER_CERT_NAME \
    --global \
    --certificate=$TEMP_DIR/cert.pem \
    --private-key=$TEMP_DIR/key.pem"
  
  rm -rf "$TEMP_DIR"
fi

echo ""
echo "=== Step 5: Create Target HTTPS Proxy ==="
if gcloud compute target-https-proxies describe $TARGET_PROXY_NAME --global &>/dev/null; then
  echo "Target HTTPS proxy '$TARGET_PROXY_NAME' already exists."
else
  run_cmd "gcloud compute target-https-proxies create $TARGET_PROXY_NAME \
    --global \
    --url-map=$URL_MAP_NAME \
    --ssl-certificates=$PLACEHOLDER_CERT_NAME"
fi

echo ""
echo "=== Step 6: Create Forwarding Rule ==="
if gcloud compute forwarding-rules describe $FORWARDING_RULE_NAME --global &>/dev/null; then
  echo "Forwarding rule '$FORWARDING_RULE_NAME' already exists."
else
  run_cmd "gcloud compute forwarding-rules create $FORWARDING_RULE_NAME \
    --global \
    --load-balancing-scheme=EXTERNAL_MANAGED \
    --target-https-proxy=$TARGET_PROXY_NAME \
    --address=$STATIC_IP_NAME \
    --ports=443"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Base infrastructure created. Next steps:"
echo ""
echo "1. Static IP for DNS configuration:"
echo "   $STATIC_IP"
echo ""
echo "2. Add services to config.yaml and deploy:"
echo "   ./deploy --env=production _dns"
echo ""
echo "3. Update DNS A records for each domain to point to: $STATIC_IP"
echo ""
echo "SSL certificates will be created automatically by deploy_project.sh"
echo "based on the domains defined in config.yaml."
echo ""
