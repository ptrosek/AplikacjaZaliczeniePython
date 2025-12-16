from time import monotonic

from textual.app import ComposeResult
from textual.containers import Container, HorizontalGroup, VerticalGroup
from textual.widgets import Button, Digits
from textual.reactive import reactive
from textual import events, on

class Stopwatch(HorizontalGroup):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Start", id="timer-start", variant="success")
        yield Button("Stop", id="timer-stop", variant="error")
        yield Button("Reset", id="timer-reset")
        yield Digits("00:00:00.00", id="timer-display")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "start":
            self.add_class("started")
        elif event.button.id == "stop":
            self.remove_class("started")
    
    start_time = reactive(monotonic)
    time = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    @on(Button.Pressed, "#timer-start")
    def start_timer(self) -> None:
        self.update_timer.resume()

    @on(Button.Pressed, "#timer-stop")
    def stop_timer(self) -> None:
        self.update_timer.pause()

    @on(Button.Pressed, "#timer-reset")
    def reset_timer(self) -> None:
        self.start_time = monotonic()
        self.time = 0.0
        
    def update_time(self) -> None:
        self.time = monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.query_one("#timer-display", Digits).update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")


class Timer(Container):
    """
    Timer Countdown logic
    """
    def compose(self) -> ComposeResult:
        yield VerticalGroup(Stopwatch(), Stopwatch())