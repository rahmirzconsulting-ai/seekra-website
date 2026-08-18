# Brief: Sidebar Navigation Redesign — Grouped Sections with Collapsible Headers

**For:** Kimi
**Effort:** 1 day
**Files:** Frontend only — no backend changes

## Context

The current sidebar is a flat list of 17+ items with no logical grouping. Each new feature adds another item, making it increasingly hard to navigate. This brief redesigns the sidebar into **grouped, collapsible sections** — similar to the reference screenshot provided.

## Reference design pattern (from the screenshot)

The reference shows:
- **Section headers** in muted gray text with a chevron (▼ expanded / ▶ collapsed)
- **Items within sections** with line-style icons
- **Active state** = left border accent + subtle background fill
- **Accordion collapse/expand** — sections can be collapsed
- **Horizontal separator** before the bottom system items

## Seekra's new sidebar structure

### Dashboard (standalone, at top — no section header)

```
[Seekra logo]  Seekra
─────────────────────────
🏠 Dashboard
```

### Section 1: DISCOVER (always expanded — primary navigation)

Visible to: viewer, editor, admin (anyone with content access)

```
DISCOVER                    ▼
  🔍  Search
  💬  AI Chat
  🔖  Saved Searches
```

### Section 2: MANAGE (collapsible)

