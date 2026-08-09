import math
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


Window.clearcolor = (0.97, 0.97, 0.98, 1)


class Calculator(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(6),
            **kwargs
        )

        self.expression = ""
        self.just_calculated = False
        self.scientific_open = False
        self.angle_mode = "DEG"

        # Top menu button
        top = BoxLayout(
            size_hint_y=None,
            height=dp(45)
        )

        top.add_widget(Label())

        self.menu = Button(
            text="☰",
            font_size=dp(23),
            size_hint_x=None,
            width=dp(55),
            background_normal="",
            background_color=(0.90, 0.90, 0.92, 1)
        )

        self.menu.bind(on_release=self.toggle_scientific)
        top.add_widget(self.menu)

        self.add_widget(top)

        # Expression
        self.expression_label = Label(
            text="",
            font_size=dp(21),
            halign="right",
            valign="middle",
            size_hint_y=None,
            height=dp(42),
            color=(0.45, 0.45, 0.45, 1)
        )

        self.expression_label.bind(
            size=lambda obj, size:
            setattr(obj, "text_size", size)
        )

        self.add_widget(self.expression_label)

        # Automatic answer
        self.answer_label = Label(
            text="",
            font_size=dp(38),
            halign="right",
            valign="middle",
            size_hint_y=None,
            height=dp(65),
            color=(0, 0, 0, 1)
        )

        self.answer_label.bind(
            size=lambda obj, size:
            setattr(obj, "text_size", size)
        )

        self.add_widget(self.answer_label)

        # Scientific buttons
        self.scientific_grid = GridLayout(
            cols=4,
            spacing=dp(5),
            size_hint_y=None,
            height=0
        )

        self.add_widget(self.scientific_grid)

        self.create_scientific_buttons()

        # Normal buttons
        self.normal_grid = GridLayout(
            cols=4,
            spacing=dp(7)
        )

        self.add_widget(self.normal_grid)

        self.create_normal_buttons()

    # -------------------------------------------------
    # BUTTON
    # -------------------------------------------------

    def button(self, text, function, color=(1, 1, 1, 1), size=20):

        b = Button(
            text=text,
            font_size=dp(size),
            background_normal="",
            background_color=color,
            color=(0, 0, 0, 1)
        )

        b.bind(on_release=function)

        return b

    # -------------------------------------------------
    # SCIENTIFIC
    # -------------------------------------------------

    def create_scientific_buttons(self):

        buttons = [
            ("sin", lambda x: self.trig("sin")),
            ("cos", lambda x: self.trig("cos")),
            ("tan", lambda x: self.trig("tan")),
            ("π", lambda x: self.add("π")),

            ("√", self.sqrt),
            ("x²", self.square),
            ("xʸ", self.power),
            ("³√", self.cube_root),

            ("1/x", self.reciprocal),
            ("log", lambda x: self.log("log")),
            ("ln", lambda x: self.log("ln")),
            ("(", lambda x: self.add("(")),

            (")", lambda x: self.add(")")),
            ("!", self.factorial),
            ("±", self.plus_minus),
            ("DEG", self.change_angle)
        ]

        for text, function in buttons:

            self.scientific_grid.add_widget(
                self.button(
                    text,
                    function,
                    (0.90, 0.90, 0.92, 1),
                    15
                )
            )

    # -------------------------------------------------
    # NORMAL
    # -------------------------------------------------

    def create_normal_buttons(self):

        gray = (0.90, 0.90, 0.92, 1)
        white = (1, 1, 1, 1)
        orange = (1, 0.475, 0, 1)

        buttons = [

            ("AC", self.clear, gray),
            ("%", self.percent, gray),
            ("⌫", self.backspace, gray),
            ("÷", lambda x: self.operator("÷"), gray),

            ("7", lambda x: self.add("7"), white),
            ("8", lambda x: self.add("8"), white),
            ("9", lambda x: self.add("9"), white),
            ("×", lambda x: self.operator("×"), gray),

            ("4", lambda x: self.add("4"), white),
            ("5", lambda x: self.add("5"), white),
            ("6", lambda x: self.add("6"), white),
            ("-", lambda x: self.operator("-"), gray),

            ("1", lambda x: self.add("1"), white),
            ("2", lambda x: self.add("2"), white),
            ("3", lambda x: self.add("3"), white),
            ("+", lambda x: self.operator("+"), gray),

            ("00", lambda x: self.add("00"), white),
            ("0", lambda x: self.add("0"), white),
            (".", lambda x: self.add("."), white),
            ("=", self.calculate, orange)
        ]

        for text, function, color in buttons:

            self.normal_grid.add_widget(
                self.button(text, function, color, 20)
            )

    # -------------------------------------------------
    # SCIENTIFIC MENU
    # -------------------------------------------------

    def toggle_scientific(self, *_):

        self.scientific_open = not self.scientific_open

        if self.scientific_open:
            self.scientific_grid.height = dp(180)
            self.menu.text = "✕"
        else:
            self.scientific_grid.height = 0
            self.menu.text = "☰"

    # -------------------------------------------------
    # DISPLAY
    # -------------------------------------------------

    def refresh(self):

        self.expression_label.text = self.expression

        result = self.get_result()

        if result is None:
            self.answer_label.text = ""
        else:
            self.answer_label.text = self.format_number(result)

    # -------------------------------------------------
    # INPUT
    # -------------------------------------------------

    def add(self, value, *_):

        if self.just_calculated:

            self.expression = ""
            self.just_calculated = False

        self.expression += value

        self.refresh()

    def operator(self, op, *_):

        if self.just_calculated:
            self.just_calculated = False

        if not self.expression:
            return

        if self.expression[-1] in "+-×÷^":
            self.expression = self.expression[:-1]

        self.expression += op

        self.refresh()

    # -------------------------------------------------
    # CLEAR
    # -------------------------------------------------

    def clear(self, *_):

        self.expression = ""
        self.answer_label.text = ""
        self.expression_label.text = ""
        self.just_calculated = False

    def backspace(self, *_):

        if self.just_calculated:
            return

        self.expression = self.expression[:-1]
        self.refresh()

    # -------------------------------------------------
    # CALCULATION ENGINE
    # -------------------------------------------------

    def convert_expression(self, expression):

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("^", "**")
        expression = expression.replace("π", "pi")

        return expression

    def get_result(self):

        if not self.expression:
            return None

        if self.expression[-1] in "+-×÷^.":
            return None

        try:

            expression = self.convert_expression(
                self.expression
            )

            # Only calculator characters are allowed
            if not re.fullmatch(
                r"[0-9+\-*/().\s*pi]+",
                expression
            ):
                return None

            result = eval(
                expression,
                {"__builtins__": {}},
                {"pi": math.pi}
            )

            if isinstance(result, (int, float)):
                if math.isfinite(result):
                    return result

        except:
            return None

        return None

    def format_number(self, number):

        if isinstance(number, float):

            if number.is_integer():
                return str(int(number))

            return f"{number:.12g}"

        return str(number)

    def calculate(self, *_):

        result = self.get_result()

        if result is None:
            return

        self.expression = self.format_number(result)
        self.expression_label.text = self.expression
        self.answer_label.text = ""

        self.just_calculated = True

    # -------------------------------------------------
    # PERCENT
    # -------------------------------------------------

    def percent(self, *_):

        result = self.get_result()

        if result is None:
            return

        result = result / 100

        self.expression = self.format_number(result)

        self.expression_label.text = self.expression
        self.answer_label.text = ""

        self.just_calculated = True

    # -------------------------------------------------
    # SCIENTIFIC FUNCTIONS
    # -------------------------------------------------

    def scientific_result(self, function):

        result = self.get_result()

        if result is None:
            return

        try:

            result = function(result)

            self.expression = self.format_number(result)

            self.expression_label.text = self.expression
            self.answer_label.text = ""

            self.just_calculated = True

        except:
            self.answer_label.text = "Error"

    def sqrt(self, *_):

        self.scientific_result(math.sqrt)

    def square(self, *_):

        self.scientific_result(lambda x: x ** 2)

    def cube_root(self, *_):

        self.scientific_result(
            lambda x:
            math.copysign(
                abs(x) ** (1 / 3),
                x
            )
        )

    def reciprocal(self, *_):

        self.scientific_result(lambda x: 1 / x)

    def plus_minus(self, *_):

        self.scientific_result(lambda x: -x)

    def power(self, *_):

        self.operator("^")

    def factorial(self, *_):

        def calculate_factorial(x):

            if x < 0 or not float(x).is_integer():
                raise ValueError

            return math.factorial(int(x))

        self.scientific_result(calculate_factorial)

    def log(self, name):

        if name == "log":
            self.scientific_result(math.log10)
        else:
            self.scientific_result(math.log)

    # -------------------------------------------------
    # TRIGONOMETRY
    # -------------------------------------------------

    def trig(self, name):

        def calculate_trig(x):

            if self.angle_mode == "DEG":
                x = math.radians(x)

            if name == "sin":
                return math.sin(x)

            if name == "cos":
                return math.cos(x)

            return math.tan(x)

        self.scientific_result(calculate_trig)

    def change_angle(self, *_):

        if self.angle_mode == "DEG":
            self.angle_mode = "RAD"
        else:
            self.angle_mode = "DEG"

        # Last scientific button
        self.scientific_grid.children[0].text = self.angle_mode


class CalculatorApp(App):

    def build(self):

        self.title = "Scientific Calculator"

        return Calculator()


if __name__ == "__main__":
    CalculatorApp().run()
