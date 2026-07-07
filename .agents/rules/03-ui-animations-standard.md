---
trigger: model_decision
description: Reference when building or modifying any UI component, page layout, styling, animation, or visual design element
---

# 1. Design System References (MANDATORY)
Before building any UI, consult:
- `docs/brand-identity.md` — Full token map, logo assets, visual patterns.
- `docs/design-system-template.md` — Component patterns, spacing, layout templates.

# 2. Component Patterns
- **Cards:** Always use the shadcn `<Card>` component. It applies Glassmorphism (`backdrop-blur`) automatically.
- **Buttons:** Always `rounded-full`. Use `variant="gradient"` for primary CTAs, `variant="outline"` for secondary, `variant="ghost"` for tertiary, `variant="glass"` for glassmorphic contexts.
- **Switch:** Uses `brand-cornflower` (`#8AA2DF`) when checked.
- **Charts:** Use `brandChartTheme` from `chart.tsx` to map Recharts colors to CSS variables.
- **Background Blobs:** Use `<VisualPattern />` component for mesh gradient backgrounds.

# 3. Typography Scale
Use the responsive semantic `text-display-*` classes — never arbitrary pixel values.
- `text-display-1` → Hero Headlines (H1)
- `text-display-2` → Page Titles (H2)
- `text-display-3` → Section Headers (H3)
- `text-display-4` → Card Titles (H4)
- `text-display-5` → Metrics & Values (H5)
- `text-display-6` → Subheadings (H6)
- `text-micro` → Stat labels with letter-spacing

# 4. Iconography
- **Library:** `lucide-react`
- **Stroke:** All icons `strokeWidth={1.5}`.
- **Sizes:** `h-5 w-5` for navigation, `h-6 w-6` for cards/sections.
- **Active State:** `text-brand-cornflower` for active navigation items.
- **Prefer** using `import { Icons } from '@/components/ui/icons'` when available.

# 5. Animation Standards
Animations must feel smooth, subtle, and professional — like a premium dashboard, not a marketing site.
- **Allowed:** `fade-up`, `fade-in`, `scale-in`, `slide-in-*`, `shimmer`, `count-up`, `blob` (ambient). All defined in `tailwind.config.js`.
- **Forbidden:** Bouncing, flashy motion, aggressive scaling, layout thrashing.
- **Framer Motion:** Use for scroll-triggered reveals and complex sequenced animations.
- **CSS Keyframes:** Use Tailwind animation utilities for simple infinite loops (shimmer, float, pulse-ring).

# 6. Shadow System
Use the custom shadow utilities from `tailwind.config.js` — never heavy traditional drop-shadows.
- `shadow-glass` / `shadow-glass-hover` → Cards and containers
- `shadow-accent` / `shadow-accent-strong` → Interactive/focused elements
- `shadow-float` / `shadow-float-lg` → Detached elements (modals, popovers)
- `shadow-inner-soft` → Input fields

# 7. Loading & Empty States
- Use `shimmer` animation for skeleton loaders on async data.
- Always show a loading state — never render empty containers while data is fetching.
- Empty states should include a descriptive message and, where appropriate, a call-to-action.

# 8. Layout Conventions
- **Sidebar:** Fixed width (260px), `bg-brand-black` (`#04060A`). Active: `bg-white/10 text-brand-cornflower`. Inactive: `text-brand-muted hover:bg-white/5`.
- **Header:** Sticky, glassmorphism (`bg-background/80 backdrop-blur-md`).
- **Content:** `flex flex-1 flex-col gap-4 bg-background p-4 lg:gap-6 lg:p-8`.
- **Card Grids:** `grid gap-6 md:grid-cols-2 lg:grid-cols-4`.
- **Border Radius:** `0.75rem` for cards, `9999px` for buttons.

# 9. Design Quality Enforcement (MANDATORY)
Before creating or modifying ANY UI component, the agent MUST:
1. **Reference** `docs/brand-identity.md` — verify color tokens, typography, and visual patterns.
2. **Use semantic tokens** — `bg-brand-navy`, `text-brand-cornflower`, `shadow-glass`. Never arbitrary hex values or pixel sizes.
3. **Use shadcn/ui primitives** before creating custom components.
4. **Check after building** — does it match the Ampersand brand system? If not, fix before committing.
5. **No bland UIs** — if a page looks like a basic CRUD table, add proper card layout, glassmorphism, and loading states.

See Rule 12 (Developer Guardrails) for the full design quality checklist and anti-pattern table.
See Rule 14 (Accessibility) — every component built under this rule must also pass the a11y bar.