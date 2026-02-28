# Maya the EZpresence Hostess - Project Specification

## Project Overview
A conversational AI agent (speech-to-speech) that helps EZpresence users understand platform features and social media strategy through natural voice conversations. Deployable as a web widget.

**Target User**: EZpresence customers who prefer voice interaction for learning
**Deployment**: Embeddable web widget (iframe-compatible)
**Timeline**: 5-8 hours
**Status**: MVP (v1.0)

---

## Core Features

### 1. Speech-to-Speech Conversation Interface
- **2D illustrated avatar** of Maya with emotional expressions (listening, thinking, happy, sad, neutral, confused, understanding)
- **Dynamic emotion display** - avatar expression changes based on response type (automatically mapped via GPT)
- **Animated expression transitions** - smooth fade between emotions
- **Real-time transcription** (user input + Maya's responses displayed as text)
- **Call controls**: Start/End Call, New Chat buttons, mic status indicator
- **Clean, professional styling** matching EZpresence brand (purple, teal, minimal aesthetic)
- **Single session architecture** - when user ends call, full transcript is sent to backend DB for analysis
- **Fresh start option** - user can start new conversation without leaving widget

### 2. Avatar Emotion System
- **5 emotional expressions**: Listening, Thinking, Happy/Helpful, Sad/Apologetic, Confused, Understanding
- **Automatic emotion classification** - GPT-4 analyzes each response and assigns an emotion
- **Expression transitions** - smooth fade animations between emotions
- **Visual feedback** - avatar shows emotional state while speaking
- **Non-intrusive** - avatar complements conversation, doesn't distract
- **Scalable design** - easy to add more expressions or adjust mapping later

### 3. Dual Transcript Display
- **User side**: Voice input + auto-transcribed text
- **Maya side**: Spoken response + text transcript
- **Real-time updates** as conversation happens
- **Scrollable history** of the full conversation
- **Copy functionality** for text snippets

### 4. Feedback System
- **Per-response rating**: Thumbs up/down appears after each Maya response (simple, non-intrusive)
- **End-of-conversation survey**: "Was this conversation helpful overall?" with prominent thumbs up/down
- **Conditional text feedback**: "What could be improved?" text field ONLY appears when user clicks thumbs down (in end survey)
- **Feedback submission**: All feedback sent to backend, which emails insights to contact@ezpresence.com
- **UX flow**: Simple, unobtrusive per-response ratings + more detailed end survey

### 5. Feature Knowledge Base (MVP)
Maya specializes in these 3 core features initially:

1. **Content Scheduling** - How to schedule posts across social platforms, timing strategies, best posting times
2. **Studio (Content Generation)** - General knowledge of the Studio feature, specific guidance on Video Creators, recommendations for different content types, best practices for each creator tool
3. **Account Setup** - Getting started, connecting social profiles, workspace configuration, initial platform orientation

*Design Note: System prompt structure allows easy addition of more features later*

---

## Technical Architecture

### Frontend Stack
- **React** (TypeScript optional but recommended)
- **LiveKit SDK** (for real-time voice/transcription)
- **Tailwind CSS** (styling)
- **TypeScript** (for type safety)

### Backend Requirements (Minimal)
- **Single endpoint** for feedback submission (POST /api/feedback)
- **Email integration** (send feedback to contact@ezpresence.com)
- **CORS-enabled** for widget embedding

### External Services
- **LiveKit**: Real-time communication infrastructure (rooms, connections, audio transport)
- **OpenAI API**: 
  - Whisper (Speech-to-Text)
  - GPT-4 (Conversational AI + Emotion Classification)
  - TTS (Text-to-Speech, Maya's voice)
- **Backend Database**: Store conversation transcripts for insights/analytics (PostgreSQL or similar)

### Deployment
- **Frontend**: Vercel (free tier fine for MVP)
- **Backend**: Simple Node.js/Next.js (can be same Vercel deployment)
- **Widget**: Embeddable via iframe with postMessage communication

---

## Maya's Personality & System Prompt

### Character Definition
- **Name**: Maya
- **Role**: EZpresence Hostess
- **Tone**: Warm, welcoming, professional, patient
- **Expertise**: EZpresence features, social media best practices
- **Communication Style**: Conversational, asks clarifying questions, adapts to user level

### System Prompt Template
```
You are Maya, the EZpresence Hostess. Your role is to welcome users and help them understand EZpresence features and social media management in a warm, conversational way.

**Your Personality:**
- Warm and welcoming, like a restaurant hostess greeting guests
- Patient and encouraging - users may be new to social media management
- Professional but approachable
- You ask clarifying questions to understand what users need

**Your Expertise Areas:**
1. Content Scheduling - helping users plan and schedule posts across platforms
2. Studio (Content Generation) - explaining the Studio feature, Video Creators, recommendations for different content types
3. Account Setup - onboarding and connecting social profiles, workspace configuration

**Guidelines:**
- Keep explanations concise but thorough (1-3 minutes per answer)
- Use examples specific to social media management when helpful
- If asked about something outside your expertise, politely redirect to EZpresence support at contact@ezpresence.com
- If user insists on talking to a human or expresses that your assistance isn't helpful, also politely direct them to contact@ezpresence.com
- Encourage users to explore features hands-on after learning about them
- End conversations warmly and let them know feedback is welcome

**Tone Examples:**
- Instead of: "Content scheduling is a feature..."
- Say: "Oh great question! Content scheduling is one of my favorite features because it saves you so much time..."
```

---

## User Flow

### 1. Widget Load
- Widget appears on page (floating button or embedded container)
- Text: "Hi! I'm Maya, your EZpresence Hostess. Click to chat!"

### 2. User Initiates Call
- User clicks "Start Conversation" button
- Brief loading state
- Call interface appears with animated waveform, "Listening..." indicator

### 3. Conversation (Single Session)
- User asks question via voice
- Real-time transcription shows what's being heard
- Maya responds conversationally with her voice + text transcript
- **Per-response feedback**: Small thumbs up/down appears below each Maya response
- User can continue asking follow-up questions or end the call
- User clicks "End Call" when done

### 4. End-of-Conversation Survey
- "Was this conversation helpful overall?" with prominent thumbs up/down
- If user clicks thumbs down, conditional text field appears: "What could be improved?"
- "Submit Feedback" button
- Confirmation message: "Thanks for your feedback!"

### 5. Post-Conversation State
- Full conversation transcript sent to backend database for analysis
- User sees options: "Start New Conversation" or "Close Widget"
- If "Start New", clear transcript and return to step 2 (fresh conversation)

### 6. Data Cleanup
- Each conversation is isolated (no history shown to user)
- Transcripts stored server-side for insights only

---

## Data Flow

### Conversation Flow
```
User Voice → OpenAI Whisper STT → User Text Transcript
                                        ↓
                                OpenAI GPT-4
                            (with Maya system prompt)
                                        ↓
                    Maya Response Text + Emotion Classification
                    (e.g., { text: "...", emotion: "understanding" })
                                        ↓
                    Emotion → Avatar Expression Update
                    Text → OpenAI TTS → Maya Voice Output
                                ↓
                         Display in Transcript + Show Avatar Expression
         
[Per-response: Collect thumbs up/down]

[End of conversation: Send FULL transcript to backend DB]
```

### Feedback Flow
```
Per-Response Thumbs: User clicks ↑/↓ after each response
                ↓
        Store in memory
        
End-of-Conversation Survey: "Was this helpful?"
            ↓
    User clicks thumbs ↑ or ↓
            ↓
    If ↓: Show "What could be improved?" text field
            ↓
    User submits (optional text + all per-response data)
            ↓
    POST /api/feedback with full conversation context
            ↓
    Backend sends email summary to contact@ezpresence.com
```

---

## Implementation Roadmap (5-8 Hours)

### Hour 0.5-1.5: Avatar Creation
- [ ] Design/create 5 avatar expressions (Figma, Procreate, or similar)
  - Listening (neutral with attention)
  - Thinking (contemplative)
  - Happy/Helpful (warm smile)
  - Sad/Apologetic (empathetic)
  - Confused (questioning)
  - Understanding (knowing nod)
- [ ] Export as SVG files or PNG with transparency
- [ ] Create component to switch between expressions

### Hour 1.5-2: Setup & Infrastructure
- [ ] Create React project (create-react-app or Vite)
- [ ] Install LiveKit SDK + dependencies
- [ ] Set up Tailwind CSS
- [ ] Create basic project structure
- [ ] Set up environment variables (.env)
- [ ] Create Avatar component with expression switching

### Hour 2-3: Core UI & Call Interface
- [ ] Build main widget container component
- [ ] Create call interface (buttons, status indicator)
- [ ] Integrate Avatar component into call interface
- [ ] Build transcript display component
- [ ] Add styling (professional, clean design)
- [ ] Test responsive design for mobile

### Hour 3-4: LiveKit Integration
- [ ] Connect LiveKit SDK to component
- [ ] Implement voice input (connect to user mic)
- [ ] Implement real-time transcription display
- [ ] Test speech-to-text functionality
- [ ] Handle call start/end states

### Hour 4-5: OpenAI Integration (Whisper + GPT-4 + Emotion Classification)
- [ ] Set up OpenAI API calls
- [ ] Create system prompt for Maya (with emotion classification extension)
- [ ] Implement GPT-4 response generation
- [ ] **Extract emotion from response** (modify system prompt to return JSON with emotion)
- [ ] Test conversational logic with sample questions
- [ ] Map emotion to avatar expression

### Hour 5-6: ElevenLabs TTS & Voice Output
- [ ] Set up ElevenLabs API
- [ ] Implement text-to-speech for Maya's responses
- [ ] Test voice quality and timing
- [ ] Sync avatar expression with voice playback
- [ ] Ensure smooth emotion transitions

### Hour 6-7: Feedback System
- [ ] Build per-response thumbs up/down component
- [ ] Build end-of-conversation survey modal
- [ ] Implement conditional text feedback field (show only on thumbs down)
- [ ] Create backend endpoint for feedback submission
- [ ] Test feedback flow

### Hour 7-8: Testing & Deployment
- [ ] End-to-end testing (full conversations with avatar + emotion)
- [ ] Test widget embedding/iframe mode
- [ ] Fix bugs and edge cases
- [ ] Refine Maya's responses and emotion mapping
- [ ] Mobile testing (avatar expressions, buttons)
- [ ] Deploy to Vercel (frontend + backend)
- [ ] Test in production

---

## Widget Embedding Instructions (For End Users)

```html
<iframe 
  src="https://maya-ezpresence.vercel.app/widget" 
  width="100%" 
  height="600px" 
  style="border: none; border-radius: 8px;">
</iframe>
```

Or as a floating button:
```html
<script src="https://maya-ezpresence.vercel.app/widget-loader.js"></script>
<script>
  MayaWidget.init({ position: 'bottom-right' });
</script>
```

---

## Success Criteria (MVP)

- ✅ User can click button and start a voice conversation
- ✅ Real-time transcription visible for both user and Maya
- ✅ Maya responds conversationally about 3-5 EZpresence features
- ✅ Conversation quality is natural and helpful
- ✅ Feedback system works and sends emails
- ✅ Widget is embeddable on external pages
- ✅ Mobile-friendly interface
- ✅ Deployed and accessible

---

## Future Enhancements (Post-MVP)

- [ ] Persistent conversation history (user accounts)
- [ ] Analytics dashboard (track common questions)
- [ ] Multi-language support
- [ ] Integration with EZpresence knowledge base (docs API)
- [ ] Sentiment analysis on feedback
- [ ] Video option (optional camera input)
- [ ] In-app action suggestions ("Let me show you how...")
- [ ] Custom branding per customer
- [ ] A/B testing different Maya responses

---

## Technical Considerations

### LiveKit Setup
- You'll need a LiveKit server (free tier available at livekit.io)
- Generate API keys for your app
- Store in environment variables

### OpenAI API
- Use GPT-4 or GPT-4 Turbo for conversational AI
- Whisper API for speech-to-text
- TTS API for text-to-speech
- Rate limit considerations for production
- Cost estimate: ~$0.01-0.02 per conversation (Whisper + GPT + TTS combined)

### Security
- Validate feedback before sending
- Rate limit API endpoints
- CORS configuration for widget embedding
- No PII in transcripts (or encrypt at rest)

### Browser Compatibility
- Works on modern browsers (Chrome, Safari, Firefox, Edge)
- Requires HTTPS for microphone access
- Mobile: iOS 14.5+, Android 6+

---

## Questions to Answer Before Building

1. **What are your 3-5 most-explained features?** (for system prompt)
2. **What's your LiveKit workspace URL/API key?**
3. **What's your Claude API key?**
4. **Email service for feedback?** (Sendgrid, Mailgun, etc.)
5. **Brand colors for widget?** (match EZpresence site)

---

## Quick Reference: Key Files to Create

```
maya-ezpresence/
├── src/
│   ├── components/
│   │   ├── MayaWidget.tsx (main component)
│   │   ├── CallInterface.tsx
│   │   ├── TranscriptDisplay.tsx
│   │   ├── FeedbackModal.tsx
│   ├── api/
│   │   ├── feedback.ts (backend endpoint)
│   │   ├── claude.ts (Claude integration)
│   │   ├── livekit.ts (LiveKit helpers)
│   ├── styles/
│   │   ├── globals.css
│   │   ├── widget.css
│   ├── App.tsx
│   └── index.tsx
├── public/
│   └── widget-loader.js (for iframe embedding)
├── .env.example
├── package.json
└── README.md
```

---

**Status**: Ready for development
**Last Updated**: Feb 28, 2026
**Owner**: You + Claude AI
