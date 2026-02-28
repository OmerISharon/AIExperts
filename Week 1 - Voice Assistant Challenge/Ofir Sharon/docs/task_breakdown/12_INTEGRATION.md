# Task 12: Full Integration & End-to-End Wiring

## Objective
Connect all previously built components into a complete, working conversation flow. Wire the voice pipeline (mic → STT → GPT → TTS → speaker), sync the avatar with conversation state, manage the full lifecycle (idle → call → ended → restart), and handle all edge cases. This is the assembly task.

---

## Context
At this point, all individual components exist:
- Avatar with emotions (Task 03)
- UI layout with call states (Task 04)
- Conversation engine with GPT-4 (Task 05)
- Backend API endpoints (Task 06)
- Voice capture (Task 07)
- Speech-to-text Whisper (Task 08)
- Text-to-speech (Task 09)
- Transcript display (Task 10)
- Feedback system (Task 11)

This task connects them into one seamless experience.

---

## Dependencies
- **All previous tasks (01–11)**

---

## Master Flow (The Complete Pipeline)

### 1. Widget Loads
```
→ MayaWidget mounts
→ callState = "idle"
→ Render IdleView with Maya avatar (happy) + "Start Conversation" button
→ Generate unique conversationId (UUID)
```

### 2. User Clicks "Start Conversation"
```
→ callState = "connecting"
→ Request mic permission (getUserMedia)
  → If denied: show error, stay on idle
  → If granted: continue
→ Initialize audio capture (LiveKit or browser)
→ Initialize Whisper hook
→ Initialize TTS hook
→ callState = "active"
→ Avatar emotion = "happy"
→ Trigger Maya's greeting:
  → Call engine.getResponse("Hello, I'm starting a conversation")
  → OR use hardcoded greeting from system prompt
  → Add greeting to transcript
  → Play greeting via TTS
  → Avatar emotion = greeting emotion (happy)
→ After greeting plays: avatar → "listening"
→ Record callStartTime
```

### 3. User Speaks
```
→ Audio capture detects speech
→ isUserSpeaking = true
→ MicIndicator shows active
→ Avatar stays on "listening"
→ Audio data feeds into Whisper buffer
```

### 4. User Pauses (Silence Detected)
```
→ Whisper silence detection triggers
→ isUserSpeaking = false
→ Audio buffer → WAV → sent to /api/whisper
→ isTranscribing = true (briefly)
→ Whisper returns transcribed text
→ If text is empty or too short: ignore, return to listening
→ Add user message to transcript
→ callState = "processing"
→ Avatar emotion = "thinking"
→ Call engine.getResponse(transcribedText) via /api/maya
```

### 5. GPT-4 Responds
```
→ /api/maya returns { response, emotion }
→ Add Maya's response to transcript (with emotion)
→ Avatar emotion = response emotion
→ callState = "speaking"
→ Mute/pause Whisper processing (prevent echo)
→ Call speak(response.response) via TTS
→ TTS generates audio → plays through speaker
```

### 6. Maya Finishes Speaking
```
→ TTS playback ends
→ Re-enable Whisper processing
→ callState = "active"
→ Avatar emotion = "listening"
→ Ready for next user input
→ Loop back to Step 3
```

### 7. User Clicks "End Call"
```
→ Stop audio capture
→ Stop any TTS playback
→ Disconnect LiveKit (if used)
→ Record callEndTime
→ callState = "ended"
→ Send transcript to /api/transcript
→ Show EndSurveyModal
```

### 8. Feedback & Restart
```
→ User rates conversation and optionally provides text
→ Submit feedback to /api/feedback
→ Show confirmation
→ User chooses:
  A) "Start New" → reset all state, callState = "idle", generate new conversationId
  B) "Close" → hide/close widget
```

---

## MayaWidget.tsx — Master Component

This is the orchestration component. It holds all top-level state and wires hooks together.

