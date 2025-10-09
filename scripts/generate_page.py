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


def generate_html(projects: List[Dict]) -> str:
    """Generate HTML page from project data."""
    
    # Sort projects by name
    projects = sorted(projects, key=lambda x: x["name"])
    
    # Generate project rows
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
            github_release_cell = f'<a href="{release_url}">{release_tag}</a> ({release_date})'
        else:
            github_release_cell = '<span class="no-data">No releases</span>'
        
        # Crates.io info
        crates_info = project.get("crates_info")
        if crates_info:
            crate = crates_info.get("crate", {})
            latest_version = crate.get("newest_version", "N/A")
            crate_name = crate.get("name", name)
            crates_url = f"https://crates.io/crates/{crate_name}"
            crates_cell = f'<a href="{crates_url}">{latest_version}</a>'
        else:
            crates_cell = '<span class="no-data">Not published</span>'
        
        project_rows.append(f"""
        <tr>
            <td><a href="{html_url}"><strong>{name}</strong></a></td>
            <td>{description}</td>
            <td>{github_release_cell}</td>
            <td>{crates_cell}</td>
        </tr>
        """)
    
    projects_html = "\n".join(project_rows)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rustedbytes Projects</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }}
        
        header p {{
            font-size: 1.2rem;
            opacity: 0.95;
        }}
        
        .intro {{
            padding: 2rem;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .intro p {{
            font-size: 1.1rem;
            color: #495057;
            margin-bottom: 1rem;
        }}
        
        .content {{
            padding: 2rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #5568d3;
        }}
        
        td {{
            padding: 1rem;
            border-bottom: 1px solid #e9ecef;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        a {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .no-data {{
            color: #6c757d;
            font-style: italic;
        }}
        
        footer {{
            padding: 2rem;
            text-align: center;
            color: #6c757d;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }}
        
        footer a {{
            color: #667eea;
            font-weight: 600;
        }}
        
        .update-time {{
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 0.5rem;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            header h1 {{
                font-size: 1.8rem;
            }}
            
            table {{
                font-size: 0.9rem;
            }}
            
            th, td {{
                padding: 0.75rem 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦀 Rustedbytes Projects</h1>
            <p>A collection of Rust-based projects</p>
        </header>
        
        <div class="intro">
            <p>
                Welcome to the Rustedbytes project collection! This page provides an overview of all 
                projects in the rustedbytes ecosystem, including their latest releases on GitHub and 
                crates.io availability.
            </p>
            <p>
                Each project is built with Rust, focusing on performance, reliability, and developer experience.
            </p>
        </div>
        
        <div class="content">
            <h2>Projects</h2>
            <table>
                <thead>
                    <tr>
                        <th>Project</th>
                        <th>Description</th>
                        <th>Latest Release</th>
                        <th>Crates.io</th>
                    </tr>
                </thead>
                <tbody>
                    {projects_html}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>
                Generated from <a href="https://github.com/{GITHUB_USER}" target="_blank">@{GITHUB_USER}</a> GitHub repositories
            </p>
            <p class="update-time">Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        </footer>
    </div>
</body>
</html>
"""
    return html


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
    
    # Generate HTML
    print("Generating HTML...")
    html = generate_html(projects)
    
    # Write to file
    output_path = "docs/index.html"
    os.makedirs("docs", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Page generated successfully: {output_path}")
    print(f"Total projects: {len(projects)}")


if __name__ == "__main__":
    main()
