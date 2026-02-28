# Task 05: Maya Conversation Engine — System Prompt + GPT-4 Integration

## Objective
Build the core AI conversation engine: the system prompt that defines Maya's personality and knowledge, the GPT-4 API integration that generates responses with emotion classification, conversation history management, and JSON response parsing. This is Maya's "brain."

---

## Context
Maya is the EZpresence Hostess — a warm, professional AI assistant that helps users learn about EZpresence platform features via voice conversation. GPT-4 generates her responses AND classifies the appropriate emotion for avatar display in a single API call (no separate emotion-detection step).

**Key design decision:** GPT-4 returns structured JSON containing both the response text and an emotion label. The system prompt enforces this format.

---

## Dependencies
- **Task 01** (project setup, types, env variables, OpenAI package installed)

## Required Environment Variables
```
VITE_OPENAI_API_KEY=sk-...
```

**Security note:** In production, the OpenAI API key must NEVER be exposed to the frontend. API calls should go through a backend proxy. For MVP, if calling from frontend, acknowledge this limitation and document it. Ideally, create a thin API route (e.g., Next.js `/api/maya`) that proxies the request.

---

## Files to Create

### 1. `src/config/prompts.ts` — System Prompt

This file contains Maya's complete system prompt. It must be carefully crafted to:
- Define Maya's personality and tone
- List her expertise areas with enough detail for helpful answers
- Enforce the JSON response format
- Define emotion classification rules with clear examples
- Handle edge cases (out-of-scope questions, frustrated users)

```typescript
export const MAYA_SYSTEM_PROMPT = `
You are Maya, the EZpresence Hostess. Your role is to welcome users and help them understand EZpresence features and social media management in a warm, conversational way.

**Your Personality:**
- Warm and welcoming, like a restaurant hostess greeting guests
- Patient and encouraging — users may be new to social media management
- Professional but approachable
- You ask clarifying questions to understand what users need
- You use conversational language, not robotic or overly formal

**Your Expertise Areas:**

1. **Content Scheduling**
   - How to schedule posts across platforms (Instagram, TikTok, Facebook, YouTube, LinkedIn)
   - Best posting times and timing strategies
   - Multi-platform scheduling workflow
   - Calendar view and content planning
   - Draft management and approval workflows

2. **Studio (Content Generation)**
   - Overview of the Studio feature for content creation
   - Video Creators — different creator tools for different content types
   - Recommendations for which creator to use for different goals
   - Best practices for short-form video content
   - Content templates and starting points
   - Tips for engaging social media content

3. **Account Setup**
   - Getting started with EZpresence
   - Connecting social media profiles
   - Workspace configuration
   - Team member invitations
   - Initial platform orientation and navigation
   - Subscription and plan information basics

**CRITICAL: Response Format**
You MUST respond in valid JSON format ONLY. No text before or after the JSON. Your response must be parseable by JSON.parse().

{
  "response": "Your conversational response here...",
  "emotion": "one_of: listening, thinking, happy, sad, confused, understanding"
}

**Emotion Classification Rules:**
- "listening": When acknowledging their input, showing attentiveness, inviting them to say more
- "thinking": When you need to consider a complex question, weighing options, analyzing their situation
- "happy": When giving helpful tips, explaining features enthusiastically, positive encouragement, greeting them
- "sad": When apologizing for limitations, expressing empathy about frustrations, addressing problems
- "confused": When the user says something unclear and you need clarification, or their question is ambiguous
- "understanding": When confirming you understand their needs, affirming their situation, "I get what you mean"

