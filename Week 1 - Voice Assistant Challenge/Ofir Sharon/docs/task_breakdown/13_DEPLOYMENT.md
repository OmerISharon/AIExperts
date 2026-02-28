# Task 13: Widget Embedding & Deployment

## Objective
Prepare the Maya widget for production deployment: create the embeddable widget loader script, configure Vercel deployment, set up environment variables for production, create iframe embedding instructions, test cross-origin embedding, and write the deployment README.

---

## Context
The Maya widget will be deployed to Vercel and embedded on the EZpresence platform (and potentially other sites) via iframe or a JavaScript widget loader. It needs to work reliably as both a standalone page and an embedded component.

---

## Dependencies
- **Task 12** (fully integrated, working application)
- Vercel account
- Production API keys (OpenAI, LiveKit, email service)

---

## Part 1: Widget Embedding System

### Option A: iframe Embedding (Simpler, Recommended)

Create a dedicated `/widget` route that renders the Maya widget in a minimal, no-chrome page.

**File: `src/pages/Widget.tsx` (or dedicated route)**
```typescript
import { MayaWidget } from "../components/MayaWidget";

export default function WidgetPage() {
  return (
    <div
      style={{
        width: "100%",
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "transparent",
        padding: 0,
        margin: 0,
      }}
    >
      <MayaWidget />
    </div>
  );
}
```

**HTML embed code for EZpresence:**
```html
<iframe
  src="https://maya-ezpresence.vercel.app/widget"
  width="420"
  height="650"
  style="border: none; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12);"
  allow="microphone"
  title="Maya - EZpresence Hostess"
></iframe>
```

**Critical:** The `allow="microphone"` attribute is required for the iframe to access the user's mic.

### Option B: JavaScript Widget Loader (Floating Button)

Create a loader script that injects a floating button + iframe on the host page.

**File: `public/widget-loader.js`**

```javascript
(function () {
  "use strict";

  const WIDGET_URL = "https://maya-ezpresence.vercel.app/widget";
  const DEFAULT_CONFIG = {
    position: "bottom-right",
    buttonColor: "#7C3AED",
    buttonSize: 60,
    widgetWidth: 420,
    widgetHeight: 650,
  };

  window.MayaWidget = {
    init: function (userConfig) {
      const config = { ...DEFAULT_CONFIG, ...userConfig };

      // Create floating button
      const button = document.createElement("div");
      button.id = "maya-widget-button";
      button.innerHTML = `
        <svg width="28" height="28" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      `;
      Object.assign(button.style, {
        position: "fixed",
        bottom: "24px",
        right: config.position === "bottom-left" ? "auto" : "24px",
        left: config.position === "bottom-left" ? "24px" : "auto",
        width: config.buttonSize + "px",
        height: config.buttonSize + "px",
        borderRadius: "50%",
        backgroundColor: config.buttonColor,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
        zIndex: "99999",
        transition: "transform 0.2s, box-shadow 0.2s",
      });
      button.onmouseenter = () => {
        button.style.transform = "scale(1.1)";
        button.style.boxShadow = "0 6px 20px rgba(0,0,0,0.2)";
      };
      button.onmouseleave = () => {
        button.style.transform = "scale(1)";
        button.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
      };

      // Create widget container (hidden initially)
      const container = document.createElement("div");
      container.id = "maya-widget-container";
      Object.assign(container.style, {
        position: "fixed",
        bottom: "96px",
        right: config.position === "bottom-left" ? "auto" : "24px",
        left: config.position === "bottom-left" ? "24px" : "auto",
        width: config.widgetWidth + "px",
        height: config.widgetHeight + "px",
        borderRadius: "12px",
        overflow: "hidden",
        boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
        zIndex: "99998",
        display: "none",
        transition: "opacity 0.3s, transform 0.3s",
        opacity: "0",
        transform: "translateY(20px)",
      });

      const iframe = document.createElement("iframe");
      iframe.src = WIDGET_URL;
      iframe.allow = "microphone";
      iframe.title = "Maya - EZpresence Hostess";
      Object.assign(iframe.style, {
        width: "100%",
        height: "100%",
        border: "none",
      });
      container.appendChild(iframe);

      // Toggle logic
      let isOpen = false;
      button.onclick = function () {
        isOpen = !isOpen;
        if (isOpen) {
          container.style.display = "block";
          requestAnimationFrame(() => {
            container.style.opacity = "1";
            container.style.transform = "translateY(0)";
          });
        } else {
          container.style.opacity = "0";
          container.style.transform = "translateY(20px)";
          setTimeout(() => {
            container.style.display = "none";
          }, 300);
        }
      };

      // Listen for close message from widget
      window.addEventListener("message", function (event) {
        if (event.data === "maya-widget-close") {
          isOpen = false;
          container.style.opacity = "0";
          container.style.transform = "translateY(20px)";
          setTimeout(() => {
            container.style.display = "none";
          }, 300);
        }
      });

      document.body.appendChild(button);
      document.body.appendChild(container);
    },
  };
})();
```

**Usage on host site:**
```html
<script src="https://maya-ezpresence.vercel.app/widget-loader.js"></script>
<script>
  MayaWidget.init({ position: 'bottom-right' });
</script>
```

### postMessage Communication

The widget iframe can communicate with the parent page:

**From widget to parent (close widget):**
```typescript
// Inside MayaWidget, when "Close" is clicked:
const handleClose = () => {
  if (window.parent !== window) {
    window.parent.postMessage("maya-widget-close", "*");
  }
};
```

