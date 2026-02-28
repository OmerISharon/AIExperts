# Maya Avatar + Emotion System Implementation Guide

## Overview

This guide covers how to build Maya's 2D illustrated avatar with automatic emotion classification and expression switching.

The system works in 3 steps:
1. **Create avatar expressions** (5 illustrated faces)
2. **Modify GPT prompt** to classify emotion for each response
3. **Map emotion → expression** in React component

---

## Part 1: Creating the Avatar Expressions

### Option A: Quick & Easy (Recommended for 5-8 hour scope)

Use an **AI avatar generator** or illustration tool:

**Tools to consider:**
- **Midjourney / DALL-E**: Generate 5 avatar variations in different emotions
  - Prompt: "Professional 2D illustrated female hostess face, warm and friendly, emoji-style or cartoon style, in these emotions: [emotion]. Flat design, matching purple and teal color palette."
  - Takes: 30 minutes
  - Cost: ~$10-30 for images
  
- **Adobe Express / Figma**: Create simple illustrated face using shapes + Figma assets
  - Takes: 1-2 hours
  - Cost: Free (Figma) or $10/month
  
- **Fiverr / Upwork**: Commission a designer to create 5 expressions
  - Takes: 1-3 days
  - Cost: $50-150

**My Recommendation**: Use Midjourney or DALL-E to generate 5 variations quickly, then:
1. Download images
2. Use an online tool (removebg.com) to remove background
3. Convert to SVG or use as PNG

### Option B: DIY Simple Illustration (If you want full control)

Create in Figma (free tier):
1. Draw simple face: circle for head, simple shapes for eyes
2. Duplicate 5 times for each emotion
3. Modify expression:
   - **Listening**: Eyes looking engaged, slight attention posture
   - **Thinking**: Hand to chin, eyes up (contemplative)
   - **Happy/Helpful**: Big warm smile, eyes crinkled
   - **Sad/Apologetic**: Gentle eyes, slight frown, empathetic
   - **Confused**: Eyebrow raised, tilted head, question mark vibe
   - **Understanding**: Knowing nod, affirming expression

### File Format

**Best format: SVG**
- Scalable (works at any size)
- Small file size
- Easy to animate CSS/React
- Example structure:
```jsx
// maya-listening.svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Head -->
  <circle cx="100" cy="100" r="80" fill="#f5d5b8"/>
  
  <!-- Eyes -->
  <circle cx="80" cy="85" r="8" fill="#333"/>
  <circle cx="120" cy="85" r="8" fill="#333"/>
  
  <!-- Mouth -->
  <path d="M 80 130 Q 100 140 120 130" stroke="#333" fill="none" stroke-width="2"/>
  
  <!-- Expression details -->
  <!-- Listening = attentive eyes -->
</svg>
```

**Fallback: PNG with transparency**
- Export each expression as PNG
- Use in React directly
- Less elegant but works fine

---

## Part 2: Emotion Classification via GPT

### Modify System Prompt

Your current system prompt tells GPT to generate responses. Now, modify it to **also classify emotion**.

**Updated System Prompt:**
```
You are Maya, the EZpresence Hostess. Your role is to welcome users and help them understand EZpresence features and social media management in a warm, conversational way.

**Your Personality:**
- Warm and welcoming, like a restaurant hostess greeting guests
- Patient and encouraging
- Professional but approachable
- You ask clarifying questions

**Your Expertise Areas:**
1. Content Scheduling
2. Studio (Content Generation)
3. Account Setup

**IMPORTANT: Response Format**
You MUST respond in the following JSON format ONLY:
{
  "response": "Your conversational response here...",
  "emotion": "one_of: listening, thinking, happy, sad, confused, understanding"
}

**Emotion Mapping Rules:**
- "listening": When acknowledging their question, showing attentiveness
- "thinking": When processing complex info or considering an answer
- "happy": When giving helpful tips, explaining features, positive feedback
- "sad": When apologizing, expressing empathy, addressing limitations
- "confused": When user says something unclear and you're asking for clarification
- "understanding": When confirming you understand them, affirming their needs, "I get it"

**Guidelines:**
- Keep explanations concise but thorough (1-3 minutes per answer)
- Use examples specific to social media management
- If asked outside expertise, redirect to contact@ezpresence.com
- If user insists on human or is unhappy, also redirect to contact@ezpresence.com
- Encourage hands-on exploration
- End conversations warmly

**Example Interaction:**

User: "How do I schedule posts?"

Your response should be:
{
  "response": "Great question! Content scheduling lets you plan posts in advance across all your platforms...",
  "emotion": "happy"
}

User: "Can I schedule to YouTube?"

Your response:
{
  "response": "Good question! Studio integrates with Instagram, TikTok, Facebook, and YouTube. You can schedule...",
  "emotion": "understanding"
}
```

