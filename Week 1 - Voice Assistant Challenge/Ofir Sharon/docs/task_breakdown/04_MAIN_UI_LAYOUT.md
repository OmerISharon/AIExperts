# Task 04: Main UI Layout & Widget Shell

## Objective
Build the complete visual shell of the Maya widget: the widget container, call interface layout, call control buttons (Start/End Call, New Chat), microphone status indicator, and overall page structure. This task is purely UI/layout — no API logic, no LiveKit, no GPT. Just the visual components with placeholder states.

---

## Context
The Maya widget is a self-contained UI panel that can either fill a page or be embedded via iframe. It has distinct visual states that map to the conversation lifecycle:

1. **Idle** — Welcome screen with Maya's intro and "Start Conversation" button
2. **Connecting** — Brief loading state while LiveKit connects
3. **Active** — Full call interface: avatar, transcript area, controls, mic indicator
4. **Ended** — Post-call view with survey prompt and "Start New" / "Close" options

All states live inside a single `MayaWidget` container component.

---

## Dependencies
- **Task 01** (project setup, types, constants, Tailwind)
- **Task 03** (Avatar component — import and place it, but it can use a placeholder if not ready)

## Types Used
```typescript
type CallState = "idle" | "connecting" | "active" | "processing" | "speaking" | "ended" | "submitted";
```

---

## Components to Build

### 1. `MayaWidget.tsx` — Main Container

The top-level wrapper. Manages `callState` and renders the appropriate view.

**Layout:**
```
┌──────────────────────────────┐
│  MayaWidget Container        │
│  (max-w-md, centered,        │
│   rounded-widget, shadow-xl) │
│                              │
│  ┌──────────────────────┐    │
│  │  Header Bar          │    │
│  │  "Maya · EZpresence" │    │
│  └──────────────────────┘    │
│                              │
│  ┌──────────────────────┐    │
│  │  Dynamic Content     │    │
│  │  (based on callState)│    │
│  └──────────────────────┘    │
│                              │
└──────────────────────────────┘
```

**Props:** None (top-level component, manages own state)

**State:**
- `callState: CallState` — drives which view renders
- `transcript: TranscriptMessage[]` — conversation messages
- `mayaEmotion: Emotion` — current avatar emotion

**Behavior:**
- When `callState === "idle"` → render `IdleView`
- When `callState === "connecting"` → render loading spinner
- When `callState === "active" | "processing" | "speaking"` → render `CallInterface`
- When `callState === "ended"` → render `EndView`
- When `callState === "submitted"` → render "Thanks" message + restart option

