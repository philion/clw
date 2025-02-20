#!.venv/bin/python
"""
Experiments with dawn, sunset and weather
"""

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Static

# CONSTANTS
TIMEOUT = 2 #seconds
DATE_FORMAT = "%a %b %d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%a %b %d %H:%M"
EMOJI = {
    "dawn": "🌄",
    "sunrise": "🌅",
    "noon": "🌞",
    "sunset": "🌇",
    "dusk": "🌃",
}


class HorizontalLayoutExample(App):
    CSS = """
        Screen {
            layout: horizontal;
        }

        .box {
            height: 100%;
            width: 1fr;
            border: solid green;
        }
    """

    #def on_click(self) -> None:
    #    self.exit()

    def on_key(self, _: events.Key) -> None:
        self.exit()

    def compose(self) -> ComposeResult:
        yield Static("01:00", classes="box")
        yield Static("02:00", classes="box")
        yield Static("03:00", classes="box")
        yield Static("04:00", classes="box")
        yield Static("05:00", classes="box")
        yield Static("06:00", classes="box")
        yield Static("07:00", classes="box")
        yield Static("08:00", classes="box")
        yield Static("09:00", classes="box")
        yield Static("10:00", classes="box")
        yield Static("11:00", classes="box")
        yield Static("12:00", classes="box")


def try_image():
    # load img
    filename = "png/alert-avalanche-danger.png"
    #img = Image.open(filename)

    #fp = io.BytesIO()
    #imgcat(img, filename=filename, fp=fp)
    #sys.stdout.buffer.write(fp.getvalue())
    #imgcat(img, filename=filename)

    #image = AutoImage(img)
    #image.draw()


def runapp():
    app = HorizontalLayoutExample()
    app.run()

if __name__ == "__main__":
    runapp()
    #cli()
    #try_image()