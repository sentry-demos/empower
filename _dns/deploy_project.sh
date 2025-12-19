#!/bin/bash
#
# Deploy DNS/Routing configuration.
# This script handles two routing mechanisms:
#   1. App Engine dispatch.yml (legacy, for services not yet migrated)
#   2. Load Balancer with Serverless NEG (new, for migrated services)
#
# The script reads config.yaml (generated from template) and creates/updates:
#   - Google-managed SSL certificates for all domains
#   - Serverless NEGs for each App Engine service
#   - Backend services using those NEGs
#   - URL map host rules to route traffic
#
# Environment-specific behavior:
#   - config.yaml.template uses per-service variables (e.g., ${GO_SUBDOMAIN})
#   - ./deploy processes the template, generating environment-specific config.yaml
#   - This script only touches resources for services defined in the generated file
#
# Prerequisites:
#   - Run first_time_setup.sh once to create base LB infrastructure
#   - Update DNS to point migrated domains to the LB static IP
#
# Usage: Called by ./deploy --env=production _dns  or  ./deploy --env=staging _dns

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration - must match first_time_setup.sh
REGION="${GCP_REGION}"
URL_MAP_NAME="empower-url-map"
TARGET_PROXY_NAME="empower-https-proxy"
PLACEHOLDER_CERT_NAME="empower-lb-placeholder-cert"
SSL_CERT_BASE_NAME="empower-ssl-cert"

echo "=== DNS/Routing Deployment ==="
gcloud config set project "${GCP_PROJECT}"

# =============================================================================
# Helper Functions
# =============================================================================

# Check if config.yaml exists (generated from template by ./deploy)
check_lb_routes() {
  if [[ ! -f "config.yaml" ]]; then
    echo "[INFO] config.yaml not found - no LB services configured for this environment"
    return 1
  fi
  return 0
}

# Extract all hosts from config.yaml
# Note: Using [[:space:]] for POSIX compatibility (macOS BSD grep/sed don't support \s)
get_all_hosts() {
  grep -E '^[[:space:]]*-[[:space:]]+host:' config.yaml 2>/dev/null | \
    sed -E 's/.*host:[[:space:]]*"([^"]*)".*/\1/' | \
    grep -v '^$' | \
    sort -u
}

# =============================================================================
# Part 1: Deploy dispatch.yml for non-migrated services
# =============================================================================
echo "=== Deploying dispatch.yml (legacy routing) ==="

# Get list of LB-managed hosts to filter out (only for current environment)
if check_lb_routes; then
  LB_HOSTS=$(get_all_hosts | tr '\n' '|' | sed 's/|$//' | xargs)
else
  LB_HOSTS=""
fi

if [[ -n "$LB_HOSTS" ]]; then
  # Filter out LB-managed services from dispatch.yml before deploying
  # Note: gcloud requires the file to be named exactly "dispatch.yaml"
  TEMP_DIR=$(mktemp -d)
  TEMP_DISPATCH="$TEMP_DIR/dispatch.yaml"
  trap "rm -rf $TEMP_DIR" EXIT
  
  # Use awk to filter out entries matching LB-managed hosts
  awk -v hosts="$LB_HOSTS" '
    BEGIN { skip=0 }
    /url:/ {
      skip=0
      for (i=1; i<=split(hosts,h,"|"); i++) {
        if (index($0, h[i]) > 0) {
          skip=1
          break
        }
      }
    }
    skip && /service:/ { skip=0; next }
    !skip { print }
  ' dispatch.yml > "$TEMP_DISPATCH"
  
  # Check if there are any remaining dispatch rules
  if grep -q 'url:' "$TEMP_DISPATCH"; then
    echo "Deploying filtered dispatch.yml (excluding LB-managed: $LB_HOSTS)..."
    gcloud app deploy "$TEMP_DISPATCH" --quiet
  else
    echo "No dispatch rules remaining after filtering - skipping dispatch.yml deploy"
  fi
else
  echo "No LB-managed services for this environment, deploying full dispatch.yml..."
  gcloud app deploy dispatch.yml --quiet
fi

# =============================================================================
# Part 2: Update Load Balancer configuration for migrated services
# =============================================================================
echo ""
echo "=== Updating Load Balancer Configuration ==="

