"""
Fireworks particle system for enhanced celebration animations.
Provides high-performance particle effects for milestone celebrations.
"""

import tkinter as tk
import math
import random
import time
from typing import List, Tuple, Optional


class Particle:
    """Individual particle with physics properties."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, color: str, life: float = 1.0):
        self.x = x
        self.y = y
        self.vx = vx  # velocity x
        self.vy = vy  # velocity y
        self.color = color
        self.life = life
        self.max_life = life
        self.gravity = 100  # pixels per second squared
        self.canvas_id: Optional[int] = None
        self.is_active = True
    
    def update(self, dt: float):
        """Update particle physics."""
        if not self.is_active:
            return
        
        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Apply gravity
        self.vy += self.gravity * dt
        
        # Reduce life
        self.life -= dt
        if self.life <= 0:
            self.is_active = False
    
    def get_alpha(self) -> float:
        """Get current alpha based on remaining life."""
        return max(0.0, self.life / self.max_life)
    
    def get_size(self) -> float:
        """Get current size based on remaining life."""
        alpha = self.get_alpha()
        return 2 + (alpha * 3)  # Size from 2 to 5 pixels


class FireworksBurst:
    """Single fireworks explosion with multiple particles."""
    
    def __init__(self, x: float, y: float, particle_count: int, colors: List[str]):
        self.x = x
        self.y = y
        self.particles: List[Particle] = []
        self.is_active = True
        
        # Create particles in a burst pattern
        for i in range(particle_count):
            angle = (2 * math.pi * i) / particle_count
            speed = random.uniform(50, 150)  # pixels per second
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(20, 60)  # Add upward bias
            
            color = random.choice(colors)
            life = random.uniform(1.5, 2.5)
            
            particle = Particle(x, y, vx, vy, color, life)
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles in this burst."""
        active_particles = []
        
        for particle in self.particles:
            particle.update(dt)
            if particle.is_active:
                active_particles.append(particle)
        
        self.particles = active_particles
        self.is_active = len(self.particles) > 0
    
    def get_active_particles(self) -> List[Particle]:
        """Get all active particles in this burst."""
        return [p for p in self.particles if p.is_active]


class ConfettiParticle(Particle):
    """Confetti particle that falls with rotation."""
    
    def __init__(self, x: float, y: float, color: str):
        # Random horizontal velocity, slight upward initial velocity
        vx = random.uniform(-30, 30)
        vy = random.uniform(-50, -20)
        life = random.uniform(3.0, 5.0)
        
        super().__init__(x, y, vx, vy, color, life)
        
        self.rotation = 0
        self.rotation_speed = random.uniform(-180, 180)  # degrees per second
        self.width = random.uniform(3, 6)
        self.height = random.uniform(8, 12)
    
    def update(self, dt: float):
        """Update confetti with rotation."""
        super().update(dt)
        self.rotation += self.rotation_speed * dt
        
        # Add air resistance
        self.vx *= 0.98
        
        # Reduce gravity slightly for confetti
        self.gravity = 80


