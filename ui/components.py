from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

from ui.colors import (
    PRIMARY,
    PRIMARY_DARK,
    CARD,
    TEXT,
    TEXT_SECONDARY,
    SUCCESS,
    DANGER,
    BORDER
)

from ui.styles import rounded_background


class PrimaryButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.color = TEXT

        self.font_size = dp(16)

        self.bold = True

        rounded_background(
            self,
            PRIMARY,
            radius=14
        )

        self.bind(
            state=self.update_state
        )

    def update_state(self, instance, value):

        if value == "down":

            self.canvas.before.clear()

            rounded_background(
                self,
                PRIMARY_DARK,
                radius=14
            )

        else:

            self.canvas.before.clear()

            rounded_background(
                self,
                PRIMARY,
                radius=14
            )


class SecondaryButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.color = TEXT_SECONDARY

        self.font_size = dp(15)

        rounded_background(
            self,
            CARD,
            radius=14,
            border_color=BORDER
        )


class TitleLabel(Label):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.color = TEXT

        self.font_size = dp(28)

        self.bold = True

        self.halign = "left"

        self.valign = "middle"

        self.text_size = (
            self.width,
            None
        )

        self.bind(
            width=self.update_text_size
        )

    def update_text_size(
        self,
        instance,
        value
    ):

        self.text_size = (
            value,
            None
        )


class SubtitleLabel(Label):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.color = TEXT_SECONDARY

        self.font_size = dp(15)

        self.halign = "left"

        self.valign = "middle"

        self.text_size = (
            self.width,
            None
        )

        self.bind(
            width=self.update_text_size
        )

    def update_text_size(
        self,
        instance,
        value
    ):

        self.text_size = (
            value,
            None
        )


class StatCard(BoxLayout):

    def __init__(
        self,
        title="",
        value="",
        **kwargs
    ):

        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.padding = [
            dp(16),
            dp(12)
        ]

        self.spacing = dp(4)

        self.size_hint_y = None

        self.height = dp(100)

        rounded_background(
            self,
            CARD,
            radius=16,
            border_color=BORDER
        )

        value_label = Label(
            text=str(value),
            color=TEXT,
            font_size=dp(26),
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign="left"
        )

        title_label = Label(
            text=title,
            color=TEXT_SECONDARY,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(25),
            halign="left"
        )

        self.add_widget(
            value_label
        )

        self.add_widget(
            title_label
        )

        self.value_label = value_label