Visible to: editor, admin (viewers excluded — they can't upload/manage files)

```
MANAGE                      ▼
  📁  Files
  ⬆️  Upload
  📋  Duplicates
```

### Section 3: GOVERNANCE (collapsible)

Visible to: auditor, admin

```
GOVERNANCE                  ▼
  📋  Audit Trail
  🛡️  PII Report
  📖  Governance Reference
  🔗  Provenance
```

### Section 4: ADMINISTRATION (collapsible)

Visible to: admin only

```
ADMINISTRATION              ▼
  👥  Users
  🔑  Permissions
  📁  Collections
  📊  System Analytics
```

### Section 5: INTELLIGENCE (collapsible)

Visible to: admin only

```
INTELLIGENCE                ▼
  🕸️  Entity Graph
```

### Bottom bar (below a horizontal separator)

```
─────────────────────────
  [theme toggle]  [lang]  ⚙️ Settings  [logout]
```

## Exact changes to make

### File 1: `frontend/src/components/sidebar-nav.tsx` — full rewrite of the nav structure

Replace the flat `mainNav` + `adminNav` arrays with a **sectioned structure**:

```typescript
interface NavItem {
  href: string;
  icon: LucideIcon;
  label: string;
}

interface NavSection {
  labelKey: string;          // i18n key for the section header
  fallbackLabel: string;     // English fallback
  items: NavItem[];
  roles: string[];            // which user roles can see this section
  defaultCollapsed: boolean;  // initial state
}

const navSections: NavSection[] = [
  {
    labelKey: "nav.sectionDiscover",
    fallbackLabel: "Discover",
    roles: ["viewer", "editor", "admin"],
    defaultCollapsed: false,  // always expanded — primary nav
    items: [
      { href: "/search/", icon: Search, label: t("nav.search") },
      { href: "/chat/", icon: MessageSquare, label: t("nav.chat") },
      { href: "/saved-searches/", icon: Bookmark, label: tf("nav.saved", "Saved") },
    ],
  },
  {
    labelKey: "nav.sectionManage",
    fallbackLabel: "Manage",
    roles: ["editor", "admin"],
    defaultCollapsed: false,
    items: [
      { href: "/files/", icon: FolderOpen, label: t("nav.files") },
      { href: "/upload/", icon: Upload, label: t("nav.upload") },
      { href: "/duplicates/", icon: Copy, label: tf("nav.duplicates", "Duplicates") },
    ],
  },
  {
    labelKey: "nav.sectionGovernance",
    fallbackLabel: "Governance",
    roles: ["auditor", "admin"],
    defaultCollapsed: true,   // collapsed by default — expanded when visiting a governance page
    items: [
      { href: "/admin/audit/", icon: ClipboardList, label: tf("nav.audit", "Audit") },
      { href: "/admin/pii/", icon: ShieldAlert, label: tf("nav.pii", "PII") },
      { href: "/admin/governance/", icon: BookOpen, label: tf("nav.governance", "Governance") },
      { href: "/admin/provenance/", icon: Network, label: tf("nav.provenance", "Provenance") },
    ],
  },
  {
    labelKey: "nav.sectionAdmin",
    fallbackLabel: "Administration",
    roles: ["admin"],
    defaultCollapsed: true,
    items: [
      { href: "/admin/users/", icon: Users, label: t("nav.users") },
      { href: "/admin/permissions/", icon: KeyRound, label: tf("nav.permissions", "Permissions") },
      { href: "/admin/collections/", icon: FolderOpen, label: tf("nav.collections", "Collections") },
      { href: "/admin/analytics/", icon: BarChart3, label: tf("nav.system", "System") },
    ],
  },
  {
    labelKey: "nav.sectionIntelligence",
    fallbackLabel: "Intelligence",
    roles: ["admin"],
    defaultCollapsed: true,
    items: [
      { href: "/admin/entities/", icon: Share2, label: tf("nav.entities", "Entities") },
    ],
  },
];
```

### Dashboard as a standalone item (above sections)

The Dashboard (`/`) is NOT inside any section — it's a standalone item at the top, like a "home" button:

```tsx
{/* Dashboard — standalone, above sections */}
{canAccessContent && !isViewer && (
  <Link
    href="/"
    className={cn("nav-item nav-item-standalone", isActive("/") && "nav-item-active")}
  >
    <LayoutDashboard className="w-4 h-4" />
    <span>{t("nav.dashboard")}</span>
  </Link>
)}

{/* Horizontal separator */}
<div className="nav-separator" />
```

### Section rendering with collapse/expand

```tsx
{navSections
  .filter(section => section.roles.some(role => userHasRole(role)))
  .map(section => {
    const collapsed = collapsedSections[section.labelKey] ?? section.defaultCollapsed;
    const hasActiveItem = section.items.some(item => isActive(item.href));

    return (
      <div key={section.labelKey} className="nav-section">
        {/* Section header — clickable to toggle */}
        <button
          onClick={() => toggleSection(section.labelKey)}
          className="nav-section-header"
          aria-expanded={!collapsed}
        >
          <span className="nav-section-label">
            {tf(section.labelKey, section.fallbackLabel)}
          </span>
          {collapsed ? (
            <ChevronRight className="w-3 h-3 nav-chevron" />
          ) : (
            <ChevronDown className="w-3 h-3 nav-chevron" />
          )}
        </button>

        {/* Items — hidden when collapsed, UNLESS the active page is in this section */}
        {(!collapsed || hasActiveItem) && (
          <ul className="nav-section-items">
            {section.items.map(item => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn("nav-item", isActive(item.href) && "nav-item-active")}
                >
                  <item.icon className="w-4 h-4 nav-item-icon" />
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  })}
```

**Key UX rule:** If the active page is inside a collapsed section, that section auto-expands. The user never loses their place.

### Collapse state persistence

```typescript
const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>(() => {
  try {
    const saved = localStorage.getItem("seekra_nav_collapsed");
    return saved ? JSON.parse(saved) : {};
  } catch {
    return {};
  }
});

const toggleSection = (key: string) => {
  setCollapsedSections(prev => {
    const next = { ...prev, [key]: !prev[key] };
    try {
      localStorage.setItem("seekra_nav_collapsed", JSON.stringify(next));
    } catch {}
    return next;
  });
};

// Auto-expand the section containing the active page
useEffect(() => {
  const activeSection = navSections.find(s =>
    s.items.some(i => pathname.startsWith(i.href.replace(/\/$/, "")))
  );
  if (activeSection && collapsedSections[activeSection.labelKey]) {
    setCollapsedSections(prev => ({ ...prev, [activeSection.labelKey]: false }));
  }
}, [pathname]);
```

### Styling — match the reference screenshot pattern

Use Seekra's brand palette (the existing CSS variables from `globals.css`). Don't introduce new colors — use the existing `primary`, `accent`, `muted`, `border` tokens.

```css
/* Section header — muted text, smaller font, clickable */
.nav-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted-foreground);
  cursor: pointer;
  user-select: none;
  transition: color 150ms;
}
.nav-section-header:hover {
  color: var(--foreground);
}

/* Section label */
.nav-section-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

/* Chevron */
.nav-chevron {
  opacity: 0.5;
  transition: transform 200ms;
}

/* Nav items within a section */
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px 8px 24px;  /* extra left padding = indentation under section */
  font-size: 14px;
  font-weight: 500;
  color: var(--muted-foreground);
  border-radius: 8px;
  transition: all 150ms;
}
.nav-item:hover {
  background: var(--accent);
  color: var(--accent-foreground);
}

/* Active state — left border accent + background fill (like the reference screenshot) */
.nav-item-active {
  color: var(--primary);
  font-weight: 600;
  position: relative;
}
.nav-item-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--primary);
  border-radius: 0 2px 2px 0;
}

/* Standalone dashboard item (above sections) */
.nav-item-standalone {
  padding-left: 12px;  /* no section indentation */
}

/* Horizontal separator */
.nav-separator {
  height: 1px;
  background: var(--border);
  margin: 8px 12px;
}
```

### File 2: `frontend/src/components/bottom-nav.tsx` — update the "More" drawer

The mobile bottom-nav's "More" drawer should use the same grouped sections. The drawer currently shows a flat list — update it to render the same `navSections` structure (without collapse/expand — all expanded in the drawer since it's already a modal).

### File 3: i18n strings — `frontend/src/i18n/dictionaries/en.json` + `ar.json`

