import logging
from logging.handlers import RotatingFileHandler
from enum import Enum


class Log(object):
    log_format_time = "[%(levelname)s] %(asctime)s - %(message)s"  # TODO
    log_format_no_time = "[%(levelname)s] %(message)s"  # TODO

    class Style(str, Enum):
        DEBUG = "\x1b[36m"
        INFO = "\x1b[0m"
        WARNING = "\x1b[33m"
        ERROR = "\x1b[31;20m"
        CRITICAL = "\x1b[41m"
        NORMAL = "\x1b[0m"
        RED = "\x1b[31;20m"
        GREEN = "\x1b[32m"
        YELLOW = "\x1b[33m"
        BLUE = "\x1b[34m"
        MAGENTA = "\x1b[35m"
        CYAN = "\x1b[36m"
        RED_BACKGROUND = "\x1b[41m"
        GREEN_BACKGROUND = "\x1b[42m"
        YELLOW_BACKGROUND = "\x1b[43m"
        BLUE_BACKGROUND = "\x1b[44m"
        MAGENTA_BACKGROUND = "\x1b[45m"
        CYAN_BACKGROUND = "\x1b[46m"
        ITALIC = "\x1b[3m"
        UNDERLINE = "\x1b[4m"
        CROSSED_OUT = "\x1b[9m"
        RESET = "\x1b[0m"

    class StyleFormatter(logging.Formatter):
        def __init__(self, format):
            super().__init__()
            self.__format = format

            self.FORMATS = {
                logging.DEBUG: Log.Style.DEBUG + self.__format + Log.Style.RESET,
                logging.INFO: Log.Style.INFO + self.__format + Log.Style.RESET,
                logging.WARNING: Log.Style.WARNING + self.__format + Log.Style.RESET,
                logging.ERROR: Log.Style.ERROR + self.__format + Log.Style.RESET,
                logging.CRITICAL: Log.Style.CRITICAL + self.__format + Log.Style.RESET,
            }

        def format(self, record):
            formatter = logging.Formatter(self.FORMATS.get(record.levelno))
            return formatter.format(record)

    def __new__(self):
        if not hasattr(self, "instance"):
            self.instance = super(Log, self).__new__(self)
        return self.instance

    def __init__(self):
        self.is_log_console = True
        self.is_log_file = False
        self._is_show_time_in_console = False
        self.is_color_console = True

        self.__handler_console = logging.StreamHandler()
        self.__handler_console.setFormatter(Log.StyleFormatter(Log.log_format_no_time))
        self.__handler_console.setLevel(logging.DEBUG)
        self.__log_console = logging.getLogger("dev.harrix.log.console")
        self.__log_console.setLevel(logging.DEBUG)
        self.__log_console.addHandler(self.__handler_console)

        self.__handler_file = RotatingFileHandler(
            "harrix.log", maxBytes=104857600, backupCount=100
        )
        self.__handler_file.setFormatter(logging.Formatter(Log.log_format_time))
        self.__handler_file.setLevel(logging.DEBUG)
        self.__log_file = logging.getLogger("dev.harrix.log.file")
        self.__log_file.setLevel(logging.DEBUG)
        self.__log_file.addHandler(self.__handler_file)

        self.__handler_file_error = RotatingFileHandler(
            "harrix_error.log", maxBytes=104857600, backupCount=100
        )
        self.__handler_file_error.setFormatter(logging.Formatter(Log.log_format_time))
        self.__handler_file_error.setLevel(logging.ERROR)
        self.__log_file_error = logging.getLogger("dev.harrix.log.file.error")
        self.__log_file_error.setLevel(logging.ERROR)
        self.__log_file_error.addHandler(self.__handler_file_error)

    @property
    def is_show_time_in_console(self):
        return self._is_show_time_in_console

    @is_show_time_in_console.setter
    def is_show_time_in_console(self, value):
        self._is_show_time_in_console = value
        if self._is_show_time_in_console:
            self.__handler_console.setFormatter(Log.StyleFormatter(Log.log_format_time))
        else:
            self.__handler_console.setFormatter(
                Log.StyleFormatter(Log.log_format_no_time)
            )

    @is_show_time_in_console.deleter
    def is_show_time_in_console(self):
        del self._is_show_time_in_console

    def __write_log(self, method, msg):
        if self.is_log_console:
            getattr(self.__log_console, method)(msg)
        if self.is_log_file:
            getattr(self.__log_file, method)(msg)
            getattr(self.__log_file_error, method)(msg)

    def debug(self, msg):
        self.__write_log("debug", msg)

    def info(self, msg):
        self.__write_log("info", msg)

    def warning(self, msg):
        self.__write_log("warning", msg)

    def error(self, msg):
        self.__write_log("error", msg)

    def critical(self, msg):
        self.__write_log("critical", msg)

    def __text_style(self, style: Style, text):
        return style + text + Log.Style.RESET

    def text_debug(self, text):
        return self.__text_style(Log.Style.DEBUG, text)

    def text_info(self, text):
        return self.__text_style(Log.Style.DEBUG, text)

    def text_warning(self, text):
        return self.__text_style(Log.Style.WARNING, text)

    def text_error(self, text):
        return self.__text_style(Log.Style.ERROR, text)

    def text_critical(self, text):
        return self.__text_style(Log.Style.CRITICAL, text)

    def text_normal(self, text):
        return self.__text_style(Log.Style.NORMAL, text)

    def text_red(self, text):
        return self.__text_style(Log.Style.RED, text)

    def text_green(self, text):
        return self.__text_style(Log.Style.GREEN, text)

    def text_yellow(self, text):
        return self.__text_style(Log.Style.YELLOW, text)

    def text_blue(self, text):
        return self.__text_style(Log.Style.BLUE, text)

    def text_magenta(self, text):
        return self.__text_style(Log.Style.MAGENTA, text)

    def text_cyan(self, text):
        return self.__text_style(Log.Style.CYAN, text)

    def text_red_background(self, text):
        return self.__text_style(Log.Style.RED_BACKGROUND, text)

    def text_green_background(self, text):
        return self.__text_style(Log.Style.GREEN_BACKGROUND, text)

    def text_yellow_background(self, text):
        return self.__text_style(Log.Style.YELLOW_BACKGROUND, text)

    def text_blue_background(self, text):
        return self.__text_style(Log.Style.BLUE_BACKGROUND, text)

    def text_magenta_background(self, text):
        return self.__text_style(Log.Style.MAGENTA_BACKGROUND, text)

    def text_cyan_background(self, text):
        return self.__text_style(Log.Style.CYAN_BACKGROUND, text)

    def text_italic(self, text):
        return self.__text_style(Log.Style.ITALIC, text)

    def text_underline(self, text):
        return self.__text_style(Log.Style.UNDERLINE, text)

    def text_crossed_out(self, text):
        return self.__text_style(Log.Style.CROSSED_OUT, text)


log = Log()

if __name__ == "__main__":
    # log.is_show_time_in_console = False
    log.is_log_file = True
    log.info("Test me 1")
    log.debug("Test {} 2".format(log.text_normal("me")))
    log.warning("Test {} 2".format(log.text_yellow("me")))
    log.debug("Test {} 2".format(log.text_green("me")))
    log.critical("Test {} 2".format(log.text_red("me")))
    log.info("Test {} 2".format(log.text_red_background("me")))
