#!/usr/bin/env python3
"""
Script to generate a static web page showing rustedbytes projects.
Fetches information from GitHub repositories and crates.io.
"""

import os
import sys
import json
import requests
import yaml
from datetime import datetime
from typing import List, Dict, Optional

# Configuration
GITHUB_USER = "mad4j"
REPO_PREFIX = "rustedbytes"
GITHUB_API_BASE = "https://api.github.com"
CRATES_API_BASE = "https://crates.io/api/v1"

# Default page configuration
DEFAULT_PAGE_CONFIG = {
    "layout": "default",
    "theme": "minima",
    "styling": {
        "page_title": "Rustedbytes Projects",
        "page_description": "A collection of Rust-based projects",
        "header_emoji": "🦀"
    }
}


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.environ.get("GITHUB_TOKEN")


def load_page_config(config_path: str = "page_config.yml") -> Dict:
    """Load page configuration from YAML file or environment variables.
    
    Environment variables take precedence over config file:
    - PAGE_LAYOUT: Override the layout setting
    - PAGE_THEME: Override the theme setting
    - PAGE_TITLE: Override the page title
    """
    config = DEFAULT_PAGE_CONFIG.copy()
    
    # Try to load from YAML file
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    # Deep merge the configuration
                    config.update(file_config)
                    if "styling" in file_config and "styling" in config:
                        config["styling"].update(file_config["styling"])
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}", file=sys.stderr)
            print("Using default configuration.", file=sys.stderr)
    
    # Override with environment variables if present
    if os.environ.get("PAGE_LAYOUT"):
        config["layout"] = os.environ.get("PAGE_LAYOUT")
    if os.environ.get("PAGE_THEME"):
        config["theme"] = os.environ.get("PAGE_THEME")
    if os.environ.get("PAGE_TITLE"):
        config["styling"]["page_title"] = os.environ.get("PAGE_TITLE")
    
    return config


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


def generate_markdown(projects: List[Dict], config: Dict) -> str:
    """Generate Jekyll-compatible Markdown page from project data.
    
    Args:
        projects: List of project data dictionaries
        config: Page configuration dictionary
    """
    
    # Sort projects by name
    projects = sorted(projects, key=lambda x: x["name"])
    
    # Extract styling configuration
    styling = config.get("styling", {})
    page_title = styling.get("page_title", "Rustedbytes Projects")
    page_description = styling.get("page_description", "A collection of Rust-based projects")
    header_emoji = styling.get("header_emoji", "🦀")
    layout = config.get("layout", "default")
    
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
    
    # Build header with optional emoji
    header = f"# {header_emoji} {page_title}" if header_emoji else f"# {page_title}"
    
    # Generate Jekyll front matter and Markdown content
    markdown = f"""---
layout: {layout}
title: {page_title}
---

{header}

{page_description}

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
    
    # Load page configuration
    print("Loading page configuration...")
    config = load_page_config()
    print(f"Using layout: {config.get('layout')}")
    print(f"Using theme: {config.get('theme')}")
    
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
    markdown = generate_markdown(projects, config)
    
    # Write to file
    output_path = "index.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"Page generated successfully: {output_path}")
    print(f"Total projects: {len(projects)}")
    print(f"Layout used: {config.get('layout')}")
    print(f"Theme configured: {config.get('theme')}")


if __name__ == "__main__":
    main()