```json
// en.json — add these keys
"nav.sectionDiscover": "Discover",
"nav.sectionManage": "Manage",
"nav.sectionGovernance": "Governance",
"nav.sectionAdmin": "Administration",
"nav.sectionIntelligence": "Intelligence",
"nav.duplicates": "Duplicates",

// ar.json — add these keys
"nav.sectionDiscover": "اكتشاف",
"nav.sectionManage": "إدارة",
"nav.sectionGovernance": "الحوكمة",
"nav.sectionAdmin": "الإدارة",
"nav.sectionIntelligence": "الذكاء",
"nav.duplicates": "المكررات",
```

## What NOT to touch

- **Backend** — no changes at all
- **Routing** — all routes stay the same (`/search/`, `/chat/`, `/admin/users/`, etc.)
- **The admin layout** (`admin/layout.tsx`) — the role gate stays as-is
- **The page content** — this is purely a navigation redesign
- **The top-nav** (`top-nav.tsx`) — the top bar (logo, theme, language, settings, logout) stays as-is

## How to verify

### Test 1 — Sections render with headers

Navigate to `/search/` as admin. The sidebar should show:
- Dashboard (standalone, at top)
- Separator
- DISCOVER section (expanded) → Search, AI Chat, Saved Searches
- MANAGE section (expanded) → Files, Upload, Duplicates
- GOVERNANCE section (expanded or collapsed) → Audit, PII, Governance, Provenance
- ADMINISTRATION section (expanded or collapsed) → Users, Permissions, Collections, System
- INTELLIGENCE section (expanded or collapsed) → Entity Graph

### Test 2 — Collapse/expand works

Click a section header. It should collapse (items hidden). Click again → expands. The chevron should rotate.

### Test 3 — Active page auto-expands its section

Collapse the GOVERNANCE section. Navigate to `/admin/audit/`. The GOVERNANCE section should auto-expand because the active page is inside it.

### Test 4 — Collapse state persists

Collapse the ADMINISTRATION section. Navigate to another page. Navigate back. The ADMINISTRATION section should still be collapsed (state persisted in localStorage).

### Test 5 — Role-based visibility

Log in as a viewer. The sidebar should show only:
- Dashboard (if visible to viewers)
- DISCOVER section → Search, AI Chat, Saved Searches

No MANAGE, GOVERNANCE, ADMINISTRATION, or INTELLIGENCE sections.

Log in as an auditor. Should show DISCOVER + GOVERNANCE (but not ADMINISTRATION or INTELLIGENCE).

### Test 6 — Active state styling

Navigate to any page. The active nav item should have:
- A left border accent (3px, primary color)
- A subtle background fill
- Bold text

### Test 7 — RTL (Arabic mode)

Switch to Arabic. The sidebar should flip to the right side. Section headers, items, and chevrons should all render correctly in RTL. The left border accent on the active item should appear on the RIGHT side (use logical properties: `inset-inline-start` instead of `left`).

### Test 8 — Mobile bottom-nav "More" drawer

On mobile (viewport < 768px), open the bottom-nav "More" drawer. It should show the same grouped sections (all expanded, no collapse/expand in the drawer).

### Test 9 — Production health

```bash
curl -s https://app-internal.seekra.pk/api/health | python3 -m json.tool
```

## Commit message

```
Sidebar redesign: grouped sections with collapsible headers

Replaced the flat 17-item nav list with 5 grouped sections:
- DISCOVER (Search, Chat, Saved) — all content users
- MANAGE (Files, Upload, Duplicates) — editors + admins
- GOVERNANCE (Audit, PII, Governance, Provenance) — auditors + admins
- ADMINISTRATION (Users, Permissions, Collections, System) — admins
- INTELLIGENCE (Entity Graph) — admins

Dashboard is a standalone item at the top (not inside a section).

Sections are collapsible (accordion pattern). Active page's section
auto-expands. Collapse state persists in localStorage.

Active item has left-border accent + background fill (matching the
reference design pattern).

Mobile bottom-nav "More" drawer uses the same grouped structure.

i18n: section headers in EN + AR.
```

## Questions before you start

1. **Should the Dashboard be visible to viewers?** Currently viewers are redirected to `/search/` and don't see the dashboard. My recommendation: keep this behavior — viewers don't need the dashboard. The sidebar for viewers starts directly with DISCOVER.

2. **Should sections have icons (next to the header text)?** The reference screenshot doesn't show section icons — just text headers. My recommendation: no icons on section headers — keep them as clean text labels with chevrons. Icons are on the items within.

3. **Should the GOVERNANCE/ADMIN/INTELLIGENCE sections be collapsed by default?** My recommendation: yes — these are secondary navigation. The primary sections (DISCOVER, MANAGE) are expanded by default. Admin sections expand only when the user navigates to an admin page.

4. **Should there be a "collapse all" / "expand all" button?** My recommendation: no — keep it simple. Each section toggles independently. The auto-expand-on-active-page behavior handles the common case.
