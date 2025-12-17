import re
from textual.app import App, ComposeResult
from textual.containers import Container, HorizontalGroup, VerticalGroup
from textual.widgets import Button, Digits, Input, Header, Footer
from textual.message import Message
from textual.reactive import reactive
from textual import on


class CountdownTimer(HorizontalGroup):
    """A timer that accepts HH:MM:SS or MM:SS format."""
    time_remaining = reactive(0.0)

    class Expired(Message):
        """Sent when the timer hits zero."""
        def __init__(self, timer_name: str) -> None:
            self.timer_name = timer_name
            super().__init__()

    def compose(self) -> ComposeResult:
        # ROW 1:
        # 1. Start (Top-Left) - will span 2 rows down
        yield Button("Start", id="countdown-timer-start", variant="success")
        
        # 2. Input (Top-Middle) - standard 1x1 size
        yield Input(placeholder="MM:SS", id="countdown-timer-input")
        
        # 3. Reset (Top-Right) - will span all 4 rows down
        yield Button("Reset", id="countdown-timer-reset")

        # ROW 2 (Hole Filling):
        # 4. Display (Middle) - fills the space under 'Input', spans 3 rows
        yield Digits("00:00:00", id="countdown-timer-display")

        # ROW 3 (Hole Filling):
        # 5. Stop (Bottom-Left) - fills the space under 'Start', spans 2 rows
        yield Button("Stop", id="countdown-timer-stop", variant="error")

    def on_mount(self) -> None:
        self.tick_timer = self.set_interval(0.1, self.tick, pause=True)

    def tick(self) -> None:
        if self.time_remaining > 0:
            self.time_remaining = max(0, self.time_remaining - 0.1)
        else:
            self.tick_timer.pause()
            self.add_class("expired")
            self.app.bell() # Native terminal beep
            self.post_message(self.Expired(self.id or "Timer"))

    def parse_time(self, time_str: str) -> float:
        """Converts HH:MM:SS or MM:SS string to total seconds."""
        parts = time_str.split(":")
        try:
            if len(parts) == 3: # HH:MM:SS
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2: # MM:SS
                m, s = map(int, parts)
                return m * 60 + s
            elif len(parts) == 1 and parts[0].isdigit(): # Plain seconds
                return float(parts[0])
        except ValueError:
            return 0.0
        return 0.0

    @on(Input.Changed, "#countdown-timer-input")
    def update_set_time(self, event: Input.Changed) -> None:
        # Parse the data input into internal seconds
        self.time_remaining = self.parse_time(event.value)

    @on(Button.Pressed, "#countdown-timer-start")
    def start(self) -> None:
        if self.time_remaining > 0:
            self.remove_class("expired")
            self.tick_timer.resume()

    @on(Button.Pressed, "#countdown-timer-reset")
    def reset(self) -> None:
        self.tick_timer.pause()
        self.time_remaining = 0.0
        self.remove_class("expired")
        self.query_one("#countdown-timer-input", Input).value = ""

    @on(Button.Pressed, "#countdown-timer-stop")
    def stop(self) -> None:
        self.tick_timer.pause()

    def watch_time_remaining(self, time: float) -> None:
        """Updates the digital display whenever time_remaining changes."""
        minutes, seconds = divmod(int(time), 60)
        hours, minutes = divmod(minutes, 60)
        self.query_one("#countdown-timer-display", Digits).update(f"{hours:02}:{minutes:02}:{seconds:02}")

class CountdownTimerContainer(Container):
    """
    Countdown Timer Container logic
    """
    def compose(self) -> ComposeResult:
        yield VerticalGroup(CountdownTimer())