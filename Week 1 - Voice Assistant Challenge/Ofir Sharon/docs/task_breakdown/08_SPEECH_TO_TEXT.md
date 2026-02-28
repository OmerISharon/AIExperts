# Task 08: Speech-to-Text — OpenAI Whisper Integration

## Objective
Implement speech-to-text transcription using OpenAI's Whisper API. Capture the user's spoken words, detect when they've finished speaking (silence detection), send the audio to Whisper for transcription, and return the transcribed text to the conversation engine.

---

## Context
In the Maya conversation flow, the user speaks into their microphone. Their speech is captured by the audio system (Task 07), accumulated into a buffer, and when the user pauses (silence detection), the buffer is sent to OpenAI Whisper for transcription. The resulting text is then passed to the conversation engine (Task 05) as the user's message.

**Flow:**
```
User speaks → Audio capture (Task 07) → Audio buffer accumulates
User pauses → Silence detected → Send buffer to Whisper API
Whisper returns text → Display in transcript → Send to GPT-4 (Task 05)
```

**Real-time vs. Batch:** For MVP, use **batch transcription** — accumulate audio until silence, then transcribe the whole utterance. Real-time streaming transcription (word-by-word) is more complex and not needed for MVP. However, show a visual indicator ("Hearing you...") while the user speaks, even before transcription.

---

## Dependencies
- **Task 01** (project setup, OpenAI package)
- **Task 07** (audio capture providing raw audio data)

## Required Environment Variable
```
OPENAI_API_KEY=sk-...  (server-side, used by /api/whisper endpoint)
```

---

## Architecture

### Silence Detection

Detect when the user stops speaking to trigger transcription:

**Algorithm:**
1. Maintain a rolling RMS (root-mean-square) value from audio data
2. If RMS drops below threshold for >1.5 seconds, consider it silence
3. When silence detected after speech, trigger transcription
4. Minimum speech duration: 0.5 seconds (ignore very short sounds like clicks)

```typescript
interface SilenceDetectorConfig {
  silenceThreshold: number;     // RMS level below which counts as silence (e.g., 0.01)
  silenceDuration: number;      // ms of continuous silence to trigger (e.g., 1500)
  minSpeechDuration: number;    // ms minimum speech to count (e.g., 500)
}
```

### Audio Buffer Management

While the user speaks, accumulate audio data into a buffer:

```typescript
class AudioBufferCollector {
  private chunks: Float32Array[] = [];
  private sampleRate: number;

  constructor(sampleRate: number = 16000) {
    this.sampleRate = sampleRate;
  }

  addChunk(data: Float32Array): void {
    this.chunks.push(new Float32Array(data)); // Copy to avoid reference issues
  }

  getDuration(): number {
    const totalSamples = this.chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    return totalSamples / this.sampleRate;
  }

  getWavBlob(): Blob {
    // Combine all chunks into a single WAV file
    // Whisper accepts: wav, mp3, m4a, webm, mp4
    // WAV is simplest to create from raw PCM
  }

  clear(): void {
    this.chunks = [];
  }
}
```

### WAV Encoding

Whisper needs an audio file, not raw PCM. Encode the buffer as a WAV:

```typescript
function encodeWAV(samples: Float32Array, sampleRate: number): Blob {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  // WAV header
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);           // PCM format
  view.setUint16(20, 1, true);            // PCM = 1
  view.setUint16(22, 1, true);            // Mono
  view.setUint32(24, sampleRate, true);   // Sample rate
  view.setUint32(28, sampleRate * 2, true); // Byte rate
  view.setUint16(32, 2, true);            // Block align
  view.setUint16(34, 16, true);           // Bits per sample
  writeString(view, 36, 'data');
  view.setUint32(40, samples.length * 2, true);

  // Write samples (convert float32 to int16)
  const offset = 44;
  for (let i = 0; i < samples.length; i++) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset + i * 2, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
  }

  return new Blob([buffer], { type: 'audio/wav' });
}

function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}
```

---

## Backend Endpoint: `POST /api/whisper`

Proxy the Whisper API call through the backend (keeps API key secure).

**File: `src/app/api/whisper/route.ts`**

```typescript
import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function POST(req: Request) {
  const formData = await req.formData();
  const audioFile = formData.get("audio") as File;

  if (!audioFile) {
    return Response.json({ error: "No audio file provided" }, { status: 400 });
  }

  try {
    const transcription = await openai.audio.transcriptions.create({
      file: audioFile,
      model: "whisper-1",
      language: "en",           // Set language for better accuracy
      response_format: "text",  // Just the text, no timestamps
    });

    return Response.json({ text: transcription });
  } catch (error) {
    console.error("Whisper error:", error);
    return Response.json({ error: "Transcription failed" }, { status: 500 });
  }
}
```

---

## React Hook: `src/hooks/useWhisper.ts`

