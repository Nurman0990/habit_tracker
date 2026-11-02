from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line


def rounded_background(
    widget,
    color,
    radius=16,
    border_color=None,
    border_width=1
):
    """
    Creates a modern rounded background for a Kivy widget.
    """

    with widget.canvas.before:

        Color(*color)

        background = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[dp(radius)]
        )

        if border_color:

            Color(*border_color)

            border = Line(
                rounded_rectangle=(
                    widget.x,
                    widget.y,
                    widget.width,
                    widget.height,
                    dp(radius)
                ),
                width=border_width
            )

    def update_background(instance, value):

        background.pos = instance.pos
        background.size = instance.size

        if border_color:

            border.rounded_rectangle = (
                instance.x,
                instance.y,
                instance.width,
                instance.height,
                dp(radius)
            )

    widget.bind(
        pos=update_background,
        size=update_background
    )

    return background


def add_divider(widget, color):

    with widget.canvas.after:

        Color(*color)

        line = Line(
            points=[
                widget.x,
                widget.y,
                widget.right,
                widget.y
            ],
            width=1
        )

    def update(instance, value):

        line.points = [
            instance.x,
            instance.y,
            instance.right,
            instance.y
        ]

    widget.bind(
        pos=update,
        size=update
    )

    return line