**From parent to widget (optional commands):**
```typescript
// Inside widget, listen for commands:
window.addEventListener("message", (event) => {
  if (event.data === "maya-widget-open-call") {
    // Auto-start a conversation
  }
});
```

---

## Part 2: Vercel Deployment

### Project Configuration

**File: `vercel.json`**
```json
{
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "headers": [
    {
      "source": "/widget",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "ALLOWALL"
        },
        {
          "key": "Content-Security-Policy",
          "value": "frame-ancestors *"
        }
      ]
    },
    {
      "source": "/widget-loader.js",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/$1"
    }
  ]
}
```

**Critical headers:**
- `/widget` route needs `X-Frame-Options: ALLOWALL` and `Content-Security-Policy: frame-ancestors *` to allow iframe embedding
- `/widget-loader.js` needs `Access-Control-Allow-Origin: *` to be loadable from any domain
- API routes need proper CORS for cross-origin requests from the iframe

### Environment Variables on Vercel

Set these in Vercel dashboard → Settings → Environment Variables:

```
# Server-side (NOT prefixed with VITE_)
OPENAI_API_KEY=sk-...
LIVEKIT_API_KEY=API...
LIVEKIT_API_SECRET=...
DATABASE_URL=postgresql://...
FEEDBACK_EMAIL=contact@ezpresence.com
SENDGRID_API_KEY=SG...

# Client-side (prefixed with VITE_)
VITE_LIVEKIT_URL=wss://your-app.livekit.cloud
VITE_API_BASE_URL=https://maya-ezpresence.vercel.app
```

### Deployment Steps

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy (first time — will prompt for project setup)
vercel

# 4. Set environment variables
vercel env add OPENAI_API_KEY
vercel env add LIVEKIT_API_KEY
# ... etc

# 5. Deploy to production
vercel --prod
```

### Build Verification

Before deploying, verify locally:

```bash
# Build
npm run build

# Preview production build
npm run preview

# Check for:
# ✅ No build errors
# ✅ No TypeScript errors
# ✅ Assets load correctly
# ✅ API routes work
# ✅ Widget page renders at /widget
```

---

## Part 3: CORS & Security for Embedding

### API CORS Middleware

All API routes need CORS for cross-origin iframe requests:

```typescript
// src/lib/cors.ts
export function corsHeaders(origin?: string) {
  return {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

// In each API route:
export async function OPTIONS() {
  return new Response(null, { status: 204, headers: corsHeaders() });
}

export async function POST(req: Request) {
  // ... handler logic
  return Response.json(data, { headers: corsHeaders() });
}
```

### Mic Permissions in iframe

- The embedding page MUST include `allow="microphone"` on the iframe
- The widget page must be served over HTTPS
- Some browsers may show a separate permission prompt for iframed content

### Content Security Policy

If the host site has a strict CSP, they may need to add:
```
frame-src https://maya-ezpresence.vercel.app;
```

---

## Part 4: README & Documentation

Create `README.md` with:

1. **Project overview** (what Maya is)
2. **Quick start** (how to run locally)
3. **Environment setup** (all required env vars)
4. **Deployment** (Vercel steps)
5. **Embedding** (iframe and widget-loader code snippets)
6. **Architecture** (high-level component diagram)
7. **API reference** (endpoints and payloads)
8. **Customization** (how to modify system prompt, add features, change voice)
9. **Troubleshooting** (common issues)

---

## Part 5: Production Checklist

### Pre-Launch
- [ ] All API keys are production keys (not test/dev)
- [ ] Database is provisioned and schema created
- [ ] Email service configured and verified (test feedback email)
- [ ] Error logging configured (Vercel logs, or add Sentry)
- [ ] Build succeeds without warnings
- [ ] No `console.log` statements in production code (use proper logger)
- [ ] `dangerouslyAllowBrowser: true` removed from OpenAI client (using proxy)

### Embedding Tests
- [ ] iframe embedding works on EZpresence site
- [ ] Widget-loader floating button works
- [ ] Mic permission works inside iframe
- [ ] Widget opens/closes smoothly
- [ ] postMessage close works from widget to parent
- [ ] No CORS errors in console
- [ ] Widget renders correctly on mobile within iframe

### Functionality Tests
- [ ] Full conversation (start → talk → end → feedback) works in production
- [ ] Feedback email received at contact@ezpresence.com
- [ ] Transcript stored in database
- [ ] Multiple concurrent users don't conflict
- [ ] Widget works after page refresh
- [ ] Widget works across browser tabs

### Performance Tests
- [ ] Widget loads in < 3 seconds
- [ ] First voice response in < 5 seconds
- [ ] TTS playback starts within 2 seconds of GPT response
- [ ] No memory leaks during extended conversations (15+ turns)
- [ ] Widget doesn't degrade host page performance

---

## Acceptance Criteria

- [ ] Widget deployable to Vercel with `vercel --prod`
- [ ] iframe embedding works with `<iframe allow="microphone">`
- [ ] Widget-loader.js creates floating button that opens/closes widget
- [ ] All API routes have proper CORS headers
- [ ] Environment variables configured on Vercel
- [ ] `vercel.json` configured with proper headers and rewrites
- [ ] README.md with complete setup and embedding instructions
- [ ] Production build has no errors or warnings
- [ ] Widget works in production on a test page
- [ ] Mic permissions work inside iframe on HTTPS

---

## Output Files
- `vercel.json`
- `public/widget-loader.js`
- `src/pages/Widget.tsx` (or equivalent route)
- `src/lib/cors.ts`
- `README.md`
- `.env.example` (updated with all variables)
