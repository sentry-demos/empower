# DNS and Routing Configuration (`_dns`)

This project manages routing for the Empower Plant demo applications. It supports two routing mechanisms:

1. **App Engine Dispatch Rules** (`dispatch.yml`) - Legacy, limited to 20 rules
2. **Load Balancer with Serverless NEG** (`config.yaml.template`) - New, unlimited host rules

## Problem: Dispatch Rule Limit

App Engine has a hard limit of 20 dispatch rules. As we add more services and staging environments, we've hit this limit.

## Solution: External Load Balancer with Serverless NEGs

Instead of using dispatch.yml, we can:
1. Put a Global External Application Load Balancer in front of App Engine
2. Create a Serverless Network Endpoint Group (NEG) for each App Engine service
3. Use URL Maps to route traffic based on hostname (unlimited host rules!)

## Files

| File | Purpose |
|------|---------|
| `dispatch.yml` | Legacy App Engine dispatch rules (for non-migrated services) |
| `config.yaml.template` | Load Balancer configuration template (parameterized by environment) |
| `deploy_project.sh` | Deployment script called by `./deploy` |
| `first_time_setup.sh` | One-time setup for base LB infrastructure |

## Environment Variables

The template uses per-service variables defined in `*.env` files:

| Variable Pattern | Example (production) | Example (staging) |
|------------------|---------------------|-------------------|
| `${<PROJ>_SUBDOMAIN}` | `GO_SUBDOMAIN=go` | `GO_SUBDOMAIN=staging-go` |
| `${<PROJ>_APP_ENGINE_SERVICE}` | `GO_APP_ENGINE_SERVICE=go` | `GO_APP_ENGINE_SERVICE=staging-go` |
| `${DOMAIN}` | `empower-plant.com` | `empower-plant.com` |
| `${GCP_REGION}` | `us-central1` | `us-central1` |

### Template Example

```yaml
services:
  - host: "${GO_SUBDOMAIN}.${DOMAIN}"
    service: ${GO_APP_ENGINE_SERVICE}
```

Only `host` and `service` are required. The `neg_name` and `backend_service` are automatically derived from the subdomain:
- `go.empower-plant.com` → `neg-go`, `backend-go`
- `staging-go.empower-plant.com` → `neg-staging-go`, `backend-staging-go`

### Custom DNS Records

You can also define custom DNS records that don't route through the Load Balancer (e.g., for external services like Vercel, Netlify, etc.):

```yaml
dns_records:
  - name: "nextjs.${DOMAIN}"
    type: CNAME
    ttl: 300
    value: "cname.vercel-dns.com."

  - name: "mail.${DOMAIN}"
    type: MX
    ttl: 300
    value: "10 mail.example.com."
```

Supported record types: `A`, `CNAME`, `TXT`, `MX`, etc.

The script will:
- Skip records that already exist with identical values
- Update records if the value or TTL differs
- Handle conflicts (e.g., delete existing A record before creating CNAME)

## One-Time Setup

### Step 1: Create Base LB Infrastructure

Run this once to create shared infrastructure:

```bash
cd _dns
chmod +x first_time_setup.sh
./first_time_setup.sh

# Or dry-run first:
./first_time_setup.sh --dry-run
```

This creates:
- Global static IP address (`empower-lb-ip`)
- Default backend service
- Empty URL map (`empower-url-map`)
- Target HTTPS proxy with placeholder certificate
- Forwarding rule (`empower-forwarding-rule`)

### Step 2: Get the Static IP

```bash
gcloud compute addresses describe empower-lb-ip --global --format='get(address)'
```

Save this IP for DNS configuration. Store it in GCP Secret Manager as `LB_STATIC_IP`.

## Deploying

### Deploy Production

```bash
./deploy --env=production _dns
```

### Deploy Staging

```bash
./deploy --env=staging _dns
```

Each deployment:
1. Processes `config.yaml.template` with environment-specific variables
2. Updates SSL certificate to include any new domains (additive)
3. Creates NEGs, Backend Services, and URL Map rules for this environment's services
4. Deploys filtered `dispatch.yml` (excluding LB-managed hosts)

## DNS Configuration

### Automatic DNS Management (Recommended)

The deploy script can automatically create/update DNS A records in Google Cloud DNS. Set `DNS_MANAGED_ZONE` in your `*.env` files:

```
DNS_MANAGED_ZONE=empower-plant-com
```

Then run the deploy - DNS records will be created automatically:

```bash
./deploy --env=staging _dns
```

### Manual DNS Configuration

If you prefer to manage DNS manually, or use a different DNS provider:

```bash
STATIC_IP=$(gcloud compute addresses describe empower-lb-ip --global --format='get(address)')

# For each domain in config.yaml.template:
gcloud dns record-sets create go.empower-plant.com. \
  --zone=empower-plant-com --type=A --ttl=300 --rrdatas=$STATIC_IP

gcloud dns record-sets create staging-go.empower-plant.com. \
  --zone=empower-plant-com --type=A --ttl=300 --rrdatas=$STATIC_IP
```

## Adding New Services

### Step 1: Add Variables to `*.env` Files

In `production.env`:
```
NEWSERVICE_SUBDOMAIN=newservice
NEWSERVICE_APP_ENGINE_SERVICE=newservice
```

In `staging.env`:
```
NEWSERVICE_SUBDOMAIN=staging-newservice
NEWSERVICE_APP_ENGINE_SERVICE=staging-newservice
```

### Step 2: Add to `config.yaml.template`

```yaml
services:
  # Existing services...
  
  - host: "${NEWSERVICE_SUBDOMAIN}.${DOMAIN}"
    service: ${NEWSERVICE_APP_ENGINE_SERVICE}
```

### Step 3: Remove from `dispatch.yml`

Remove entries for both production and staging.

### Step 4: Deploy Both Environments

```bash
./deploy --env=production _dns
./deploy --env=staging _dns
```

### Step 5: Update DNS

Add A records for the new domains pointing to the static IP.

## Architecture

```
                    ┌─────────────────┐
                    │   Google DNS    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Static IP     │
                    │  (shared)       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  HTTPS Proxy    │
                    │  (shared)       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    URL Map      │
                    │  (shared)       │
                    └────────┬────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
         ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│  PRODUCTION     │                     │    STAGING      │
├─────────────────┤                     ├─────────────────┤
│ backend-go      │                     │ backend-staging │
│    ↓            │                     │    -go          │
│ neg-go          │                     │    ↓            │
│    ↓            │                     │ neg-staging-go  │
│ App Engine: go  │                     │    ↓            │
└─────────────────┘                     │ App Engine:     │
                                        │   staging-go    │
                                        └─────────────────┘
```

## Troubleshooting

### Check URL Map Configuration

```bash
gcloud compute url-maps describe empower-url-map --global
```

### Check SSL Certificate Status

```bash
gcloud compute ssl-certificates list --global
gcloud compute ssl-certificates describe <cert-name> --global --format="yaml(managed)"
```

### Check Backend Service Health

```bash
gcloud compute backend-services get-health <backend-name> --global
```

### Common Issues

1. **SSL certificate stuck in PROVISIONING**
   - Ensure DNS A records point to the LB static IP
   - Wait up to 24 hours after DNS update

2. **502 Bad Gateway**
   - Check if App Engine service is deployed and healthy
   - Verify NEG points to correct service

3. **404 Not Found**  
   - Verify host rule exists in URL map
   - Ensure request uses HTTPS
