# Task 09: Text-to-Speech Integration — Maya's Voice

## Objective
Implement text-to-speech so Maya can speak her responses aloud. Integrate with OpenAI TTS (primary) or ElevenLabs (optional upgrade), manage audio playback, sync the avatar emotion state with voice output, and handle the playback lifecycle.

---

## Context
When GPT-4 generates Maya's response, the text is converted to speech and played through the user's speaker. During playback, the avatar stays on the response's emotion. When playback ends, the avatar returns to "listening" for the next user input.

**Flow:**
```
GPT-4 response (text + emotion) → TTS API → Audio data
  → Set avatar to response emotion
  → Play audio through speaker
  → Audio ends → Set avatar to "listening"
  → Ready for next user input
```

**TTS Options:**
1. **OpenAI TTS** — Simpler, cheaper ($0.015/1K chars), good quality
2. **ElevenLabs** — Premium quality, more natural, higher cost (~$0.30/1K chars), configurable voices

Implement OpenAI TTS as the default. ElevenLabs as an optional swap-in.

---

## Dependencies
- **Task 01** (project setup, OpenAI package)
- **Task 05** (conversation engine provides response text)

## Required Environment Variables
```
# OpenAI TTS (primary)
OPENAI_API_KEY=sk-...  (server-side, already configured in Task 06)

# ElevenLabs (optional)
VITE_ELEVENLABS_API_KEY=...
VITE_ELEVENLABS_VOICE_ID=...
```

---

## Backend Endpoint: `POST /api/tts`

Proxy TTS calls through backend (keeps API key secure, allows easy provider switching).

**File: `src/app/api/tts/route.ts`**

```typescript
import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function POST(req: Request) {
  const { text, voice } = await req.json();

  if (!text || text.trim().length === 0) {
    return Response.json({ error: "No text provided" }, { status: 400 });
  }

  try {
    const mp3Response = await openai.audio.speech.create({
      model: "tts-1",         // or "tts-1-hd" for higher quality
      voice: voice || "nova", // Maya's voice — "nova" is warm and female
      input: text,
      speed: 1.0,             // Normal speed (0.25 to 4.0)
    });

    // Return the audio as a stream/buffer
    const audioBuffer = await mp3Response.arrayBuffer();

    return new Response(audioBuffer, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Length": audioBuffer.byteLength.toString(),
      },
    });
  } catch (error) {
    console.error("TTS error:", error);
    return Response.json({ error: "Speech generation failed" }, { status: 500 });
  }
}
```

**OpenAI Voice Options (pick one for Maya):**
- `"nova"` — ✅ Recommended. Warm, friendly female voice
- `"shimmer"` — Soft, warm female voice
- `"alloy"` — Neutral, balanced
- Test both `nova` and `shimmer`, pick whichever sounds more like a "hostess"

### Optional: ElevenLabs Provider

```typescript
// Alternative TTS provider
async function elevenLabsTTS(text: string): Promise<ArrayBuffer> {
  const response = await fetch(
    `https://api.elevenlabs.io/v1/text-to-speech/${process.env.ELEVENLABS_VOICE_ID}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "xi-api-key": process.env.ELEVENLABS_API_KEY!,
      },
      body: JSON.stringify({
        text,
        model_id: "eleven_monolingual_v1",
        voice_settings: {
          stability: 0.6,       // Slightly variable for natural feel
          similarity_boost: 0.75,
        },
      }),
    }
  );
  return response.arrayBuffer();
}
```

---

## React Hook: `src/hooks/useTTS.ts`

```typescript
import { useState, useRef, useCallback } from "react";

interface UseTTSOptions {
  onPlaybackStart?: () => void;    // Maya starts speaking
  onPlaybackEnd?: () => void;      // Maya finishes speaking
  onError?: (error: string) => void;
}

interface UseTTSReturn {
  speak: (text: string) => Promise<void>;  // Convert text to speech and play
  stop: () => void;                         // Stop current playback
  isSpeaking: boolean;                      // Audio currently playing
  isGenerating: boolean;                    // TTS API call in progress
  error: string | null;
}

