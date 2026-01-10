# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

French general knowledge documentation site built with Antora. Content is written in AsciiDoc and organized into knowledge "circles" (cercle1-4).

## Build Commands

```bash
# Generate main documentation site (from content/ directory)
cd content && antora antora-playbook.yml

# Generate docs site (from docs/ directory)
cd docs && antora antora-playbook.yml
```

Output: `content/build/culture-generale/antora/index.html`

## Repository Structure

- `content/` - Main knowledge content site
  - `modules/ROOT/` - Landing pages
  - `modules/cercle1-4/` - Content organized by knowledge circle
    - `pages/` - AsciiDoc files
    - `nav.adoc` - Module navigation
- `docs/` - Repository documentation (separate Antora site)

## CI/CD

Deploys to GitHub Pages on push to `antora` branch. The `check_broken_links.yml` workflow validates AsciiDoc links (non-blocking).
