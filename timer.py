from datetime import datetime


class SessionTimer:
    """Simple session timer to keep GUI code concise.

    Responsibilities:
    - start()/pause()/resume()/stop() session timing
    - return elapsed seconds (excluding paused time)
    - format as HH:MM:SS for display
    """
    def __init__(self):
        self.start_time = None
        self.paused_time = None
        self.total_paused_duration = 0

    def start(self):
        if self.start_time is None:
            self.start_time = datetime.now()
            self.total_paused_duration = 0

    def pause(self):
        if self.start_time and not self.paused_time:
            self.paused_time = datetime.now()

    def resume(self):
        if self.paused_time:
            pause_duration = (datetime.now() - self.paused_time).total_seconds()
            self.total_paused_duration += pause_duration
            self.paused_time = None

    def stop(self):
        self.start_time = None
        self.paused_time = None
        self.total_paused_duration = 0

    def reset(self):
        self.start_time = None
        self.paused_time = None
        self.total_paused_duration = 0

    def is_paused(self):
        return self.paused_time is not None

    def elapsed_seconds(self):
        if not self.start_time:
            return 0
        
        current_time = datetime.now()
        total_elapsed = (current_time - self.start_time).total_seconds()
        
        # Subtract total paused duration
        active_elapsed = total_elapsed - self.total_paused_duration
        
        # If currently paused, subtract the current pause duration
        if self.paused_time:
            current_pause_duration = (current_time - self.paused_time).total_seconds()
            active_elapsed -= current_pause_duration
            
        return max(0, int(active_elapsed))

    def format_hms(self):
        secs = self.elapsed_seconds()
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
