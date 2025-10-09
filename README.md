# rustedbytes

Rustedbytes summary page - A collection of Rust-based projects.

## Overview

This repository automatically generates a static web page that showcases all projects in the rustedbytes ecosystem. The page is updated automatically via GitHub Actions and deployed to GitHub Pages.

## Features

- **Automatic Discovery**: Finds all GitHub repositories with the 'rustedbytes' prefix
- **Release Tracking**: Shows the latest release version and date from GitHub
- **Crates.io Integration**: Displays the latest published version on crates.io where available
- **Automatic Updates**: Runs daily to keep information fresh
- **Beautiful UI**: Modern, responsive design with a clean interface

## How It Works

1. A GitHub Actions workflow runs daily (or on-demand)
2. The Python script fetches all repositories with the 'rustedbytes' prefix
3. For each repository:
   - Retrieves the latest GitHub release
   - Checks crates.io for published versions
4. Generates a static HTML page with all the information
5. Deploys to GitHub Pages

## Manual Trigger

You can manually trigger the page generation from the GitHub Actions tab by running the "Generate Static Page" workflow.

## Local Development

To test the page generation locally:

```bash
# Install dependencies
pip install requests

# Set your GitHub token (optional, but recommended to avoid rate limits)
export GITHUB_TOKEN=your_token_here

# Run the script
python3 scripts/generate_page.py
```

The generated page will be in `docs/index.html`.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
