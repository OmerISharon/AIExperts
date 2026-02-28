# Task 07: LiveKit Real-Time Voice Integration

## Objective
Integrate LiveKit SDK to enable real-time voice communication: connect to a LiveKit room, capture microphone audio from the user, manage audio tracks, handle connection states, and provide hooks for audio data that downstream tasks (STT, TTS) will consume.

---

## Context
LiveKit provides the WebRTC infrastructure for Maya's voice conversations. It handles:
- Microphone capture and audio streaming
- Room management (create/join/leave)
- Audio track publishing (user mic) and subscribing (Maya's voice)
- Connection state management
- Browser permission handling

**Architecture:**
```
User's Mic → LiveKit SDK (capture) → Audio Data → Whisper STT (Task 08)
Maya's Voice → TTS Audio (Task 09) → LiveKit SDK (publish) → User's Speaker
```

For MVP, LiveKit primarily manages the mic capture and room lifecycle. Audio data is extracted from LiveKit tracks and fed to OpenAI Whisper for transcription. Maya's TTS audio can be played directly via the Web Audio API (simpler) or published as a LiveKit track.

**Alternative simplified approach (if LiveKit setup is complex):** Skip LiveKit entirely for MVP and use the browser's `MediaRecorder` API directly for mic capture + `Web Audio API` for playback. This removes a dependency but loses WebRTC optimization. Document this as a trade-off and provide both approaches.

---

## Dependencies
- **Task 01** (project setup, LiveKit SDK installed)
- **Task 04** (UI shell with call interface to integrate into)

## Required Environment Variables
```
VITE_LIVEKIT_URL=wss://your-app.livekit.cloud
VITE_LIVEKIT_API_KEY=APIxxxxxxxx
VITE_LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxx
```

## LiveKit Account Setup
Before implementing, ensure:
1. LiveKit Cloud account created at https://cloud.livekit.io
2. A project created with API key and secret generated
3. Server URL available (format: `wss://your-project.livekit.cloud`)

---

## Approach A: Full LiveKit Integration

### 1. Token Generation (Server-Side)

LiveKit requires a JWT token to join rooms. This must be generated server-side.

**Create `src/app/api/livekit-token/route.ts`:**

```typescript
import { AccessToken } from "livekit-server-sdk";

export async function POST(req: Request) {
  const { roomName, participantName } = await req.json();

  const token = new AccessToken(
    process.env.LIVEKIT_API_KEY!,
    process.env.LIVEKIT_API_SECRET!,
    { identity: participantName }
  );

  token.addGrant({
    roomJoin: true,
    room: roomName,
    canPublish: true,        // User can publish mic audio
    canSubscribe: true,      // User can hear Maya
    canPublishData: true,
  });

  return Response.json({ token: await token.toJwt() });
}
```

Install server SDK: `npm install livekit-server-sdk`

### 2. LiveKit Hook: `src/hooks/useLiveKit.ts`

```typescript
import { useState, useCallback, useRef } from "react";
import {
  Room,
  RoomEvent,
  LocalParticipant,
  Track,
  ConnectionState,
} from "livekit-client";

interface UseLiveKitOptions {
  url: string;
  onAudioData?: (audioBuffer: Float32Array) => void; // For Whisper STT
  onConnectionChange?: (state: ConnectionState) => void;
}

interface UseLiveKitReturn {
  connect: (roomName: string) => Promise<void>;
  disconnect: () => void;
  connectionState: ConnectionState;
  isMicEnabled: boolean;
  toggleMic: () => void;
  isUserSpeaking: boolean;
  error: string | null;
}

export function useLiveKit(options: UseLiveKitOptions): UseLiveKitReturn {
  // Implementation details below
}
```

**`connect` flow:**
1. Fetch token from `/api/livekit-token` with a generated room name
2. Create new `Room()` instance
3. Register event listeners:
   - `RoomEvent.Connected` — update state
   - `RoomEvent.Disconnected` — cleanup
   - `RoomEvent.TrackSubscribed` — handle incoming Maya audio
   - `RoomEvent.ActiveSpeakersChanged` — detect user speaking
   - `RoomEvent.MediaDevicesError` — handle mic permission denied
4. Connect: `room.connect(url, token)`
5. Enable mic: `room.localParticipant.setMicrophoneEnabled(true)`
6. Set up audio capture for STT (see Audio Capture section)

**`disconnect` flow:**
1. Disable mic
2. Call `room.disconnect()`
3. Clean up event listeners
4. Reset state

**Audio Capture for STT:**
Use an `AudioContext` + `MediaStreamAudioSourceNode` + `ScriptProcessorNode` (or `AudioWorklet`) to extract raw PCM audio data from the local mic track:

```typescript
function setupAudioCapture(track: MediaStreamTrack, onAudioData: Function) {
  const audioContext = new AudioContext({ sampleRate: 16000 }); // Whisper prefers 16kHz
  const source = audioContext.createMediaStreamSource(new MediaStream([track]));
  const processor = audioContext.createScriptProcessor(4096, 1, 1);

  processor.onaudioprocess = (event) => {
    const audioData = event.inputBuffer.getChannelData(0);
    onAudioData(new Float32Array(audioData));
  };

  source.connect(processor);
  processor.connect(audioContext.destination); // Required for processing to work

  return () => {
    processor.disconnect();
    source.disconnect();
    audioContext.close();
  };
}
```

**Speaking Detection:**
LiveKit provides `ActiveSpeakersChanged` event. Alternatively, analyze audio buffer amplitude:
```typescript
function detectSpeaking(audioData: Float32Array, threshold: number = 0.01): boolean {
  const rms = Math.sqrt(audioData.reduce((sum, val) => sum + val * val, 0) / audioData.length);
  return rms > threshold;
}
```

---

## Approach B: Simplified Browser-Only Audio (No LiveKit)

If LiveKit setup is too complex for MVP timeline, use browser APIs directly:

### `src/hooks/useAudioCapture.ts`

```typescript
import { useState, useRef, useCallback } from "react";

interface UseAudioCaptureReturn {
  startCapture: () => Promise<void>;
  stopCapture: () => void;
  isCapturing: boolean;
  isUserSpeaking: boolean;
  error: string | null;
}

export function useAudioCapture(
  onAudioData?: (audioBuffer: Float32Array) => void
): UseAudioCaptureReturn {
  // Uses navigator.mediaDevices.getUserMedia({ audio: true })
  // Sets up AudioContext for processing
  // Provides same interface as LiveKit approach
}
```

**`startCapture` flow:**
1. Request mic permission: `navigator.mediaDevices.getUserMedia({ audio: true })`
2. Create `AudioContext` at 16kHz sample rate
3. Set up `ScriptProcessorNode` or `AudioWorkletNode`
4. Feed audio data to callback
5. Run speaking detection

**`stopCapture` flow:**
1. Stop all media tracks
2. Close AudioContext
3. Reset state

**For TTS playback (Approach B):**
```typescript
function playAudioBuffer(audioData: ArrayBuffer): Promise<void> {
  return new Promise((resolve) => {
    const audioContext = new AudioContext();
    audioContext.decodeAudioData(audioData, (buffer) => {
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.onended = () => {
        audioContext.close();
        resolve();
      };
      source.start();
    });
  });
}
```

---

## Integration with CallInterface

Update `CallInterface.tsx` (from Task 04) to use the voice hook:

```typescript
// In CallInterface.tsx
const {
  connect,
  disconnect,
  isMicEnabled,
  isUserSpeaking,
  connectionState,
} = useLiveKit({
  url: import.meta.env.VITE_LIVEKIT_URL,
  onAudioData: handleAudioData, // Feed to Whisper in Task 08
});

// Wire up buttons
const handleStartCall = async () => {
  setCallState("connecting");
  await connect(`maya-${Date.now()}`);
  setCallState("active");
};

const handleEndCall = () => {
  disconnect();
  setCallState("ended");
};

// Pass to MicIndicator
<MicIndicator isActive={isMicEnabled} isUserSpeaking={isUserSpeaking} />
```

---

## Error Handling

Handle these scenarios gracefully:
1. **Mic permission denied:** Show clear message: "Maya needs microphone access to have a conversation. Please allow mic access and try again."
2. **LiveKit connection failed:** "Having trouble connecting. Please check your internet and try again."
3. **Mic not found:** "No microphone detected. Please connect a microphone."
4. **Connection dropped mid-conversation:** Attempt auto-reconnect (3 attempts), then show "Connection lost" with retry button.
5. **Browser not supported:** "Voice conversations require a modern browser. Please use Chrome, Safari, Firefox, or Edge."

---

## Browser Compatibility Notes

- `getUserMedia` requires HTTPS (except localhost)
- `AudioContext` may need user gesture to start (click handler)
- iOS Safari requires `webkitAudioContext` (handled by LiveKit SDK)
- ScriptProcessorNode is deprecated but widely supported — AudioWorklet is the modern replacement but more complex

---

## Acceptance Criteria

- [ ] User can grant mic permission when starting a call
- [ ] Mic audio is captured and available as raw audio data (for Whisper)
- [ ] Speaking detection works (isUserSpeaking flag updates)
- [ ] Connection state management works (connecting, connected, disconnected)
- [ ] Mic can be toggled on/off
- [ ] Clean disconnect with no resource leaks
- [ ] Error handling for all failure modes (permission, connection, browser)
- [ ] MicIndicator component reflects real mic state
- [ ] Works on Chrome, Safari, Firefox (desktop + mobile)
- [ ] Audio data flows at 16kHz sample rate (Whisper-compatible)

---

## Output Files
- `src/hooks/useLiveKit.ts` (or `src/hooks/useAudioCapture.ts` for Approach B)
- `src/app/api/livekit-token/route.ts` (Approach A only)
- Utility: audio processing helpers (speaking detection, audio context setup)
