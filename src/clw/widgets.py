"""widgets"""
import logging

from textual.app import App
from textual.widgets import Log


#log = logging.getLogger(__name__)


LOG_FORMAT = "{asctime} {levelname:<8s} {name:<16} {message}"


class LogHandlerWidget(Log):
    """wrap the log widget to install the handler"""
    def __init__(self, app:App, level:int, **kwargs):
        super().__init__(**kwargs)
        # create handler
        handler = TextualLogHandler(app)

        # install handler
        logging.basicConfig(handlers=[handler], format=LOG_FORMAT, style='{')
        logging.getLogger("clw").setLevel(level) # FIXME derive from module name


class TextualLogHandler(logging.Handler):
    """Route logs to internal log panel"""
    def __init__(self, app: App) -> None:
        super().__init__()
        self.app = app


    def emit(self, record: logging.LogRecord) -> None:
        log_widget = self.app.query_one(LogHandlerWidget)
        log_entry = self.format(record)
        log_widget.write_line(log_entry)
