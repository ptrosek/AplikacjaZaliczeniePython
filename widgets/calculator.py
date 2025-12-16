from decimal import Decimal
from textual import events, on
from textual.app import ComposeResult
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import var
from textual.widgets import Button, Digits, Log

class Calculator(Container):
    """A working 'desktop' calculator widget."""

    numbers = var("0")
    show_ac = var(True)
    left = var(Decimal("0"))
    right = var(Decimal("0"))
    value = var("")
    operator = var("plus")
    
    NAME_MAP = {
        "asterisk": "multiply",
        "slash": "divide",
        "underscore": "plus-minus",
        "full_stop": "point",
        "plus_minus_sign": "plus-minus",
        "percent_sign": "percent",
        "equals_sign": "equals",
        "minus": "minus",
        "plus": "plus",
        "c": "clear",      # Mapped 'c' key to our new single button
    }

    # Watchers
    # Created using reactive var feature of Textual https://textual.textualize.io/guide/reactivity/ 
    # These methods are called automatically when the variable changes.
    def watch_numbers(self, value: str) -> None:
        try:
            self.query_one("#numbers", Digits).update(value)
        except NoMatches:
            pass

    def compute_show_ac(self) -> bool:
        return self.value in ("", "0") and self.numbers == "0"

    def watch_show_ac(self, show_ac: bool) -> None:
        """Update the label of the clear button instead of swapping buttons."""
        try:
            # FIX: Just change the text label. 
            # If show_ac is True, label is AC. If False, label is C.
            self.query_one("#clear", Button).label = "AC" if show_ac else "C"
        except NoMatches:
            pass

    def compose(self) -> ComposeResult:
        with Container(id="calculator-grid"):
            yield Log(id="left_number", max_lines=10, highlight=True, auto_scroll=True)
            yield Digits(id="numbers")
            yield Button("AC", id="clear", variant="primary", classes="calc-button") 
            yield Button("+/-", id="plus-minus", variant="primary", classes="calc-button")
            yield Button("%", id="percent", variant="primary", classes="calc-button")
            yield Button("÷", id="divide", classes="operation-button calc-button")
            yield Button("7", id="number-7", classes="number calc-button")
            yield Button("8", id="number-8", classes="number calc-button")
            yield Button("9", id="number-9", classes="number calc-button")
            yield Button("×", id="multiply", classes="operation-button calc-button")
            yield Button("4", id="number-4", classes="number calc-button")
            yield Button("5", id="number-5", classes="number calc-button")
            yield Button("6", id="number-6", classes="number calc-button")
            yield Button("-", id="minus", classes="operation-button calc-button")
            yield Button("1", id="number-1", classes="number calc-button")
            yield Button("2", id="number-2", classes="number calc-button")
            yield Button("3", id="number-3", classes="number calc-button")
            yield Button("+", id="plus", classes="operation-button calc-button")
            yield Button("0", id="number-0", classes="number calc-button")
            yield Button(".", id="point", classes="calc-button")
            yield Button("=", id="equals", classes="operation-button calc-button")

    def on_mount(self) -> None:
        self.query_one("#left_number", Log).write("Calculator Ready\n")
        self.query_one("#numbers", Digits).update(self.numbers)
        # Initialize the label
        self.watch_show_ac(self.show_ac)

    def on_key(self, event: events.Key) -> None:
        def press(button_id: str) -> None:
            try:
                self.query_one(f"#{button_id}", Button).press()
            except NoMatches:
                pass

        key = event.key
        if key.isdecimal():
            press(f"number-{key}")
        elif key == "c":
            press("clear") # Press the single clear button
        else:
            button_id = self.NAME_MAP.get(key)
            if button_id is not None:
                press(button_id)

    @on(Button.Pressed, ".number")
    def number_pressed(self, event: Button.Pressed) -> None:
        assert event.button.id is not None
        number = event.button.id.partition("-")[-1]
        self.numbers = self.value = self.value.lstrip("0") + number

    @on(Button.Pressed, "#plus-minus")
    def plus_minus_pressed(self) -> None:
        self.numbers = self.value = str(Decimal(self.value or "0") * -1)

    @on(Button.Pressed, "#percent")
    def percent_pressed(self) -> None:
        self.numbers = self.value = str(Decimal(self.value or "0") / Decimal(100))

    @on(Button.Pressed, "#point")
    def pressed_point(self) -> None:
        if "." not in self.value:
            self.numbers = self.value = (self.value or "0") + "."

    # FIX: Combined logic for the single button
    @on(Button.Pressed, "#clear")
    def pressed_clear(self) -> None:
        """Pressed AC or C"""
        if self.show_ac:
            # AC Behavior
            self.value = ""
            self.left = self.right = Decimal(0)
            self.operator = "plus"
            self.numbers = "0"
            self.app.clear_history()
            self.query_one("#left_number", Log).clear()
            self.query_one("#left_number", Log).write("Calculator Reset\n")
        else:
            # C Behavior
            self.value = ""
            self.numbers = "0"

    def _do_math(self) -> None:
        """Does the math: LEFT OPERATOR RIGHT"""
        try:
            # We capture the specific values before modifying them
            current_left = self.left
            current_right = self.right
            current_op = self.operator
            print(f"CALCulating: {current_left} {current_op} {current_right}")
            if self.operator == "plus":
                self.left += self.right
            elif self.operator == "minus":
                self.left -= self.right
            elif self.operator == "divide":
                self.left /= self.right
            elif self.operator == "multiply":
                self.left *= self.right
            
            self.numbers = str(self.left)

            self.app.add_calculation(current_left, current_op, current_right, self.left)
            self.query_one("#left_number", Log).write(f"{self.app.calc_history[-1][-2]} = {self.app.calc_history[-1][-1]}\n")

            self.value = ""
        except Exception:
            self.numbers = "Error"

    @on(Button.Pressed, "#plus,#minus,#divide,#multiply")
    def pressed_op(self, event: Button.Pressed) -> None:
        if not self.value:
            self.operator = event.button.id  # Just change the operator
            print(f"CALC Operator changed to: {self.operator}")
            return
        self.right = Decimal(self.value or "0")
        self._do_math()
        assert event.button.id is not None
        self.operator = event.button.id

    @on(Button.Pressed, "#equals")
    def pressed_equals(self) -> None:
        if self.value:
            self.right = Decimal(self.value)
        self._do_math()
