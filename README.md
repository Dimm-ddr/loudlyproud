

# 🌈 Loudly Proud — A Multilingual LGBTQIA+ Literature Catalog

**Loudly Proud** is a multilingual catalog of LGBTQIA+ literature, designed to improve discoverability, accessibility, and representation of queer books across languages and cultures. The project is open-source and deployed as a static website using [Hugo](https://gohugo.io/).

It is maintained by and for readers who want a curated space to explore queer narratives — especially those not easily found in mainstream platforms or limited to one language.

---

## 🌟 Project Goals

- 📚 **Curate** a growing library of LGBTQIA+ books with rich metadata
- 🌍 **Support** multilingual access to queer literature  
  _Currently supported: Russian 🇷🇺, English 🇬🇧, Farsi 🇮🇷, Kurdish 🇹🇯_
- 🧭 **Enable** exploration via an advanced tag system (themes, identities, genres)
- ✍️ **Invite** community feedback and contributions
- 🖥️ **Maintain** a lightweight, fast, and accessible static site

---

## 🔎 Key Features

- ✅ Searchable and filterable book catalog
- 🏷️ Tag-based browsing with hierarchy and color-coded visual markers
- 🌐 Multilingual structure with language-specific navigation
- 💬 Feedback and book suggestion system
- 🌙 Responsive layout with dark mode support
- ♿ Built-in accessibility enhancements
- ⚙️ Automated content validation and tag monitoring (CI-powered)

---

## 🛠 Tech Stack Overview

> While the site is reader-facing, here's a brief tech summary:

- **Static Generator**: Hugo  
- **Styling**: TailwindCSS  
- **Interactivity**: Alpine.js + TypeScript  
- **Content Management**: Decap CMS (Netlify CMS fork)  
- **Search**: Pagefind (static, client-side)  
- **Deployment**: Netlify  
- **CI/CD**: GitHub Actions  
- **Linting & formatting**: Prettier, flake8, custom style guide

Docs and tools are organized under:
- `.tools/`: scripts for tag management, content validation, and CI
- `docs/`: contributor guides and editing conventions

### 🏗️ Architecture & Implementation Details

**Component System**: The project implements a comprehensive component system for consistent UI:
- Component CSS organized in `assets/css/components/` directory
- Reusable Hugo partials that implement these components
- Style categories: Typography, Buttons, Form Controls, Tags, Cards
- Style guide available at `/style-guide` for development reference

**Tag System**: Advanced hierarchical tagging with:
- Tag normalization and validation processes
- Color-coded visual organization
- Automated tag monitoring for pull requests
- Registry-based tag management

**Content Management**: 
- Structured validation for book entries
- Automated workflows via GitHub Actions
- Content stored in language-specific directories

---

## 🧑‍💻 Development & Build

### Prerequisites

To run the project locally, you'll need:

- [Hugo (extended)](https://gohugo.io/getting-started/installing/) ≥ v0.111
- [pnpm](https://pnpm.io/) or npm
- Node.js ≥ 18

### Setup Instructions

```bash
# Install frontend dependencies
pnpm install

# Start local Hugo server with drafts and multilingual support
pnpm run dev
```

This will start the site at `http://localhost:1313` with auto-reload and full multilingual content.

### Build the Production Site

```bash
pnpm run build
```

The final output will be placed in the `public/` directory.

> 🧩 The `build-config.js` script ensures that the correct environment-specific configuration is applied. You normally don't need to touch this unless you're debugging config overrides.

---

### ✅ Dev Tips

* The Tailwind and TypeScript setup is minimal but structured; feel free to add your own components under `assets/` and `src/`.
* Content for books is stored in language-specific Markdown files under `content/`.
* Use `pnpm run format` to auto-format code and markdown before committing.
* Tag logic is in `.tools/tags/`; run tag-related checks with `pnpm run check:tags`.

---

## 🤝 Contributing

We welcome contributions from anyone who wants to help grow and improve this catalog — especially book suggestions, metadata fixes, or translations.

* Submit feedback and book ideas via the site
* Fork the repo and open pull requests
* See [`docs/content-editing-guide.md`](docs/content-editing-guide.md) for content formatting help

---

## 📄 License

This project is licensed under the MIT License — you are free to use, copy, and adapt it, including for commercial purposes, as long as attribution is given.
See the [LICENSE](LICENSE) file for the full legal text.

---

## 🌐 Live Site

Explore the catalog here:
🔗 **[https://loudlyproud.netlify.app](https://loudlyproud.netlify.app)**


