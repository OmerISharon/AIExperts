# Task 11: Feedback System — End-of-Conversation Survey & Submission

## Objective
Build the end-of-conversation feedback flow: a survey modal shown after the user ends a call, with overall rating (thumbs up/down), conditional text feedback (appears only on thumbs down), and submission to the backend. Also wire up per-response ratings (from Task 10) into the final submission payload.

---

## Context
When the user clicks "End Call," the following happens:
1. Call is disconnected (voice stops)
2. Full transcript is sent to backend for storage
3. The **end-of-conversation survey** appears
4. User rates the conversation (👍 or 👎)
5. If thumbs down: a text field appears asking "What could be improved?"
6. User submits feedback
7. All feedback (overall + per-response ratings + optional text) is sent to backend
8. Backend emails summary to `contact@ezpresence.com`
9. User sees confirmation and options to "Start New Conversation" or "Close"

---

## Dependencies
- **Task 04** (UI layout — `EndView` state in MayaWidget)
- **Task 06** (backend `/api/feedback` endpoint)
- **Task 10** (per-response thumbs are collected in transcript state)

## Types Used
```typescript
interface FeedbackPayload {
  conversationId: string;
  transcript: TranscriptMessage[];
  overallRating: "up" | "down" | null;
  feedbackText: string;
  perResponseRatings: Array<{ messageId: string; rating: "up" | "down" }>;
  submittedAt: string;
}
```

---

## Component: `EndSurveyModal.tsx`

### Props
```typescript
interface EndSurveyModalProps {
  conversationId: string;
  transcript: TranscriptMessage[];
  onSubmitted: () => void;        // Called after successful submission
  onStartNew: () => void;         // Start a new conversation
  onClose: () => void;            // Close the widget entirely
}
```

### Visual Layout

**State 1: Survey (initial)**
```
┌──────────────────────────────┐
│                              │
│       [Maya Avatar]          │
│       (happy emotion)        │
│                              │
│   "Thanks for chatting       │
│    with me today!"           │
│                              │
│   Was this conversation      │
│   helpful?                   │
│                              │
│   ┌──────┐    ┌──────┐      │
│   │  👍  │    │  👎  │      │
│   │ Yes  │    │  No  │      │
│   └──────┘    └──────┘      │
│                              │
└──────────────────────────────┘
```

**State 2: After thumbs DOWN clicked**
```
┌──────────────────────────────┐
│                              │
│   Was this helpful?          │
│   [👍]  [👎 selected]        │
│                              │
│   What could be improved?    │
│   ┌──────────────────────┐   │
│   │                      │   │
│   │  (text area)         │   │
│   │                      │   │
│   └──────────────────────┘   │
│                              │
│   ┌────────────────────┐     │
│   │  Submit Feedback   │     │
│   └────────────────────┘     │
│                              │
└──────────────────────────────┘
```

**State 3: After thumbs UP clicked**
```
┌──────────────────────────────┐
│                              │
│   Was this helpful?          │
│   [👍 selected]  [👎]        │
│                              │
│   ┌────────────────────┐     │
│   │  Submit Feedback   │     │
│   └────────────────────┘     │
│                              │
└──────────────────────────────┘
```
(No text field appears for thumbs up — keep it simple)

**State 4: Submitted confirmation**
```
┌──────────────────────────────┐
│                              │
│         ✓                    │
│                              │
│   Thanks for your feedback!  │
│                              │
│   ┌──────────────────────┐   │
│   │ Start New Conversation│  │
│   └──────────────────────┘   │
│                              │
│   ┌──────────────────────┐   │
│   │    Close Widget      │   │
│   └──────────────────────┘   │
│                              │
└──────────────────────────────┘
```

### Internal State

