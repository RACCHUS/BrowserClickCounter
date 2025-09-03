"""
Lightweight celebration animation system for Browser Click Counter.
Provides non-intrusive milestone celebrations with minimal performance impact.
"""

import tkinter as tk
import math
import time
import random
from typing import Optional, List, Callable


class FloatingText:
    """A small floating text animation for celebrations."""
    
    def __init__(self, parent: tk.Widget, text: str, x: int, y: int, color: str = "#a6e3a1"):
        self.parent = parent
        self.label = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            fg=color,
            bg=parent.cget('bg'),
            relief='flat',
            bd=0
        )
        
        # Position the label
        self.start_x = x
        self.start_y = y
        self.current_y = y
        
        self.label.place(x=x, y=y)
        
        # Animation properties
        self.start_time = time.time()
        self.duration = 2.0  # seconds
        self.is_active = True
        
        # Start animation
        self._animate()
    
    def _animate(self):
        """Animate the floating text."""
        if not self.is_active:
            return
            
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            self.cleanup()
            return
        
        # Float upward and fade out
        offset_y = int(-30 * progress)  # Move up 30 pixels
        alpha = 1.0 - progress  # Fade out
        
        new_y = self.start_y + offset_y
        self.label.place(x=self.start_x, y=new_y)
        
        # Simple alpha effect by darkening the color
        if alpha > 0.5:
            self.label.configure(fg="#a6e3a1")
        elif alpha > 0.2:
            self.label.configure(fg="#7ba87d")
        else:
            self.label.configure(fg="#5a7a5e")
        
        # Continue animation
        self.parent.after(16, self._animate)  # ~60fps
    
    def cleanup(self):
        """Clean up the floating text."""
        self.is_active = False
        if self.label:
            self.label.destroy()


class PulseEffect:
    """Simple pulse effect for the count label."""
    
    def __init__(self, label: tk.Label, colors: List[str], duration: float = 1.0):
        self.label = label
        self.colors = colors
        self.duration = duration
        self.start_time = time.time()
        self.original_color = label.cget('fg')
        self.is_active = True
        
        self._animate()
    
    def _animate(self):
        """Animate the pulse effect."""
        if not self.is_active:
            return
            
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration
        
        if progress >= 1.0:
            self.label.configure(fg=self.original_color)
            self.is_active = False
            return
        
        # Calculate current color
        if len(self.colors) > 1:
            # Cycle through colors
            color_progress = progress * (len(self.colors) - 1)
            color_index = int(color_progress)
            
            if color_index < len(self.colors) - 1:
                current_color = self.colors[color_index]
            else:
                current_color = self.colors[-1]
            
            self.label.configure(fg=current_color)
        
        # Continue animation
        self.label.after(16, self._animate)  # ~60fps


class SparkleParticle:
    """Small sparkle particle that appears around the count."""
    
    def __init__(self, parent: tk.Widget, x: int, y: int, color: str = "#f9e2af"):
        self.parent = parent
        self.start_x = x
        self.start_y = y
        self.color = color
        
        # Random animation properties
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(20, 40)
        self.life = random.uniform(1.0, 1.5)
        
        # Create small sparkle
        self.label = tk.Label(
            parent,
            text="✨",
            font=("Segoe UI", 10),
            fg=color,
            bg=parent.cget('bg'),
            relief='flat',
            bd=0
        )
        
        self.start_time = time.time()
        self.is_active = True
        
        self.label.place(x=x, y=y)
        self._animate()
    
    def _animate(self):
        """Animate the sparkle particle."""
        if not self.is_active:
            return
            
        elapsed = time.time() - self.start_time
        progress = elapsed / self.life
        
        if progress >= 1.0:
            self.cleanup()
            return
        
        # Move in a direction
        distance = self.speed * elapsed
        new_x = self.start_x + math.cos(self.angle) * distance
        new_y = self.start_y + math.sin(self.angle) * distance
        
        self.label.place(x=int(new_x), y=int(new_y))
        
        # Fade out
        alpha = 1.0 - progress
        if alpha > 0.5:
            self.label.configure(fg=self.color)
        elif alpha > 0.2:
            self.label.configure(fg="#b8a566")
        else:
            self.label.configure(fg="#8a7a4a")
        
        # Continue animation
        self.parent.after(16, self._animate)
    
    def cleanup(self):
        """Clean up the sparkle particle."""
        self.is_active = False
        if self.label:
            self.label.destroy()