```typescript
import React, { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { Emotion, CallState, TranscriptMessage } from "../types";
import { Avatar } from "./Avatar";
import { CallInterface } from "./CallInterface";
import { TranscriptDisplay } from "./TranscriptDisplay";
import { EndSurveyModal } from "./EndSurveyModal";
import { MicIndicator } from "./MicIndicator";
import { useConversation } from "../hooks/useConversation";
import { useLiveKit } from "../hooks/useLiveKit"; // or useAudioCapture
import { useWhisper } from "../hooks/useWhisper";
import { useTTS } from "../hooks/useTTS";
import { storeTranscript } from "../services/feedback";

export const MayaWidget: React.FC = () => {
  // ─── State ───
  const [callState, setCallState] = useState<CallState>("idle");
  const [conversationId, setConversationId] = useState(uuidv4());
  const [mayaEmotion, setMayaEmotion] = useState<Emotion>("happy");
  const callStartTimeRef = useRef<Date | null>(null);

  // ─── Hooks ───
  const {
    transcript,
    currentEmotion,
    isProcessing,
    sendMessage,
    resetConversation: resetEngine,
    getGreeting,
    rateMessage,
  } = useConversation();

  const { speak, stop: stopSpeaking, isSpeaking } = useTTS({
    onPlaybackStart: () => setCallState("speaking"),
    onPlaybackEnd: () => {
      setCallState("active");
      setMayaEmotion("listening");
      setTranscriptionEnabled(true); // Re-enable after Maya speaks
    },
  });

  // Whisper state control
  const [transcriptionEnabled, setTranscriptionEnabled] = useState(true);

  const { feedAudioData, isTranscribing, isUserSpeaking } = useWhisper({
    onTranscription: async (text) => {
      if (!transcriptionEnabled) return;
      if (text.trim().length < 2) return; // Ignore noise

      setCallState("processing");
      setMayaEmotion("thinking");
      setTranscriptionEnabled(false); // Prevent processing during GPT call

      const response = await sendMessage(text);
      if (response) {
        setMayaEmotion(response.emotion);
        await speak(response.response);
      } else {
        // Error case — return to listening
        setCallState("active");
        setMayaEmotion("listening");
        setTranscriptionEnabled(true);
      }
    },
    onSpeechStart: () => {
      // If Maya is speaking and user interrupts:
      if (isSpeaking) {
        stopSpeaking();
      }
    },
  });

  const {
    connect: connectAudio,
    disconnect: disconnectAudio,
    isMicEnabled,
  } = useLiveKit({
    url: import.meta.env.VITE_LIVEKIT_URL,
    onAudioData: (data) => {
      if (transcriptionEnabled) {
        feedAudioData(data);
      }
    },
  });

  // ─── Handlers ───
  const handleStartCall = useCallback(async () => {
    try {
      setCallState("connecting");
      await connectAudio(`maya-${conversationId}`);
      setCallState("active");
      callStartTimeRef.current = new Date();

      // Play Maya's greeting
      setMayaEmotion("happy");
      const greeting = await getGreeting();
      if (greeting) {
        setMayaEmotion(greeting.emotion);
        await speak(greeting.response);
      }
    } catch (error) {
      console.error("Failed to start call:", error);
      setCallState("idle");
      // Show error to user
    }
  }, [conversationId, connectAudio, getGreeting, speak]);

  const handleEndCall = useCallback(async () => {
    stopSpeaking();
    disconnectAudio();
    setCallState("ended");

    // Store transcript
    if (callStartTimeRef.current) {
      await storeTranscript({
        conversationId,
        transcript,
        startedAt: callStartTimeRef.current.toISOString(),
        endedAt: new Date().toISOString(),
        messageCount: transcript.length,
        duration: Math.round(
          (Date.now() - callStartTimeRef.current.getTime()) / 1000
        ),
      });
    }
  }, [conversationId, transcript, stopSpeaking, disconnectAudio]);

  const handleNewChat = useCallback(() => {
    resetEngine();
    setConversationId(uuidv4());
    setMayaEmotion("happy");
    setCallState("idle");
    setTranscriptionEnabled(true);
    callStartTimeRef.current = null;
  }, [resetEngine]);

  const handleRateMessage = useCallback(
    (messageId: string, rating: "up" | "down") => {
      rateMessage(messageId, rating);
    },
    [rateMessage]
  );

  // ─── Render ───
  // Route based on callState:
  // "idle" → IdleView
  // "connecting" → Loading spinner
  // "active" | "processing" | "speaking" → CallInterface with Avatar, Transcript, Controls
  // "ended" → EndSurveyModal
  // "submitted" → Thank you + restart options
};
```

