from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable


class CalculatorHistory(Container):
    def compose(self) -> ComposeResult:
        # Create a table to hold the history
        yield DataTable()

    def on_mount(self) -> None:
        """Setup the table columns and load initial data."""
        table = self.query_one(DataTable)
        table.add_columns("Time", "Expression", "Result")
        
        # Load existing history from the App (if any exists)
        # We access the main app using 'self.app'
        if hasattr(self.app, "calc_history"):
            for row in self.app.calc_history:
                table.add_row(*row)

    def add_line(self, row_data):
        """Helper to add a line dynamically."""
        table = self.query_one(DataTable)
        table.add_row(*row_data)
        # Scroll to the bottom so the newest is visible
        table.scroll_end(animate=False)