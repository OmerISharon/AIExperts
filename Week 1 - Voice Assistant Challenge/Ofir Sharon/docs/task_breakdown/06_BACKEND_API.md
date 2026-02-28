# Task 06: Backend API — Feedback, Transcripts, Email & GPT Proxy

## Objective
Build the backend API layer: a GPT-4 proxy endpoint (so the API key stays server-side), a feedback submission endpoint, a transcript storage endpoint, and email notification when feedback is submitted. Implemented as Next.js API routes or a simple Express server.

---

## Context
The Maya widget needs a lightweight backend for three reasons:
1. **Security** — The OpenAI API key must not be exposed in the frontend bundle. All GPT-4 calls should be proxied through a backend endpoint.
2. **Feedback** — When users submit feedback (thumbs up/down + optional text), it must be stored and emailed to `contact@ezpresence.com`.
3. **Transcripts** — When a conversation ends, the full transcript is sent to the backend for storage and future analytics.

For MVP, this can be a few API routes in the same Vite/Next.js project or a small standalone Express server.

---

## Dependencies
- **Task 01** (project setup, types)

## Required Environment Variables (server-side, NOT `VITE_` prefixed)
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@localhost:5432/maya  (or Supabase connection string)
FEEDBACK_EMAIL=contact@ezpresence.com
SENDGRID_API_KEY=SG.xxxxxx  (or RESEND_API_KEY, or SMTP config)
```

---

## Architecture Decision

**Option A: Next.js API Routes (Recommended if using Next.js)**
- Files live in `src/app/api/` or `pages/api/`
- Deploy alongside frontend on Vercel
- Zero extra infrastructure

**Option B: Standalone Express Server (If using plain Vite)**
- Separate `server/` directory with Express
- Runs on a different port (e.g., 3001)
- Deploy separately or on same Vercel as serverless functions

**For this spec, we assume Option A (Next.js API routes)**. If using plain Vite + Express, adapt the route handlers into Express route handlers — the logic is identical.

---

## Endpoints to Build

### 1. `POST /api/maya` — GPT-4 Proxy

Proxies conversation requests to OpenAI so the API key stays server-side.

**Request body:**
```typescript
{
  messages: Array<{
    role: "user" | "assistant";
    content: string;
  }>;
}
```

**Server-side logic:**
1. Validate request body (messages array exists, is not empty)
2. Prepend the system prompt to messages array
3. Call OpenAI GPT-4:
   ```typescript
   const response = await openai.chat.completions.create({
     model: "gpt-4-turbo",
     messages: [
       { role: "system", content: MAYA_SYSTEM_PROMPT },
       ...req.body.messages,
     ],
     temperature: 0.7,
     max_tokens: 400,
     response_format: { type: "json_object" },
   });
   ```
4. Parse the response JSON to validate format
5. Return to client:
   ```typescript
   {
     response: string;  // Maya's text response
     emotion: Emotion;  // Classified emotion
   }
   ```

**Error handling:**
- If OpenAI returns an error: return `500` with generic error message
- If JSON parsing fails: return the raw text with `"happy"` as default emotion
- Rate limiting: optionally limit to 10 requests per minute per IP (simple in-memory counter for MVP)

**Response:** `200 OK`
```json
{
  "response": "Great question! Content scheduling lets you...",
  "emotion": "happy"
}
```

### 2. `POST /api/feedback` — Feedback Submission

Receives end-of-conversation feedback and per-response ratings.

**Request body (matches `FeedbackPayload` type):**
```typescript
{
  conversationId: string;       // UUID
  transcript: TranscriptMessage[];
  overallRating: "up" | "down" | null;
  feedbackText: string;
  perResponseRatings: Array<{
    messageId: string;
    rating: "up" | "down";
  }>;
  submittedAt: string;          // ISO timestamp
}
```

**Server-side logic:**
1. Validate required fields (conversationId, transcript exist)
2. Store feedback in database (see Database Schema below)
3. If `overallRating` is not null, send email notification
4. Return `201 Created`

**Email notification content:**
```
Subject: Maya Feedback — [👍/👎] — [timestamp]

Conversation ID: [conversationId]
Overall Rating: [👍 Helpful / 👎 Not Helpful]
Feedback Text: [feedbackText or "No additional feedback"]

Per-Response Ratings:
- Message #1 (Maya): 👍
- Message #3 (Maya): 👎
- ... (only messages that were rated)

Transcript Summary:
User: How do I schedule posts?
Maya: Great question! Content scheduling lets you...
User: What about YouTube?
Maya: Studio integrates with Instagram, TikTok...