# Check if config.yaml exists
if ! check_lb_routes; then
  echo "No config.yaml found - skipping LB configuration"
  exit 0
fi

# Check if URL map exists (first_time_setup.sh must run first)
if ! gcloud compute url-maps describe $URL_MAP_NAME --global &>/dev/null; then
  echo "[WARNING] URL map '$URL_MAP_NAME' not found."
  echo "Run first_time_setup.sh first to create the base LB infrastructure."
  echo "Skipping LB configuration update."
  exit 0
fi

# =============================================================================
# Part 2a: Manage SSL Certificates
# =============================================================================
echo ""
echo "=== Managing SSL Certificates ==="

# Get domains for THIS environment from config.yaml
ENV_DOMAINS=$(get_all_hosts | tr '\n' ',' | sed 's/,$//')

# Trim whitespace from ENV_DOMAINS
ENV_DOMAINS=$(echo "$ENV_DOMAINS" | xargs)

if [[ -z "$ENV_DOMAINS" ]]; then
  echo "No domains found in config.yaml - skipping SSL certificate management"
  echo "[DEBUG] Contents of config.yaml:"
  cat config.yaml
else
  echo "Domains for this environment: $ENV_DOMAINS"
  
  # Get all existing certificates on the proxy
  EXISTING_CERTS=$(gcloud compute target-https-proxies describe $TARGET_PROXY_NAME --global \
    --format="value(sslCertificates)" 2>/dev/null | tr ';' '\n' | xargs -I{} basename {} || echo "")
  
  # Build list of domains already covered by ACTIVE certificates
  COVERED_DOMAINS=""
  ACTIVE_CERTS=""
  PROVISIONING_CERTS=""
  
  for cert in $EXISTING_CERTS; do
    if [[ "$cert" == "$PLACEHOLDER_CERT_NAME" ]]; then
      continue
    fi
    
    # Check certificate status
    CERT_STATUS=$(gcloud compute ssl-certificates describe "$cert" --global \
      --format="value(managed.status)" 2>/dev/null || echo "")
    CERT_DOMAINS=$(gcloud compute ssl-certificates describe "$cert" --global \
      --format="value(managed.domains)" 2>/dev/null | tr ';' ',' || echo "")
    
    if [[ "$CERT_STATUS" == "ACTIVE" ]]; then
      ACTIVE_CERTS="$ACTIVE_CERTS $cert"
      if [[ -n "$COVERED_DOMAINS" ]]; then
        COVERED_DOMAINS="${COVERED_DOMAINS},${CERT_DOMAINS}"
      else
        COVERED_DOMAINS="$CERT_DOMAINS"
      fi
    else
      PROVISIONING_CERTS="$PROVISIONING_CERTS $cert"
      echo "[INFO] Certificate '$cert' is still $CERT_STATUS"
    fi
  done
  
  echo "Domains covered by ACTIVE certificates: ${COVERED_DOMAINS:-none}"
  
  # Find domains that need a new certificate
  MISSING_DOMAINS=""
  for domain in $(echo "$ENV_DOMAINS" | tr ',' '\n'); do
    if ! echo "$COVERED_DOMAINS" | tr ',' '\n' | grep -q "^${domain}$"; then
      if [[ -n "$MISSING_DOMAINS" ]]; then
        MISSING_DOMAINS="${MISSING_DOMAINS},${domain}"
      else
        MISSING_DOMAINS="$domain"
      fi
    fi
  done
  
  if [[ -n "$MISSING_DOMAINS" ]]; then
    echo "Domains needing certificate: $MISSING_DOMAINS"
    
    # Check if there's already a provisioning cert that covers these domains
    NEEDS_NEW_CERT=true
    for cert in $PROVISIONING_CERTS; do
      CERT_DOMAINS=$(gcloud compute ssl-certificates describe "$cert" --global \
        --format="value(managed.domains)" 2>/dev/null | tr ';' ',' || echo "")
      
      # Check if all missing domains are in this provisioning cert
      ALL_COVERED=true
      for domain in $(echo "$MISSING_DOMAINS" | tr ',' '\n'); do
        if ! echo "$CERT_DOMAINS" | tr ',' '\n' | grep -q "^${domain}$"; then
          ALL_COVERED=false
          break
        fi
      done
      
      if [[ "$ALL_COVERED" == "true" ]]; then
        echo "[INFO] Certificate '$cert' is already provisioning for these domains. Waiting..."
        NEEDS_NEW_CERT=false
        break
      fi
    done
    
    if [[ "$NEEDS_NEW_CERT" == "true" ]]; then
      # Create new certificate for missing domains only
      NEW_CERT_NAME="${SSL_CERT_BASE_NAME}-$(date +%Y%m%d%H%M%S)"
      
      echo "Creating new SSL certificate: $NEW_CERT_NAME"
      echo "Domains: $MISSING_DOMAINS"
      gcloud compute ssl-certificates create "$NEW_CERT_NAME" \
        --global \
        --domains="$MISSING_DOMAINS"
      
      # ADD to proxy alongside existing certs (don't replace!)
      ALL_CERTS_FOR_PROXY="$NEW_CERT_NAME"
      for cert in $ACTIVE_CERTS $PROVISIONING_CERTS; do
        ALL_CERTS_FOR_PROXY="$ALL_CERTS_FOR_PROXY,$cert"
      done
      # Remove leading/trailing commas and spaces
      ALL_CERTS_FOR_PROXY=$(echo "$ALL_CERTS_FOR_PROXY" | sed 's/^,//' | sed 's/,$//' | tr ' ' ',' | sed 's/,,*/,/g')
      
      echo "Updating HTTPS proxy to use certificates: $ALL_CERTS_FOR_PROXY"
      gcloud compute target-https-proxies update $TARGET_PROXY_NAME \
        --global \
        --ssl-certificates="$ALL_CERTS_FOR_PROXY"
      
      echo ""
      echo "[INFO] New certificate created: $NEW_CERT_NAME"
      echo "[INFO] Certificate provisioning can take up to 24 hours after DNS propagation."
      echo "[INFO] Existing services remain available via existing certificates."
      echo "[INFO] Check status: gcloud compute ssl-certificates describe $NEW_CERT_NAME --global"
    fi
  else
    echo "All domains already covered by ACTIVE certificates"
  fi
  
  # Cleanup: Remove placeholder cert if we have active certs
  if [[ -n "$ACTIVE_CERTS" ]]; then
    for cert in $EXISTING_CERTS; do
      if [[ "$cert" == "$PLACEHOLDER_CERT_NAME" ]]; then
        echo "Removing placeholder certificate from proxy..."
        # Get current certs and remove placeholder
        CURRENT_CERTS=$(gcloud compute target-https-proxies describe $TARGET_PROXY_NAME --global \
          --format="value(sslCertificates)" 2>/dev/null | tr ';' '\n' | xargs -I{} basename {} | grep -v "$PLACEHOLDER_CERT_NAME" | tr '\n' ',' | sed 's/,$//')
        if [[ -n "$CURRENT_CERTS" ]]; then
          gcloud compute target-https-proxies update $TARGET_PROXY_NAME --global --ssl-certificates="$CURRENT_CERTS" || true
          gcloud compute ssl-certificates delete "$PLACEHOLDER_CERT_NAME" --global --quiet || true
        fi
      fi
    done
  fi
