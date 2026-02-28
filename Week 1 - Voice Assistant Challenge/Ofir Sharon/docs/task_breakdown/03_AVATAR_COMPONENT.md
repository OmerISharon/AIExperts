# Task 03: Avatar React Component with Emotion Transitions

## Objective
Build a React component (`Avatar.tsx`) that displays Maya's SVG avatar and smoothly transitions between emotional expressions. This component receives an `emotion` prop and handles fade animations, loading states, and accessibility.

---

## Context
Maya's avatar is displayed prominently at the top of the call interface during voice conversations. The expression changes each time GPT-4 returns a response with an emotion classification. The transitions must feel smooth and natural — not jarring.

**Visual sequence during a conversation:**
1. User speaks → Avatar shows **"listening"**
2. Waiting for GPT response → Avatar shows **"thinking"** (with optional loading spinner)
3. GPT responds → Avatar transitions to the classified emotion (e.g., **"happy"**)
4. Maya speaks via TTS → Avatar stays on that emotion
5. Maya finishes → Avatar returns to **"listening"**

---

## Dependencies
- **Task 01** (project setup, types, constants)
- **Task 02** (SVG avatar files in `public/avatars/`)

## Types (from `src/types/index.ts`)
```typescript
export type Emotion = "listening" | "thinking" | "happy" | "sad" | "confused" | "understanding";
```

## Constants (from `src/config/constants.ts`)
```typescript
export const AVATAR_PATHS: Record<string, string> = {
  listening: "/avatars/maya-listening.svg",
  thinking: "/avatars/maya-thinking.svg",
  happy: "/avatars/maya-happy.svg",
  sad: "/avatars/maya-sad.svg",
  confused: "/avatars/maya-confused.svg",
  understanding: "/avatars/maya-understanding.svg",
};
```

---

## Component Specification

### Props Interface

```typescript
interface AvatarProps {
  emotion: Emotion;         // Current emotion to display
  isLoading?: boolean;      // Show loading indicator (thinking spinner)
  size?: "sm" | "md" | "lg"; // Avatar size: sm=80px, md=128px, lg=200px
  className?: string;       // Additional CSS classes
}
```

### Behavior

1. **Emotion Switching:**
   - When `emotion` prop changes, fade out current expression (300ms), swap image, fade in new expression (300ms)
   - Total transition duration: ~600ms
   - If emotion changes again mid-transition, cancel current transition and start new one

2. **Loading State:**
   - When `isLoading` is true, show a pulsing ring/spinner around the avatar
   - Avatar still shows the current emotion underneath the spinner
   - Spinner uses brand purple color (`#7C3AED`)

3. **Image Preloading:**
   - On component mount, preload ALL 6 SVG images so transitions are instant
   - No visible loading flicker when switching emotions

4. **Accessibility:**
   - `alt` text describes current emotion: `"Maya is listening"`, `"Maya is thinking"`, etc.
   - `role="img"` on container
   - Reduced motion: if user has `prefers-reduced-motion`, skip fade animation (instant swap)

### Size Variants
| Size | Dimensions | Use Case |
|------|-----------|----------|
| `sm` | 80×80px | Compact widget mode |
| `md` | 128×128px | Default call interface |
| `lg` | 200×200px | Full-screen or hero view |

---

## Implementation

### File: `src/components/Avatar.tsx`

```typescript
import React, { useState, useEffect, useRef, useCallback } from "react";
import { Emotion } from "../types";
import { AVATAR_PATHS } from "../config/constants";
import clsx from "clsx";

interface AvatarProps {
  emotion: Emotion;
  isLoading?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZE_MAP = {
  sm: "80px",
  md: "128px",
  lg: "200px",
};

export const Avatar: React.FC<AvatarProps> = ({
  emotion,
  isLoading = false,
  size = "md",
  className,
}) => {
  // Implementation here — see detailed requirements below
};
```

### Core Logic Requirements

1. **State management:**
   - `displayedEmotion` (Emotion) — the currently rendered SVG
   - `isTransitioning` (boolean) — whether a fade transition is in progress

2. **Transition logic (useEffect on emotion change):**
   ```
   When emotion prop changes AND differs from displayedEmotion:
     1. Set isTransitioning = true (triggers fade-out CSS)
     2. After 300ms timeout:
        a. Set displayedEmotion = new emotion
        b. Set isTransitioning = false (triggers fade-in CSS)
   ```

3. **Image preloading (useEffect on mount):**
   ```
   On mount, create new Image() for each AVATAR_PATHS value and set .src
   This forces browser to cache all SVGs
   ```

4. **Cleanup:** Clear any pending timeouts on unmount to avoid memory leaks.

### CSS Classes / Animation

Use `styled-components` to style the Avatar and spinner. Create styled components `AvatarContainer`, `AvatarImage`, `LoadingSpinner` inside `Avatar.tsx` mapped to the logic described above.

- `AvatarContainer`: relative positioning, flex center.
- `AvatarImage`: object-fit contain, transitions opacity and scale.
- `LoadingSpinner`: absolute overlay, spin animation, brand purple border.

Also consider adding a subtle scale animation on transition:
- Fade out: opacity 1→0, scale 1→0.95
- Fade in: opacity 0→1, scale 0.95→1

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  .avatar-image {
    transition: none !important;
  }
}
```

Or handle in JS:
```typescript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const transitionDuration = prefersReducedMotion ? 0 : 300;
```

---

## Status Label (Optional Sub-Component)

Below the avatar, display a subtle text label showing the current state:

```
"Listening..." | "Thinking..." | "Maya is helping" | etc.
```

This can be a simple `<p>` rendered below the avatar image, styled in `text-sm text-slate-500`. Pass as optional prop or derive from emotion:

```typescript
const EMOTION_LABELS: Record<Emotion, string> = {
  listening: "Listening...",
  thinking: "Thinking...",
  happy: "Here to help!",
  sad: "I understand...",
  confused: "Let me clarify...",
  understanding: "Got it!",
};
```

---

## Testing Checklist

- [ ] Renders correctly with each of the 6 emotions
- [ ] Transitions smoothly when emotion changes (fade out → swap → fade in)
- [ ] No flicker or blank frame during transition
- [ ] Loading spinner appears when `isLoading={true}`
- [ ] All 3 size variants render at correct dimensions
- [ ] Alt text updates with emotion
- [ ] Images preloaded on mount (check Network tab — all 6 SVGs loaded)
- [ ] Reduced motion preference respected
- [ ] No memory leaks (timeout cleanup on unmount)
- [ ] Component accepts and applies additional `className`

---

## Acceptance Criteria

- [ ] `Avatar.tsx` is a clean, self-contained React component
- [ ] Smooth 600ms total transition between emotions
- [ ] Loading spinner overlay works
- [ ] All 6 SVG paths resolve correctly
- [ ] Images are preloaded on mount
- [ ] TypeScript compiles cleanly with no `any` types
- [ ] Accessibility: proper alt text and role
- [ ] Exported from `src/components/Avatar.tsx`

---

## Output Files
- `src/components/Avatar.tsx`
