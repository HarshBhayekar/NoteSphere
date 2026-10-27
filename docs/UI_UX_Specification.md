# UI/UX DESIGN SPECIFICATION
## Cloud-Based Notes Sharing Platform (NoteSphere)

**Version:** 1.0  
**Design Style:** Modern, Minimal, Academic  
**Target Platforms:** Desktop, Tablet, Mobile  
**Frontend:** HTML5, CSS3, JavaScript (Vanilla)  
**Backend Integration:** Python Flask, Firebase Authentication, Cloud Firestore, Cloudinary  

---

## 1. DESIGN VISION

### Product Identity
The platform functions as a clean, organized, distraction-free academic digital library tailored for college students to upload, browse, and access study materials effortlessly.

### Design Principles
1. **Minimalism:** Clean whitespace, structured cards, zero visual clutter.
2. **Clarity:** Immediate visibility for search, filtering, upload status, and download actions.
3. **Consistency:** Unified typography, spacing tokens, and color semantic badges across all views.
4. **Subtle Motion:** 100–200ms CSS transitions for hover, focus, modals, and toasts.
5. **Accessibility:** WCAG AA compliant contrast, semantic HTML, keyboard accessible controls, and `prefers-reduced-motion` support.
6. **Responsive Design:** 1200px max width container scaling down cleanly across desktop, tablet, and mobile.

---

## 2. COLOR SYSTEM & DESIGN TOKENS

| Token | Name | Hex | Semantic Usage |
|---|---|---|---|
| `--color-primary` | Deep Blue | `#2563EB` | Primary buttons, active tabs, links |
| `--color-primary-hover` | Darker Blue | `#1D4ED8` | Button hover and active press |
| `--color-heading` | Slate 900 | `#0F172A` | Page headings and high-emphasis text |
| `--color-body` | Slate 600 | `#475569` | Descriptions, metadata, and secondary labels |
| `--color-background` | Slate 50 | `#F8FAFC` | App page background |
| `--color-surface` | White | `#FFFFFF` | Cards, navbar, modals, form controls |
| `--color-border` | Slate 200 | `#E2E8F0` | Structural dividers and card borders |
| `--color-success` | Forest Green | `#15803D` | Approved badges, success toasts |
| `--color-warning` | Warm Amber | `#B45309` | Pending moderation badges |
| `--color-error` | Crimson Red | `#B91C1C` | Rejected status, validation errors |
| `--color-soft-blue` | Blue 50 | `#EFF6FF` | Hero accent, search containers, banners |

---

## 3. TYPOGRAPHY & SPACING TOKENS

**Primary Font:** `Inter`, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif.

| Element | Desktop Size | Weight |
|---|---|---|
| Main Page Heading (H1) | 32–36 px | 700 (Bold) |
| Section Heading (H2) | 22–24 px | 600 (SemiBold) |
| Card Title (H3) | 16–18 px | 600 (SemiBold) |
| Body Text | 14–16 px | 400 (Regular) |
| Button Text | 14–15 px | 600 (SemiBold) |
| Form Labels | 14 px | 500 (Medium) |
| Metadata / Badges | 12–13 px | 400 / 500 |

### Spacing Scale (4px Base)
- **XS (4px):** Icon gaps, micro spacing
- **SM (8px):** Compact element gaps, button inner padding
- **MD (16px):** Form inputs, card padding, default gutters
- **LG (24px):** Section sub-spacing, modal padding
- **XL (32px):** Container padding on desktop
- **2XL (48px):** Section division
- **3XL (64px):** Hero section vertical padding

### Radii & Shadows
- **Card Radius:** 12 px
- **Input / Button Radius:** 8 px
- **Badge Radius:** 9999 px (Pill) or 6 px
- **Border:** 1px solid `#E2E8F0`
- **Subtle Elevation:** `0 4px 12px rgba(15, 23, 42, 0.05)`

---

## 4. APPLICATION VIEWS & INTERFACES

### 4.1 Home Page (`index.html`)
- **Navigation Bar:** Brand logo + NoteSphere title, Navigation links (Home, Browse Notes), Auth buttons (Login, Sign Up / Upload Notes, User dropdown).
- **Hero Section:** "Your Study Materials, All in One Place." with direct search bar and quick action buttons.
- **Browse by Semester:** Quick shortcut cards (Semester 1 through Semester 6).
- **Recent Notes Grid:** 3 columns desktop, 2 tablet, 1 mobile. Cards include PDF badge, title, subject, semester, date, download action.
- **Upload CTA Banner:** Soft blue highlight encouraging peer contributions.
- **Footer:** Informational links, semester list, and copyright.

### 4.2 Browse Notes (`browse.html`)
- **Filters Row:** Live text search + Subject dropdown + Semester dropdown + Department filter + Sort dropdown (Newest / Most Downloaded) + "Clear Filters".
- **Notes Grid:** Responsive approved note cards.
- **Empty State:** Clean illustration/icon with "No notes found" and "Clear Filters" CTA.
- **Loading State:** Subtle pulse/shimmer skeleton cards.

### 4.3 Note Details (`note-details.html`)
- **Main Section:** Note title, subject, semester, department, full description, upload date, contributor attribution.
- **Action Box:** PDF file type badge, file size in MB, Download button (triggers secure backend count & download), optional PDF preview container.

### 4.4 Authentication (`login.html` & `register.html`)
- Centered card on `#F8FAFC`.
- Clean form fields with visible labels and password visibility toggle.
- Friendly error displays directly under inputs.

### 4.5 Upload Notes (`upload.html`)
- Form with Title, Subject, Semester, Department, Description.
- Interactive drag-and-drop dropzone for PDF (max 10MB).
- Real-time file name and size display upon selection.
- Clear upload progress and pending approval status alert.

### 4.6 My Uploads (`my-uploads.html`)
- Tabular / Card view of the user's submissions.
- Status badges:
  - `Pending` (Amber)
  - `Approved` (Green)
  - `Rejected` (Red, reveals admin rejection reason on click/hover).
- "Upload More Notes" primary button.

### 4.7 Admin Dashboard & Moderation (`admin-dashboard.html`)
- **Metrics Cards:** Total Notes, Pending Review, Published Notes, Total Downloads.
- **Moderation Table:** Document title, subject, semester, uploader, date, status, actions.
- **Moderation Actions:**
  - View / Inspect PDF
  - Approve (turns status to `approved`)
  - Reject (opens modal for rejection reason)
  - Delete (confirmation modal; deletes Firestore record and purges Cloudinary asset).

---

## 5. UI COMPONENTS & MICRO-INTERACTIONS

- **CSS Transitions:** Standard 150ms–200ms ease-out transitions for buttons, card elevation, and modal backdrops.
- **Status Badges:** Distinct semantic pill badges:
  - Pending: `bg: #FEF3C7; text: #B45309`
  - Approved: `bg: #DCFCE7; text: #15803D`
  - Rejected: `bg: #FEE2E2; text: #B91C1C`
- **Toast Notifications:** Fixed top-right floating notifications for success, warning, and error messages.
- **Modal Dialogs:** Accessible backdrop with ESC key and click-outside dismissal.
