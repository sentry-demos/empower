#!python3
import argparse
import http.client
import json
from urllib.parse import urlparse
import sys
from datetime import datetime, timezone

SENTRY_API_BASE = "https://sentry.io/api/0"
MINIMUM_EXCLUDED_COUNT = 19
ACTIVE_PROJECT_THRESHOLD_EVENTS_24H = 1000  # Adjust this threshold as needed
PROJECT_AGE_THRESHOLD_DAYS = 14
STATS_CATEGORIES = [
    'error',
    'transaction',
    'replay',
    'profile',
    'monitor',
    'span'
]

def get_projects(org_slug, auth_token):
    projects = []
    url = f"{SENTRY_API_BASE}/organizations/{org_slug}/projects/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    while url:
        parsed_url = urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc)
        conn.request("GET", parsed_url.path + ("?" + parsed_url.query if parsed_url.query else ""), headers=headers)
        response = conn.getresponse()
        
        if response.status != 200:
            raise Exception(f"Failed to fetch projects: {response.read().decode()}")
        
        data = json.loads(response.read().decode())
        projects.extend([{
            "slug": proj["slug"], 
            "id": proj["id"],
            "dateCreated": proj["dateCreated"]
        } for proj in data])
        
        # Handle pagination
        link_header = response.getheader("Link", "")
        next_url = None
        for link in link_header.split(","):
            parts = link.split(";")
            if len(parts) < 2:
                continue
            url_part = parts[0].strip()[1:-1]
            rel_part = parts[1].strip()
            
            if rel_part == 'rel="next"' and 'results="true"' in link:
                next_url = url_part
                break
        
        url = next_url
    
    return projects


def get_project_activity(org_slug, project_id, auth_token):
    total_events = 0
    
    for category in STATS_CATEGORIES:
        url = f"{SENTRY_API_BASE}/organizations/{org_slug}/stats_v2/?project={project_id}&field=sum(quantity)&interval=24h&category={category}&statsPeriod=24h"
        parsed_url = urlparse(url)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        conn = http.client.HTTPSConnection(parsed_url.netloc)
        conn.request("GET", parsed_url.path + "?" + parsed_url.query, headers=headers)
        response = conn.getresponse()
        
        if response.status != 200:
            print(f"Warning: Failed to fetch stats for category {category}: {response.read().decode()}")
            continue
            
        data = json.loads(response.read().decode())
        if data["groups"] and data["groups"][0]["series"]["sum(quantity)"]:
            # Get the last (most recent) interval's value
            total_events += data["groups"][0]["series"]["sum(quantity)"][-1]
    
    return total_events


def delete_project(org_slug, project_slug, auth_token, dry_run):
    url = f"{SENTRY_API_BASE}/projects/{org_slug}/{project_slug}/"
    parsed_url = urlparse(url)
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    if dry_run:
        print(f"[Dry Run] Would delete project: {project_slug}")
    else:
        conn = http.client.HTTPSConnection(parsed_url.netloc)
        conn.request("DELETE", parsed_url.path, headers=headers)
        response = conn.getresponse()
        
        if response.status == 204:
            print(f"Deleted project: {project_slug}")
        else:
            print(f"Failed to delete {project_slug}: {response.read().decode()}")


def get_project_age_days(date_created):
    created_date = datetime.fromisoformat(date_created.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    return (now - created_date).days


def main():
    parser = argparse.ArgumentParser(description="Delete all Sentry projects in an organization except those excluded.")
    parser.add_argument("org_slug", help="Sentry organization slug")
    parser.add_argument("auth_token", help="Sentry API auth token")
    parser.add_argument("--exclude", nargs="+", required=True, help="List of project slugs to keep")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    
    args = parser.parse_args()
    
    projects = get_projects(args.org_slug, args.auth_token)
    
    count_excluded = 0
    for project in projects:
        if project["slug"] in args.exclude:
            count_excluded += 1

    if count_excluded < MINIMUM_EXCLUDED_COUNT:
        print(f"ERROR: At least {MINIMUM_EXCLUDED_COUNT} existing projects must be excluded. Excluded projects: {count_excluded}")
        sys.exit(1)

    
    count_skipped = 0
    count_deleted = 0
    for project in projects:
        if project["slug"] not in args.exclude:
            # Check project age before proceeding
            project_age = get_project_age_days(project["dateCreated"])
            if project_age > PROJECT_AGE_THRESHOLD_DAYS:
                print(f"ERROR: Project {project['slug']} is {project_age} days old (older than {PROJECT_AGE_THRESHOLD_DAYS} days threshold)")
                print("Aborting deletion to prevent data loss")
                sys.exit(1)

            # Check project activity before deletion
            event_count = get_project_activity(args.org_slug, project["id"], args.auth_token)
            if event_count > ACTIVE_PROJECT_THRESHOLD_EVENTS_24H:
                print(f"ERROR: Active project {project['slug']} found with {event_count} events in last 24h")
                print("Aborting deletion to prevent data loss")
                sys.exit(1)
                
            delete_project(args.org_slug, project["slug"], args.auth_token, args.dry_run)
            count_deleted += 1
        else:
            count_skipped += 1
            print(f"Skipping excluded project: {project['slug']}")

    print(f"{'Would have deleted' if args.dry_run else 'Deleted'} {count_deleted} projects")
    print(f"Skipped {count_excluded} projects")  


if __name__ == "__main__":
    main()