fi

# =============================================================================
# Part 2b: Create/Update NEGs, Backend Services, and URL Map rules
# =============================================================================
echo ""
echo "=== Updating Backend Services and URL Map ==="

parse_lb_routes() {
  local in_services=false
  local current_host=""
  local current_service=""
  
  while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${line// /}" ]] && continue
    
    # Check if we're in services section
    if [[ "$line" =~ ^services: ]]; then
      in_services=true
      continue
    fi
    
    if [[ "$in_services" == true ]]; then
      # New service entry (starts with "- host:")
      if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*host:[[:space:]]*\"?([^\"]*)\"? ]]; then
        # Process previous service if exists
        if [[ -n "$current_host" ]]; then
          create_or_update_service "$current_host" "$current_service"
        fi
        current_host="${BASH_REMATCH[1]}"
        current_service=""
      elif [[ "$line" =~ [[:space:]]*service:[[:space:]]*(.+) ]]; then
        current_service="${BASH_REMATCH[1]}"
      fi
      # neg_name and backend_service are now derived automatically
    fi
  done < config.yaml
  
  # Process last service
  if [[ -n "$current_host" ]]; then
    create_or_update_service "$current_host" "$current_service"
  fi
}

create_or_update_service() {
  local host="$1"
  local service="$2"
  
  # Derive subdomain from host (everything before the first dot)
  local subdomain="${host%%.*}"
  
  # Derive neg_name and backend_name from subdomain
  local neg_name="neg-${subdomain}"
  local backend_name="backend-${subdomain}"
  
  echo ""
  echo "--- Processing: $host -> $service ---"
  echo "    Subdomain: $subdomain | NEG: $neg_name | Backend: $backend_name"
  
  # 1. Create or update Serverless NEG
  if ! gcloud compute network-endpoint-groups describe "$neg_name" --region=$REGION &>/dev/null; then
    echo "Creating Serverless NEG: $neg_name"
    gcloud compute network-endpoint-groups create "$neg_name" \
      --region=$REGION \
      --network-endpoint-type=serverless \
      --app-engine-service="$service"
  else
    # NEG exists - check if it points to the correct service
    # For serverless NEGs, the App Engine service is in the 'appEngineUrlMask' field
    # The field contains either a URL mask pattern or the literal service name
    NEG_JSON=$(gcloud compute network-endpoint-groups describe "$neg_name" \
      --region=$REGION --format="json" 2>/dev/null)
    
    CURRENT_NEG_SERVICE=$(echo "$NEG_JSON" | \
      python3 -c "
import sys, json
d = json.load(sys.stdin)
svc = ''
# Check appEngine structure (for App Engine services)
if 'appEngine' in d:
    svc = d['appEngine'].get('service', '')
# Fallback: check appEngineUrlMask (older format)
if not svc:
    svc = d.get('appEngineUrlMask', '')
# Check cloudRun structure
if not svc:
    svc = d.get('cloudRun', {}).get('service', '')
# Check cloudFunction structure
if not svc:
    svc = d.get('cloudFunction', {}).get('function', '')
print(svc)
" 2>/dev/null || echo "")
    
    if [[ -z "$CURRENT_NEG_SERVICE" ]]; then
      # Could not determine current service - show debug info and skip update
      echo "[WARNING] Could not determine current App Engine service for NEG '$neg_name'"
      echo "[DEBUG] NEG JSON fields:"
      echo "$NEG_JSON" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  appEngine: {d.get('appEngine', '<not set>')}\")
print(f\"  appEngineUrlMask: {d.get('appEngineUrlMask', '<not set>')}\")
print(f\"  cloudRun: {d.get('cloudRun', '<not set>')}\")
print(f\"  cloudFunction: {d.get('cloudFunction', '<not set>')}\")
print(f\"  All top-level keys: {list(d.keys())}\")
" 2>/dev/null || true
      echo "Skipping NEG update - please verify manually"
    elif [[ "$CURRENT_NEG_SERVICE" != "$service" ]]; then
      echo "Serverless NEG '$neg_name' exists but points to '$CURRENT_NEG_SERVICE' instead of '$service'"
      echo "Recreating NEG with correct service..."
      
      # Must remove NEG from backend service before deleting
      if gcloud compute backend-services describe "$backend_name" --global &>/dev/null; then
        echo "Removing NEG from backend service..."
        gcloud compute backend-services remove-backend "$backend_name" \
          --global \
          --network-endpoint-group="$neg_name" \
          --network-endpoint-group-region=$REGION 2>/dev/null || true
      fi
      
      # Delete and recreate the NEG
      echo "Deleting old NEG..."
      gcloud compute network-endpoint-groups delete "$neg_name" --region=$REGION --quiet
      
      echo "Creating new NEG with service: $service"
      gcloud compute network-endpoint-groups create "$neg_name" \
        --region=$REGION \
        --network-endpoint-type=serverless \
        --app-engine-service="$service"
      
      # Re-add NEG to backend service if it exists
      if gcloud compute backend-services describe "$backend_name" --global &>/dev/null; then
        echo "Re-adding NEG to backend service..."
        gcloud compute backend-services add-backend "$backend_name" \
          --global \
          --network-endpoint-group="$neg_name" \
          --network-endpoint-group-region=$REGION
      fi
    else
      echo "Serverless NEG '$neg_name' already exists with correct service"
    fi
  fi
  
  # 2. Create Backend Service if it doesn't exist
  if ! gcloud compute backend-services describe "$backend_name" --global &>/dev/null; then
    echo "Creating Backend Service: $backend_name"
    # Note: Don't specify --protocol for serverless NEGs (no port_name allowed)
    gcloud compute backend-services create "$backend_name" \
      --global \
      --load-balancing-scheme=EXTERNAL_MANAGED
    
    # Add NEG to backend service
    echo "Adding NEG to Backend Service..."
    gcloud compute backend-services add-backend "$backend_name" \
      --global \
      --network-endpoint-group="$neg_name" \
      --network-endpoint-group-region=$REGION
  else
    echo "Backend Service '$backend_name' already exists"
  fi
  
  # 3. Add/update host rule in URL map
  echo "Checking URL map host rule for: $host"
  
  # Check if host rule already exists and get its path matcher
  EXISTING_RULE=$(gcloud compute url-maps describe $URL_MAP_NAME --global \
    --format="json" 2>/dev/null | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
for rule in data.get('hostRules', []):
    if '$host' in rule.get('hosts', []):
        print(rule.get('pathMatcher', ''))
        break
" 2>/dev/null || echo "")

  if [[ -n "$EXISTING_RULE" ]]; then
    # Host rule exists - check if it points to the correct backend service
    CURRENT_BACKEND=$(gcloud compute url-maps describe $URL_MAP_NAME --global \
      --format="json" 2>/dev/null | \
      python3 -c "
import sys, json
data = json.load(sys.stdin)
for pm in data.get('pathMatchers', []):
    if pm.get('name') == '$EXISTING_RULE':
        # Extract just the backend service name from the full URL
        default_svc = pm.get('defaultService', '')
        print(default_svc.split('/')[-1] if default_svc else '')
        break
" 2>/dev/null || echo "")
    
    if [[ "$CURRENT_BACKEND" != "$backend_name" ]]; then
      echo "Host rule for '$host' exists but points to '$CURRENT_BACKEND' instead of '$backend_name'"
      echo "Updating path matcher to use correct backend service..."
      
      # Update the path matcher with the correct backend service
      # We need to remove and re-add because gcloud doesn't have a direct update for default-service
      gcloud compute url-maps remove-path-matcher $URL_MAP_NAME \
        --global \
        --path-matcher-name="$EXISTING_RULE"
      
      gcloud compute url-maps add-path-matcher $URL_MAP_NAME \
        --global \
        --path-matcher-name="$EXISTING_RULE" \
        --default-service="$backend_name" \
        --new-hosts="$host"
      
      echo "Updated host rule for '$host' to use '$backend_name'"
    else
      echo "Host rule for '$host' already exists with correct backend (pathMatcher: $EXISTING_RULE)"
    fi
  else
    # Create a path matcher name from the host
    PATH_MATCHER_NAME=$(echo "$host" | sed 's/[^a-zA-Z0-9]/-/g' | sed 's/--*/-/g')
    
    echo "Adding path matcher: $PATH_MATCHER_NAME"
    gcloud compute url-maps add-path-matcher $URL_MAP_NAME \
      --global \
      --path-matcher-name="$PATH_MATCHER_NAME" \
      --default-service="$backend_name" \
      --new-hosts="$host"
  fi
}

# Parse and process all services from config.yaml
parse_lb_routes

# =============================================================================
# Part 2c: Create/Update DNS Records
# =============================================================================
echo ""
echo "=== Managing DNS Records ==="

# Check if DNS zone is configured
if [[ -z "$DNS_MANAGED_ZONE" ]]; then
  echo "[INFO] DNS_MANAGED_ZONE not set - skipping DNS record management"
  echo "[INFO] To enable automatic DNS management, set DNS_MANAGED_ZONE in your *.env file"
else
  # Get the static IP for the Load Balancer
  STATIC_IP_NAME="empower-lb-ip"
  LB_IP=$(gcloud compute addresses describe $STATIC_IP_NAME --global --format='get(address)' 2>/dev/null || echo "")
  
  if [[ -z "$LB_IP" ]]; then
    echo "[WARNING] Could not get LB static IP ($STATIC_IP_NAME) - skipping DNS management"
    echo "[INFO] Run first_time_setup.sh first to create the static IP"
  else
    echo "Load Balancer IP: $LB_IP"
    echo "DNS Zone: $DNS_MANAGED_ZONE"
    
    # Create DNS records for each host
    for host in $(get_all_hosts); do
      echo ""
      echo "--- DNS: $host ---"
      
      # Check if A record already exists
      EXISTING_A=$(gcloud dns record-sets describe "$host." \
        --zone="$DNS_MANAGED_ZONE" \
        --type=A \
        --format="value(rrdatas[0])" 2>/dev/null || echo "")
      
      # Check if CNAME record exists (need to delete before creating A record)
      EXISTING_CNAME=$(gcloud dns record-sets describe "$host." \
        --zone="$DNS_MANAGED_ZONE" \
        --type=CNAME \
        --format="value(rrdatas[0])" 2>/dev/null || echo "")
      
      if [[ -n "$EXISTING_CNAME" ]]; then
        echo "Found existing CNAME record: $host -> $EXISTING_CNAME"
        echo "Deleting CNAME to replace with A record for Load Balancer..."
        # Get TTL of existing record for deletion
        CNAME_TTL=$(gcloud dns record-sets describe "$host." \
          --zone="$DNS_MANAGED_ZONE" \
          --type=CNAME \
          --format="value(ttl)" 2>/dev/null || echo "300")
        gcloud dns record-sets delete "$host." \
          --zone="$DNS_MANAGED_ZONE" \
          --type=CNAME \
          --quiet
      fi
      
      if [[ -n "$EXISTING_A" ]]; then
        if [[ "$EXISTING_A" == "$LB_IP" ]]; then
          echo "DNS A record already exists and points to correct IP ($LB_IP)"
        else
          echo "DNS A record exists but points to $EXISTING_A (expected $LB_IP)"
          echo "Updating DNS record..."
          gcloud dns record-sets update "$host." \
            --zone="$DNS_MANAGED_ZONE" \
            --type=A \
            --ttl=300 \
            --rrdatas="$LB_IP"
        fi
      else
        echo "Creating DNS A record: $host -> $LB_IP"
        gcloud dns record-sets create "$host." \
          --zone="$DNS_MANAGED_ZONE" \
          --type=A \
          --ttl=300 \
          --rrdatas="$LB_IP"
      fi
    done
    
    # =============================================================================
    # Part 2d: Create/Update Custom DNS Records (from dns_records section)
    # =============================================================================
    echo ""
    echo "=== Managing Custom DNS Records ==="
    
    parse_custom_dns_records() {
      local in_dns_records=false
      local current_name=""
      local current_type=""
      local current_ttl=""
      local current_value=""
      
      while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// /}" ]] && continue
        
        # Check if we're in dns_records section
        if [[ "$line" =~ ^dns_records: ]]; then
          in_dns_records=true
          continue
        fi
        
        # Exit dns_records section if we hit another top-level key
        if [[ "$in_dns_records" == true ]] && [[ "$line" =~ ^[a-z_]+: ]] && [[ ! "$line" =~ ^[[:space:]] ]]; then
          # Process last record before exiting
          if [[ -n "$current_name" && -n "$current_type" && -n "$current_value" ]]; then
            create_custom_dns_record "$current_name" "$current_type" "${current_ttl:-300}" "$current_value"
          fi
          in_dns_records=false
          continue
        fi
        
        if [[ "$in_dns_records" == true ]]; then
          # New record entry (starts with "- name:")
          if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*\"?([^\"]*)\"? ]]; then
            # Process previous record if exists
            if [[ -n "$current_name" && -n "$current_type" && -n "$current_value" ]]; then
              create_custom_dns_record "$current_name" "$current_type" "${current_ttl:-300}" "$current_value"
            fi
            current_name="${BASH_REMATCH[1]}"
            current_type=""
            current_ttl=""
            current_value=""
          elif [[ "$line" =~ [[:space:]]*type:[[:space:]]*(.+) ]]; then
            current_type="${BASH_REMATCH[1]}"
          elif [[ "$line" =~ [[:space:]]*ttl:[[:space:]]*(.+) ]]; then
            current_ttl="${BASH_REMATCH[1]}"
          elif [[ "$line" =~ [[:space:]]*value:[[:space:]]*\"?([^\"]*)\"? ]]; then
            current_value="${BASH_REMATCH[1]}"
          fi
        fi
      done < config.yaml
      
      # Process last record
      if [[ -n "$current_name" && -n "$current_type" && -n "$current_value" ]]; then
        create_custom_dns_record "$current_name" "$current_type" "${current_ttl:-300}" "$current_value"
      fi
    }
    
    create_custom_dns_record() {
      local name="$1"
      local type="$2"
      local ttl="$3"
      local value="$4"
      
      echo ""
      echo "--- Custom DNS: $name ($type) ---"
      
      # Ensure name ends with a dot for DNS
      [[ "$name" != *. ]] && name="${name}."
      # Ensure CNAME value ends with a dot
      if [[ "$type" == "CNAME" ]] && [[ "$value" != *. ]]; then
        value="${value}."
      fi
      
      # Check if record already exists
      EXISTING_VALUE=$(gcloud dns record-sets describe "$name" \
        --zone="$DNS_MANAGED_ZONE" \
        --type="$type" \
        --format="value(rrdatas[0])" 2>/dev/null || echo "")
      
      EXISTING_TTL=$(gcloud dns record-sets describe "$name" \
        --zone="$DNS_MANAGED_ZONE" \
        --type="$type" \
        --format="value(ttl)" 2>/dev/null || echo "")
      
      if [[ -n "$EXISTING_VALUE" ]]; then
        if [[ "$EXISTING_VALUE" == "$value" ]] && [[ "$EXISTING_TTL" == "$ttl" ]]; then
          echo "DNS $type record already exists and matches: $name -> $value (TTL: $ttl)"
        else
          echo "DNS $type record exists but differs:"
          echo "  Current: $EXISTING_VALUE (TTL: $EXISTING_TTL)"
          echo "  Desired: $value (TTL: $ttl)"
          echo "Updating DNS record..."
          gcloud dns record-sets update "$name" \
            --zone="$DNS_MANAGED_ZONE" \
            --type="$type" \
            --ttl="$ttl" \
            --rrdatas="$value"
        fi
      else
        # Check if there's a conflicting record type (e.g., A record when adding CNAME)
        if [[ "$type" == "CNAME" ]]; then
          CONFLICTING_A=$(gcloud dns record-sets describe "$name" \
            --zone="$DNS_MANAGED_ZONE" \
            --type=A \
            --format="value(rrdatas[0])" 2>/dev/null || echo "")
          if [[ -n "$CONFLICTING_A" ]]; then
            echo "Found conflicting A record: $name -> $CONFLICTING_A"
            echo "Deleting A record to create CNAME..."
            gcloud dns record-sets delete "$name" \
              --zone="$DNS_MANAGED_ZONE" \
              --type=A \
              --quiet
          fi
        elif [[ "$type" == "A" ]]; then
          CONFLICTING_CNAME=$(gcloud dns record-sets describe "$name" \
            --zone="$DNS_MANAGED_ZONE" \
            --type=CNAME \
            --format="value(rrdatas[0])" 2>/dev/null || echo "")
          if [[ -n "$CONFLICTING_CNAME" ]]; then
            echo "Found conflicting CNAME record: $name -> $CONFLICTING_CNAME"
            echo "Deleting CNAME record to create A record..."
            gcloud dns record-sets delete "$name" \
              --zone="$DNS_MANAGED_ZONE" \
              --type=CNAME \
              --quiet
          fi
        fi
        
        echo "Creating DNS $type record: $name -> $value (TTL: $ttl)"
        gcloud dns record-sets create "$name" \
          --zone="$DNS_MANAGED_ZONE" \
          --type="$type" \
          --ttl="$ttl" \
          --rrdatas="$value"
      fi
    }
    
    # Parse and process custom DNS records
    if grep -q "^dns_records:" config.yaml 2>/dev/null; then
      parse_custom_dns_records
    else
      echo "No custom DNS records defined in config.yaml"
    fi
  fi
fi

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To verify the configuration:"
echo "  gcloud compute url-maps describe $URL_MAP_NAME --global"
echo ""
echo "To check SSL certificate status:"
echo "  gcloud compute ssl-certificates list --global"
echo ""
echo "To check DNS records:"
echo "  gcloud dns record-sets list --zone=$DNS_MANAGED_ZONE"
echo ""
