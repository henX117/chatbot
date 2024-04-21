import time
import threading
from .speaking import Speaker

class Pomodoro:
    def __init__(self, work_minutes=30, break_minutes=5, long_break_minutes=60, pomodoros_before_long_break=4):
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.long_break_minutes = long_break_minutes
        self.pomodoros_before_long_break = pomodoros_before_long_break
        self.pomodoros_completed = 0
        self.timer_running = False
        self.timer_thread = None
    
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.start()
    
    def stop_timer(self):
        self.timer_running = False
    
    def _run_timer(self):
        while self.timer_running:
            self._do_work_session()
            self.pomodoros_completed += 1
            if self.pomodoros_completed % self.pomodoros_before_long_break == 0:
                self._do_long_break_session()
            else:
                self._do_break_session()
    
    def _do_work_session(self):
        print("Work session started")
        self._countdown(self.work_minutes, "work")
        print("Work session completed")
    
    def _do_break_session(self):
        print("Break session started")
        self._countdown(self.break_minutes, "break")
        print("Break session completed")
    
    def _do_long_break_session(self):
        print("Long break session started")
        self._countdown(self.long_break_minutes, "long_break")
        print("Long break session completed")
    
    def _countdown(self, minutes, session_type):
        seconds = minutes * 60
        while seconds > 0 and self.timer_running:
            print(f"Time remaining: {seconds // 60:02d}:{seconds % 60:02d}")
            
            if session_type != "break" and (seconds // 60) == 5:
                Speaker.speak("Reminder: 5 minutes remaining in the current session.")
            
            time.sleep(60)  # Sleep for 60 seconds (1 minute)
            seconds -= 60  # Decrement seconds by 60 (1 minute)