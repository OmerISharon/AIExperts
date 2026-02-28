# Maya the EZpresence Hostess — Task Breakdown Index

## Project Overview
A speech-to-speech conversational AI assistant (web widget) for EZpresence. Features a 2D illustrated avatar ("Maya") with emotion-driven expressions, real-time voice conversation via LiveKit, GPT-4 conversational engine, TTS voice output, live transcript, and a feedback system.

**Tech Stack:** React (TypeScript), Vite, styled-components, LiveKit SDK, OpenAI API (Whisper + GPT-4 + TTS), ElevenLabs TTS (optional upgrade), Next.js API routes, PostgreSQL/Supabase, Vercel deployment.

---

## Task Execution Order

Tasks are ordered by dependency. Tasks at the same level can be parallelized.

```
PHASE 1 — Foundation
  └─ Task 01: Project Scaffolding & Configuration

PHASE 2 — Core Components (parallelizable)
  ├─ Task 02: Avatar SVG Assets Creation
  ├─ Task 03: Avatar React Component (depends on 02)
  └─ Task 04: Main UI Layout & Widget Shell (depends on 01)

PHASE 3 — Backend & AI Engine
  ├─ Task 05: Maya Conversation Engine — System Prompt + GPT-4 (depends on 01)
  └─ Task 06: Backend API — Feedback, Transcripts, Email (depends on 01)

PHASE 4 — Voice Pipeline
  ├─ Task 07: LiveKit Real-Time Voice Integration (depends on 04)
  ├─ Task 08: Speech-to-Text — Whisper Integration (depends on 07)
  └─ Task 09: Text-to-Speech Integration (depends on 05)

PHASE 5 — UI Features
  ├─ Task 10: Transcript Display Component (depends on 04, 05)
  └─ Task 11: Feedback System — UI + Submission (depends on 04, 06)

PHASE 6 — Assembly & Ship
  ├─ Task 12: Full Integration & End-to-End Wiring (depends on all above)
  └─ Task 13: Widget Embedding & Deployment (depends on 12)
```

---

## Task Summary Table

| # | Task | Est. Time | Dependencies | Key Output |
|---|------|-----------|-------------|------------|
| 01 | Project Scaffolding & Configuration | 30 min | None | Working Vite+React+TS+styled-components project |
| 02 | Avatar SVG Assets Creation | 45 min | None | 6 SVG files in `public/avatars/` |
| 03 | Avatar React Component | 30 min | 02 | `<Avatar>` component with emotion transitions |
| 04 | Main UI Layout & Widget Shell | 45 min | 01 | Full widget layout with call controls |
| 05 | Maya Conversation Engine | 45 min | 01 | GPT-4 integration with emotion classification |
| 06 | Backend API | 45 min | 01 | `/api/feedback`, `/api/transcript` endpoints |
| 07 | LiveKit Voice Integration | 60 min | 04 | Real-time mic capture + audio transport |
| 08 | Speech-to-Text (Whisper) | 30 min | 07 | Live transcription of user speech |
| 09 | Text-to-Speech | 30 min | 05 | Maya voice playback via TTS |
| 10 | Transcript Display | 30 min | 04, 05 | Scrollable chat transcript component |
| 11 | Feedback System UI | 45 min | 04, 06 | Per-response + end-survey feedback |
| 12 | Full Integration & E2E Wiring | 60 min | All | Complete working conversation flow |
| 13 | Widget Embedding & Deployment | 45 min | 12 | Deployed to Vercel, embeddable widget |

**Total Estimated Time: ~7.5 hours**

---

## File Structure (Target)

```
maya-ezpresence/
├── public/
│   ├── avatars/
│   │   ├── maya-listening.svg
│   │   ├── maya-thinking.svg
│   │   ├── maya-happy.svg
│   │   ├── maya-sad.svg
│   │   ├── maya-confused.svg
│   │   └── maya-understanding.svg
│   └── widget-loader.js
├── src/
│   ├── components/
│   │   ├── Avatar.tsx
│   │   ├── MayaWidget.tsx
│   │   ├── CallInterface.tsx
│   │   ├── TranscriptDisplay.tsx
│   │   ├── FeedbackThumb.tsx
│   │   ├── EndSurveyModal.tsx
│   │   └── MicIndicator.tsx
│   ├── hooks/
│   │   ├── useLiveKit.ts
│   │   ├── useWhisper.ts
│   │   ├── useTTS.ts
│   │   └── useConversation.ts
│   ├── services/
│   │   ├── mayaEngine.ts
│   │   ├── openai.ts
│   │   ├── tts.ts
│   │   └── feedback.ts
│   ├── api/
│   │   ├── feedback.ts
│   │   └── transcript.ts
│   ├── types/
│   │   └── index.ts
│   ├── config/
│   │   ├── prompts.ts
│   │   └── constants.ts
│   ├── styles/
│   │   └── globals.css
│   ├── App.tsx
│   └── main.tsx
├── .env.example
├── tsconfig.json
├── vite.config.ts
├── package.json
└── README.md
```

---

## Environment Variables Required

```env
# OpenAI
VITE_OPENAI_API_KEY=sk-...

# LiveKit
VITE_LIVEKIT_URL=wss://your-app.livekit.cloud
VITE_LIVEKIT_API_KEY=API...
VITE_LIVEKIT_API_SECRET=...

# ElevenLabs (optional, for premium TTS)
VITE_ELEVENLABS_API_KEY=...
VITE_ELEVENLABS_VOICE_ID=...

# Backend
VITE_API_BASE_URL=http://localhost:3001
DATABASE_URL=postgresql://...
FEEDBACK_EMAIL=contact@ezpresence.com
SENDGRID_API_KEY=SG...
```

---

## Brand Guidelines

- **Primary Purple:** `#7C3AED` (violet-600)
- **Primary Teal:** `#14B8A6` (teal-500)
- **Background:** `#F8FAFC` (slate-50)
- **Text Primary:** `#1E293B` (slate-800)
- **Text Secondary:** `#64748B` (slate-500)
- **Accent/Success:** `#10B981` (emerald-500)
- **Warning:** `#F59E0B` (amber-500)
- **Font:** Inter or system sans-serif
- **Border Radius:** 12px (rounded-xl) for containers, 8px for buttons
- **Style:** Clean, minimal, professional — not playful or cartoon-like
