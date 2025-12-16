from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static


class Timer(Container):
    """
    Placeholder widget for the Timer function.
    TODO: Implement countdown/stopwatch logic here.
    """
    def compose(self) -> ComposeResult:
        yield Static("Timer Function (To Be Implemented)", classes="placeholder-text")

class ReadingPredictor(Container):
    """
    Placeholder widget for the Reading Time Predictor.
    TODO: Implement calibration and prediction logic here.
    """
    def compose(self) -> ComposeResult:
        yield Static("Reading Predictor Function (To Be Implemented)", classes="placeholder-text")


class OptionalFunction2(Container):
    """
    Placeholder for the second optional function (e.g., System Info).
    """
    def compose(self) -> ComposeResult:
        yield Static("Optional Function 2 (To Be Implemented)", classes="placeholder-text")
