# DESIGN_SYSTEM.md — Bias Audit Dashboard

> **Version:** 1.0
> **Status:** Production
> **Always dark. No light mode toggle.**

This document is the complete implementation guide for the design system.
A developer who has never seen the codebase should be able to open this
file and build something that looks identical.

---

## 1. Design Philosophy

**Professional B2B SaaS. Dark. Precise. Data-dense but breathable.**

Every design decision reinforces that this is a trust and safety tool,
not a consumer app.

Core principles:

- Restraint over decoration. No gradients, no shadows, no glow effects.
  Flat surfaces separated by 1px borders.
- Amber is a signal, not a brand colour. Amber (#E8C547) is the only
  warm element in an otherwise cold monochrome system. It marks active
  state, progress, and focus. Use it sparingly.
- Precision typography. ALL CAPS for labels, tabs, and headings. Tight
  tracking. Three fonts, each with a single role. No freestyle sizing.
- Purposeful density. Pack data close together but give content room to
  breathe with consistent padding.
- Never auto-load anything. Every AI call is triggered by an explicit
  user action. Token spend equals user intent.

---

## 2. Colour Tokens

All values live in `styles/tokens.css`. Never hardcode a hex value anywhere else.

```css
/* styles/tokens.css */
:root {
  /* ── Backgrounds ─────────────────────────────── */
  --background:  #0D0D0D;
  --panel:       #141414;
  --panel-dark:  #1A1A1A;
  --recommendations-bg: #1A1600;

  /* ── Semantic surface aliases (used by shadcn/ui) */
  --card:        #141414;
  --popover:     #1A1A1A;
  --secondary:   #1A1A1A;
  --muted:       #1A1A1A;
  --input:       #141414;

  /* ── Foregrounds ─────────────────────────────── */
  --foreground:             #F0F0F0;
  --card-foreground:        #F0F0F0;
  --popover-foreground:     #F0F0F0;
  --secondary-foreground:   #F0F0F0;
  --destructive-foreground: #F0F0F0;
  --muted-foreground:       #888888;
  --primary-foreground:     #0D0D0D;
  --accent-foreground:      #0D0D0D;

  /* ── Brand accent ────────────────────────────── */
  --primary:  #E8C547;
  --accent:   #E8C547;
  --ring:     #E8C547;

  /* ── State ───────────────────────────────────── */
  --destructive: #E85D4A;

  /* ── Borders ─────────────────────────────────── */
  --border: #2A2A2A;

  /* ── Score colours ───────────────────────────── */
  --score-high: #4CAF50;
  --score-mid:  #E8C547;
  --score-low:  #E85D4A;

  /* ── Bias verdict colours ────────────────────── */
  --verdict-neutral:     #4CAF50;
  --verdict-low:         #E8C547;
  --verdict-medium:      #E8954A;
  --verdict-high:        #E85D4A;

  /* ── Gated / IN DEVELOPMENT ──────────────────── */
  --gated:            #111111;
  --gated-border:     #1E1E1E;
  --gated-foreground: #333333;

  /* ── Shape ───────────────────────────────────── */
  --radius: 2px;

  /* ── Scrollbar ───────────────────────────────── */
  --scrollbar-width:       6px;
  --scrollbar-track:       var(--panel);
  --scrollbar-thumb:       var(--border);
  --scrollbar-thumb-hover: var(--primary);
}

.dark {
  --background:  #0D0D0D;
  --panel:       #141414;
  --panel-dark:  #1A1A1A;
  --foreground:  #F0F0F0;
  --muted-foreground: #888888;
  --primary:     #E8C547;
  --border:      #2A2A2A;
  --destructive: #E85D4A;
  --score-high:  #4CAF50;
  --score-mid:   #E8C547;
  --score-low:   #E85D4A;
  --verdict-neutral: #4CAF50;
  --verdict-low:     #E8C547;
  --verdict-medium:  #E8954A;
  --verdict-high:    #E85D4A;
}
```

### Bias verdict colour logic

```tsx
const getVerdictClass = (category: string, score: number) => {
  if (category === "neutral")           return "text-verdict-neutral";
  if (score < 30)                       return "text-verdict-low";
  if (score < 65)                       return "text-verdict-medium";
  return "text-verdict-high";
};
```

### Background usage

| Token            | Tailwind               | Use                                     |
|------------------|------------------------|-----------------------------------------|
| `--background`   | `bg-background`        | Page canvas. Darkest layer.             |
| `--panel`        | `bg-panel`             | Cards, sidebars, info panels.           |
| `--panel-dark`   | `bg-panel-dark`        | Top nav, dropdowns, elevated surfaces.  |
| `--recommendations-bg` | `bg-recommendations` | Amber-tinted explanation panels.  |
| `--gated`        | `bg-gated`             | Locked/coming-soon states.              |

---

## 3. Typography

### Fonts

| Role         | Font             | Weight       | Tailwind      |
|--------------|------------------|--------------|---------------|
| Display/Logo | Gilroy ExtraBold | 900          | `font-black`  |
| Logo sub     | Gilroy Light     | 300          | `font-light`  |
| UI, body     | Inter            | 400, 500     | `font-sans`   |
| Numbers/code | JetBrains Mono   | 400          | `font-mono`   |

Only three weights allowed: 400 (normal), 500 (medium), 900 (black).
No 600, 700, or 800 in the UI.

### Font imports

```tsx
// app/layout.tsx
import { Inter, JetBrains_Mono } from 'next/font/google'

const inter = Inter({ subsets: ["latin"], variable: '--font-inter' });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: '--font-jetbrains' });
```

Gilroy is self-hosted via @font-face in globals.css:

```css
@font-face {
  font-family: 'Gilroy';
  src: url('/fonts/Gilroy-ExtraBold.woff2') format('woff2');
  font-weight: 900;
  font-display: swap;
}
@font-face {
  font-family: 'Gilroy';
  src: url('/fonts/Gilroy-Light.woff2') format('woff2');
  font-weight: 300;
  font-display: swap;
}
```

### Typography rules

ALL CAPS for: navigation labels, section headings, tab labels, button text,
data labels and metadata.

Never ALL CAPS for: body copy, descriptions, user-generated content.

Tracking: ALL CAPS labels use `tracking-widest` or `tracking-wider`.
Body text uses default.

### Font size scale

| Tailwind       | px  | Use                             |
|----------------|-----|---------------------------------|
| `text-[9px]`   | 9   | Micro labels, section headings  |
| `text-[10px]`  | 10  | Button text, tags, metadata     |
| `text-[11px]`  | 11  | Sidebar labels, small UI text   |
| `text-xs`      | 12  | Secondary body, captions        |
| `text-sm`      | 14  | Primary body copy               |
| `text-base`    | 16  | Wordmark                        |
| `text-xl`      | 20  | Wordmark on login page          |

---

## 4. Spacing System

All spacing uses the Tailwind scale. No custom spacing values.

| Tailwind       | px | Use                               |
|----------------|----|-----------------------------------|
| `p-1` / `gap-1`| 4  | Micro gaps between inline elements|
| `p-2` / `gap-2`| 8  | Tight gaps, small pills           |
| `p-3` / `gap-3`| 12 | Panel internal padding (small)    |
| `p-4` / `gap-4`| 16 | Standard card padding             |
| `p-5` / `gap-5`| 20 | Comfortable panel padding         |
| `p-6` / `gap-6`| 24 | Page section padding              |
| `p-8` / `gap-8`| 32 | Large page padding                |

### Layout rules

- Max content width: `max-w-2xl` (672px) single column, `max-w-4xl` (896px) dashboard
- Top nav height: `h-14` (56px)
- Sidebar width: `w-[240px]` fixed, `shrink-0`
- Two-column layouts: `grid grid-cols-1 md:grid-cols-2 gap-4`

---

## 5. Component Patterns

### Dark panel card

```tsx
<div className="bg-panel border border-border p-4 space-y-3">
  <h3 className="text-[10px] tracking-widest text-muted-foreground uppercase">
    SECTION TITLE
  </h3>
  <p className="text-sm text-foreground leading-relaxed">
    Content goes here.
  </p>
</div>
```

### Amber accent button (primary action)

```tsx
<button
  disabled={!isValid || isBusy}
  className="w-full h-11 bg-primary text-primary-foreground text-[10px] font-medium tracking-[0.2em] uppercase hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
>
  ANALYSE
</button>
```

### Subtle border button (secondary action)

```tsx
<button className="px-5 py-2 border border-border text-muted-foreground text-[10px] tracking-widest uppercase hover:border-foreground hover:text-foreground transition-colors">
  EXPORT
</button>
```

### Verdict badge

```tsx
const getBadgeClass = (category: string, score: number) => {
  if (category === "neutral")  return "border-verdict-neutral text-verdict-neutral";
  if (score < 30)              return "border-verdict-low text-verdict-low";
  if (score < 65)              return "border-verdict-medium text-verdict-medium";
  return "border-verdict-high text-verdict-high";
};

<span className={`inline-block text-[9px] tracking-widest uppercase px-2.5 py-1 border ${getBadgeClass(category, score)}`}>
  {category.replace("_", " ").toUpperCase()}
</span>
```

### Input field

```tsx
<input
  type="text"
  placeholder="Paste a headline, social post, or video description..."
  className="w-full h-11 px-3 bg-panel border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/60 transition-colors"
/>

<textarea
  rows={4}
  className="w-full bg-background border border-border text-sm text-foreground placeholder:text-muted-foreground p-4 resize-none focus:outline-none focus:border-primary transition-colors"
/>
```

### Score bar (2px thin)

```tsx
function ScoreRow({ name, score }: { name: string; score: number }) {
  const barColor =
    score >= 8 ? "bg-score-high" :
    score >= 6 ? "bg-score-mid"  : "bg-score-low";

  return (
    <div className="py-1">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[9px] tracking-wider text-muted-foreground uppercase">{name}</span>
        <span className={`font-mono text-[10px] tabular-nums ${barColor.replace("bg-", "text-")}`}>
          {score.toFixed(1)}
        </span>
      </div>
      <div className="w-full h-[2px] bg-border/30 relative">
        <div
          className={`absolute inset-y-0 left-0 transition-all score-bar ${barColor}`}
          style={{ '--score-bar-width': `${score * 10}%` } as React.CSSProperties}
        />
      </div>
    </div>
  );
}
```

`.score-bar` in globals.css:
```css
.score-bar { width: var(--score-bar-width, 0%); }
```

### Tab navigation with amber underline

```tsx
const TABS = ["ANALYSER", "AUDIT DASHBOARD", "FAIRNESS METRICS", "AUDIT LOG"];

<div className="flex border-b border-border overflow-x-auto scrollbar-hide">
  {TABS.map(tab => (
    <button
      key={tab}
      onClick={() => setActiveTab(tab)}
      className={`relative px-4 py-3 text-[10px] tracking-widest uppercase whitespace-nowrap shrink-0 transition-colors ${
        activeTab === tab
          ? "text-foreground"
          : "text-muted-foreground hover:text-foreground/70"
      }`}
    >
      {tab}
      {activeTab === tab && (
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-primary" />
      )}
    </button>
  ))}
</div>
```

### Chat result card (Live Analyser)

```tsx
<div className="bg-panel border border-border p-4 space-y-3">

  {/* Content snippet */}
  <p className="text-sm text-foreground/80 leading-relaxed border-l-2 border-border pl-3 italic">
    "{contentSnippet}"
  </p>

  {/* Verdict row */}
  <div className="flex items-center gap-3 flex-wrap">
    <span className={`text-[9px] tracking-widest uppercase px-2.5 py-1 border ${getBadgeClass(category, score)}`}>
      {category.replace("_", " ")}
    </span>
    <span className="font-mono text-[10px] text-muted-foreground tabular-nums">
      {(score * 100).toFixed(0)}% confidence
    </span>
    <span className={`font-mono text-[10px] tabular-nums ${getVerdictClass(category, score)}`}>
      Risk: {score < 0.3 ? "LOW" : score < 0.65 ? "MEDIUM" : "HIGH"}
    </span>
  </div>

  {/* SHAP highlights */}
  <div className="space-y-1">
    <p className="text-[9px] tracking-widest text-muted-foreground uppercase">
      TRIGGERED BY
    </p>
    <div className="flex flex-wrap gap-1.5">
      {shapWords.map((word, i) => (
        <span key={i} className="text-[10px] px-1.5 py-0.5 bg-primary/10 border border-primary/30 text-primary font-mono">
          {word}
        </span>
      ))}
    </div>
  </div>

  {/* Plain English explanation */}
  <div className="bg-recommendations border-l-2 border-primary px-4 py-3">
    <p className="text-[9px] tracking-widest text-primary uppercase mb-1">EXPLANATION</p>
    <p className="text-xs text-foreground/90 leading-relaxed">{explanation}</p>
  </div>

  {/* Reviewer action row */}
  <div className="flex items-center gap-2 pt-1 border-t border-border">
    <p className="text-[9px] tracking-widest text-muted-foreground uppercase mr-auto">
      REVIEWER ACTION
    </p>
    <button className="px-3 py-1.5 border border-score-high text-score-high text-[9px] tracking-widest uppercase hover:bg-score-high hover:text-background transition-colors">
      APPROVE
    </button>
    <button className="px-3 py-1.5 border border-score-mid text-score-mid text-[9px] tracking-widest uppercase hover:bg-score-mid hover:text-background transition-colors">
      FLAG
    </button>
    <button className="px-3 py-1.5 border border-destructive text-destructive text-[9px] tracking-widest uppercase hover:bg-destructive hover:text-background transition-colors">
      ESCALATE
    </button>
  </div>

</div>
```

### Amber recommendation panel

```tsx
<div className="bg-recommendations border-l-2 border-primary px-5 py-4 space-y-2">
  <p className="text-[9px] tracking-widest text-primary uppercase font-medium">
    EXPLANATION
  </p>
  <p className="text-xs text-foreground/90 leading-relaxed">{explanation}</p>
</div>
```

### Empty state

```tsx
<div className="border border-border border-dashed p-10 flex flex-col items-center justify-center text-center space-y-3">
  <h3 className="text-sm tracking-wider text-foreground uppercase">
    NO CONTENT ANALYSED YET
  </h3>
  <p className="text-sm text-muted-foreground max-w-sm leading-relaxed">
    Type or paste content below to begin analysis.
  </p>
</div>
```

### Loading skeleton

```css
/* globals.css */
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.shimmer {
  background: linear-gradient(
    90deg,
    var(--panel-dark) 0%,
    var(--border)     50%,
    var(--panel-dark) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
```

### Gated / coming soon

```tsx
<div className="bg-gated border border-gated-border border-dashed p-6 space-y-3">
  <div className="flex items-center gap-3">
    <h3 className="text-[11px] tracking-widest text-gated-foreground uppercase">
      FEATURE NAME
    </h3>
    <span className="text-[8px] tracking-widest uppercase px-2 py-0.5 border border-gated-border text-gated-foreground">
      IN DEVELOPMENT
    </span>
  </div>
  <p className="text-[11px] text-gated-foreground leading-relaxed">
    This feature will be available in Phase 2.
  </p>
</div>
```

---

## 6. Navigation Pattern

### Top bar layout

```tsx
<nav className="border-b border-border bg-panel-dark shrink-0">
  <div className="flex items-center justify-between px-5 h-14">

    {/* Left: Wordmark */}
    <div className="flex flex-col leading-none">
      <span className="text-base font-black tracking-tight text-foreground">
        BIAS AUDIT
      </span>
      <span className="text-[10px] font-light tracking-wide text-muted-foreground">
        dashboard
      </span>
    </div>

    {/* Centre: Nav tabs */}
    <div className="absolute left-1/2 -translate-x-1/2 flex items-center gap-8">
      {NAV_ITEMS.map(item => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.key}
            href={item.href}
            className={`relative py-4 text-[11px] tracking-widest transition-colors ${
              active
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground/70"
            }`}
          >
            {item.label}
            {active && (
              <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-primary" />
            )}
          </Link>
        );
      })}
    </div>

    {/* Right: Account */}
    <AccountButton />

  </div>
</nav>
```

Active state: amber 2px underline + `text-foreground`
Inactive state: `text-muted-foreground` → hover `text-foreground/70`

---

## 7. Wordmark

```tsx
{/* Stacked — login page */}
<div className="flex flex-col items-center gap-2">
  <div className="flex flex-col items-center leading-none">
    <span className="text-xl font-black tracking-tight text-foreground">
      BIAS AUDIT
    </span>
    <span className="text-[11px] font-light tracking-wide text-muted-foreground">
      dashboard
    </span>
  </div>
</div>

{/* Inline — top nav */}
<div className="flex flex-col leading-none">
  <span className="text-base font-black tracking-tight text-foreground">
    BIAS AUDIT
  </span>
  <span className="text-[10px] font-light tracking-wide text-muted-foreground">
    dashboard
  </span>
</div>
```

Rules:
- Top word: always ALL CAPS, `font-black`, `tracking-tight`
- Bottom word: always lowercase, `font-light`, `tracking-wide`, `text-muted-foreground`
- Never on the same line
- No colour changes — always `text-foreground` / `text-muted-foreground`

---

## 8. Animations and Transitions

```tsx
// All interactive elements
className="... transition-colors"
// Never transition-all
```

```css
/* globals.css */
@keyframes status-pulse {
  0%, 100% { opacity: 1;   }
  50%       { opacity: 0.3; }
}
.status-pulse {
  animation: status-pulse 2s ease-in-out infinite;
}
```

Chevron rotation (expand/collapse):
```tsx
<svg className={`w-3 h-3 transition-transform ${expanded ? "rotate-180" : ""}`} />
```

---

## 9. Tailwind Configuration

Uses Tailwind v4. No `tailwind.config.ts`. All theme configuration in `globals.css` inside `@theme inline {}`.

```css
/* app/globals.css */
@import '../styles/tokens.css';
@import 'tailwindcss';

@custom-variant dark (&:is(.dark *));

@theme inline {
  --font-sans: var(--font-inter), 'Inter', system-ui, sans-serif;
  --font-mono: var(--font-jetbrains), 'JetBrains Mono', monospace;

  --color-background:          var(--background);
  --color-foreground:          var(--foreground);
  --color-card:                var(--card);
  --color-card-foreground:     var(--card-foreground);
  --color-primary:             var(--primary);
  --color-primary-foreground:  var(--primary-foreground);
  --color-muted:               var(--muted);
  --color-muted-foreground:    var(--muted-foreground);
  --color-accent:              var(--accent);
  --color-accent-foreground:   var(--accent-foreground);
  --color-destructive:         var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border:              var(--border);
  --color-input:               var(--input);
  --color-ring:                var(--ring);
  --color-panel:               var(--panel);
  --color-panel-dark:          var(--panel-dark);
  --color-recommendations:     var(--recommendations-bg);
  --color-score-high:          var(--score-high);
  --color-score-mid:           var(--score-mid);
  --color-score-low:           var(--score-low);
  --color-verdict-neutral:     var(--verdict-neutral);
  --color-verdict-low:         var(--verdict-low);
  --color-verdict-medium:      var(--verdict-medium);
  --color-verdict-high:        var(--verdict-high);
  --color-gated:               var(--gated);
  --color-gated-border:        var(--gated-border);
  --color-gated-foreground:    var(--gated-foreground);

  --radius-sm: 2px;
  --radius-md: 2px;
  --radius-lg: 2px;
  --radius-xl: 4px;
}

@layer base {
  * { @apply border-border outline-ring/50; }
  body { @apply bg-background text-foreground; }
}
```

---

## 10. Scrollbar Styling

```css
::-webkit-scrollbar { width: var(--scrollbar-width); height: var(--scrollbar-width); }
::-webkit-scrollbar-track { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-thumb-hover); }
::-webkit-scrollbar-corner { background: var(--scrollbar-track); }

* { scrollbar-width: thin; scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track); }

.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
```

---

## 11. Responsive Rules

| Prefix | Width  | Device           |
|--------|--------|------------------|
| (none) | 0px+   | Mobile first     |
| `sm:`  | 640px  | Large phones     |
| `md:`  | 768px  | iPad portrait    |
| `lg:`  | 1024px | Laptop           |
| `xl:`  | 1280px | Desktop          |

Chat analyser on mobile: single column, input fixed at bottom, results scroll above.
Dashboard and fairness panels: `grid grid-cols-1 md:grid-cols-2 gap-4`.
All tap targets minimum 44×44px — `min-h-[44px]`.

---

## 12. Dark Mode

Always dark. No toggle.

```tsx
// app/layout.tsx
<html lang="en" className="dark">
```

---

## 13. Absolute Rules — The Don'ts

### Never hardcode values

```tsx
// WRONG
<div style={{ color: '#E8C547' }}>
<p className="text-[#E8C547]">

// RIGHT
<div className="text-primary">
```

### Never use inline styles except CSS variable injection

```tsx
// Only allowed inline style
<div
  className="score-bar"
  style={{ '--score-bar-width': `${score * 10}%` } as React.CSSProperties}
/>
```

### Nothing loads automatically

```tsx
// WRONG
useEffect(() => { fetchAnalysis(); }, []);

// RIGHT — every API call behind a button click
<button onClick={handleAnalyse}>ANALYSE</button>
```

### No font weights above 500 for body text

```tsx
// WRONG
<p className="font-bold">   // 700
<p className="font-semibold"> // 600

// RIGHT
<p className="font-medium">  // 500
<p className="font-normal">  // 400
// Exception: font-black (900) for wordmark only
```

### Never hover-only on touch

```tsx
// WRONG
<button className="opacity-0 hover:opacity-100">

// RIGHT
<button className="opacity-0 group-hover:opacity-100 focus:opacity-100">
```

---

## Quick Reference

```
Amber accent:      #E8C547  →  text-primary / bg-primary / border-primary
Page canvas:       #0D0D0D  →  bg-background
Card surface:      #141414  →  bg-panel
Elevated surface:  #1A1A1A  →  bg-panel-dark
All borders:       #2A2A2A  →  border-border
Primary text:      #F0F0F0  →  text-foreground
Secondary text:    #888888  →  text-muted-foreground
Score green:       #4CAF50  →  text-score-high
Score amber:       #E8C547  →  text-score-mid
Score red:         #E85D4A  →  text-score-low / text-destructive
Verdict neutral:   #4CAF50  →  text-verdict-neutral
Verdict low:       #E8C547  →  text-verdict-low
Verdict medium:    #E8954A  →  text-verdict-medium
Verdict high:      #E85D4A  →  text-verdict-high

Wordmark top:    font-black tracking-tight   (ALL CAPS)
Wordmark sub:    font-light tracking-wide    (lowercase)
Labels:          text-[9px] tracking-widest uppercase text-muted-foreground
Body:            text-sm text-foreground leading-relaxed
Numbers:         font-mono tabular-nums
Buttons:         text-[10px] tracking-widest uppercase
Radius:          2px everywhere
Border:          border border-border (always 1px)
Transition:      transition-colors (always, never transition-all)
```