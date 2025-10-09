# rustedbytes

Rustedbytes summary page - A collection of Rust-based projects.

## Overview

This repository automatically generates a static web page that showcases all projects in the rustedbytes ecosystem. The page is updated automatically via GitHub Actions and deployed to GitHub Pages.

## Features

- **Automatic Discovery**: Finds all GitHub repositories with the 'rustedbytes' prefix
- **Release Tracking**: Shows the latest release version and date from GitHub
- **Crates.io Integration**: Displays the latest published version on crates.io where available
- **Automatic Updates**: Runs daily to keep information fresh
- **Version Controlled**: Generated content is committed to the main branch for tracking and review
- **Beautiful UI**: Modern, responsive design with a clean interface
- **Configurable Themes**: Choose from multiple layouts or create custom themes via `page_config.yml`

## How It Works

1. A GitHub Actions workflow runs daily (or on-demand)
2. The Python script fetches all repositories with the 'rustedbytes' prefix
3. For each repository:
   - Retrieves the latest GitHub release
   - Checks crates.io for published versions
4. Generates a Jekyll-compatible Markdown page with all the information
5. Commits and pushes the generated `index.md` to the main branch
6. GitHub Pages processes the Markdown using Jekyll
7. Deploys the generated site to GitHub Pages

## Manual Trigger

You can manually trigger the page generation from the GitHub Actions tab by running the "Generate Static Page with Jekyll" workflow.

## Theme Customization

The page design is configurable via the `page_config.yml` file:

```yaml
# Choose from available layouts: 'default' or 'minimal'
layout: default

# Customize page content
styling:
  page_title: "Rustedbytes Projects"
  page_description: "A collection of Rust-based projects"
  header_emoji: "🦀"
```

Available layouts:
- **default**: Modern gradient design with purple/blue theme
- **minimal**: Terminal-style dark theme with green accents

You can also create custom layouts by adding new HTML files to the `_layouts/` directory. See [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md) for detailed customization instructions.

## Local Development

To test the page generation locally:

```bash
# Install dependencies
pip install requests pyyaml

# Set your GitHub token (optional, but recommended to avoid rate limits)
export GITHUB_TOKEN=your_token_here

# Run the script
python3 scripts/generate_page.py
```

The generated page will be in `index.md` (a Jekyll-compatible Markdown file).

To preview the site locally with Jekyll:

```bash
# Install Jekyll (if not already installed)
gem install bundler jekyll

# Serve the site locally
jekyll serve

# Open http://localhost:4000 in your browser
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
