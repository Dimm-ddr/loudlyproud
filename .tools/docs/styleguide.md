# LoudlyProud Style System

## Colors & Typography

### Color System

All colors are defined in `tailwind.config.js > theme.extend.colors`

#### Primary Colors

- Purpose: Main text and important elements
- Light mode: ![#000000](https://img.shields.io/badge/-%23000000-000000) `#000000`
- Dark mode: ![#ffffff](https://img.shields.io/badge/-%23ffffff-ffffff) `#ffffff`
- Usage: `text-primary`, `text-primary-dark`

#### Secondary Colors

- Purpose: Container backgrounds, cards, main content areas
- Light mode: ![#eee7dc](https://img.shields.io/badge/-%23eee7dc-eee7dc) `#eee7dc`
- Dark mode: ![#2d2d2d](https://img.shields.io/badge/-%232d2d2d-2d2d2d) `#2d2d2d`
- Usage: `bg-secondary`, `bg-secondary-dark`

#### Background Colors

- Purpose: Page background
- Light mode: ![#b7b0a7](https://img.shields.io/badge/-%23b7b0a7-b7b0a7) `#b7b0a7`
- Dark mode: ![#1a1a1a](https://img.shields.io/badge/-%231a1a1a-1a1a1a) `#1a1a1a`
- Usage: `bg-background`, `bg-background-dark`

#### Text Colors

- Purpose: Regular text content
- Light mode: ![#333333](https://img.shields.io/badge/-%23333333-333333) `#333333`
- Dark mode: ![#e5e5e5](https://img.shields.io/badge/-%23e5e5e5-e5e5e5) `#e5e5e5`
- Usage: `text-text`, `text-text-dark`

#### Accent Colors

1. Accent1 (Red)

   - Light: ![#E74C3C](https://img.shields.io/badge/-%23E74C3C-E74C3C) `#E74C3C`
   - Dark: ![#ff6b5d](https://img.shields.io/badge/-%23ff6b5d-ff6b5d) `#ff6b5d`
   - Usage: Alerts, important actions

2. Accent2 (Green)

   - Light: ![#2ECC71](https://img.shields.io/badge/-%232ECC71-2ECC71) `#2ECC71`
   - Dark: ![#4fdd91](https://img.shields.io/badge/-%234fdd91-4fdd91) `#4fdd91`
   - Usage: Success states, positive actions

3. Accent3 (Blue)
   - Light: ![#3498DB](https://img.shields.io/badge/-%233498DB-3498DB) `#3498DB`
   - Dark: ![#5dafec](https://img.shields.io/badge/-%235dafec-5dafec) `#5dafec`
   - Usage: Links, interactive elements

### Typography

#### Text Styles

- Page Title: `text-4xl font-black text-primary dark:text-primary-dark`
- Section Headers: `text-2xl font-bold text-primary dark:text-primary-dark`
- Body Text: `text-lg text-text dark:text-text-dark`
- Small Text: `text-sm text-text dark:text-text-dark`
- Code/Mono: `font-mono text-primary dark:text-primary-dark`

#### Font Weights

All weights are available through Lato font:

- Thin: `font-thin` (100)
- Light: `font-light` (300)
- Regular: `font-normal` (400)
- Bold: `font-bold` (700)
- Black: `font-black` (900)

## Components

### Buttons & Interactive Elements

#### Primary Button

```html
class="inline-block px-6 py-2 bg-secondary dark:bg-secondary-dark
       text-primary dark:text-primary-dark rounded-lg font-medium
       hover:bg-secondary-light dark:hover:bg-secondary-dark/80
       transition-colors"
```

#### Link Button

```html
class="text-accent1 hover:text-accent1-dark transition-colors"
```

### Tag System

Defined in `assets/css/tailwind.css` and `tailwind.config.js`

#### Base Tag Style

```css
.tag-base {
  @apply inline-block px-3 py-1 rounded-full text-sm font-bold
         transition-colors duration-200;
}
```

#### Tag Colors

Each tag type has light and dark mode variants with hover states:

- Amber: `tag-amber` - Warm, attention-grabbing
- Aubergine: `tag-aubergine` - Deep purple, sophisticated
- Burgundy: `tag-burgundy` - Rich red, emphasis
- Deep Blue: `tag-deep-blue` - Professional, trustworthy
- Forest: `tag-forest` - Natural, growth
- Marine: `tag-marine` - Fresh, clean
- Plum: `tag-plum` - Creative, playful
- Rust: `tag-rust` - Earthy, grounding
- Slate: `tag-slate` - Neutral, balanced
- Fallback: `tag-fallback` - Default style

### Container Hierarchy

1. Page Background: `bg-background dark:bg-background-dark`
2. Main Containers: `bg-secondary dark:bg-secondary-dark`
3. Nested Elements: Use opacity variants of parent colors

   ```html
   class="bg-secondary-light/30 dark:bg-secondary-dark/50"
   ```

### Accessibility

- All color combinations maintain WCAG AA contrast ratios
- Interactive elements have hover states
- Dark mode support throughout
- Font sizes scale appropriately for readability