```typescript
import { useState, useRef, useCallback } from "react";

interface UseWhisperOptions {
  silenceThreshold?: number;
  silenceDuration?: number;
  minSpeechDuration?: number;
  onTranscription: (text: string) => void;  // Called when transcription is ready
  onSpeechStart?: () => void;               // Called when user starts speaking
  onSpeechEnd?: () => void;                 // Called when user stops speaking
}

interface UseWhisperReturn {
  feedAudioData: (data: Float32Array) => void;  // Connect to audio capture
  isTranscribing: boolean;                       // Whisper API call in progress
  isUserSpeaking: boolean;                       // Currently detecting speech
  lastTranscription: string | null;              // Most recent result
  error: string | null;
}

export function useWhisper(options: UseWhisperOptions): UseWhisperReturn {
  // Implementation
}
```

**`feedAudioData` logic (called per audio chunk from Task 07):**

```
1. Calculate RMS of incoming chunk
2. If RMS > silenceThreshold:
   a. Mark as speaking (set isSpeaking = true)
   b. Reset silence timer
   c. Add chunk to buffer
3. If RMS <= silenceThreshold:
   a. Start/continue silence timer
   b. Still add chunk to buffer (captures trailing audio)
   c. If silence timer exceeds silenceDuration AND buffer has > minSpeechDuration:
      - Set isSpeaking = false
      - Call onSpeechEnd()
      - Trigger transcription:
        i. Set isTranscribing = true
        ii. Convert buffer to WAV blob
        iii. Send to /api/whisper
        iv. On success: call onTranscription(text), clear buffer
        v. On failure: set error, clear buffer
        vi. Set isTranscribing = false
```

**Sending to Whisper:**
```typescript
async function transcribeAudio(wavBlob: Blob): Promise<string> {
  const formData = new FormData();
  formData.append("audio", wavBlob, "recording.wav");

  const response = await fetch("/api/whisper", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) throw new Error("Transcription failed");

  const data = await response.json();
  return data.text.trim();
}
```

---

## Integration with Conversation Flow

Wire `useWhisper` into the `CallInterface`:

```typescript
// In CallInterface or MayaWidget
const { sendMessage, currentEmotion } = useConversation();

const { feedAudioData, isTranscribing, isUserSpeaking } = useWhisper({
  silenceThreshold: 0.01,
  silenceDuration: 1500,
  minSpeechDuration: 500,
  onTranscription: async (text) => {
    // User finished speaking, we have their text
    console.log("User said:", text);
    await sendMessage(text);  // Send to GPT-4 via conversation engine
  },
  onSpeechStart: () => {
    // Update UI: show "Hearing you..."
    setMayaEmotion("listening");
  },
  onSpeechEnd: () => {
    // Update UI: show "Processing..."
    setMayaEmotion("thinking");
  },
});

// Connect audio capture to Whisper
const audioCapture = useLiveKit({
  // or useAudioCapture
  onAudioData: feedAudioData,  // Pipeline: mic → whisper hook
});
```

---

## Real-Time Transcription Preview (Optional Enhancement)

For a better UX, show partial text while the user speaks (before Whisper processes):
- Use the browser's `webkitSpeechRecognition` API as a fast preview
- Show preview text in gray/italic
- Replace with Whisper result when it arrives

This is optional for MVP but significantly improves perceived responsiveness.

```typescript
// Optional: browser-native speech recognition for preview
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = true;
recognition.interimResults = true;
recognition.onresult = (event) => {
  const transcript = event.results[event.results.length - 1][0].transcript;
  setPreviewText(transcript); // Show gray preview text
};
```

---

## Edge Cases to Handle

1. **Very short utterances** (< 0.5s): Ignore — likely accidental noise
2. **Very long utterances** (> 30s): Split into 30s chunks for Whisper (it has a 25MB / ~30 min limit, but latency increases with length)
3. **Empty transcription result**: Whisper returns empty string — ignore, don't send to GPT
4. **Non-English speech**: If detected, respond gracefully (Maya currently English-only)
5. **Background noise**: Adjust `silenceThreshold` — may need to be tunable
6. **Simultaneous speaking** (user speaks while Maya's TTS is playing): Implement echo cancellation or mute mic during Maya's speech

---

## Acceptance Criteria

- [ ] Audio data from mic flows into the Whisper pipeline
- [ ] Silence detection correctly identifies when user stops speaking
- [ ] Audio buffer correctly encoded as WAV
- [ ] `/api/whisper` endpoint transcribes audio via OpenAI Whisper API
- [ ] Transcribed text sent to conversation engine
- [ ] `isTranscribing` state updates correctly (for UI loading indicator)
- [ ] `isUserSpeaking` state updates correctly (for mic indicator)
- [ ] Empty transcriptions are discarded
- [ ] Very short audio (< 0.5s) is ignored
- [ ] Errors handled gracefully (API failure, network issues)
- [ ] No audio memory leaks (buffers cleared after transcription)

---

## Output Files
- `src/hooks/useWhisper.ts`
- `src/app/api/whisper/route.ts`
- Audio utility functions (WAV encoding, silence detection, buffer management)
