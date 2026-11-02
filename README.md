# Kiro Crew Cookbook

[![Build and Deploy](https://github.com/requix/kirocrew-cookbook/actions/workflows/deploy.yml/badge.svg)](https://github.com/requix/kirocrew-cookbook/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Recipes from real work with Kiro Crew. Checked against the Kiro Crew source, not written from memory.

🌐 **Live site:** [requix.github.io/kirocrew-cookbook](https://requix.github.io/kirocrew-cookbook)

## What's inside

- **Getting started guides** — Install, first hour, dashboard basics
- **Core concepts** — How Kiro Crew works under the hood
- **Apps documentation** — Building and using Kiro Crew apps
- **Recipes** — Step-by-step solutions to real problems

## Quick start

```bash
# Clone
git clone https://github.com/requix/kirocrew-cookbook.git
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

## Local preview

After building, start a local server:

```bash
cd build/preview/dist
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

**Custom port or network access:**

```bash
# Different port
python3 -m http.server 3000

# Accessible from other devices on your network
python3 -m http.server 8000 --bind 0.0.0.0
```

The server runs until you press Ctrl+C.

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

## Contributing

We welcome contributions! Here's how you can help:

### Found a typo or error?

[Open an issue](https://github.com/requix/kirocrew-cookbook/issues/new?template=bug_report.yml) describing what's wrong and where you found it.

### Have a content idea?

[Suggest content](https://github.com/requix/kirocrew-cookbook/issues/new?template=suggest_content.yml) — tell us what recipe, concept, or topic you'd like documented.

### Want to contribute a recipe?

1. Fork this repository
2. Copy `content/recipes/TEMPLATE.txt` to `content/recipes/your-recipe.md`
3. Fill in the frontmatter and content
4. Add the filename (without `.md`) to `content/recipes/meta.json`
5. Run `cd build/preview && python3 build.py` — it validates your content
6. Open a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

## Code of Conduct

Be kind. Be helpful. Assume good intent.

## License

MIT License. See [LICENSE](LICENSE).

## Links

- [Live Cookbook](https://requix.github.io/kirocrew-cookbook)
- [Kiro Crew](https://crew.kiro.dev)
- [Report an Issue](https://github.com/requix/kirocrew-cookbook/issues/new?template=bug_report.yml)
- [Suggest Content](https://github.com/requix/kirocrew-cookbook/issues/new?template=suggest_content.yml)
