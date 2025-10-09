#!/usr/bin/env python3
"""
Script to generate a static web page showing rustedbytes projects.
Fetches information from GitHub repositories and crates.io.
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional

# Configuration
GITHUB_USER = "mad4j"
REPO_PREFIX = "rustedbytes"
GITHUB_API_BASE = "https://api.github.com"
CRATES_API_BASE = "https://crates.io/api/v1"


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.environ.get("GITHUB_TOKEN")


def fetch_repos_with_prefix(user: str, prefix: str, token: Optional[str] = None) -> List[Dict]:
    """Fetch all repositories for a user that match the prefix."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    repos = []
    page = 1
    
    while True:
        url = f"{GITHUB_API_BASE}/users/{user}/repos"
        params = {"page": page, "per_page": 100, "type": "all"}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        page_repos = response.json()
        if not page_repos:
            break
            
        # Filter repos with the prefix
        filtered = [repo for repo in page_repos if repo["name"].startswith(prefix)]
        repos.extend(filtered)
        
        page += 1
        
        # Break if we got less than 100 repos (last page)
        if len(page_repos) < 100:
            break
    
    return repos


def get_latest_release(owner: str, repo: str, token: Optional[str] = None) -> Optional[Dict]:
    """Get the latest release for a repository."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases/latest"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching release for {repo}: {e}", file=sys.stderr)
    
    return None


def get_crates_info(crate_name: str) -> Optional[Dict]:
    """Get information from crates.io for a crate."""
    url = f"{CRATES_API_BASE}/crates/{crate_name}"
    headers = {"User-Agent": "rustedbytes-page-generator"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching crate info for {crate_name}: {e}", file=sys.stderr)
    
    return None


def format_date(date_str: str) -> str:
    """Format ISO date string to a readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str


def generate_markdown(projects: List[Dict]) -> str:
    """Generate Jekyll-compatible Markdown page from project data."""
    
    # Sort projects by name
    projects = sorted(projects, key=lambda x: x["name"])
    
    # Generate project rows in Markdown table format
    project_rows = []
    for project in projects:
        name = project["name"]
        description = project.get("description", "No description available")
        html_url = project["html_url"]
        
        # Latest GitHub release
        github_release = project.get("latest_release")
        if github_release:
            release_tag = github_release.get("tag_name", "N/A")
            release_date = format_date(github_release.get("published_at", ""))
            release_url = github_release.get("html_url", html_url)
            github_release_cell = f'[{release_tag}]({release_url}) ({release_date})'
        else:
            github_release_cell = '_No releases_'
        
        # Crates.io info
        crates_info = project.get("crates_info")
        if crates_info:
            crate = crates_info.get("crate", {})
            latest_version = crate.get("newest_version", "N/A")
            crate_name = crate.get("name", name)
            crates_url = f"https://crates.io/crates/{crate_name}"
            crates_cell = f'[{latest_version}]({crates_url})'
        else:
            crates_cell = '_Not published_'
        
        # Escape pipe characters in description to avoid breaking table
        description = description.replace("|", "\\|") if description else "No description available"
        
        project_rows.append(f'| [**{name}**]({html_url}) | {description} | {github_release_cell} | {crates_cell} |')
    
    projects_table = "\n".join(project_rows)
    
    # Generate Jekyll front matter and Markdown content
    markdown = f"""---
layout: default
title: Rustedbytes Projects
---

# 🦀 Rustedbytes Projects

A collection of Rust-based projects

---

Welcome to the Rustedbytes project collection! This page provides an overview of all projects in the rustedbytes ecosystem, including their latest releases on GitHub and crates.io availability.

Each project is built with Rust, focusing on performance, reliability, and developer experience.

## Projects

| Project | Description | Latest Release | Crates.io |
|---------|-------------|----------------|-----------|
{projects_table}

---

*Generated from [@{GITHUB_USER}](https://github.com/{GITHUB_USER}) GitHub repositories*

*Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}*
"""
    return markdown


def main():
    """Main function to generate the static page."""
    print("Starting page generation...")
    
    # Get GitHub token
    token = get_github_token()
    if not token:
        print("Warning: No GITHUB_TOKEN found. API rate limits may apply.", file=sys.stderr)
    
    # Fetch repositories
    print(f"Fetching repositories for user '{GITHUB_USER}' with prefix '{REPO_PREFIX}'...")
    repos = fetch_repos_with_prefix(GITHUB_USER, REPO_PREFIX, token)
    print(f"Found {len(repos)} repositories")
    
    # Enrich with release and crates.io information
    projects = []
    for repo in repos:
        print(f"Processing {repo['name']}...")
        
        project_data = {
            "name": repo["name"],
            "description": repo["description"],
            "html_url": repo["html_url"],
        }
        
        # Get latest release
        latest_release = get_latest_release(GITHUB_USER, repo["name"], token)
        if latest_release:
            project_data["latest_release"] = latest_release
        
        # Try to get crates.io info (use repo name as crate name)
        crates_info = get_crates_info(repo["name"])
        if crates_info:
            project_data["crates_info"] = crates_info
        
        projects.append(project_data)
    
    # Generate Markdown
    print("Generating Markdown...")
    markdown = generate_markdown(projects)
    
    # Write to file
    output_path = "index.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"Page generated successfully: {output_path}")
    print(f"Total projects: {len(projects)}")


if __name__ == "__main__":
    main()
