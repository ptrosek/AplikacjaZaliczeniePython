from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane

from widgets.calculator import Calculator
from widgets.placeholders import Timer, ReadingPredictor, CalculatorHistory, OptionalFunction2

import datetime

class MultifunctionApp(App):
    """A multifunctional terminal application."""

    CSS_PATH = "tcss/main.tcss"
    BINDINGS = [("q", "quit", "Quit")]

    calc_history = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with TabbedContent(initial="calculator"):
            with TabPane("Kalkulator", id="calculator"):
                yield Calculator()

            with TabPane("Historia Kalkulatora", id="history"):
                yield CalculatorHistory(id="history_widget")
            
            with TabPane("Stoper/Minutnik", id="timer"):
                yield Timer()
                
            with TabPane("Przewidywanie Czasu", id="reader"):
                yield ReadingPredictor()
                
                
            with TabPane("Opcja 2", id="opt2"):
                yield OptionalFunction2()

        yield Footer()
    def add_calculation(self, left, operator, right, result):
        """Receives data from calculator, saves it, and updates the view."""
        
        # Create a timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Map operator words to symbols
        op_map = {
            "plus": "+", "minus": "-", "multiply": "×", "divide": "÷", 
            "plus-minus": "±", "percent": "%"
        }
        op_symbol = op_map.get(operator, operator)
        
        # Format the expression string (e.g., "5 + 5")
        expression = f"{left} {op_symbol} {right}"
        
        # Create the row data
        row_data = (timestamp, expression, str(result))
        
        # A. Save to memory variable
        self.calc_history.append(row_data)
        
        # B. Try to update the widget immediately if it exists
        try:
            self.query_one("#history_widget", CalculatorHistory).add_line(row_data)
        except Exception:
            pass

if __name__ == "__main__":
    app = MultifunctionApp()
    app.run()