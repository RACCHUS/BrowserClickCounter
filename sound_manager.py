"""
Sound notification system for timer alerts.
Provides cross-platform audio playback with fallbacks.
"""

import os
import sys
import threading
import wave
import struct
import math
from typing import Optional, Dict, Union, Any
from pathlib import Path

# Optional imports - these are handled gracefully if not available
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False

try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    playsound = None
    PLAYSOUND_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    winsound = None
    WINSOUND_AVAILABLE = False


class SoundManager:
    """
    Manages timer sound notifications with cross-platform support.
    Provides multiple audio backend options with graceful fallbacks.
    """
    
    def __init__(self) -> None:
        """Initialize sound manager with available backends."""
        self.sounds_dir = Path(__file__).parent / "sounds"
        self.sounds_dir.mkdir(exist_ok=True)
        
        # Available sound files
        self.sound_files: Dict[str, str] = {
            'timer_complete': 'timer_alert.wav',
            'timer_warning': 'timer_warning.wav',  # Optional: for 1-minute warning
            'timer_tick': 'timer_tick.wav'          # Optional: for tick sounds
        }
        
        # Sound settings
        self.volume: float = 0.7  # 0.0 to 1.0
        self.enabled: bool = True
        self.current_backend: Optional[str] = None
        
        # Repeating sound management
        self.is_repeating: bool = False
        self.repeat_job_id: Optional[str] = None
        self.repeat_interval: int = 3000  # 3 seconds between repeats
        self.parent_widget: Optional[Any] = None
        
        # Initialize audio backend
        self._init_audio_backend()
    
    def _init_audio_backend(self) -> None:
        """Initialize the best available audio backend."""
        # Try different audio libraries in order of preference
        backends = [
            self._init_pygame,
            self._init_playsound,
            self._init_winsound,
            self._init_system_beep
        ]
        
        for backend_init in backends:
            if backend_init():
                break
    
    def _init_pygame(self) -> bool:
        """Try to initialize pygame mixer."""
        if not PYGAME_AVAILABLE or pygame is None:
            return False
            
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.current_backend = 'pygame'
            return True
        except Exception:
            return False
    
    def _init_playsound(self) -> bool:
        """Try to initialize playsound."""
        if not PLAYSOUND_AVAILABLE or playsound is None:
            return False
            
        try:
            # Test that playsound is working
            self.current_backend = 'playsound'
            return True
        except Exception:
            return False
    
    def _init_winsound(self) -> bool:
        """Try to initialize Windows winsound."""
        if sys.platform != 'win32' or not WINSOUND_AVAILABLE or winsound is None:
            return False
        
        try:
            self.current_backend = 'winsound'
            return True
        except Exception:
            return False
    
    def _init_system_beep(self) -> bool:
        """Fallback to system beep."""
        self.current_backend = 'system_beep'
        return True
    
    def play_sound(self, sound_name: str, blocking: bool = False) -> bool:
        """
        Play a sound notification.
        
        Args:
            sound_name: Name of the sound ('timer_complete', etc.)
            blocking: Whether to block until sound finishes
            
        Returns:
            bool: True if sound was played successfully
        """
        if not self.enabled:
            return False
        
        if blocking:
            return self._play_sound_sync(sound_name)
        else:
            # Play sound in background thread
            thread = threading.Thread(
                target=self._play_sound_sync, 
                args=(sound_name,),
                daemon=True
            )
            thread.start()
            return True
    
    def start_repeating_sound(self, sound_name: str, parent_widget: Optional[Any] = None) -> bool:
        """
        Start playing a sound repeatedly until stopped.
        
        Args:
            sound_name: Name of the sound to repeat
            parent_widget: Widget to use for scheduling (needed for tkinter.after)
            
        Returns:
            bool: True if repeating sound was started
        """
        if self.is_repeating:
            self.stop_repeating_sound()
        
        if not self.enabled:
            return False
        
        self.is_repeating = True
        self.parent_widget = parent_widget
        
        # Play the sound immediately
        self.play_sound(sound_name, blocking=False)
        
        # Schedule repeating
        if parent_widget:
            self._schedule_repeat(sound_name)
        
        return True
    
    def stop_repeating_sound(self) -> bool:
        """
        Stop repeating sound playback.
        
        Returns:
            bool: True if repeating sound was stopped
        """
        if not self.is_repeating:
            return False
        
        self.is_repeating = False
        
        # Cancel scheduled repeat
        if self.repeat_job_id and hasattr(self, 'parent_widget') and self.parent_widget:
            try:
                self.parent_widget.after_cancel(self.repeat_job_id)
            except:
                pass
        
        self.repeat_job_id = None
        self.parent_widget = None
        return True
    
    def _schedule_repeat(self, sound_name: str) -> None:
        """Schedule the next sound repeat."""
        if not self.is_repeating or not self.parent_widget:
            return
        
        def repeat_sound() -> None:
            if self.is_repeating:
                self.play_sound(sound_name, blocking=False)
                self._schedule_repeat(sound_name)
        
        self.repeat_job_id = self.parent_widget.after(self.repeat_interval, repeat_sound)
    
    def _play_sound_sync(self, sound_name: str) -> bool:
        """Play sound synchronously using the current backend."""
        if sound_name not in self.sound_files:
            return False
        
        sound_file = self.sounds_dir / self.sound_files[sound_name]
        
        # Check if sound file exists, create default if not
        if not sound_file.exists():
            self._create_default_sound(sound_name, sound_file)
        
        try:
            if self.current_backend == 'pygame':
                return self._play_with_pygame(sound_file)
            elif self.current_backend == 'playsound':
                return self._play_with_playsound(sound_file)
            elif self.current_backend == 'winsound':
                return self._play_with_winsound(sound_file)
            elif self.current_backend == 'system_beep':
                return self._play_system_beep()
        except Exception:
            # Fallback to system beep
            return self._play_system_beep()
        
        return False
    
    def _play_with_pygame(self, sound_file: Path) -> bool:
        """Play sound using pygame."""
        if not PYGAME_AVAILABLE or pygame is None:
            return False
            
        try:
            sound = pygame.mixer.Sound(str(sound_file))
            sound.set_volume(self.volume)
            sound.play()
            return True
        except Exception:
            return False
    
    def _play_with_playsound(self, sound_file: Path) -> bool:
        """Play sound using playsound."""
        if not PLAYSOUND_AVAILABLE or playsound is None:
            return False
            
        try:
            playsound(str(sound_file), block=False)
            return True
        except Exception:
            return False
    
    def _play_with_winsound(self, sound_file: Path) -> bool:
        """Play sound using Windows winsound."""
        if not WINSOUND_AVAILABLE or winsound is None:
            return False
            
        try:
            winsound.PlaySound(str(sound_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except Exception:
            return False
    
    def _play_system_beep(self) -> bool:
        """Play system beep as fallback."""
        try:
            if sys.platform == 'win32' and WINSOUND_AVAILABLE and winsound is not None:
                # Play system exclamation sound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:
                # Unix/Linux/Mac
                print('\a')  # ASCII bell character
            return True
        except Exception:
            return False
    
    def _create_default_sound(self, sound_name: str, sound_file: Path) -> None:
        """Create a default sound file if it doesn't exist."""
        if sound_name == 'timer_complete':
            self._create_timer_alert_sound(sound_file)
        elif sound_name == 'timer_warning':
            self._create_timer_warning_sound(sound_file)
        elif sound_name == 'timer_tick':
            self._create_timer_tick_sound(sound_file)
    
    def _create_timer_alert_sound(self, sound_file: Path) -> None:
        """Create a default timer alert sound."""
        try:
            # Sound parameters
            sample_rate = 22050
            duration = 1.0  # 1 second
            frequency = 800  # 800 Hz tone
            
            # Generate samples
            num_samples = int(sample_rate * duration)
            samples = []
            
            for i in range(num_samples):
                # Create a simple sine wave with fade out
                t = i / sample_rate
                fade = max(0, 1 - (t / duration) * 2)  # Fade out in second half
                amplitude = 0.3 * fade  # 30% volume with fade
                sample = amplitude * math.sin(2 * math.pi * frequency * t)
                samples.append(int(sample * 32767))  # 16-bit signed
            
            # Write WAV file
            with wave.open(str(sound_file), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Pack samples as 16-bit signed integers
                packed_samples = struct.pack('<' + 'h' * len(samples), *samples)
                wav_file.writeframes(packed_samples)
                
        except Exception:
            # If WAV creation fails, just use system beep
            pass
    
    def _create_timer_warning_sound(self, sound_file: Path) -> None:
        """Create a default timer warning sound (shorter, higher pitch)."""
        try:
            sample_rate = 22050
            duration = 0.5  # Shorter for warning
            frequency = 1000  # Higher pitch
            
            num_samples = int(sample_rate * duration)
            samples = []
            
            for i in range(num_samples):
                t = i / sample_rate
                amplitude = 0.2  # Quieter than alert
                sample = amplitude * math.sin(2 * math.pi * frequency * t)
                samples.append(int(sample * 32767))
            
            with wave.open(str(sound_file), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                packed_samples = struct.pack('<' + 'h' * len(samples), *samples)
                wav_file.writeframes(packed_samples)
                
        except Exception:
            pass
    
    def _create_timer_tick_sound(self, sound_file: Path) -> None:
        """Create a default timer tick sound."""
        try:
            sample_rate = 22050
            duration = 0.1  # Very short tick
            frequency = 1200
            
            num_samples = int(sample_rate * duration)
            samples = []
            
            for i in range(num_samples):
                t = i / sample_rate
                amplitude = 0.1  # Very quiet
                sample = amplitude * math.sin(2 * math.pi * frequency * t)
                samples.append(int(sample * 32767))
            
            with wave.open(str(sound_file), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                packed_samples = struct.pack('<' + 'h' * len(samples), *samples)
                wav_file.writeframes(packed_samples)
                
        except Exception:
            pass
    
    def set_volume(self, volume: float) -> bool:
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            bool: True if volume was set successfully
        """
        if not 0.0 <= volume <= 1.0:
            return False
        
        self.volume = volume
        return True
    
    def set_enabled(self, enabled: bool):
        """Enable or disable sound notifications."""
        self.enabled = enabled
    
    def is_enabled(self) -> bool:
        """Check if sound notifications are enabled."""
        return self.enabled
    
    def get_backend_info(self) -> Dict:
        """Get information about the current audio backend."""
        return {
            'backend': self.current_backend,
            'enabled': self.enabled,
            'volume': self.volume,
            'sounds_dir': str(self.sounds_dir),
            'available_sounds': list(self.sound_files.keys()),
            'is_repeating': self.is_repeating,
            'repeat_interval_ms': self.repeat_interval
        }
    
    def test_sound(self, sound_name: str = 'timer_complete') -> bool:
        """Test a sound notification."""
        return self.play_sound(sound_name, blocking=False)
