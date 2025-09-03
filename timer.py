from datetime import datetime


class SessionTimer:
    """Simple session timer to keep GUI code concise.

    Responsibilities:
    - start()/stop() session timing
    - return elapsed seconds
    - format as HH:MM:SS for display
    """
    def __init__(self):
        self.start_time = None

    def start(self):
        if self.start_time is None:
            self.start_time = datetime.now()

    def stop(self):
        self.start_time = None

    def reset(self):
        self.start_time = None

    def elapsed_seconds(self):
        if not self.start_time:
            return 0
        return int((datetime.now() - self.start_time).total_seconds())

    def format_hms(self):
        secs = self.elapsed_seconds()
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