---
Sent from Maya · EZpresence Hostess Widget
```

### 3. `POST /api/transcript` — Transcript Storage

Stores the full conversation transcript when a call ends (even without feedback).

**Request body:**
```typescript
{
  conversationId: string;
  transcript: TranscriptMessage[];
  startedAt: string;            // ISO timestamp
  endedAt: string;              // ISO timestamp
  messageCount: number;
  duration: number;             // seconds
}
```

**Server-side logic:**
1. Validate required fields
2. Store in database
3. Return `201 Created` with `{ stored: true }`

---

## Database Schema

**Option A: PostgreSQL (recommended)**

```sql
-- Conversations table
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id VARCHAR(255) UNIQUE NOT NULL,
  transcript JSONB NOT NULL,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP NOT NULL,
  message_count INTEGER NOT NULL DEFAULT 0,
  duration_seconds INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback table
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id VARCHAR(255) NOT NULL REFERENCES conversations(conversation_id),
  overall_rating VARCHAR(10),  -- 'up', 'down', or NULL
  feedback_text TEXT,
  per_response_ratings JSONB,  -- Array of {messageId, rating}
  submitted_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index for querying feedback by rating
CREATE INDEX idx_feedback_rating ON feedback(overall_rating);
CREATE INDEX idx_conversations_date ON conversations(created_at);
```

**Option B: Supabase (simpler setup)**
- Same schema, created via Supabase dashboard or migrations
- Use Supabase JS client for queries
- Free tier supports this volume easily

**Option C: JSON file storage (simplest MVP)**
- If no database is available, write to a JSON file on disk
- Only suitable for local development / demo
- Not recommended for production

---

## Email Integration

**Option A: SendGrid**
```typescript
import sgMail from "@sendgrid/mail";
sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

async function sendFeedbackEmail(feedback: FeedbackPayload) {
  await sgMail.send({
    to: process.env.FEEDBACK_EMAIL!,
    from: "maya-noreply@ezpresence.com",
    subject: `Maya Feedback — ${feedback.overallRating === "up" ? "👍" : "👎"} — ${new Date(feedback.submittedAt).toLocaleDateString()}`,
    text: formatFeedbackEmail(feedback),
    html: formatFeedbackEmailHTML(feedback),
  });
}
```

**Option B: Resend (simpler, modern)**
```typescript
import { Resend } from "resend";
const resend = new Resend(process.env.RESEND_API_KEY);
// Similar send() call
```

**Option C: Nodemailer + SMTP (if existing email infra)**
```typescript
import nodemailer from "nodemailer";
// Configure SMTP transport
```

**For MVP**, pick whichever email service the team already uses. If none, Resend has the simplest setup.

---

## CORS Configuration

If frontend and backend are on different origins (e.g., during development), configure CORS:

```typescript
// For Next.js API routes, add to each handler:
export async function POST(req: Request) {
  // ... handler logic
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",  // Restrict in production
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
```

For Express:
```typescript
import cors from "cors";
app.use(cors({ origin: ["https://maya-ezpresence.vercel.app", "http://localhost:5173"] }));
```

---

## Frontend Service Update

Once this backend exists, update `src/services/mayaEngine.ts` (from Task 05) to call `/api/maya` instead of calling OpenAI directly:

```typescript
async getResponse(userMessage: string): Promise<MayaResponse> {
  this.history.push({ role: "user", content: userMessage });

  const res = await fetch("/api/maya", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages: this.history }),
  });

  const data = await res.json();
  this.history.push({ role: "assistant", content: data.response });
  return { response: data.response, emotion: data.emotion };
}
```

And create `src/services/feedback.ts`:
```typescript
import { FeedbackPayload } from "../types";

export async function submitFeedback(payload: FeedbackPayload): Promise<boolean> {
  const res = await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.ok;
}

export async function storeTranscript(data: {
  conversationId: string;
  transcript: TranscriptMessage[];
  startedAt: string;
  endedAt: string;
  messageCount: number;
  duration: number;
}): Promise<boolean> {
  const res = await fetch("/api/transcript", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.ok;
}
```

---

## Testing

1. **GPT Proxy:** Send a POST to `/api/maya` with test messages, verify JSON response with emotion
2. **Feedback:** Send a POST to `/api/feedback` with mock payload, verify DB insert and email sent
3. **Transcript:** Send a POST to `/api/transcript`, verify DB insert
4. **Error cases:** Send malformed requests, verify 400 responses
5. **CORS:** Test from frontend origin, verify no CORS errors

---

## Acceptance Criteria

- [ ] `POST /api/maya` proxies GPT-4 calls and returns `{ response, emotion }`
- [ ] OpenAI API key is server-side only (not in VITE_ env vars)
- [ ] `POST /api/feedback` stores feedback and sends email notification
- [ ] `POST /api/transcript` stores conversation transcript
- [ ] Email notification formatted clearly with ratings and transcript summary
- [ ] Database schema created (or JSON fallback for demo)
- [ ] CORS configured for widget embedding
- [ ] Error handling for all endpoints (validation, API failures)
- [ ] Frontend services updated to use backend endpoints
- [ ] All endpoints return proper HTTP status codes

---

## Output Files
- `src/app/api/maya/route.ts` (or `server/routes/maya.ts`)
- `src/app/api/feedback/route.ts` (or `server/routes/feedback.ts`)
- `src/app/api/transcript/route.ts` (or `server/routes/transcript.ts`)
- `src/services/feedback.ts` (frontend service)
- Database migration file or schema SQL
- Email template formatting function
