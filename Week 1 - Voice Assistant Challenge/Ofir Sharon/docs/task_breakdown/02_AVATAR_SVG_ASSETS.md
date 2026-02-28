# Task 02: Avatar SVG Assets Creation

## Objective
Create 6 distinct SVG avatar expression files for Maya — the EZpresence AI hostess. Each SVG represents a different emotional state that will be displayed during conversations. The avatars must be visually consistent, professional, on-brand, and clearly distinguishable from each other.

---

## Context
Maya is a warm, professional, female AI hostess for EZpresence (a social media management platform). Her avatar is displayed prominently during voice conversations and switches expressions based on GPT-4's emotion classification of each response.

**The 6 emotions to create:**
1. **Listening** — Attentive, neutral-warm, engaged eyes, slight smile
2. **Thinking** — Contemplative, eyes slightly upward or to the side, hand-on-chin optional
3. **Happy** — Warm broad smile, eyes crinkled/squinted with joy, welcoming
4. **Sad** — Empathetic, gentle eyes, slight frown, caring concern
5. **Confused** — One eyebrow raised, slight head tilt, questioning expression
6. **Understanding** — Knowing nod expression, affirming smile, confident warmth

---

## Design Specifications

### Style
- **2D illustrated / flat design** — not photorealistic, not cartoon/chibi
- **Professional and warm** — think "friendly customer success manager," not "anime character"
- **Consistent across all 6 expressions** — same face shape, hair, skin tone, proportions
- **Head and shoulders only** (bust portrait) — no full body
- **Transparent background** — no background shape or color

### Brand Colors
Use these throughout the avatar design:
- **Hair/Accent:** `#7C3AED` (brand purple) or a natural dark color with purple highlights
- **Clothing/Accessory accent:** `#14B8A6` (brand teal)
- **Skin:** Warm, medium tone (e.g., `#D4A574` or `#C68642`)
- **Eyes:** Dark, expressive (`#1E293B` slate-800)
- **Lips:** Soft natural (`#E8998D` or similar)

### Dimensions
- **viewBox:** `0 0 200 200`
- **Actual render size:** Flexible (SVG scales), but designed to look good at 128×128px and 200×200px
- **All 6 files must use the same viewBox and proportions** so switching between them is seamless

### File Naming
```
public/avatars/maya-listening.svg
public/avatars/maya-thinking.svg
public/avatars/maya-happy.svg
public/avatars/maya-sad.svg
public/avatars/maya-confused.svg
public/avatars/maya-understanding.svg
```

---

## Expression Details

### 1. `maya-listening.svg`
- **Eyes:** Open, looking straight ahead, attentive
- **Eyebrows:** Neutral, slightly raised (engaged)
- **Mouth:** Gentle closed-lip smile — not big, just warm
- **Head position:** Straight, slight forward lean implied
- **Overall vibe:** "I'm paying attention to you"

### 2. `maya-thinking.svg`
- **Eyes:** Looking slightly upward and to the right
- **Eyebrows:** Slightly furrowed inward (concentration)
- **Mouth:** Closed, neutral or slight pucker
- **Optional:** Index finger touching chin or small thought indicator
- **Overall vibe:** "Let me consider that..."

### 3. `maya-happy.svg`
- **Eyes:** Slightly squinted/crinkled (genuine smile)
- **Eyebrows:** Relaxed, slightly raised
- **Mouth:** Open smile showing warmth (not teeth necessarily, but broad)
- **Overall vibe:** "I love this question! Let me help you!"

### 4. `maya-sad.svg`
- **Eyes:** Soft, slightly downturned outer corners
- **Eyebrows:** Inner edges slightly raised (empathetic concern)
- **Mouth:** Gentle downturn, closed lips
- **Overall vibe:** "I'm sorry about that, let me help"

### 5. `maya-confused.svg`
- **Eyes:** One slightly wider than the other, or both slightly widened
- **Eyebrows:** One raised higher than the other (asymmetric)
- **Mouth:** Slight open or skewed to one side
- **Optional:** Small `?` indicator near head
- **Overall vibe:** "Hmm, could you clarify that?"

### 6. `maya-understanding.svg`
- **Eyes:** Warm, steady gaze, slightly narrowed with knowing expression
- **Eyebrows:** Relaxed, neutral
- **Mouth:** Confident warm smile, slightly asymmetric (knowing)
- **Optional:** Subtle nod posture (head tilted very slightly)
- **Overall vibe:** "I totally get it, here's what you need"

---

## SVG Structure Guide

Each SVG should follow this general layered structure for consistency:

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Hair (back layer) -->
  <!-- Head/Face shape -->
  <!-- Ears (if visible) -->
  <!-- Hair (front layer / bangs) -->
  <!-- Eyebrows -->
  <!-- Eyes -->
  <!-- Nose -->
  <!-- Mouth -->
  <!-- Clothing neckline / shoulders hint -->
  <!-- Optional: accessories, expression indicators -->
</svg>
```

**Important SVG practices:**
- Use `<path>`, `<circle>`, `<ellipse>`, `<rect>` primitives
- Use `fill` attributes with hex colors, not CSS classes (for maximum compatibility)
- Keep SVGs optimized — no unnecessary `<g>` groups, no editor metadata
- No embedded fonts — use paths for any text elements
- No external references or `<image>` tags
- Total file size target: under 5KB per SVG

---

## Implementation Approach

Since you are an AI agent, create the SVGs programmatically by writing the SVG markup directly. The key is:

1. **Start with `maya-listening.svg`** as the base template — establish the face shape, hair, skin, features
2. **Duplicate and modify** for each subsequent emotion — only change the parts that express emotion (eyebrows, eyes, mouth primarily)
3. **Keep the head, hair, nose, ears, and clothing identical** across all 6 — only facial expression elements change

This ensures seamless transitions when the frontend swaps between SVG files.

---

## Acceptance Criteria

- [ ] 6 SVG files exist at the correct paths under `public/avatars/`
- [ ] All 6 use `viewBox="0 0 200 200"`
- [ ] All 6 share the same face shape, hair, skin tone, and clothing
- [ ] Each emotion is **clearly visually distinct** from the others (you can tell which is which at a glance)
- [ ] No SVG file exceeds 10KB
- [ ] SVGs render correctly in a browser (open the file directly)
- [ ] Transparent background (no `<rect>` background fill)
- [ ] Colors align with brand palette (purple, teal accents)
- [ ] Professional, warm aesthetic — not cartoonish or childish

---

## Output Files
```
public/avatars/maya-listening.svg
public/avatars/maya-thinking.svg
public/avatars/maya-happy.svg
public/avatars/maya-sad.svg
public/avatars/maya-confused.svg
public/avatars/maya-understanding.svg
```