export function useTTS(options: UseTTSOptions = {}): UseTTSReturn {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const speak = useCallback(async (text: string) => {
    // 1. Cancel any current playback
    stop();

    // 2. Call TTS API
    setIsGenerating(true);
    setError(null);

    try {
      abortControllerRef.current = new AbortController();

      const response = await fetch("/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) throw new Error("TTS generation failed");

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      // 3. Play audio
      setIsGenerating(false);
      setIsSpeaking(true);
      options.onPlaybackStart?.();

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl); // Cleanup
        options.onPlaybackEnd?.();
      };

      audio.onerror = () => {
        setIsSpeaking(false);
        setError("Audio playback failed");
        URL.revokeObjectURL(audioUrl);
        options.onPlaybackEnd?.();
      };

      await audio.play();
    } catch (err) {
      if ((err as Error).name === "AbortError") return; // Intentional cancel
      setIsGenerating(false);
      setIsSpeaking(false);
      setError("Failed to generate speech");
      options.onError?.((err as Error).message);
    }
  }, [options]);

  const stop = useCallback(() => {
    // Abort any in-flight API call
    abortControllerRef.current?.abort();

    // Stop any playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }

    setIsSpeaking(false);
    setIsGenerating(false);
  }, []);

  return { speak, stop, isSpeaking, isGenerating, error };
}
```

---

## Integration with Conversation Flow

Wire TTS into the conversation pipeline in `MayaWidget` or `CallInterface`:

```typescript
const { speak, stop, isSpeaking } = useTTS({
  onPlaybackStart: () => {
    setCallState("speaking");
    // Mute user's mic during Maya's speech to prevent echo
    // (optional but recommended)
  },
  onPlaybackEnd: () => {
    setCallState("active");
    setMayaEmotion("listening");
    // Unmute user's mic
  },
});

// After GPT-4 response is received:
const handleMayaResponse = async (response: MayaResponse) => {
  setMayaEmotion(response.emotion);  // Update avatar
  await speak(response.response);     // Play voice
  // After speak() resolves, avatar returns to "listening" (via onPlaybackEnd)
};
```

---

## Audio Queue (For Long Responses)

If Maya's response is long, the TTS API call takes longer. Consider:

1. **Simple approach (recommended for MVP):** Send entire text at once, wait for full audio, play it
2. **Chunked approach (advanced):** Split text into sentences, generate TTS for first sentence, start playing immediately, generate remaining sentences in parallel

For MVP, use the simple approach. Long responses should be avoided anyway (system prompt limits to 2-4 sentences).

---

## Mic Management During Playback

To prevent echo (Maya's voice being picked up by the user's mic and re-transcribed):

**Option A: Mute mic during playback**
```typescript
onPlaybackStart: () => {
  // Disable Whisper processing (don't transcribe during playback)
  setTranscriptionEnabled(false);
},
onPlaybackEnd: () => {
  setTranscriptionEnabled(true);
},
```

**Option B: Echo cancellation flag**
- Set a flag that tells the Whisper hook to ignore audio during playback
- Simpler than actually muting the hardware mic

---

## Edge Cases

1. **User interrupts Maya mid-speech:** Stop TTS playback, start listening immediately
   ```typescript
   onSpeechStart: () => {
     if (isSpeaking) stop(); // User interrupted, stop Maya
   }
   ```

2. **Empty response text:** Don't call TTS, go straight to listening state

3. **TTS API failure:** Show text-only response in transcript, display error toast, continue conversation

4. **Browser autoplay policy:** Audio may be blocked until user interacts. The "Start Conversation" button click satisfies this requirement.

5. **Consecutive rapid responses:** Queue them — don't overlap audio

---

## Acceptance Criteria

- [ ] Maya's text responses are converted to speech via OpenAI TTS
- [ ] Audio plays through user's speaker
- [ ] `/api/tts` endpoint generates audio and returns MP3 buffer
- [ ] `useTTS` hook manages playback lifecycle (generating → speaking → done)
- [ ] Avatar emotion stays on response emotion during playback
- [ ] Avatar returns to "listening" when playback ends
- [ ] Playback can be stopped (user interruption or "End Call")
- [ ] No echo: user's mic input is ignored during Maya's speech
- [ ] Errors handled gracefully (API failure shows text-only fallback)
- [ ] Audio resources cleaned up (object URLs revoked, Audio elements removed)
- [ ] No overlapping audio playback

---

## Output Files
- `src/hooks/useTTS.ts`
- `src/app/api/tts/route.ts`
- `src/services/tts.ts` (optional: provider abstraction for OpenAI vs ElevenLabs)
