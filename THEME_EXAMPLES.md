# Theme Configuration Examples

This document provides examples of different theme configurations for the Rustedbytes page.

## Using the Default Layout

The default layout uses a modern gradient design with purple/blue colors.

**page_config.yml:**
```yaml
layout: default
theme: minima
styling:
  page_title: "Rustedbytes Projects"
  page_description: "A collection of Rust-based projects"
  header_emoji: "🦀"
```

## Using the Minimal Layout

The minimal layout uses a terminal-style dark theme with green accents.

**page_config.yml:**
```yaml
layout: minimal
theme: minima
styling:
  page_title: "Rustedbytes Projects"
  page_description: "A collection of Rust-based projects"
  header_emoji: "🦀"
```

## Using Environment Variables

You can override configuration settings using environment variables in the GitHub Actions workflow.

Edit `.github/workflows/generate-page.yml`:

```yaml
- name: Generate page
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    PAGE_LAYOUT: minimal              # Use minimal layout
    PAGE_TITLE: "My Rust Projects"    # Custom title
    PAGE_THEME: custom                # Custom theme (optional)
  run: |
    python scripts/generate_page.py
```

## Creating a Custom Layout

1. Create a new HTML file in `_layouts/` directory (e.g., `_layouts/custom.html`)
2. Use the following template as a starting point:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title | default: site.title }}</title>
    <style>
        /* Add your custom CSS styles here */
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        /* ... more styles ... */
    </style>
</head>
<body>
    {{ content }}
</body>
</html>
```

3. Update `page_config.yml`:

```yaml
layout: custom
theme: minima
styling:
  page_title: "My Custom Page"
  page_description: "Custom description"
  header_emoji: "✨"
```

## Customizing Colors

To customize the colors in existing layouts:

### For Default Layout

Edit `_layouts/default.html` and modify the CSS variables:

```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Change to your preferred gradient colors */
}

h1, h2 {
    color: #667eea;
    /* Change to your preferred heading color */
}

th {
    background: #667eea;
    /* Change to your preferred table header color */
}
```

### For Minimal Layout

Edit `_layouts/minimal.html` and modify the CSS:

```css
body {
    background: #1a1a1a;  /* Background color */
    color: #e0e0e0;       /* Text color */
}

h1, h2 {
    color: #00ff00;       /* Heading color */
}

a {
    color: #00aaff;       /* Link color */
}
```

## Testing Locally

To test different layouts locally:

```bash
# Install dependencies
pip install pyyaml requests

# Test with default layout
python3 scripts/generate_page.py

# Test with minimal layout
PAGE_LAYOUT=minimal python3 scripts/generate_page.py

# Preview with Jekyll
jekyll serve
```

Then open http://localhost:4000 in your browser to see the result.
