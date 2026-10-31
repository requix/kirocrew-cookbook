# KiroCrew Cookbook

Recipes from real work with KiroCrew. Checked against the KiroCrew source, not written from memory.

## Quick start

```bash
# Clone
git clone https://github.com/YOUR_ORG/kirocrew-cookbook.git
cd kirocrew-cookbook

# Install dependencies
pip install pygments pyyaml markdown-it-py

# Build
cd build/preview
python3 build.py

# Preview locally
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
# Open http://localhost:8000
```

## Project structure

```
content/                  # Markdown content (contributors edit here)
├── index.md             # Landing page
├── meta.json            # Section order
├── start/               # Getting started guides
├── find/                # Navigation helpers
├── concepts/            # Core concepts
├── apps/                # Apps documentation
└── recipes/             # How-to recipes

build/                   # Build system (maintainers only)
├── preview/             # Python static site generator
│   ├── build.py         # Build script
│   ├── dist/            # Generated site (gitignored)
│   └── assets/          # Site CSS/JS
└── data/                # Shared data files
```

## Adding a recipe

1. Copy `content/recipes/TEMPLATE.txt` to `content/recipes/your-recipe.md`
2. Fill in the frontmatter and content
3. Add the filename (without `.md`) to `content/recipes/meta.json`
4. Run `cd build/preview && python3 build.py` — it validates your content
5. Open a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License. See [LICENSE](LICENSE).
