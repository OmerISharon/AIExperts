# Task 10: Transcript Display Component

## Objective
Build the scrollable, real-time conversation transcript component that displays both user and Maya messages in a chat-like format, auto-scrolls to the latest message, shows per-message feedback thumbs (for Maya's messages), and supports text copying.

---

## Context
The transcript sits in the middle section of the `CallInterface` layout (between the avatar and the control buttons). It shows the full conversation history in real-time, styled like a chat interface. Each Maya message has a small thumbs up/down button for per-response feedback.

**Layout reference:**
```
┌──────────────────────────────┐
│  [Avatar + Emotion Label]    │
│──────────────────────────────│
│  Transcript Area (scrollable)│
│                              │
│  Maya: "Hi! How can I help?" │
│         [👍] [👎]            │
│                              │
│        User: "How do I..."   │
│                              │
│  Maya: "Great question!..."  │
│         [👍] [👎]            │
│                              │
│  ● Maya is thinking...       │
│                              │
│──────────────────────────────│
│  [End Call]  [New Chat]      │
└──────────────────────────────┘
```

---

## Dependencies
- **Task 01** (types: `TranscriptMessage`)
- **Task 04** (call interface layout — this component plugs into the middle section)
- **Task 05** (conversation engine provides transcript data)

## Types Used
```typescript
interface TranscriptMessage {
  id: string;
  role: "user" | "maya";
  text: string;
  timestamp: Date;
  emotion?: Emotion;
  feedbackRating?: "up" | "down" | null;
}
```

---

## Component: `TranscriptDisplay.tsx`

### Props
```typescript
interface TranscriptDisplayProps {
  messages: TranscriptMessage[];
  isProcessing: boolean;           // Show "thinking" indicator
  onRateMessage: (messageId: string, rating: "up" | "down") => void;
}
```

### Layout Structure

Each message is a **message bubble** with distinct styling for user vs. Maya:

**Maya's messages (left-aligned):**
```
┌─────────────────────────────┐
│ 🟣 Maya                     │
│ "Great question! Content..." │
│                              │
│ [👍] [👎]      2:34 PM      │
└─────────────────────────────┘
```
- Background: `bg-white` with `border border-slate-200`
- Text color: `text-slate-800`
- Aligned: left
- Small purple dot or avatar mini-icon as identifier
- Name label: "Maya" in `text-xs font-medium text-brand-purple`
- Feedback thumbs: small icon buttons, only on Maya's messages
- Timestamp: `text-xs text-slate-400`, right-aligned within bubble

**User's messages (right-aligned):**
```
                ┌─────────────────────────┐
                │ "How do I schedule..."   │
                │                2:34 PM   │
                └─────────────────────────┘
```
- Background: `bg-brand-purple/10` (light purple) or `bg-slate-100`
- Text color: `text-slate-800`
- Aligned: right
- No feedback buttons
- Timestamp: `text-xs text-slate-400`

**Thinking indicator (when `isProcessing` is true):**
```
┌───────────────────────┐
│ 🟣 Maya               │
│ ● ● ●  (animated dots)│
└───────────────────────┘
```
- Three animated dots (typing indicator style)
- Appears at bottom of message list
- Disappears when response arrives

### Auto-Scroll Behavior

- Automatically scroll to bottom when a new message is added
- Use `scrollIntoView({ behavior: "smooth" })` on a dummy div at the bottom
- If user has manually scrolled up (reading history), DON'T auto-scroll — let them read
- Resume auto-scroll when user scrolls back to near-bottom

```typescript
const messagesEndRef = useRef<HTMLDivElement>(null);
const containerRef = useRef<HTMLDivElement>(null);
const [isAutoScroll, setIsAutoScroll] = useState(true);

// Detect if user scrolled away from bottom
const handleScroll = () => {
  const container = containerRef.current;
  if (!container) return;
  const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
  setIsAutoScroll(isNearBottom);
};

// Scroll to bottom when new messages arrive (if auto-scroll is on)
useEffect(() => {
  if (isAutoScroll) {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }
}, [messages, isProcessing, isAutoScroll]);
```

### Per-Message Feedback (Thumbs)

For each Maya message, show small thumbs up/down icons:

```typescript
interface FeedbackThumbProps {
  messageId: string;
  currentRating: "up" | "down" | null;
  onRate: (messageId: string, rating: "up" | "down") => void;
}
```

**Behavior:**
- Initially: both thumbs are gray/unselected
- Click thumbs up: fills green, thumbs down stays gray
- Click thumbs down: fills red/orange, thumbs up stays gray
- Clicking again on same thumb: deselects (returns to null)
- Clicking opposite thumb: switches selection
- Non-intrusive: small icons, don't draw attention away from conversation
- Only appears on Maya's messages, not user messages

**Styling:**
- Icons: 16px, `text-slate-300` when unselected
- Thumbs up selected: `text-emerald-500`
- Thumbs down selected: `text-amber-500`
- Hover: `text-slate-500`
- Container: `flex gap-1` below the message text

### Copy Functionality

Each message bubble should have a subtle "copy" button that appears on hover:

```
Message text appears...
                         [📋]  ← appears on hover
```

- Icon: small clipboard icon, `text-slate-300 hover:text-slate-500`
- On click: copies message text to clipboard
- Brief "Copied!" tooltip or toast confirmation
- Use `navigator.clipboard.writeText(text)`

### Empty State

When there are no messages yet (conversation just started):

```
┌──────────────────────────┐
│                          │
│   Start speaking to Maya │
│   She's ready to listen  │
│                          │
└──────────────────────────┘
```

Centered text in `text-sm text-slate-400`

---

## Thinking Indicator Sub-Component

```typescript
const ThinkingIndicator: React.FC = () => (
  <div className="flex items-start gap-2 px-4 py-2">
    <div className="w-6 h-6 rounded-full bg-brand-purple flex items-center justify-center">
      <span className="text-white text-xs">M</span>
    </div>
    <div className="bg-white border border-slate-200 rounded-xl px-4 py-3">
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  </div>
);
```

---

## Responsive Considerations

- **Mobile:** Full width, slightly smaller text (text-sm), smaller thumbs
- **Desktop:** Max width within widget container, comfortable text size (text-base for Maya, text-sm for meta)
- Message bubbles: `max-w-[80%]` so they don't stretch full width
- Padding: `px-4 py-2` for each message row

---

## Acceptance Criteria

- [ ] Messages render in chronological order
- [ ] Maya's messages left-aligned, User's messages right-aligned
- [ ] Visual distinction between Maya and User messages (colors, alignment)
- [ ] Feedback thumbs appear only on Maya's messages
- [ ] Thumbs up/down toggle correctly (select, deselect, switch)
- [ ] Auto-scroll to latest message on new messages
- [ ] Auto-scroll pauses when user scrolls up, resumes when at bottom
- [ ] Thinking indicator (animated dots) shows when `isProcessing` is true
- [ ] Copy button works on hover for each message
- [ ] Empty state shows when no messages exist
- [ ] Timestamps displayed on each message
- [ ] Smooth, no-jank scrolling
- [ ] Responsive: looks good on mobile (375px) and desktop

---

## Output Files
- `src/components/TranscriptDisplay.tsx`
- `src/components/FeedbackThumb.tsx` (or inline within TranscriptDisplay)
- `src/components/ThinkingIndicator.tsx` (or inline)
