# MAYA — Agent Execution Manifest

> **Project:** Maya the EZpresence Hostess  
> **Repository:** `AIExperts/Week 1 - Voice Assistant Challenge/Ofir Sharon`  
> **Agent Target:** Google Antigravity / Gemini Code Assist  
> **Generated:** 2026-02-28  
> **Est. Total Time:** ~7.5 hours · 13 tasks · 6 phases

---

## Agent Behavior Contract

Each task has a self-contained instruction file in `docs/task_breakdown/`. An agent assigned to a task:

1. **MUST** read the full task file before writing any code
2. **MUST** read spec files listed in the task's Context Injection row (see §Task Table below)
3. **MUST** produce all files listed in the task's "Output Files" section
4. **MUST** pass all items in the task's "Acceptance Criteria" checklist before marking complete
5. **MUST NOT** modify files owned by other tasks unless the task file explicitly says "Update"
6. **SHOULD** commit per task: `feat(maya): complete task XX — <task_name>`

---

## Reference Documents

Located in `docs/specs/` (read-only):

| Shorthand | File | Contains |
|-----------|------|----------|
| **SPEC** | `MAYA_PROJECT_SPEC.md` | Full technical spec, architecture, user flows, data flows |
| **AVATAR** | `MAYA_AVATAR_GUIDE.md` | Avatar creation, emotion system, GPT prompt template |
| **SUMMARY** | `MAYA_PROJECT_SUMMARY.md` | Executive summary, cost model, stack overview |

Located in `docs/task_breakdown/` (read-only):

| File | Purpose |
|------|---------|
| `00_TASK_INDEX.md` | Master index with file structure, brand guidelines, env vars |
| `01` – `13_*.md` | Individual task instructions (one per task) |

---

## Shared Code Artifacts

Created by Task 01, imported by all subsequent tasks. **No task should redefine these locally.**

| File | Exports |
|------|---------|
| `src/types/index.ts` | `Emotion`, `TranscriptMessage`, `MayaResponse`, `FeedbackPayload`, `CallState`, `WidgetConfig` |
| `src/config/constants.ts` | `BRAND`, `EMOTIONS`, `AVATAR_PATHS`, `API_ENDPOINTS` |

---

## Dependency DAG & Execution Order

```
PHASE 1 — Foundation
  01 Scaffolding ─────────────────────────────────────────┐
                                                           │
PHASE 2 — Core Components (parallel)                       │
  02 SVG Assets ──────┐                                    │
  03 Avatar Component ─(02)──┐                             │
  04 UI Layout ───────(01)───┤                             │
                             │                             │
PHASE 3 — Backend & AI (parallel)                          │
  05 GPT Engine ──────(01)───┤                             │
  06 Backend API ─────(01)───┤                             │
                             │                             │
PHASE 4 — Voice Pipeline                                   │
  07 LiveKit/Mic ─────(04)───┤                             │
  08 Whisper STT ─────(07)───┤                             │
  09 TTS ─────────────(05)───┤  ← parallel with 07/08     │
                             │                             │
PHASE 5 — UI Features (parallel)                           │
  10 Transcript ──────(04,05)┤                             │
  11 Feedback UI ─────(04,06)┤                             │
                             │                             │
PHASE 6 — Assembly & Ship                                  │
  12 Integration ─────(ALL)──┤                             │
  13 Deploy ──────────(12)───┘                             │
```

**Critical path:** `01 → 04 → 07 → 08 → 12 → 13`  
**Bottleneck:** Tasks 07→08 (voice pipeline) are sequential and on the critical path.

### Parallelism Rules

| Phase | Can Run Simultaneously |
|-------|----------------------|
| 2 | 02 + 04 (03 waits for 02) |
| 3 | 05 + 06 |
| 4 | 09 can run alongside 07→08 |
| 5 | 10 + 11 |

---

## Task Table

Each row points to the task file (which contains all implementation details, output files, and acceptance criteria) and lists which spec files to read as context.

