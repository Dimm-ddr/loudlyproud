---
title: Style Guide
description: A guide to the components, typography, and colors used across the site
layout: single
---

# Style Guide

This guide documents the components, typography, and colors used across the site to maintain visual consistency.

## Colors

Our site uses a consistent color palette in both light and dark modes:

### Primary Colors

- **Primary**: `#000000` (dark mode: `#ffffff`)
- **Secondary**: `#eee7dc` (dark mode: `#2d2d2d`)
- **Tertiary**: `#d3ccb8` (dark mode: `#443e36`)

### Accent Colors

- **Accent 1**: `#E74C3C` (dark mode: `#ff6b5d`)
- **Accent 2**: `#2ECC71` (dark mode: `#4fdd91`)
- **Accent 3**: `#3498DB` (dark mode: `#5dafec`)

### UI Colors

- **Background**: `#b7b0a7` (dark mode: `#1a1a1a`)
- **Text**: `#333333` (dark mode: `#e5e5e5`)
- **Light Gray**: `#eaeaea` (dark mode: `#404040`)

## Typography

### Font Family

- **Primary**: "Lato", system-ui, sans-serif
- **Cyrillic**: "Noto Sans", sans-serif
- **Arabic**: "Noto Sans Arabic", sans-serif

### Font Weights

- **Thin**: 100
- **Light**: 300
- **Normal**: 400
- **Bold**: 700
- **Black**: 900

### Headings

- **Heading 1**: `text-4xl font-black`
- **Heading 2**: `text-3xl font-black`
- **Heading 3**: `text-2xl font-bold`
- **Heading 4**: `text-xl font-bold`
- **Heading 5**: `text-lg font-bold`
- **Heading 6**: `text-base font-bold`

### Body Text

- **Body**: `text-base font-normal`
- **Body Small**: `text-sm font-normal`
- **Body Large**: `text-lg font-normal`
- **Caption**: `text-sm font-normal` (80% opacity)
- **Overline**: `text-xs font-bold uppercase tracking-wider` (70% opacity)

## Components

### Buttons

```html
<!-- Primary button -->
<button class="btn-primary">Primary Button</button>

<!-- Secondary button -->
<button class="btn-secondary">Secondary Button</button>

<!-- Tertiary button -->
<button class="btn-tertiary">Tertiary Button</button>

<!-- Size variants -->
<button class="btn-primary btn-sm">Small Button</button>
<button class="btn-primary btn-lg">Large Button</button>

<!-- Disabled button -->
<button class="btn-primary btn-disabled" disabled>Disabled Button</button>
```

### Form Controls

```html
<!-- Text input -->
<input type="text" class="input-control">

<!-- Select dropdown -->
<select class="select-control">
  <option>Option 1</option>
  <option>Option 2</option>
</select>

<!-- Checkbox -->
<input type="checkbox" class="checkbox-control">

<!-- Radio button -->
<input type="radio" class="radio-control">

<!-- Label -->
<label class="form-label">Form Label</label>
<label class="form-label-inline">Inline Label</label>
```

### Tags

```html
<!-- Standard tag -->
<span class="tag">Standard Tag</span>

<!-- Active tag -->
<span class="tag active">Active Tag</span>

<!-- Colored tags -->
<span class="tag-base tag-amber">Amber Tag</span>
<span class="tag-base tag-aubergine">Aubergine Tag</span>
<span class="tag-base tag-burgundy">Burgundy Tag</span>
<span class="tag-base tag-deep-blue">Deep Blue Tag</span>
<span class="tag-base tag-forest">Forest Tag</span>
<span class="tag-base tag-marine">Marine Tag</span>
<span class="tag-base tag-plum">Plum Tag</span>
<span class="tag-base tag-rust">Rust Tag</span>
<span class="tag-base tag-slate">Slate Tag</span>
<span class="tag-base tag-fallback">Fallback Tag</span>
```

### Cards

```html
<!-- Basic card -->
<div class="card">
  <div class="p-4">Card content</div>
</div>

<!-- Book card -->
<div class="book-card">
  <a href="#">
    <img src="book-cover.jpg" alt="Book title">
  </a>
  <div class="p-4">Book details</div>
</div>

<!-- Language card -->
<div class="language-card language-card-ltr">
  <div class="p-4">Language content</div>
</div>
```

## How to Use

1. Import the component classes in your HTML markup
2. For consistent styling, always use the predefined components rather than creating new styles
3. Reference this guide when creating new templates or components

## Accessibility Considerations

- All colors meet WCAG 2.1 AA contrast requirements
- Interactive elements have focus states
- Form elements have proper labeling
- Dark mode is supported for light sensitivity preferences 