class ParticleSystem:
    """Manages multiple particle effects efficiently."""
    
    def __init__(self, canvas: tk.Canvas, max_particles: int = 20):
        self.canvas = canvas
        self.max_particles = max_particles
        self.bursts: List[FireworksBurst] = []
        self.confetti: List[ConfettiParticle] = []
        self.last_update = time.time()
        self.particle_objects = {}  # Maps particle to canvas object ID
    
    def add_burst(self, x: float, y: float, particle_count: int, colors: List[str]):
        """Add new fireworks burst at position."""
        # Limit total particles
        current_particles = sum(len(burst.particles) for burst in self.bursts)
        if current_particles >= self.max_particles:
            return
        
        # Limit particle count if needed
        available_slots = self.max_particles - current_particles
        actual_count = min(particle_count, available_slots)
        
        if actual_count > 0:
            burst = FireworksBurst(x, y, actual_count, colors)
            self.bursts.append(burst)
    
    def add_confetti(self, x: float, y: float, count: int, colors: List[str]):
        """Add confetti particles."""
        for _ in range(min(count, self.max_particles - len(self.confetti))):
            color = random.choice(colors)
            confetti = ConfettiParticle(x + random.uniform(-20, 20), y, color)
            self.confetti.append(confetti)
    
    def update(self):
        """Update all particles, remove dead ones."""
        current_time = time.time()
        dt = current_time - self.last_update
        dt = min(dt, 0.1)  # Cap delta time to prevent large jumps
        self.last_update = current_time
        
        # Update bursts
        active_bursts = []
        for burst in self.bursts:
            burst.update(dt)
            if burst.is_active:
                active_bursts.append(burst)
            else:
                # Clean up canvas objects for dead particles
                for particle in burst.particles:
                    if particle.canvas_id and particle.canvas_id in self.particle_objects:
                        self.canvas.delete(particle.canvas_id)
                        del self.particle_objects[particle.canvas_id]
        
        self.bursts = active_bursts
        
        # Update confetti
        active_confetti = []
        for confetti in self.confetti:
            confetti.update(dt)
            if confetti.is_active:
                active_confetti.append(confetti)
            else:
                # Clean up canvas object
                if confetti.canvas_id and confetti.canvas_id in self.particle_objects:
                    self.canvas.delete(confetti.canvas_id)
                    del self.particle_objects[confetti.canvas_id]
        
        self.confetti = active_confetti
    
    def render(self):
        """Render all active particles."""
        # Render burst particles
        for burst in self.bursts:
            for particle in burst.get_active_particles():
                self._render_particle(particle)
        
        # Render confetti
        for confetti in self.confetti:
            if confetti.is_active:
                self._render_confetti(confetti)
    
    def _render_particle(self, particle: Particle):
        """Render a single burst particle."""
        if not particle.is_active:
            return
        
        size = particle.get_size()
        alpha = particle.get_alpha()
        
        # Create or update canvas object
        if particle.canvas_id is None:
            particle.canvas_id = self.canvas.create_oval(
                particle.x - size, particle.y - size,
                particle.x + size, particle.y + size,
                fill=particle.color,
                outline="",
                width=0
            )
            self.particle_objects[particle.canvas_id] = particle
        else:
            # Update position and size
            self.canvas.coords(
                particle.canvas_id,
                particle.x - size, particle.y - size,
                particle.x + size, particle.y + size
            )
            
            # Update alpha by adjusting color brightness
            color = self._apply_alpha_to_color(particle.color, alpha)
            self.canvas.itemconfig(particle.canvas_id, fill=color)
    
    def _render_confetti(self, confetti: ConfettiParticle):
        """Render a confetti particle with rotation."""
        if not confetti.is_active:
            return
        
        alpha = confetti.get_alpha()
        
        # Create or update canvas object
        if confetti.canvas_id is None:
            # Create rectangle for confetti
            confetti.canvas_id = self.canvas.create_rectangle(
                confetti.x - confetti.width/2, confetti.y - confetti.height/2,
                confetti.x + confetti.width/2, confetti.y + confetti.height/2,
                fill=confetti.color,
                outline="",
                width=0
            )
            self.particle_objects[confetti.canvas_id] = confetti
        else:
            # Update position
            self.canvas.coords(
                confetti.canvas_id,
                confetti.x - confetti.width/2, confetti.y - confetti.height/2,
                confetti.x + confetti.width/2, confetti.y + confetti.height/2
            )
            
            # Update alpha
            color = self._apply_alpha_to_color(confetti.color, alpha)
            self.canvas.itemconfig(confetti.canvas_id, fill=color)
    
    def _apply_alpha_to_color(self, color: str, alpha: float) -> str:
        """Apply alpha to a hex color by darkening it."""
        if alpha >= 1.0:
            return color
        
        # Convert hex to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Apply alpha by blending with black
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def has_active_particles(self) -> bool:
        """Check if any particles are still active."""
        return len(self.bursts) > 0 or len(self.confetti) > 0
    
    def get_particle_count(self) -> int:
        """Get total number of active particles."""
        burst_count = sum(len(burst.particles) for burst in self.bursts)
        return burst_count + len(self.confetti)
    
    def cleanup(self):
        """Clean up all particles and canvas objects."""
        # Delete all canvas objects
        for canvas_id in self.particle_objects:
            self.canvas.delete(canvas_id)
        
        self.particle_objects.clear()
        self.bursts.clear()
        self.confetti.clear()
    
    def create_celebration_sequence(self, canvas_width: int, canvas_height: int, colors: List[str]):
        """Create a pre-designed celebration sequence."""
        # Central burst
        self.add_burst(canvas_width * 0.5, canvas_height * 0.3, 8, colors)
        
        # Side bursts with delay (will be called by celebration manager)
        burst_positions = [
            (canvas_width * 0.25, canvas_height * 0.4),
            (canvas_width * 0.75, canvas_height * 0.4),
            (canvas_width * 0.4, canvas_height * 0.2),
            (canvas_width * 0.6, canvas_height * 0.2)
        ]
        
        return burst_positions  # Return positions for delayed creation