class CelebrationManager:
    """Manages lightweight celebration animations for milestone achievements."""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.active_effects: List = []
        
        # Color scheme (aligned with existing theme)
        self.colors = {
            'success': '#a6e3a1',
            'celebration_gold': '#f9e2af',
            'blue': '#89b4fa',
            'purple': '#cba6f7',
            'text_primary': '#cdd6f4'
        }
    
    def trigger_celebration(self, milestone_type: str, count: int):
        """Trigger appropriate celebration based on milestone type."""
        if milestone_type == "minor":  # 100-click intervals
            self._create_light_celebration(count)
        elif milestone_type == "major":  # 1000-click intervals
            self._create_enhanced_celebration(count)
    
    def _create_light_celebration(self, count: int):
        """Create 100-click interval celebration with light effects."""
        # Get count label position
        label = self.gui.count_label
        
        try:
            # Update the GUI to get current positions
            label.update_idletasks()
            
            # Get label position relative to main window
            label_x = label.winfo_x()
            label_y = label.winfo_y()
            label_width = label.winfo_width()
            label_height = label.winfo_height()
            
            # Center position
            center_x = label_x + label_width // 2
            center_y = label_y + label_height // 2
            
            # 1. Pulse effect on the count label
            pulse_colors = [self.colors['success'], self.colors['celebration_gold'], self.colors['success']]
            pulse_effect = PulseEffect(label, pulse_colors, 1.5)
            self.active_effects.append(pulse_effect)
            
            # 2. Floating "+100!" text
            floating_text = FloatingText(
                self.gui.main_frame, 
                f"+{count}!",
                center_x - 20,  # Slightly offset
                center_y - 30,
                self.colors['celebration_gold']
            )
            self.active_effects.append(floating_text)
            
            # 3. Small sparkles around the count
            for i in range(3):
                angle = (2 * math.pi * i) / 3  # Evenly spaced
                offset_x = center_x + math.cos(angle) * 40
                offset_y = center_y + math.sin(angle) * 40
                
                sparkle = SparkleParticle(
                    self.gui.main_frame,
                    int(offset_x),
                    int(offset_y),
                    self.colors['celebration_gold']
                )
                self.active_effects.append(sparkle)
                
        except Exception as e:
            # Fallback to simple pulse if positioning fails
            pulse_colors = [self.colors['success'], self.colors['celebration_gold'], self.colors['success']]
            pulse_effect = PulseEffect(label, pulse_colors, 1.5)
            self.active_effects.append(pulse_effect)
    
    def _create_enhanced_celebration(self, count: int):
        """Create 1000-click interval celebration with enhanced effects."""
        # Get count label position
        label = self.gui.count_label
        
        try:
            # Update the GUI to get current positions
            label.update_idletasks()
            
            # Get label position relative to main window
            label_x = label.winfo_x()
            label_y = label.winfo_y()
            label_width = label.winfo_width()
            label_height = label.winfo_height()
            
            # Center position
            center_x = label_x + label_width // 2
            center_y = label_y + label_height // 2
            
            # 1. Enhanced pulse effect with rainbow colors
            rainbow_colors = [
                self.colors['success'], self.colors['blue'], 
                self.colors['purple'], self.colors['celebration_gold'],
                self.colors['success']
            ]
            pulse_effect = PulseEffect(label, rainbow_colors, 2.5)
            self.active_effects.append(pulse_effect)
            
            # 2. Floating milestone text
            floating_text = FloatingText(
                self.gui.main_frame, 
                f"🎉 {count}! 🎉",
                center_x - 40,
                center_y - 40,
                self.colors['blue']
            )
            self.active_effects.append(floating_text)
            
            # 3. More sparkles in a burst pattern
            for i in range(8):
                angle = (2 * math.pi * i) / 8
                offset_x = center_x + math.cos(angle) * 50
                offset_y = center_y + math.sin(angle) * 50
                
                # Alternate colors
                color = self.colors['blue'] if i % 2 == 0 else self.colors['purple']
                
                sparkle = SparkleParticle(
                    self.gui.main_frame,
                    int(offset_x),
                    int(offset_y),
                    color
                )
                self.active_effects.append(sparkle)
                
                # Add a delayed second ring
                if i < 4:
                    def delayed_sparkle(x=offset_x, y=offset_y, c=color):
                        sparkle2 = SparkleParticle(
                            self.gui.main_frame,
                            int(x + random.randint(-10, 10)),
                            int(y + random.randint(-10, 10)),
                            c
                        )
                        self.active_effects.append(sparkle2)
                    
                    self.gui.root.after(500, delayed_sparkle)
                
        except Exception as e:
            # Fallback to enhanced pulse if positioning fails
            rainbow_colors = [
                self.colors['success'], self.colors['blue'], 
                self.colors['purple'], self.colors['celebration_gold'],
                self.colors['success']
            ]
            pulse_effect = PulseEffect(label, rainbow_colors, 2.5)
            self.active_effects.append(pulse_effect)
    
    def cleanup_all(self):
        """Clean up all active effects."""
        for effect in self.active_effects:
            if hasattr(effect, 'cleanup'):
                effect.cleanup()
            elif hasattr(effect, 'is_active'):
                effect.is_active = False
        
        self.active_effects.clear()