### Implementation in Code

When you call GPT, parse the JSON response:

```javascript
async function getMayaResponse(userMessage: string): Promise<{
  response: string;
  emotion: Emotion;
}> {
  const response = await openai.chat.completions.create({
    model: "gpt-4-turbo",
    messages: [
      {
        role: "system",
        content: MAYA_SYSTEM_PROMPT, // Use the prompt above
      },
      {
        role: "user",
        content: userMessage,
      },
    ],
    temperature: 0.7,
    max_tokens: 300,
  });

  const content = response.choices[0].message.content;
  
  // Parse JSON response
  const parsed = JSON.parse(content);
  
  return {
    response: parsed.response,
    emotion: parsed.emotion as Emotion,
  };
}

type Emotion = 
  | "listening"
  | "thinking"
  | "happy"
  | "sad"
  | "confused"
  | "understanding";
```

### Testing the Emotion Classification

Test prompts:
- "How do I schedule content?" → Expect: **happy**
- "I'm confused about Studio" → Expect: **listening**
- "This is too complicated" → Expect: **sad**
- "What do you mean by Video Creators?" → Expect: **confused**
- "I understand, but can you clarify X?" → Expect: **understanding**

---

## Part 3: Avatar Component Implementation

### React Component Structure

```typescript
// Avatar.tsx
import React, { useState, useEffect } from "react";

type Emotion = 
  | "listening"
  | "thinking"
  | "happy"
  | "sad"
  | "confused"
  | "understanding";

interface AvatarProps {
  emotion: Emotion;
  isLoading?: boolean;
}

export const Avatar: React.FC<AvatarProps> = ({ emotion, isLoading }) => {
  const [currentEmotion, setCurrentEmotion] = useState<Emotion>(emotion);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    if (currentEmotion !== emotion) {
      setIsTransitioning(true);
      // Fade out duration
      const timer = setTimeout(() => {
        setCurrentEmotion(emotion);
        setIsTransitioning(false);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [emotion, currentEmotion]);

  const emotionImages = {
    listening: "/avatars/maya-listening.svg",
    thinking: "/avatars/maya-thinking.svg",
    happy: "/avatars/maya-happy.svg",
    sad: "/avatars/maya-sad.svg",
    confused: "/avatars/maya-confused.svg",
    understanding: "/avatars/maya-understanding.svg",
  };

  return (
    <div className="flex justify-center items-center">
      <img
        src={emotionImages[currentEmotion]}
        alt={`Maya is ${currentEmotion}`}
        className={`w-32 h-32 object-contain transition-opacity duration-300 ${
          isTransitioning ? "opacity-0" : "opacity-100"
        }`}
      />
      {isLoading && (
        <div className="absolute animate-pulse">
          <div className="w-32 h-32 rounded-full border-4 border-purple-300 border-t-purple-600 animate-spin"></div>
        </div>
      )}
    </div>
  );
};
```

### Using the Avatar in Call Interface

```typescript
// CallInterface.tsx
export const CallInterface: React.FC = () => {
  const [mayaEmotion, setMayaEmotion] = useState<Emotion>("listening");
  const [isLoading, setIsLoading] = useState(false);

  const handleUserMessage = async (message: string) => {
    setIsLoading(true);
    setMayaEmotion("thinking"); // Show thinking while processing
    
    const { response, emotion } = await getMayaResponse(message);
    
    setIsLoading(false);
    setMayaEmotion(emotion); // Update to actual response emotion
    
    // Send response text to TTS
    await playMayaVoice(response);
    
    // Add to transcript
    addToTranscript("Maya", response);
  };

  return (
    <div className="flex flex-col items-center gap-6">
      <Avatar emotion={mayaEmotion} isLoading={isLoading} />
      
      <div className="text-center">
        {isLoading ? "Maya is thinking..." : "Ready to listen"}
      </div>
      
      {/* Rest of UI */}
    </div>
  );
};
```

---

## Part 4: Styling & Animation

### Smooth Expression Transitions

Use CSS animations for smooth fading between expressions:

```css
/* styles/avatar.css */
.avatar-image {
  width: 128px;
  height: 128px;
  object-fit: contain;
  transition: opacity 0.3s ease-in-out;
}

.avatar-image.fade-out {
  opacity: 0;
}

.avatar-image.fade-in {
  opacity: 1;
}

/* Optional: Add subtle scale animation */
@keyframes expressionChange {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0;
    transform: scale(0.95);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.avatar-image.transitioning {
  animation: expressionChange 0.6s ease-in-out;
}
```

### Layout Integration

```jsx
<div className="flex flex-col items-center gap-8 p-6">
  {/* Avatar takes up top 1/3 */}
  <div className="w-full flex justify-center">
    <Avatar emotion={mayaEmotion} isLoading={isLoading} />
  </div>

  {/* Waveform or status indicator */}
  <div className="text-sm text-gray-600">
    {isLoading ? "Maya is thinking..." : "Listening..."}
  </div>

  {/* Controls */}
  <div className="flex gap-4">
    <button>End Call</button>
    <button>New Chat</button>
  </div>

  {/* Transcript below */}
  <div className="w-full max-h-96 overflow-y-auto">
    <Transcript messages={messages} />
  </div>
</div>
```

---

## Part 5: Putting It All Together

### Complete Flow Example

**User asks a question:**
```
User: "How do I use Studio to create content?"
```

**Backend processes:**
```javascript
1. Whisper transcribes: "How do I use Studio to create content?"
2. Send to GPT with system prompt
3. GPT returns:
   {
     "response": "Studio is our content generation tool. You can use different Video Creators...",
     "emotion": "happy"
   }
4. Frontend receives response
5. Update emotion: listening → thinking → happy
6. Call ElevenLabs TTS with response text
7. Play Maya's voice while showing happy expression
8. Add to transcript
```

**Visual sequence:**
- User speaks → Avatar shows "listening"
- Wait for response → Avatar shows "thinking"
- Response comes → Avatar transitions to "happy"
- Maya speaks → Avatar stays "happy" during speech
- Next interaction → Avatar returns to "listening"

---

## Troubleshooting

### Emotion Classification Not Working

**Problem**: GPT not returning valid JSON

**Solution**: 
- Ensure system prompt explicitly requires JSON format
- Use `response_format` parameter (if available in your OpenAI version):
```javascript
const response = await openai.chat.completions.create({
  model: "gpt-4-turbo",
  response_format: { type: "json_object" },
  // ...
});
```

### Avatar Expression Not Changing

**Problem**: Same emotion showing repeatedly

**Solution**:
- Check emotion classification is actually different
- Log the emotion value: `console.log("Current emotion:", emotion)`
- Verify SVG files exist at correct paths
- Check browser console for 404 errors on image files

### Emotion Doesn't Match Response

**Problem**: Wrong expression for the content

**Solution**:
- Refine emotion mapping rules in system prompt
- Add more specific examples
- Test with different phrasings
- Consider adjusting emotion thresholds

---

## Design Tips

### Keep Expressions Simple
- Don't try too many subtle differences
- 5-6 expressions is ideal
- Big, clear changes are better than subtle ones

### Consistency
- Use same art style across all expressions
- Maintain same size and proportions
- Consistent color palette (match EZpresence brand)

### Accessibility
- Don't rely ONLY on emotion to convey meaning
- Use text ("Maya is thinking...") alongside expression
- Ensure good contrast for readability

### Performance
- Use SVG for small file size
- Cache emotion images
- Limit animation frequency to avoid jank

---

## Optional Enhancements (Post-MVP)

- Add subtle **idle animations** (breathing, blinking)
- **Eye movement** to follow user's voice
- **Mouth movement** synced to TTS (lip-sync)
- **Custom expressions** per user preference
- **Emotion confidence levels** (show uncertainty)

---

## Estimated Time Breakdown

| Task | Time |
|------|------|
| Avatar creation (Midjourney/Figma) | 30 min - 1 hour |
| System prompt modification | 15 min |
| Avatar React component | 30 min |
| Emotion classification logic | 15 min |
| Integration & testing | 30 min |
| **Total** | **~2-2.5 hours** |

This leaves you **5.5-6 hours** for the rest of the build (UI, LiveKit, TTS, feedback system, deployment).

---

## Resources

- **Emotion Wheel**: https://en.wikipedia.org/wiki/Emotion_wheel (for refining emotion categories)
- **Avatar Design Tools**:
  - Figma: https://figma.com
  - Midjourney: https://midjourney.com
  - DALL-E: https://openai.com/dall-e-3
- **SVG Optimization**: https://svgo.dev/
- **React Animation**: https://www.react-spring.dev/

---

Good luck building Maya! 🎨✨
