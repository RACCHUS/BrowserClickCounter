# Plan: Fireworks Animation for Milestone Celebrations

## Goals
- Display a visually appealing fireworks animation when the click count reaches multiples of 100 (simple) and 1000 (more elaborate).
- Ensure the animation is smooth and does not cause UI lag or performance issues.
- Keep the animation non-intrusive (does not block user interaction for long).

## Steps

### 1. Design the Animation Approach
- Use a `tk.Canvas` overlay for drawing fireworks, as it allows efficient custom drawing and animation.
- For 100-click milestones: Show a quick, simple burst (few particles, short duration).
- For 1000-click milestones: Show a larger, multi-burst, more colorful and longer animation.

### 2. Integrate Animation Trigger
- In the method that updates the click count, check if the count is a multiple of 100 or 1000.
- Trigger the appropriate animation without blocking the main event loop.

### 3. Implement Fireworks Animation
- Create a `FireworksAnimator` class or function:
  - Draws animated particles (lines/circles) radiating from a central point.
  - Uses `after()` for smooth, non-blocking frame updates.
  - Randomizes colors, directions, and speeds for realism.
  - For 1000s, trigger multiple bursts in sequence or at different locations.
- Ensure the animation overlays the main window but does not interfere with button clicks.

### 4. Performance Considerations
- Limit the number of particles and animation duration (e.g., 0.5–1s for 100, 1–2s for 1000).
- Remove the canvas or clear it after the animation completes.
- Avoid using blocking loops or excessive redraws.

### 5. Visual Quality
- Use bright, contrasting colors for particles.
- Add fading or shrinking effects for realism.
- Optionally, add a subtle sound effect (with user option to mute).

### 6. Testing & Tuning
- Test on various hardware to ensure smoothness.
- Adjust particle count, duration, and effects for best balance of looks and performance.

## Acceptance Criteria
- Fireworks animation appears instantly and smoothly at each milestone.
- No noticeable lag or UI freeze during or after animation.
- Animation is visually distinct for 100 vs. 1000 milestones.
- Animation does not interfere with normal app usage.
