#!python3
import argparse
import http.client
import json
from urllib.parse import urlparse

SENTRY_API_BASE = "https://sentry.io/api/0"


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
        projects.extend([proj["slug"] for proj in data])
        
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


def main():
    parser = argparse.ArgumentParser(description="Delete all Sentry projects in an organization except those excluded.")
    parser.add_argument("org_slug", help="Sentry organization slug")
    parser.add_argument("auth_token", help="Sentry API auth token")
    parser.add_argument("--exclude", nargs="+", required=True, help="List of project slugs to keep")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    
    args = parser.parse_args()
    
    projects = get_projects(args.org_slug, args.auth_token)
    
    for project in projects:
        if project not in args.exclude:
            delete_project(args.org_slug, project, args.auth_token, args.dry_run)
        else:
            print(f"Skipping excluded project: {project}")


if __name__ == "__main__":
    main()
