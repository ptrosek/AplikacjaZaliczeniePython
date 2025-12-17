import math
import random
import re

from textual.app import ComposeResult
from textual.containers import Container, HorizontalGroup, VerticalGroup
from textual.widgets import Button, DirectoryTree, Label, Static
from textual import on


from textual.screen import ModalScreen
from textual.widgets import Label, Static, Button
from textual.containers import Container, Vertical

from .stopwatch import Stopwatch

class CalibrationScreen(ModalScreen[float]):
    """Screen to calibrate reading speed using a stopwatch and sample text.
    Returns the calculated WPM (words per minute) on dismissal.
    """
    BINDINGS = [
        ("q", "dismiss_screen", "Quit Analysis") 
    ]
    def __init__(self, sample_text: str):
        super().__init__()
        self.sample_text = sample_text
        self.word_count = len(sample_text.split())
    
    def action_dismiss_screen(self) -> None:
        """Called when user hits 'q'."""
        self.dismiss(0.0)

    def compose(self) -> ComposeResult:
        with Container(id="calib-container"):
            yield Label(f"Read this sample ({self.word_count} words), then click Done:", classes="header")
            yield Static(self.sample_text, id="sample-text")
            yield Stopwatch(id="my-stopwatch")
            with Vertical(id="calib-controls"):
                yield Button("Done Reading - Analyze", variant="primary", id="btn-analyze")

    @on(Button.Pressed, "#btn-analyze")
    def complete_calibration(self):
        timer = self.query_one(Stopwatch)
        
        timer.stop_timer()
        
        seconds = timer.elapsed_seconds
        
        if seconds <= 0:
            seconds = 1
            
        wpm = (self.word_count / seconds) * 60
        
        self.dismiss(wpm)

class FileOperator(VerticalGroup):
    """
    Handles file loading, ARI calculation, and reading analysis synchronously.
    """
    def compose(self):
        yield DirectoryTree("./", id="file-tree")
        yield Static("Select a file to begin...", id="analysis-results")

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.load_and_process_file(str(event.path))

    def load_and_process_file(self, file_path: str) -> None:
        """
        Reads file in chunks (sync), calculates stats, and triggers calibration.
        """
        results_widget = self.query_one("#analysis-results", Static)
        results_widget.update("Processing file...")

        try:
            full_content = []
            
            with open(file_path, "r", encoding="utf-8") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    full_content.append(chunk)
            
            text = "".join(full_content)

            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            words = text.split()
            
            word_count = len(words)
            sentence_count = len(sentences)

            if sentence_count < 5 or word_count < 15:
                self.notify("File too short (needs 5+ sentences & 15+ words).", severity="error")
                results_widget.update("Analysis failed: File too short.")
                return

            char_count = sum(c.isalnum() for c in text)
            
            ari_score = 0.0
            if word_count > 0 and sentence_count > 0:
                ari_score = (
                    4.71 * (char_count / word_count) + 
                    0.5 * (word_count / sentence_count) - 
                    21.43
                )
                ari_score = max(0, ari_score)

            random.shuffle(sentences)
            
            sample_text_parts = []
            current_sample_words = 0
            
            for sentence in sentences:
                s_len = len(sentence.split())
                
                if current_sample_words + s_len < 75:
                    sample_text_parts.append(sentence)
                    current_sample_words += s_len
                
                if current_sample_words >= 15:
                    break
            
            final_sample = ". ".join(sample_text_parts) + "."

            self.app.push_screen(
                CalibrationScreen(final_sample),
                lambda wpm: self.analyze_file(word_count, ari_score, wpm)
            )

        except Exception as e:
            self.notify(f"Error processing file: {e}", severity="error")
            results_widget.update(f"Error: {e}")

    def analyze_file(self, total_words: int, ari: float, wpm: float) -> None:
        """
        Called after calibration completes.
        """
        if not wpm or wpm <= 0:
            self.query_one("#analysis-results", Static).update("Analysis Cancelled.")
            return

        est_minutes = total_words / wpm
        
        grade_level = math.ceil(ari)
        if grade_level > 14:
            grade_str = "College"
        elif grade_level > 12:
            grade_str = "High School"
        elif grade_level < 1:
            grade_str = "Kindergarten"
        else:
            grade_str = f"Grade {grade_level}"

        report = (
            f"## Analysis Complete\n\n"
            f"**Total Words:** {total_words:,}\n"
            f"**Readability (ARI):** {ari:.1f} ({grade_str})\n"
            f"**Your Speed:** {wpm:.0f} WPM\n"
            f"**Time to Finish:** {est_minutes:.1f} minutes"
        )
        
        self.query_one("#analysis-results", Static).update(report)


class ReadingPredictor(Container):
    """
    Wrapper container to be used as the Tab content.
    """
    def compose(self) -> ComposeResult:
        yield FileOperator()