| # | Task | File | Deps | Est. | Context: Also Read |
|---|------|------|------|------|--------------------|
| 01 | Project Scaffolding | `01_PROJECT_SCAFFOLDING.md` | — | 30m | SPEC §Technical Architecture |
| 02 | Avatar SVG Assets | `02_AVATAR_SVG_ASSETS.md` | — | 45m | AVATAR §Part 1 |
| 03 | Avatar Component | `03_AVATAR_COMPONENT.md` | 02 | 30m | `src/types/index.ts`, `src/config/constants.ts` |
| 04 | UI Layout & Widget Shell | `04_MAIN_UI_LAYOUT.md` | 01 | 45m | SPEC §User Flow |
| 05 | Conversation Engine | `05_CONVERSATION_ENGINE.md` | 01 | 45m | SPEC §System Prompt, AVATAR §Part 2 |
| 06 | Backend API | `06_BACKEND_API.md` | 01 | 45m | SPEC §Data Flow |
| 07 | LiveKit / Mic Capture | `07_LIVEKIT_VOICE.md` | 04 | 60m | SPEC §LiveKit Setup |
| 08 | Whisper STT | `08_SPEECH_TO_TEXT.md` | 07 | 30m | Task 07 output (hook interface) |
| 09 | Text-to-Speech | `09_TEXT_TO_SPEECH.md` | 05 | 30m | SUMMARY §Technology Stack |
| 10 | Transcript Display | `10_TRANSCRIPT_DISPLAY.md` | 04,05 | 30m | `src/types/index.ts` |
| 11 | Feedback System UI | `11_FEEDBACK_SYSTEM.md` | 04,06 | 45m | SPEC §Feedback System |
| 12 | Full Integration | `12_INTEGRATION.md` | ALL | 60m | SPEC §Data Flow, SUMMARY §UX Flow |
| 13 | Deployment | `13_DEPLOYMENT.md` | 12 | 45m | SPEC §Widget Embedding, §Deployment |

All task files are in `docs/task_breakdown/`. All spec shorthand references (SPEC, AVATAR, SUMMARY) are in `docs/specs/`.

---

## Validation

### Per-Task
Every task file has an "Acceptance Criteria" checklist. The agent must pass all items. Common validation commands:

```bash
npx tsc --noEmit          # TypeScript compiles
npm run dev               # Dev server starts clean
npm run build             # Production build succeeds
curl -X POST /api/...     # API endpoints respond
```

### End-to-End (after Task 12)

Three scenarios to verify — details in `12_INTEGRATION.md` §Testing Checklist:

1. **Happy path:** Start → speak → hear response → multi-turn → end → feedback → restart
2. **Error recovery:** Network drop mid-conversation → graceful handling → resume
3. **Interrupt:** Speak while Maya is talking → her audio stops → new response cycle

### Production Smoke Test (after Task 13)

```
1. Open deployed URL → see welcome screen
2. Start conversation → grant mic → hear greeting
3. Ask "How do I schedule posts?" → hear answer
4. Ask follow-up → verify context maintained
5. End call → rate → submit → verify email received
6. Test iframe embedding with allow="microphone"
```

**Performance targets:** Widget load < 3s · First response < 5s · TTS latency < 2s

---

## Error Recovery

| Blocker | Fix |
|---------|-----|
| npm install fails | Delete `node_modules` + lockfile, retry |
| TS errors in shared types | Verify `src/types/index.ts` matches Task 01 output |
| API key missing | Check `.env` exists; client vars need `VITE_` prefix |
| LiveKit won't connect | Fall back to Approach B (browser-only) per Task 07 |
| GPT returns non-JSON | Ensure `response_format: { type: "json_object" }` in API call |
| CORS errors | Check API route headers + `vercel.json` |
| Mic blocked | HTTPS required (`getUserMedia`); localhost exempt |
| Vercel deploy fails | Check build output + env vars in Vercel dashboard |

---

*Implementation details, output file lists, and acceptance criteria live in each task file. This manifest provides orchestration only.*