**Emotion Examples:**
- User: "How do I schedule posts?" → emotion: "happy" (you're excited to help with a clear question)
- User: "This is too complicated" → emotion: "sad" (empathy for their frustration)
- User: "What do you mean by that?" → emotion: "understanding" (acknowledging and re-explaining)
- User: "asdjfkl video thing" → emotion: "confused" (unclear input, ask for clarification)
- User: "I connected my Instagram" → emotion: "understanding" (affirming their progress)
- User: "What's the best strategy for growth?" → emotion: "thinking" (considering a complex question)

**Behavioral Guidelines:**
- Keep responses concise but helpful — aim for 2-4 sentences typically, up to a short paragraph for complex topics
- Responses will be spoken aloud via text-to-speech, so write naturally spoken language (avoid bullet points, markdown, special characters)
- Use examples specific to social media management when helpful
- If asked about something outside your expertise areas, politely say: "That's a great question, but it's a bit outside my area. For that, I'd recommend reaching out to the EZpresence team at contact@ezpresence.com — they'll be able to help you out!"
- If user is frustrated or insists on talking to a human, warmly say: "I completely understand. Let me connect you with our team. You can reach them directly at contact@ezpresence.com and they'll take great care of you."
- Encourage users to explore features hands-on after learning about them
- End conversations warmly: "It was great chatting with you! Feel free to come back anytime you have questions."
- Never make up features that don't exist
- Never provide specific pricing unless you're certain (redirect to website/support instead)

**Your Greeting (use for first message of conversation):**
"Hey there! I'm Maya, your EZpresence Hostess. I'm here to help you get the most out of the platform — whether it's scheduling content, using Studio, or setting things up. What can I help you with today?"
`;
```

### 2. `src/services/mayaEngine.ts` — Conversation Engine

The core module that manages conversation history and calls GPT-4.

```typescript
import { Emotion, MayaResponse, TranscriptMessage } from "../types";

// Conversation history for multi-turn context
interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
}

export class MayaEngine {
  private history: ConversationTurn[] = [];
  private apiKey: string;
  private model: string;

  constructor(apiKey: string, model: string = "gpt-4-turbo") {
    this.apiKey = apiKey;
    this.model = model;
  }

  // Send user message, get Maya's response + emotion
  async getResponse(userMessage: string): Promise<MayaResponse> { ... }

  // Reset conversation (new chat)
  reset(): void { ... }

  // Get full history (for transcript storage)
  getHistory(): ConversationTurn[] { ... }
}
```

**`getResponse()` implementation details:**

1. Add user message to history: `{ role: "user", content: userMessage }`
2. Call OpenAI API:
   ```
   POST https://api.openai.com/v1/chat/completions
   {
     model: "gpt-4-turbo",
     messages: [
       { role: "system", content: MAYA_SYSTEM_PROMPT },
       ...this.history
     ],
     temperature: 0.7,
     max_tokens: 400,
     response_format: { type: "json_object" }
   }
   ```
3. Parse response JSON: extract `response` and `emotion` fields
4. Add assistant response to history: `{ role: "assistant", content: parsed.response }`
5. Validate emotion is one of the 6 valid values — if not, default to `"happy"`
6. Return `{ response: parsed.response, emotion: parsed.emotion }`

**Error handling:**
- If JSON parse fails: extract text content, use emotion `"happy"` as fallback
- If API call fails: return `{ response: "I'm having a little trouble right now. Could you try asking again?", emotion: "sad" }`
- If response is empty: return `{ response: "Sorry, I didn't catch that. Could you rephrase?", emotion: "confused" }`

**History management:**
- Keep last 20 turns max (10 user + 10 assistant) to stay within context window
- When exceeding, trim oldest turns (keep system prompt always)
- `reset()` clears history array

### 3. `src/services/openai.ts` — OpenAI API Client

A thin wrapper around OpenAI API calls. Can use the `openai` npm package or raw `fetch`.

**Using the `openai` package:**
```typescript
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true, // MVP only — move to backend for production
});

export { openai };
```

**Or using raw fetch (if you want to avoid exposing the key):**
```typescript
export async function callGPT(messages: Array<{role: string, content: string}>) {
  const response = await fetch("/api/maya", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  return response.json();
}
```

### 4. `src/hooks/useConversation.ts` — React Hook

A custom hook that wraps `MayaEngine` for easy use in React components.

```typescript
import { useState, useRef, useCallback } from "react";
import { Emotion, TranscriptMessage, MayaResponse } from "../types";
import { MayaEngine } from "../services/mayaEngine";

interface UseConversationReturn {
  transcript: TranscriptMessage[];
  currentEmotion: Emotion;
  isProcessing: boolean;
  sendMessage: (text: string) => Promise<void>;
  resetConversation: () => void;
  getGreeting: () => Promise<void>;
}

export function useConversation(): UseConversationReturn {
  // Initialize MayaEngine
  // Manage transcript state
  // Handle sending messages and updating state
  // Handle errors gracefully
}
```

**`sendMessage` flow:**
1. Set `isProcessing = true`
2. Add user message to transcript (with generated UUID)
3. Set emotion to `"thinking"`
4. Call `engine.getResponse(text)`
5. Add Maya's response to transcript (with emotion)
6. Set `currentEmotion` to response emotion
7. Set `isProcessing = false`
8. Return (caller can then trigger TTS)

**`getGreeting` flow:**
1. Call `engine.getResponse("Hello")` (or use a hardcoded greeting)
2. Add greeting to transcript as Maya message
3. Set emotion to `"happy"`

**`resetConversation` flow:**
1. Call `engine.reset()`
2. Clear transcript array
3. Set emotion to `"listening"`
4. Set `isProcessing = false`

---

## Testing the Engine

Create a quick test by calling the engine from a temporary button in the UI:

```typescript
// Temporary test in App.tsx
const { sendMessage, transcript, currentEmotion } = useConversation();

// Test cases to verify:
await sendMessage("How do I schedule posts?");
// Expected: emotion "happy", helpful response about scheduling

await sendMessage("This is too complicated for me");
// Expected: emotion "sad", empathetic response

await sendMessage("asjdfklj what video thing");
// Expected: emotion "confused", clarification request

await sendMessage("I see, that makes sense");
// Expected: emotion "understanding", affirming response

await sendMessage("Can you help me with my taxes?");
// Expected: out-of-scope redirect to contact@ezpresence.com
```

Verify:
- Responses are coherent and in-character
- Emotions match the content
- JSON parsing works consistently
- Conversation history maintains context (follow-up questions work)
- Error handling doesn't crash the app

---

## Acceptance Criteria

- [ ] `MAYA_SYSTEM_PROMPT` is comprehensive and produces consistent JSON responses
- [ ] `MayaEngine.getResponse()` correctly calls GPT-4 and parses JSON
- [ ] Emotion classification is accurate for typical conversation patterns
- [ ] Conversation history maintains multi-turn context
- [ ] History trimming works (doesn't exceed 20 turns)
- [ ] `reset()` fully clears state
- [ ] Error handling covers: JSON parse failure, API error, empty response
- [ ] `useConversation` hook provides clean React interface
- [ ] `response_format: { type: "json_object" }` is used to enforce JSON output
- [ ] No API key exposed in frontend bundle (or documented as MVP limitation)
- [ ] TypeScript compiles cleanly

---

## Output Files
- `src/config/prompts.ts`
- `src/services/mayaEngine.ts`
- `src/services/openai.ts`
- `src/hooks/useConversation.ts`
