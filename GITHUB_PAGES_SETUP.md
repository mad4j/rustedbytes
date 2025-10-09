# GitHub Pages Setup Instructions

This document explains how to enable GitHub Pages for the rustedbytes project.

## Prerequisites

- Repository must be public or you need a GitHub Pro account
- You must have admin access to the repository

## Steps to Enable GitHub Pages

1. **Go to Repository Settings**
   - Navigate to your repository on GitHub
   - Click on "Settings" tab

2. **Navigate to Pages Section**
   - In the left sidebar, scroll down and click on "Pages"

3. **Configure Source**
   - Under "Build and deployment" section
   - Source: Select "GitHub Actions"
   
4. **Verify Permissions**
   - Go to "Settings" → "Actions" → "General"
   - Scroll to "Workflow permissions"
   - Ensure "Read and write permissions" is selected
   - Save if changed

5. **Trigger the Workflow**
   - Go to "Actions" tab
   - Click on "Generate Static Page" workflow
   - Click "Run workflow" → "Run workflow" button
   
6. **Wait for Deployment**
   - The workflow will:
     1. Fetch all rustedbytes repositories
     2. Collect release information
     3. Check crates.io for versions
     4. Generate a Jekyll-compatible Markdown page
     5. Process the page with Jekyll
     6. Deploy to GitHub Pages
   - This usually takes 1-2 minutes

7. **Access Your Page**
   - Once deployed, your page will be available at:
     `https://mad4j.github.io/rustedbytes/`

## Automatic Updates

The workflow is configured to run:
- **Daily at midnight UTC** - Keeps information fresh
- **On every push to main** - Updates immediately after changes
- **Manually** - Via the Actions tab whenever you want

## Troubleshooting

### Workflow Fails

If the workflow fails:

1. **Check Permissions**
   - Settings → Actions → General → Workflow permissions
   - Ensure "Read and write permissions" is enabled

2. **Check Secrets**
   - The workflow uses `GITHUB_TOKEN` which is automatically provided
   - No manual secret configuration needed

3. **Check Logs**
   - Go to Actions tab
   - Click on the failed workflow run
   - Review the logs for specific error messages

### Page Not Loading

1. **Verify GitHub Pages is Enabled**
   - Settings → Pages
   - Source should be "GitHub Actions"

2. **Check Workflow Status**
   - Actions tab → Most recent "Generate Static Page" run
   - Should show green checkmark

3. **Wait a Few Minutes**
   - GitHub Pages deployment can take 1-5 minutes
   - Try clearing browser cache

### API Rate Limits

If you hit GitHub API rate limits:

1. **Use a Personal Access Token** (Optional)
   - Create a token: Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Scopes needed: `public_repo`
   - Add as repository secret named `GH_TOKEN`
   - Update workflow to use `${{ secrets.GH_TOKEN }}` instead of `${{ secrets.GITHUB_TOKEN }}`

## Customization

### Change Update Frequency

Edit `.github/workflows/generate-page.yml`:

```yaml
schedule:
  - cron: '0 0 * * *'  # Currently: Daily at midnight UTC
```

Examples:
- Every 6 hours: `'0 */6 * * *'`
- Weekly on Monday: `'0 0 * * 1'`
- Twice daily: `'0 0,12 * * *'`

### Modify Page Design

The page design can be customized in two places:

**Option 1: Edit the Jekyll layout**

Edit `_layouts/default.html`:

- Modify the HTML structure
- Update the CSS styles in the `<style>` tag
- Colors, fonts, and layout can all be customized

**Option 2: Edit the Markdown generation**

Edit `scripts/generate_page.py`:

- Find the `generate_markdown()` function
- Modify the Markdown template
- Change the structure and content of the generated page

**Option 3: Customize Jekyll configuration**

Edit `_config.yml`:

- Change the theme (currently using minima)
- Add Jekyll plugins
- Customize site metadata

### Add More Data Sources

Edit `scripts/generate_page.py`:

- Add new API calls in the `main()` function
- Modify `generate_markdown()` to display the new data in Markdown format

## Support

For issues or questions:
- Open an issue in the repository
- Check existing issues for similar problems
- Review GitHub Actions logs for detailed error information
