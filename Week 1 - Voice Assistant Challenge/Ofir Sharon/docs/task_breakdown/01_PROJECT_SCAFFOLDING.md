# Task 01: Project Scaffolding & Configuration

## Objective
Create the foundational React + TypeScript project with all dependencies installed, Tailwind CSS configured, project directory structure created, and environment variable template in place. Every subsequent task depends on this.

---

## Context
You are building **Maya the EZpresence Hostess** — a speech-to-speech conversational AI widget. This task sets up the empty project skeleton that all other tasks will build into.

**Tech choices:**
- **Vite** (fast dev server, better than CRA)
- **React 18+** with TypeScript
- **Tailwind CSS v3** for styling
- **pnpm** or **npm** as package manager

---

## Steps

### 1. Initialize Project

```bash
npm create vite@latest maya-ezpresence -- --template react-ts
cd maya-ezpresence
npm install
```

### 2. Install All Dependencies

Install everything the project will need across all tasks:

```bash
# Core UI
npm install tailwindcss @tailwindcss/forms postcss autoprefixer

# LiveKit (real-time voice)
npm install @livekit/components-react @livekit/components-styles livekit-client

# OpenAI (GPT-4, Whisper, TTS)
npm install openai

# Utility
npm install clsx uuid
npm install -D @types/uuid

# Optional: ElevenLabs TTS
npm install elevenlabs
```

### 3. Configure Tailwind CSS

Initialize Tailwind:
```bash
npx tailwindcss init -p
```

Update `tailwind.config.ts`:
```typescript
import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          purple: '#7C3AED',
          'purple-light': '#A78BFA',
          'purple-dark': '#5B21B6',
          teal: '#14B8A6',
          'teal-light': '#5EEAD4',
          'teal-dark': '#0D9488',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        'widget': '12px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-out': 'fadeOut 0.3s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config
```

Update `src/styles/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### 4. Create Directory Structure

Create all directories that will be populated by subsequent tasks:

```
src/
├── components/        # React UI components
├── hooks/             # Custom React hooks
├── services/          # API service modules
├── api/               # Backend API route handlers
├── types/             # TypeScript type definitions
├── config/            # Configuration, prompts, constants
├── styles/            # CSS files
├── App.tsx
└── main.tsx
public/
├── avatars/           # SVG avatar expression files (Task 02)
└── widget-loader.js   # Widget embedding script (Task 13)
```

### 5. Create Shared Types File

Create `src/types/index.ts`:

```typescript
// Emotion types for Maya's avatar expressions
export type Emotion =
  | "listening"
  | "thinking"
  | "happy"
  | "sad"
  | "confused"
  | "understanding";

// A single message in the conversation transcript
export interface TranscriptMessage {
  id: string;
  role: "user" | "maya";
  text: string;
  timestamp: Date;
  emotion?: Emotion;          // Only present for Maya's messages
  feedbackRating?: "up" | "down" | null;  // Per-response feedback
}

// Maya's parsed GPT response
export interface MayaResponse {
  response: string;
  emotion: Emotion;
}

// Feedback payload sent to backend
export interface FeedbackPayload {
  conversationId: string;
  transcript: TranscriptMessage[];
  overallRating: "up" | "down" | null;
  feedbackText: string;        // Only populated if overallRating === "down"
  perResponseRatings: Array<{
    messageId: string;
    rating: "up" | "down";
  }>;
  submittedAt: string;         // ISO timestamp
}

// Call/conversation state machine
export type CallState =
  | "idle"          // Widget loaded, not in call
  | "connecting"    // LiveKit connecting
  | "active"        // In conversation
  | "processing"    // Maya is thinking (GPT call in progress)
  | "speaking"      // Maya is speaking (TTS playing)
  | "ended"         // Call ended, showing survey
  | "submitted";    // Feedback submitted

// Widget configuration (for embedding)
export interface WidgetConfig {
  position?: "bottom-right" | "bottom-left" | "center";
  theme?: "light" | "dark";
  apiBaseUrl?: string;
}
```

### 6. Create Constants File

Create `src/config/constants.ts`:

```typescript
export const BRAND = {
  name: "EZpresence",
  agentName: "Maya",
  supportEmail: "contact@ezpresence.com",
  colors: {
    purple: "#7C3AED",
    purpleLight: "#A78BFA",
    purpleDark: "#5B21B6",
    teal: "#14B8A6",
    tealLight: "#5EEAD4",
    tealDark: "#0D9488",
  },
} as const;

export const EMOTIONS = [
  "listening",
  "thinking",
  "happy",
  "sad",
  "confused",
  "understanding",
] as const;

export const AVATAR_PATHS: Record<string, string> = {
  listening: "/avatars/maya-listening.svg",
  thinking: "/avatars/maya-thinking.svg",
  happy: "/avatars/maya-happy.svg",
  sad: "/avatars/maya-sad.svg",
  confused: "/avatars/maya-confused.svg",
  understanding: "/avatars/maya-understanding.svg",
};

export const API_ENDPOINTS = {
  feedback: "/api/feedback",
  transcript: "/api/transcript",
} as const;
```

### 7. Create Environment Variable Template

Create `.env.example`:
```env
# === OpenAI ===
VITE_OPENAI_API_KEY=sk-...

# === LiveKit ===
VITE_LIVEKIT_URL=wss://your-app.livekit.cloud
VITE_LIVEKIT_API_KEY=APIxxxxxxxx
VITE_LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxx

# === ElevenLabs (optional, premium TTS) ===
VITE_ELEVENLABS_API_KEY=
VITE_ELEVENLABS_VOICE_ID=

# === Backend ===
VITE_API_BASE_URL=http://localhost:3001
DATABASE_URL=postgresql://user:pass@localhost:5432/maya
FEEDBACK_EMAIL=contact@ezpresence.com
SENDGRID_API_KEY=SG.xxxxxxxx
```

### 8. Set Up Minimal App.tsx

Replace `src/App.tsx` with a shell:

```tsx
import "./styles/globals.css";

function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-slate-800">
          Maya — EZpresence Hostess
        </h1>
        <p className="text-slate-500 mt-2">Widget loading...</p>
      </div>
    </div>
  );
}

export default App;
```

### 9. Verify Everything Works

```bash
npm run dev
```

Confirm:
- Dev server starts without errors
- Tailwind classes render (check the styled heading)
- TypeScript compiles cleanly
- No missing dependency warnings

---

## Acceptance Criteria

- [ ] `npm run dev` starts cleanly with no errors
- [ ] Tailwind utility classes apply correctly (brand colors, font, etc.)
- [ ] All directories exist: `components/`, `hooks/`, `services/`, `api/`, `types/`, `config/`, `styles/`, `public/avatars/`
- [ ] `src/types/index.ts` exports all shared types
- [ ] `src/config/constants.ts` exports brand config and avatar paths
- [ ] `.env.example` exists with all required variable placeholders
- [ ] TypeScript compiles without errors (`npx tsc --noEmit`)
- [ ] All dependencies from Step 2 are in `package.json`

---

## Output Files
- `package.json` (with all deps)
- `tailwind.config.ts`
- `src/styles/globals.css`
- `src/types/index.ts`
- `src/config/constants.ts`
- `.env.example`
- `src/App.tsx` (shell)
- Empty directory placeholders
