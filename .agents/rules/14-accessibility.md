---
trigger: model_decision
description: Reference when building or modifying any frontend UI component — every component must meet the WCAG 2.2 AA bar before commit.
---

# 1. The Bar: WCAG 2.2 AA, Always
This is an internal enterprise platform. Operators may use it 8+ hours a day, may have visual impairments, may rely on keyboard navigation, may use screen readers. Accessibility is not a polish item — it's a usability baseline.

Every component you build or modify must meet **WCAG 2.2 Level AA**. If you don't know whether a pattern passes, look it up before shipping.

# 2. Keyboard Navigation (CRITICAL)
- **Every interactive element** must be reachable and operable via keyboard alone — no exceptions.
- **Focus order** must follow visual order (don't reorder with `tabindex` to jump around).
- **Focus styles** must be visible — never `outline: none` without a replacement. Use `focus-visible:ring-2 focus-visible:ring-brand-cornflower`.
- **Skip links** for the main nav: a hidden link that becomes visible on focus to "Skip to main content".
- **Modals/dialogs:** trap focus inside while open. Restore focus to the trigger element on close. Esc closes.
- **Dropdowns/menus:** arrow keys navigate, Enter activates, Esc closes, Tab moves to the next focusable element.

Use shadcn/Radix primitives — they handle focus management correctly. Do **not** roll your own modal, dropdown, or combobox unless you can't avoid it.

# 3. Semantic HTML First
- Use `<button>` for actions, `<a href>` for navigation. Never a `<div onClick>` for an interactive element.
- Use `<form>` with proper `<label htmlFor>` for inputs. Every input has a label — placeholder is **not** a label.
- Use heading hierarchy (`<h1>` → `<h2>` → `<h3>`) without skipping levels. One `<h1>` per page.
- Use `<nav>`, `<main>`, `<aside>`, `<header>`, `<footer>` landmarks. Screen readers use them to navigate.
- Lists are `<ul>` / `<ol>`. Tables are `<table>` with `<th scope="col">` headers — not div grids pretending to be tables.

# 4. ARIA — When You Need It, Use It Right
ARIA is a fallback when semantic HTML can't express the meaning. The first rule of ARIA is: **don't use ARIA if a native element already does the job.**
- `aria-label` for icon-only buttons (`<Button aria-label="Close dialog">`).
- `aria-describedby` to link an input to its helper text or error message.
- `aria-live="polite"` regions for async status updates (toasts, AI thinking indicators).
- `role="status"` for non-critical async updates; `role="alert"` for errors that need immediate attention.
- `aria-expanded` on disclosure triggers (accordions, dropdowns).
- `aria-current="page"` on the active sidebar nav item.

Do not slap `role="button"` on a `<div>` — use a `<Button>`. Do not use `aria-hidden="true"` on a focusable element — that's a screen-reader trap.

# 5. Color & Contrast
- **Body text:** ≥ 4.5:1 contrast against background.
- **Large text** (18pt+ or 14pt+ bold): ≥ 3:1.
- **Interactive elements** (buttons, links, focus rings, form borders): ≥ 3:1 against adjacent colors.
- **Never rely on color alone** to convey meaning. Add an icon, label, or pattern. Status badges need a glyph or text, not just a colored dot.

The Ampersand palette (Rule 03) was tuned for AA on `bg-background` — but custom combinations require manual checking. Use a contrast checker (DevTools, Polypane, or `npm i -D axe-core`).

# 6. Forms
- Every input has a `<label>`. If the design hides the label, use `sr-only` (visually hidden but read by screen readers) — don't drop it.
- Required fields: mark with both `required` attribute AND a visible indicator (asterisk + legend) — never asterisk alone.
- Error messages: linked via `aria-describedby`, with `aria-invalid="true"` on the input. The error must be specific ("Email must include @") not generic ("Invalid").
- Group related radio/checkbox sets in `<fieldset><legend>`.
- Don't disable the submit button while validating async — show inline progress instead. Disabled buttons don't tell screen readers why.

# 7. Images, Icons, & Media
- `<img>`: every one has an `alt` attribute. Decorative images: `alt=""` (empty string, not omitted). Informational: descriptive alt text.
- **Icon-only buttons:** the button itself has `aria-label`; the icon has `aria-hidden="true"`.
- **Charts:** Recharts components must have a text alternative — either a description below, a `<title>` element, or a "View as table" toggle for the underlying data.
- **Loading spinners:** `role="status"` with a screen-reader text ("Loading data…").
- **Animations:** respect `prefers-reduced-motion`. Wrap non-essential animations in `@media (prefers-reduced-motion: no-preference)` or use Framer Motion's reduced-motion hook.

# 8. Tables (Data Grids)
- Use `<table>` with `<thead>`, `<tbody>`, `<th scope="col">` for column headers, `<th scope="row">` for row headers when applicable.
- Sortable columns: button inside the `<th>` with `aria-sort="ascending" | "descending" | "none"`.
- Empty state: a `<caption>` or visible message — not a blank `<tbody>`.
- Pagination: visible "Page X of Y" — not just numbered links.

# 9. The Pre-Commit a11y Check
For every UI commit, verify (skim through your changes):

- [ ] Every interactive element is reachable via Tab.
- [ ] Focus is visible at every step (no missing rings).
- [ ] No `<div onClick>` — use `<Button>` or `<a>`.
- [ ] Every input has a `<label>` (or `sr-only` label).
- [ ] Every icon-only button has `aria-label`.
- [ ] Every image has `alt`.
- [ ] Color is not the only signal (icon/text accompanies it).
- [ ] Animations respect `prefers-reduced-motion`.
- [ ] You ran a quick screen-reader test on the most complex new component (VoiceOver: Cmd+F5; NVDA on Windows).

If any of these are no, fix before committing. **A broken keyboard flow blocks merge.**
