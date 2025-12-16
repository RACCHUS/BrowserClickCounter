# Compact Window Improvements - Summary

## Changes Made

### 1. **Smaller Compact Window Size**
- Changed from `220x220` to `160x160` pixels
- This makes the collapsed window much more compact and less intrusive

### 2. **Added IPH Display to Compact View**
- Added `compact_iph_label` to show Images Per Hour in the collapsed window
- Font: Segoe UI, size 8, secondary color (same style as region status)
- Updates in real-time along with the click count

### 3. **Optimized Compact Layout**
- Reduced font size of main count from 24 to 20 for better fit
- Reduced padding throughout the compact view
- Removed control buttons from compact view (they're still accessible in expanded view)
- Cleaner, more minimal appearance focusing on key stats

### 4. **Real-time IPH Updates**
- Modified `update_stats_loop()` to calculate IPH for both expanded and compact views
- IPH updates every second in compact view showing current session rate
- Formula: `clicks / (session_time_in_hours)`

## Compact View Now Shows:
1. **Click Count** (main large number)
2. **Region Status** (e.g., "Region: 100×100 at (100,100)")
3. **IPH Rate** (e.g., "IPH: 45.3")
4. **Timer Widget** (if countdown timer is active)
5. **Expand Button** (to access full controls)

## Layout Order (top to bottom):
```
┌─────────────────┐
│      42         │  ← Click count (size 20, bold)
│                 │
│ Region: 100×100 │  ← Region status (size 8)
│   IPH: 45.3     │  ← Images per hour (size 8)
│                 │
│ [Timer Widget]  │  ← Countdown timer (if active)
│                 │
│   ⚙ Expand      │  ← Expand button
└─────────────────┘
```

## Benefits:
- **Much smaller footprint** when collapsed (160×160 vs 220×220)
- **Shows essential stats** without needing to expand
- **Live IPH tracking** for performance monitoring
- **Clean, minimal design** that doesn't clutter the screen
- **Quick access** to expand for full controls when needed

The compact view is now perfect for monitoring your clicking session without taking up much screen space, while still showing the most important information at a glance.