# KARIS OS™ Version 1.0.0-PROD-V1 — Brand Guidelines & High-Resolution Vector Assets

**Document Version:** 15.0.0-PROD-V1 (`Commercial & Brand Track`)  
**Target Audience:** UI/UX Designers, Frontend React/Next.js Developers & Commercial Brand Managers  
**Enforces:** Section 31 (`Omnichannel Portal Gateway`), Section 53 (`White-Label Customization Engine`), and Brand Consistency across Kenya & East Africa (`Africa/Nairobi`)

---

## 1. Official Brand Identity & Color Palette (`CSS Variables`)

Our visual identity reflects trust, institutional cryptographic security (`Rule 9`), and agricultural vitality (`KARIS FARM™`). Below are the official CSS design tokens located in `/home/user/karis-os-core/BRAND_ASSETS/karis_os_color_palette.css`:

```css
:root {
  /* Primary Institutional Palette */
  --karis-navy: #0B2545;       /* Deep Navy: Master headers, executive C-suite cards, primary typography */
  --karis-slate: #134074;      /* Slate Blue: Secondary navigation, active tab borders, gradient accents */
  --karis-blue: #1D4ED8;       /* Royal Blue: Primary action buttons, active links, PalPlus checkouts (`#2563EB`) */
  --karis-light-blue: #EFF6FF; /* Ice Blue: Card backgrounds, hover states, data tables */

  /* Specialized Vertical & Incentive Palette */
  --karis-emerald: #10B981;    /* Emerald Green: KARIS FARM produce traceability, Rule 9 verified clean badges */
  --karis-forest: #059669;     /* Forest Green: Agricultural harvest batch status, Safaricom M-Pesa Enterprise white-label */
  --karis-gold: #F59E0B;       /* East African Gold: POWER BOT X prediction economy, KRT loyalty token badges */
  --karis-purple: #8B5CF6;     /* Royal Purple: KARIS INNOVATION SUITE (`Pharma-Trace, Prop-Share, Edu-Pay`) */
  --karis-pink: #EC4899;       /* Magenta Pink: KARIS LOOP™ social intelligence, creator tipping badges (`50 KRT`) */
  --karis-maroon: #8B0000;     /* Equity Red: Equity Bank Fintech Hub white-label profile (`Section 53`) */

  /* System Grays & Borders */
  --karis-bg: #F8FAFC;         /* Master application canvas background */
  --karis-border: #E2E8F0;     /* Clean structural table and panel borders */
  --karis-text: #1E293B;       /* High-contrast body text */
  --karis-muted: #64748B;      /* Secondary captions and timestamps */
}
```

---

## 2. High-Resolution SVG Vector Logos (`Ready for Web, Mobile & Print`)

All vector logos are standalone, scalable, and self-contained right inside your `BRAND_ASSETS/` folder:

### **A. Primary Navy Vector Logo (`BRAND_ASSETS/karis_os_logo_navy.svg`):**
Ideal for light backgrounds (`#F8FAFC`, `#FFFFFF`), invoice headers, and formal PDF/Word engineering manuals:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100" width="100%" height="100%">
  <rect width="400" height="100" rx="16" fill="#F8FAFC"/>
  <circle cx="50" cy="50" r="32" fill="#0B2545"/>
  <path d="M40 34 L54 50 L40 66 M54 50 L68 34 M54 50 L68 66" stroke="#10B981" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="96" y="58" font-family="Arial, -apple-system, sans-serif" font-weight="900" font-size="34" fill="#0B2545" letter-spacing="-1">KARIS <tspan fill="#1D4ED8">OS</tspan>™</text>
  <text x="98" y="78" font-family="Arial, -apple-system, sans-serif" font-weight="600" font-size="11" fill="#64748B" letter-spacing="1.5">ENTERPRISE &amp; DIGITAL ECONOMY PLATFORM</text>
</svg>
```

### **B. Primary White/Negative Vector Logo (`BRAND_ASSETS/karis_os_logo_white.svg`):**
Ideal for dark headers (`#0B2545`), dark mode dashboards, and executive slide presentations:
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 100" width="100%" height="100%">
  <rect width="400" height="100" rx="16" fill="#0B2545"/>
  <circle cx="50" cy="50" r="32" fill="#1D4ED8"/>
  <path d="M40 34 L54 50 L40 66 M54 50 L68 34 M54 50 L68 66" stroke="#10B981" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="96" y="58" font-family="Arial, -apple-system, sans-serif" font-weight="900" font-size="34" fill="#FFFFFF" letter-spacing="-1">KARIS <tspan fill="#10B981">OS</tspan>™</text>
  <text x="98" y="78" font-family="Arial, -apple-system, sans-serif" font-weight="600" font-size="11" fill="#93C5FD" letter-spacing="1.5">ENTERPRISE &amp; DIGITAL ECONOMY PLATFORM</text>
</svg>
```

---

## 3. Marketing & Onboarding Copy for Commercial Licensees

When pitching to commercial banking licensees (`Safaricom, Equity Bank, PalPlus`) or agricultural cooperatives:
* **The Master Tagline:** *"One Identity. One Double-Entry Kernel. Nineteen Industry Verticals."*
* **The Agricultural Elevator Pitch:** *"Digitize smallholder farming from seed input financing through harvest QR traceability (`KARIS-TRACE-QR-...`) to supermarket checkout (`KES + KRT mixed payments`), guaranteeing instant settlement under exact double-entry protection (`Rule 9`)."*
* **The Social & AI Prediction Pitch:** *"Power self-improving digital economies (`POWER BOT X` & `KARIS LOOP™`) where short-form video, WhatsApp status kits (`wa.me`), and shoppable product checkouts operate natively on KRT tokens without leaving your wallet."*

All vector assets and stylesheets are ready for immediate frontend incorporation.