**Styling:**
- Container: `max-w-md w-full mx-auto bg-white rounded-widget shadow-xl overflow-hidden`
- Min height: `min-h-[600px]` (so it doesn't collapse)
- Max height: `max-h-[90vh]` with internal scrolling
- Border: `border border-slate-200`

### 2. `IdleView` (inline or sub-component)

The welcome screen before the user starts a call.

**Layout:**
```
┌────────────────────────────┐
│                            │
│       [Maya Avatar]        │
│       (happy emotion)      │
│                            │
│   "Hi! I'm Maya, your     │
│    EZpresence Hostess."    │
│                            │
│   "I can help you with     │
│    scheduling, Studio,     │
│    and account setup."     │
│                            │
│   ┌────────────────────┐   │
│   │ Start Conversation │   │
│   └────────────────────┘   │
│                            │
│   🎤 Requires microphone   │
│      access                │
│                            │
└────────────────────────────┘
```

- Avatar shows "happy" expression
- "Start Conversation" button: `bg-brand-purple hover:bg-brand-purple-dark text-white font-medium px-8 py-3 rounded-lg`
- Small note about mic permission: `text-xs text-slate-400`

### 3. `CallInterface.tsx` — Active Call View

The main conversation view, shown during active/processing/speaking states.

**Layout:**
```
┌────────────────────────────┐
│  ┌──────────────────────┐  │
│  │    [Maya Avatar]     │  │  ← Top 1/3
│  │   + emotion label    │  │
│  │   + mic indicator    │  │
│  └──────────────────────┘  │
│                            │
│  ┌──────────────────────┐  │
│  │   Transcript Area    │  │  ← Middle (scrollable)
│  │   [messages here]    │  │
│  │                      │  │
│  └──────────────────────┘  │
│                            │
│  ┌──────────────────────┐  │
│  │ [End Call] [New Chat] │  │  ← Bottom controls
│  └──────────────────────┘  │
└────────────────────────────┘
```

**Props:**
```typescript
interface CallInterfaceProps {
  callState: CallState;
  emotion: Emotion;
  transcript: TranscriptMessage[];
  onEndCall: () => void;
  onNewChat: () => void;
}
```

**Sub-elements:**

**a. Avatar Section (top)**
- Avatar component (from Task 03) centered
- Below avatar: emotion label text (e.g., "Listening...")
- Below that: `MicIndicator` component

**b. Transcript Area (middle)**
- Placeholder for `TranscriptDisplay` (Task 10)
- For now, render a simple scrollable div with placeholder messages
- `flex-1 overflow-y-auto` to fill available space

**c. Controls Bar (bottom)**
- "End Call" button: `bg-red-500 hover:bg-red-600 text-white rounded-lg px-6 py-2.5`
- "New Chat" button: `bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg px-6 py-2.5`
- Buttons in a flex row with `gap-3`, centered
- Sticky bottom: `sticky bottom-0 bg-white border-t border-slate-100 p-4`

### 4. `MicIndicator.tsx` — Microphone Status

A small visual indicator showing whether the mic is active and picking up audio.

**Props:**
```typescript
interface MicIndicatorProps {
  isActive: boolean;      // Mic is on and connected
  isUserSpeaking: boolean; // Audio detected
}
```

**Visual states:**
- **Mic off / not connected:** Gray mic icon, "Mic off" text
- **Mic on, silent:** Green mic icon, subtle pulse, "Listening..."
- **Mic on, user speaking:** Green mic icon with animated sound bars or pulsing ring, "Hearing you..."

**Implementation:** Use a simple SVG mic icon (inline) + CSS animations. Three small bars that animate height when `isUserSpeaking` is true (like an audio level visualizer). Use Tailwind `animate-bounce` or custom keyframes.

### 5. `EndView` (inline or sub-component)

Shown after the user clicks "End Call." This is the survey prompt screen.

**Layout:**
```
┌────────────────────────────┐
│                            │
│       [Maya Avatar]        │
│       (happy emotion)      │
│                            │
│   "Thanks for chatting!"   │
│                            │
│   [Feedback survey here]   │
│   (placeholder for Task 11)│
│                            │
│  ┌─────────┐ ┌───────────┐│
│  │Start New│ │Close Widget││
│  └─────────┘ └───────────┘│
│                            │
└────────────────────────────┘
```

---

## Header Bar Component

A slim header at the top of the widget.

```
┌──────────────────────────────┐
│ 🟣 Maya · EZpresence    [×] │
└──────────────────────────────┘
```

- Left: Small purple dot + "Maya · EZpresence" in `text-sm font-medium text-slate-700`
- Right: Close button (×) — `text-slate-400 hover:text-slate-600`
- Background: `bg-white border-b border-slate-100`
- Height: ~48px
- Only show close button if widget is floating (not full-page)

---

## Responsive Design

- **Mobile (< 640px):** Widget fills full width, full height
- **Tablet / Desktop (≥ 640px):** Widget is `max-w-md` (448px), centered with shadow
- Avatar size: `md` (128px) on desktop, `sm` (80px) on mobile
- Transcript area: flexes to fill available space
- Controls: always visible at bottom (not scrolled away)

---

## Placeholder / Mock Data

For this task, use hardcoded mock data so the UI can be visually verified:

```typescript
const MOCK_TRANSCRIPT: TranscriptMessage[] = [
  {
    id: "1",
    role: "maya",
    text: "Hi! I'm Maya, your EZpresence Hostess. How can I help you today?",
    timestamp: new Date(),
    emotion: "happy",
  },
  {
    id: "2",
    role: "user",
    text: "How do I schedule posts?",
    timestamp: new Date(),
  },
  {
    id: "3",
    role: "maya",
    text: "Great question! Content scheduling lets you plan posts in advance across all your platforms...",
    timestamp: new Date(),
    emotion: "happy",
  },
];
```

---

## Acceptance Criteria

- [ ] `MayaWidget.tsx` renders correctly and fills container
- [ ] All 4 visual states render: idle, connecting, active, ended
- [ ] "Start Conversation" button triggers state change to "connecting"
- [ ] "End Call" button triggers state change to "ended"
- [ ] "New Chat" clears transcript and returns to "idle"
- [ ] Avatar is displayed in the call interface with the correct emotion
- [ ] MicIndicator shows all 3 states (off, listening, speaking)
- [ ] Header bar renders with brand name and close button
- [ ] Responsive: looks correct on 375px mobile and 1024px desktop widths
- [ ] Smooth transitions between states (no layout jumps)
- [ ] Tailwind styling matches brand colors (purple, teal, slate)
- [ ] No console errors

---

## Output Files
- `src/components/MayaWidget.tsx`
- `src/components/CallInterface.tsx`
- `src/components/MicIndicator.tsx`
- Updated `src/App.tsx` (renders `<MayaWidget />`)
