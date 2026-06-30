# JanHit UI Design Document

## Philosophy

JanHit is government software for frontline welfare workers in rural India. It is not a startup landing page, not a crypto dashboard, not SaaS analytics. The design must be readable in bright sunlight on budget Android phones, usable on government office desktops, and calm enough for workers who see dozens of citizens per day.

## Design Principles

1. **Extremely readable** — Large type, high contrast, no thin fonts.
2. **Sunlight readable** — Dark text on light backgrounds. No dark mode by default.
3. **Simple icons** — Lucide icons only. No illustrations.
4. **Minimal animation** — No floating blobs, no glassmorphism, no huge gradients.
5. **Fast** — Every screen answers "What does this worker need to do next?"
6. **Calm** — White cards, light gray backgrounds, limited color palette.
7. **Trustworthy** — Looks like government digital infrastructure, not a startup.

## Inspiration

- Apple Health (clarity, large type, calm)
- Stripe Dashboard (clean tables, purposeful buttons)
- UK Government Digital Service (accessibility first, minimal, professional)
- Linear (density without clutter)

## Color System

Only five functional colors plus neutrals:

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary | Deep Blue | `#1e3a5f` | Headers, primary buttons, navigation |
| Success | Green | `#15803d` | Eligible, completed, positive status |
| Warning | Amber | `#b45309` | Pending, needs action, follow-up |
| Error | Red | `#dc2626` | Missing documents, blocked, urgent |
| Background | Light Gray | `#f3f4f6` | Page backgrounds |
| Card | White | `#ffffff` | Cards, panels |
| Text Primary | Near Black | `#111827` | Headings, body text |
| Text Secondary | Gray | `#6b7280` | Labels, captions |

No gradients on cards. No purple. No indigo. No colorful dashboards.

## Typography

- Font: System sans-serif stack (already fast, already familiar on every device)
- Headings: 24px–32px, weight 600
- Body: 16px–18px, weight 400
- Labels: 14px, weight 500, uppercase tracking-wide
- Minimum touch target: 44px height for buttons and inputs

## Layout

- Max content width: 768px for mobile-first screens, 1200px for workspace
- Cards: white background, 1px gray border, 8px border radius, 16px padding
- Spacing: 8px base unit (8, 16, 24, 32, 48)
- Every screen has a clear single purpose

## Screen Inventory

### 1. Landing Page
- Hero: "JanHit" + tagline
- Three primary actions: Run Demo, New Assessment, Field Worker Login
- Three feature cards: Create Beneficiary Case, Find Eligible Schemes, Generate Action Plan
- Workflow illustration (text only, no graphics)

### 2. Beneficiary Assessment
- Step-based form (4 steps)
- Very large controls, progress bar
- Touch-friendly radio buttons, large text inputs
- Demo button pre-fills Asha Devi data

### 3. Eligibility Results
- Large scheme cards
- Each card: scheme name, why eligible, missing docs, estimated next step
- No AI explanations. Plain language.

### 4. Action Plan
- Vertical timeline
- Each step: status badge, owner, due date
- Large cards, clear hierarchy
- This is the hero feature

### 5. Shareable Citizen Record
- Mobile-first, minimal
- Citizen name, current status, next step, where to go
- Nothing else

### 6. Field Worker Workspace
- Task manager layout
- Tabs: Today's Cases, Pending, Completed, Needs Follow-up
- Simple list, not CRM

### 7. District Intelligence
- Minimal charts
- Bar charts only, simple tables, KPI cards
- Government-ready appearance

### 8. Settings
- Language selector
- Font size toggle
- Minimal options

## Demo Mode

- "Run Demo" button on landing page
- Instantly populates assessment with Asha Devi data
- Skips to completed workflow in under 30 seconds
- No typing required for judges

## Accessibility

- WCAG AA minimum, AAA where possible
- Color contrast ratio > 4.5:1 for all text
- Focus indicators visible
- Touch targets >= 44px
- Screen reader friendly labels

## Component Decisions

- **shadcn/ui Button**: Large size default, solid colors only
- **shadcn/ui Card**: White background, subtle border
- **shadcn/ui Progress**: Thick bar, high contrast
- **shadcn/ui Badge**: Solid colors, no outlines for status
- **shadcn/ui Tabs**: Large touch targets, clear active state
- **Custom Timeline**: Vertical, left-aligned, color-coded dots

## Why These Decisions

- **Light theme only**: Rural workers use phones in direct sunlight. Dark screens become unreadable.
- **Large typography**: Budget phones have lower DPI. Older workers may have presbyopia.
- **Limited color palette**: Reduces cognitive load. Workers see many citizens per day.
- **White cards on gray**: Creates clear hierarchy without shadows or glass effects.
- **Step-based assessment**: Breaks complex form into manageable chunks. Shows progress.
- **Timeline action plan**: Visualizes sequence without training. Everyone understands time.
- **Minimal charts**: Government reports prefer tables. Bar charts for comparisons only.
- **No AI language**: Workers and citizens trust clear statements, not "AI-powered" labels.
