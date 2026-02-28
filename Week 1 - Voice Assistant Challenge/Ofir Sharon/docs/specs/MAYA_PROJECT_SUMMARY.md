# Maya the EZpresence Hostess - Project Summary

**Status**: Ready to Build  
**Scope**: 5-8 Hours  
**Last Updated**: Feb 28, 2026

---

## What You're Building

A **speech-to-speech conversational AI assistant** that helps EZpresence users learn about platform features through natural voice conversations. The assistant, Maya, has a friendly 2D avatar that expresses emotions matching her responses.

### Key Features
✅ Voice conversation with real-time transcription  
✅ 2D illustrated avatar with 5+ emotional expressions  
✅ Automatic emotion classification (happy, sad, confused, understanding, etc.)  
✅ Per-response and end-of-conversation feedback (thumbs up/down)  
✅ Deployable as web widget (embeddable on EZpresence platform)  
✅ Single-session architecture (transcripts stored server-side for analysis)  

---

## Project Scope & Timeline

### What You'll Know How To Do:
- Build real-time voice interfaces with LiveKit
- Integrate OpenAI (Whisper for STT, GPT-4 for conversation)
- Use ElevenLabs for natural-sounding text-to-speech
- Create animated React components with emotion-driven expressions
- Build conversational AI with emotion classification
- Deploy to production (Vercel)

### Time Allocation (5-8 hours)
- **0.5-1.5 hrs**: Avatar creation (Midjourney/Figma)
- **1.5-2 hrs**: Setup, React component structure, LiveKit setup
- **2-3 hrs**: OpenAI integration (Whisper + GPT-4 + emotion classification)
- **1-1.5 hrs**: ElevenLabs TTS integration + avatar emotion switching
- **1-1.5 hrs**: Feedback system (per-response + end survey)
- **1 hr**: Testing, bug fixes, deployment

---

## Feature Details

### 1. Maya's Knowledge Areas
She's an expert in:
1. **Content Scheduling** - How to schedule posts, timing strategies, multi-platform scheduling
2. **Studio (Content Generation)** - Video Creators, content types, best practices
3. **Account Setup** - Onboarding, connecting social profiles, workspace config

### 2. Avatar System
- **5 emotional expressions**: Listening, Thinking, Happy, Sad, Confused, Understanding
- **Automatic emotion classification**: GPT-4 analyzes each response and returns emotion
- **Smooth transitions**: Fade animations between expressions
- **Professional style**: 2D illustrated, matches EZpresence brand colors

### 3. Feedback System
- **Per-response thumbs**: Simple up/down after each response (non-intrusive)
- **End-of-conversation survey**: "Was this helpful?" with thumbs
- **Conditional feedback**: "What could be improved?" appears only when thumbs down clicked
- **Data sent to backend**: Stored in database + email summary to contact@ezpresence.com

### 4. Single Session Design
- User starts conversation → asks questions → gets answers
- When done, full transcript automatically sent to backend
- User can start fresh conversation or leave
- **No conversation history shown to user** (clean slate each time)
- Transcripts stored server-side for insights/analytics

---

## Technology Stack

### Frontend
- **React** (TypeScript recommended)
- **LiveKit SDK** (real-time voice transport)
- **styled-components** (styling)
- **OpenAI API** (Whisper for transcription)

### Backend  
- **Next.js** (simple API endpoints)
- **PostgreSQL** (store transcripts + feedback)
- **Email service** (send feedback summaries)

### External Services
| Service | Purpose | Cost per Conversation |
|---------|---------|-----|
| **LiveKit** | Voice transport (WebRTC) | ~$0.001 |
| **OpenAI Whisper** | Speech-to-text (2 min) | ~$0.002 |
| **OpenAI GPT-4** | Conversational AI (avg 3K tokens) | ~$0.004 |
| **OpenAI TTS** | Text-to-speech (2K chars) | **~$0.03** |
| **Vercel** | Hosting | Free tier |
| **PostgreSQL** | Database | Free/paid tiers |
| | **TOTAL** | **~$0.04 per conversation** |

---

## User Experience Flow

### 1. User Initiates
```
Widget appears: "Hi! I'm Maya, your EZpresence Hostess. Click to chat!"
User clicks → call interface loads
```

### 2. Conversation
```
Avatar: [Listening expression]
User (voice): "How do I schedule posts?"
  ↓
[Avatar transitions to Thinking]
Maya processes response via GPT-4
  ↓
[Avatar shows Happy/Understanding expression]
Maya (voice): "Great question! Content scheduling lets you..."
User sees: Transcription of both voices + Avatar expression
User rates: [👍] [👎] (per-response feedback)
```

### 3. Multiple Exchanges
User can continue asking questions. Avatar and feedback work for each response.

### 4. End Conversation
```
User clicks: "End Call"
  ↓
Full transcript sent to backend database
  ↓
Survey appears: "Was this conversation helpful overall?"
User rates: [👍] [👎]
If thumbs down → "What could be improved?" text field appears
  ↓
User submits feedback
  ↓
Backend emails summary to contact@ezpresence.com
  ↓
Widget shows: "Chat ended. [Start New Conversation] [Close Widget]"
```

---

## What Makes This Project Great