```typescript
const [overallRating, setOverallRating] = useState<"up" | "down" | null>(null);
const [feedbackText, setFeedbackText] = useState("");
const [isSubmitting, setIsSubmitting] = useState(false);
const [isSubmitted, setIsSubmitted] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### Behavior

1. **Rating selection:**
   - Click 👍: set `overallRating = "up"`, hide text field
   - Click 👎: set `overallRating = "down"`, reveal text field with smooth animation
   - Can switch between 👍 and 👎 before submitting

2. **Text feedback (conditional):**
   - Only visible when `overallRating === "down"`
   - Placeholder: "Tell us what could be better..."
   - Max length: 500 characters
   - Character counter shown
   - Optional — user can submit without text

3. **Submit:**
   - Gathers: conversationId, transcript, overallRating, feedbackText, perResponseRatings
   - Per-response ratings extracted from transcript messages that have `feedbackRating` set
   - Calls `submitFeedback()` from `src/services/feedback.ts`
   - Shows loading state on button while submitting
   - On success: transition to "submitted" state
   - On error: show error message, keep form active for retry

4. **Post-submission:**
   - Show confirmation message
   - "Start New Conversation" button → calls `onStartNew()`
   - "Close Widget" button → calls `onClose()`

### Styling

**Rating buttons:**
- Unselected: `bg-white border-2 border-slate-200 text-slate-500 rounded-xl px-8 py-4`
- 👍 selected: `bg-emerald-50 border-2 border-emerald-500 text-emerald-600`
- 👎 selected: `bg-amber-50 border-2 border-amber-500 text-amber-600`
- Hover: `hover:border-slate-300`
- Transition: `transition-all duration-200`
- Emoji size: `text-2xl`

**Text area:**
- `w-full border border-slate-200 rounded-lg p-3 text-sm text-slate-700 focus:ring-2 focus:ring-brand-purple focus:border-transparent resize-none`
- Height: 3-4 rows
- Animate in from `opacity-0 max-h-0` to `opacity-100 max-h-40`

**Submit button:**
- `bg-brand-purple text-white font-medium rounded-lg px-6 py-2.5 hover:bg-brand-purple-dark`
- Disabled state: `opacity-50 cursor-not-allowed` (when no rating selected)
- Loading state: show spinner, text "Submitting..."

**Post buttons:**
- "Start New": `bg-brand-purple text-white rounded-lg px-6 py-2.5`
- "Close Widget": `bg-white border border-slate-200 text-slate-600 rounded-lg px-6 py-2.5`

---

## Feedback Payload Assembly

When submitting, assemble the full payload:

```typescript
const handleSubmit = async () => {
  setIsSubmitting(true);
  setError(null);

  // Extract per-response ratings from transcript
  const perResponseRatings = transcript
    .filter((msg) => msg.role === "maya" && msg.feedbackRating != null)
    .map((msg) => ({
      messageId: msg.id,
      rating: msg.feedbackRating!,
    }));

  const payload: FeedbackPayload = {
    conversationId,
    transcript,
    overallRating,
    feedbackText: overallRating === "down" ? feedbackText.trim() : "",
    perResponseRatings,
    submittedAt: new Date().toISOString(),
  };

  try {
    const success = await submitFeedback(payload);
    if (success) {
      setIsSubmitted(true);
      onSubmitted();
    } else {
      setError("Failed to submit feedback. Please try again.");
    }
  } catch {
    setError("Something went wrong. Please try again.");
  } finally {
    setIsSubmitting(false);
  }
};
```

---

## Skip Feedback Option

User should be able to skip the survey entirely:

- Small "Skip" text link below the rating buttons
- `text-sm text-slate-400 hover:text-slate-600 cursor-pointer`
- Clicking "Skip" goes directly to the "submitted" state (or post-call options)
- Still send transcript to backend even if feedback is skipped

---

## Integration with MayaWidget

In `MayaWidget.tsx`, when `callState === "ended"`:

```typescript
{callState === "ended" && (
  <EndSurveyModal
    conversationId={conversationId}
    transcript={transcript}
    onSubmitted={() => {
      // Feedback saved
    }}
    onStartNew={() => {
      resetConversation();
      setCallState("idle");
    }}
    onClose={() => {
      // Close widget (postMessage to parent if iframe, or hide)
    }}
  />
)}
```

---

## Automatic Transcript Storage

When the call ends (before showing survey), automatically store the transcript:

```typescript
const handleEndCall = async () => {
  disconnect(); // Stop voice
  setCallState("ended");

  // Store transcript immediately
  await storeTranscript({
    conversationId,
    transcript,
    startedAt: callStartTime.toISOString(),
    endedAt: new Date().toISOString(),
    messageCount: transcript.length,
    duration: Math.round((Date.now() - callStartTime.getTime()) / 1000),
  });
};
```

---

## Acceptance Criteria

- [ ] End-of-conversation survey appears after "End Call"
- [ ] 👍/👎 rating buttons work (select, switch, deselect)
- [ ] Text feedback field appears ONLY when 👎 is selected
- [ ] Text field has character limit (500) with counter
- [ ] Submit button disabled until a rating is selected
- [ ] Submit sends full payload to `/api/feedback`
- [ ] Loading state shown during submission
- [ ] Error state shows message and allows retry
- [ ] Confirmation screen shows after successful submission
- [ ] "Start New" resets conversation and returns to idle
- [ ] "Close Widget" closes or hides the widget
- [ ] "Skip" option available to bypass feedback
- [ ] Transcript automatically stored when call ends (even without feedback)
- [ ] Per-response ratings from transcript included in payload
- [ ] Smooth animations for text field reveal

---

## Output Files
- `src/components/EndSurveyModal.tsx`
- Updates to `src/components/MayaWidget.tsx` (wire in EndSurveyModal)