---

## State Synchronization Rules

Keep these states in sync:

| Event | callState | Avatar Emotion | Transcription |
|-------|-----------|----------------|---------------|
| Widget loads | idle | happy | disabled |
| Start call | connecting → active | happy → listening | enabled |
| User speaks | active | listening | enabled |
| User pauses, transcribing | active | listening | enabled |
| GPT processing | processing | thinking | disabled |
| Maya speaking | speaking | (response emotion) | disabled |
| Maya finishes | active | listening | enabled |
| End call | ended | happy | disabled |
| New chat | idle | happy | disabled |

**Key rule:** Transcription MUST be disabled when:
1. Maya is speaking (prevent echo)
2. GPT is processing (prevent double-sends)
3. Call is not active

---

## Error Handling & Recovery

### Mic Permission Denied
```
→ Show modal: "Maya needs microphone access"
→ "How to enable" link (browser-specific instructions)
→ "Try Again" button → re-request permission
→ "Use Text Instead" button → fallback to text input (stretch goal)
```

### GPT API Failure
```
→ Show in transcript: "I'm having trouble thinking right now. Could you try again?"
→ Emotion: "sad"
→ Return to listening state
→ Log error for debugging
```

### TTS API Failure
```
→ Show Maya's text response in transcript (text-only fallback)
→ Skip voice playback
→ Return to listening state
→ Small toast: "Voice unavailable, showing text response"
```

### Network Disconnection
```
→ Detect with navigator.onLine
→ Show banner: "Connection lost. Reconnecting..."
→ Retry API calls with exponential backoff (3 attempts)
→ If fails: "Please check your internet connection. Your transcript has been saved."
```

### Whisper Returns Empty
```
→ Ignore the empty result
→ Stay in listening state
→ Don't send empty message to GPT
```

---

## Performance Considerations

1. **Debounce rapid state changes** — Don't update avatar emotion more than once per 300ms
2. **Abort in-flight requests** — When ending call, abort any pending GPT or TTS calls
3. **Memory cleanup** — Clear audio buffers, revoke object URLs, disconnect audio contexts
4. **Transcript limit** — If conversation exceeds 50 messages, start virtual scrolling (unlikely for MVP)

---

## Testing Checklist

### Happy Path
- [ ] Start conversation → hear Maya's greeting → see transcript
- [ ] Speak a question → see "thinking" state → hear Maya's answer
- [ ] Multiple back-and-forth exchanges maintain context
- [ ] End call → survey appears → submit feedback → confirmation
- [ ] Start new conversation → clean slate

### Edge Cases
- [ ] Mic permission denied → clear error message
- [ ] Very short utterance (< 0.5s) → ignored
- [ ] Very long pause before speaking → stays in listening state
- [ ] GPT returns invalid JSON → fallback response shown
- [ ] TTS fails → text-only response shown
- [ ] User interrupts Maya mid-speech → Maya stops, starts listening
- [ ] Rapid consecutive questions → queued properly
- [ ] Close widget mid-conversation → clean disconnect
- [ ] Network drops → graceful error handling

### Cross-Browser
- [ ] Chrome (desktop + mobile)
- [ ] Safari (desktop + iOS)
- [ ] Firefox (desktop)
- [ ] Edge (desktop)

---

## Acceptance Criteria

- [ ] Complete end-to-end voice conversation works (speak → hear response)
- [ ] Avatar emotion transitions match conversation context
- [ ] Transcript updates in real-time for both user and Maya messages
- [ ] Per-response feedback thumbs work
- [ ] End-of-call survey works and submits to backend
- [ ] "Start New" fully resets state
- [ ] No audio leaks (mic properly disconnected on end)
- [ ] No memory leaks (buffers cleared, listeners removed)
- [ ] Error states handled gracefully for all failure modes
- [ ] Console is clean (no uncaught errors or warnings)
- [ ] Performance is smooth (no jank during transitions)

---

## Output Files
- Updated `src/components/MayaWidget.tsx` (fully wired)
- Updated `src/App.tsx` (renders MayaWidget)
- Any additional utility/helper files needed for wiring