✨ **You'll Actually Use It**
- Solves a real problem for EZpresence users
- Can be deployed into production
- Provides data insights (what users ask about)

✨ **Technically Impressive**
- Real-time voice + conversational AI
- Emotion classification + avatar animation
- Full production-ready architecture
- Cost-effective to operate (~$0.04 per conversation)

✨ **Manageable Scope**
- 5-8 hours is achievable
- Clear milestones and deliverables
- Builds real skills (voice AI, conversational agents, real-time systems)

✨ **Extensible**
- Easy to add more features to Maya's knowledge base
- Can upgrade to ElevenLabs voice later if needed (simple swap)
- Can add more emotion expressions
- Can integrate with EZpresence docs/API

---

## Next Steps Before Building

### 1. Get API Keys
- [ ] **OpenAI**: Get GPT-4 API access (https://platform.openai.com)
- [ ] **ElevenLabs**: Create account, get API key (https://elevenlabs.io)
- [ ] **LiveKit**: Create free account, get API credentials (https://livekit.io)

### 2. Choose Avatar Style
- [ ] Decide: Create in Midjourney, DALL-E, or Figma?
- [ ] Design 5 expressions (or commission from Fiverr)
- [ ] Export as SVG or PNG

### 3. Plan Backend
- [ ] Choose database (PostgreSQL recommended, or Supabase for simplicity)
- [ ] Plan email service (Sendgrid, Mailgun, Resend, or simple SMTP)
- [ ] Consider Vercel for hosting both frontend + backend

### 4. Prepare EZpresence Info
- [ ] Exact wording for feature descriptions (for Maya's knowledge)
- [ ] Brand colors/logo for widget styling
- [ ] Embedding location on platform (widget or page integration?)

---

## Documentation You Have

1. **MAYA_PROJECT_SPEC.md** - Complete technical specification with implementation roadmap
2. **MAYA_AVATAR_GUIDE.md** - Detailed guide for avatar creation + emotion system
3. **MAYA_ARCHITECTURE_CLARIFICATIONS.md** - Deep dives on design decisions (UX, services, data flow)
4. **This document** - Executive summary

---

## Quick Reference: System Prompt Structure

Your GPT system prompt will:
1. Define Maya's personality (warm, welcoming hostess)
2. List her expertise areas (Scheduling, Studio, Account Setup)
3. Provide response format template (JSON with response + emotion)
4. Include emotion classification rules
5. Define redirect behaviors (out-of-scope, frustrated users)

**Important**: The system prompt handles emotion classification, so you don't need extra API calls. Same response includes both text + emotion.

---

## Success Criteria (MVP)

✅ User can click button and start voice conversation  
✅ Maya responds naturally about Scheduling, Studio, Account Setup  
✅ Avatar displays appropriate emotions during conversation  
✅ Real-time transcription visible for both user and Maya  
✅ Per-response feedback (thumbs up/down) works  
✅ End-of-conversation survey with optional text feedback  
✅ Feedback submitted to backend (email to contact@ezpresence.com)  
✅ Widget is embeddable via iframe  
✅ Mobile-friendly interface  
✅ Deployed to Vercel and accessible  

---

## Known Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Avatar expressions don't match response | Refine emotion mapping in system prompt; test with various phrasings |
| Voice quality not warm enough | ElevenLabs TTS solves this; way better than OpenAI TTS |
| Emotion classification fails | Use JSON response format with explicit rules; test edge cases |
| Real-time latency issues | LiveKit handles optimization; ensure proper error handling |
| Mobile mic permissions | Clear UI requesting permission; fallback to text if needed |
| Emotion → Avatar switching lag | Use React state management + CSS transitions for smoothness |

---

## Future Enhancements (Post-MVP)

- Persistent conversation history (user accounts)
- Dashboard showing common questions asked
- Multi-language support
- Integration with EZpresence docs/knowledge base
- Video option (optional camera)
- More emotion expressions
- Custom avatars per EZpresence brand
- A/B testing different response styles
- Sentiment analysis on feedback
- Idle animations (breathing, blinking)

---

## Resources You'll Need

**API Docs:**
- OpenAI: https://platform.openai.com/docs
- ElevenLabs: https://elevenlabs.io/docs
- LiveKit: https://docs.livekit.io

**Tools:**
- Figma: https://figma.com
- Midjourney: https://midjourney.com
- SVG Optimizer: https://svgo.dev

**Learning:**
- LiveKit + React: https://docs.livekit.io/realtime/client-sdk/javascript/
- Real-time transcription: OpenAI Whisper docs
- SVG animation: CSS Tricks, MDN Web Docs

---

## Final Thoughts

You're building something **real and useful**. This isn't just a homework project—it's a tool that can genuinely help EZpresence users understand your platform through natural conversation.

The combination of voice, emotion, and conversational AI creates an experience that feels personal and helpful, not robotic.

**You've got this!** 🚀

---

**Ready to start building?** Begin with Hour 0: Avatar creation. Pick your tool (Midjourney, Figma, or Fiverr), design 5 expressions, and you'll be ready to start coding by the time you're done.

Feel free to reach out as you build. I'm here to help with architecture questions, debugging, or pivoting if needed.

Good luck, Maya! 🎨✨
