# notebooklm-sources

Public GitHub Pages site for publishing Markdown and image artifacts as clean static pages.

## What this is for

- Turn local `.md` files into public single-page HTML documents
- Turn local images into simple public viewer pages
- Produce stable public URLs that can be pasted into NotebookLM as web sources

## Local publishing

This repo is managed from the main OpenClaw workspace.

Use the workspace helper:

```bash
/Users/weibao/.openclaw/workspace/scripts/publish-github-pages <path-to-md-or-image>
```

Examples:

```bash
scripts/publish-github-pages translate/aakash-karpathy-prompt-loop-timeline-zh-CN/translation.md
scripts/publish-github-pages output/cards/example.png --title "Example card"
```

The publisher will:

1. Convert Markdown into static HTML
2. Copy local referenced images into the page folder
3. Update the site index
4. Commit and push changes to GitHub

## GitHub Pages

This repo is intended to publish from the `main` branch, `/docs` folder.
