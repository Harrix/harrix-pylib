import logging
from logging.handlers import RotatingFileHandler
from enum import Enum


class Logger(object):
    class Style(str, Enum):
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
                logging.DEBUG: Logger.text_cyan(self.__format),
                logging.INFO: Logger.text_normal(self.__format),
                logging.WARNING: Logger.text_yellow(self.__format),
                logging.ERROR: Logger.text_red(self.__format),
                logging.CRITICAL: Logger.text_red_background(self.__format),
            }

        def format(self, record):
            formatter = logging.Formatter(self.FORMATS.get(record.levelno))
            return formatter.format(record)

    log_format_time = "[%(levelname)s] %(asctime)s - %(message)s"
    log_format_no_time = "[%(levelname)s] %(message)s"

    def __new__(self):
        if not hasattr(self, "instance"):
            self.instance = super(Logger, self).__new__(self)
        return self.instance

    def __init__(self):
        self.is_log_console = True
        self.is_log_file = False
        self._is_show_time_in_console = False

        self.__logger_console = logging.getLogger("dev.harrix.logger.console")
        self.__logger_console.setLevel(logging.DEBUG)

        self.__handler_console = logging.StreamHandler()
        self.__handler_console.setFormatter(
            Logger.StyleFormatter(Logger.log_format_no_time)
        )
        self.__handler_console.setLevel(logging.DEBUG)
        self.__logger_console.addHandler(self.__handler_console)

        self.__logger_file = logging.getLogger("dev.harrix.logger.file")
        self.__logger_file.setLevel(logging.DEBUG)
        self.__handler_file = RotatingFileHandler(
            "harrix.log", maxBytes=104857600, backupCount=100
        )
        self.__handler_file.setFormatter(Logger.StyleFormatter(Logger.log_format_time))
        self.__handler_file.setLevel(logging.DEBUG)
        self.__logger_file.addHandler(self.__handler_file)

        self.__logger_file_error = logging.getLogger("dev.harrix.logger.file.error")
        self.__logger_file_error.setLevel(logging.ERROR)
        self.__handler_file_error = RotatingFileHandler(
            "harrix_error.log", maxBytes=104857600, backupCount=100
        )
        self.__handler_file_error.setFormatter(
            Logger.StyleFormatter(Logger.log_format_time)
        )
        self.__handler_file_error.setLevel(logging.ERROR)
        self.__logger_file_error.addHandler(self.__handler_file_error)

    @property
    def is_show_time_in_console(self):
        return self._is_show_time_in_console

    @is_show_time_in_console.setter
    def is_show_time_in_console(self, value):
        self._is_show_time_in_console = value
        if self._is_show_time_in_console:
            self.__handler_console.setFormatter(
                Logger.StyleFormatter(Logger.log_format_time)
            )
        else:
            self.__handler_console.setFormatter(
                Logger.StyleFormatter(Logger.log_format_no_time)
            )

    @is_show_time_in_console.deleter
    def is_show_time_in_console(self):
        del self._is_show_time_in_console

    def debug(self, msg):
        if self.is_log_console:
            self.__logger_console.debug(msg)
        if self.is_log_file:
            self.__logger_file.debug(msg)
            self.__logger_file_error.debug(msg)

    def info(self, msg):
        if self.is_log_console:
            self.__logger_console.info(msg)
        if self.is_log_file:
            self.__logger_file.info(msg)
            self.__logger_file_error.info(msg)

    def warning(self, msg):
        if self.is_log_console:
            self.__logger_console.warning(msg)
        if self.is_log_file:
            self.__logger_file.warning(msg)
            self.__logger_file_error.warning(msg)

    def error(self, msg):
        if self.is_log_console:
            self.__logger_console.error(msg)
        if self.is_log_file:
            self.__logger_file.error(msg)
            self.__logger_file_error.error(msg)

    def critical(self, msg):
        if self.is_log_console:
            self.__logger_console.critical(msg)
        if self.is_log_file:
            self.__logger_file.critical(msg)
            self.__logger_file_error.critical(msg)

    def exception(self, msg):
        if self.is_log_console:
            self.__logger_console.exception(msg)
        if self.is_log_file:
            self.__logger_file.exception(msg)
            self.__logger_file_error.exception(msg)

    @classmethod
    def text_normal(self, text):
        return Logger.Style.NORMAL + text + Logger.Style.RESET

    @classmethod
    def text_red(self, text):
        return Logger.Style.RED + text + Logger.Style.RESET

    @classmethod
    def text_green(self, text):
        return Logger.Style.GREEN + text + Logger.Style.RESET

    @classmethod
    def text_yellow(self, text):
        return Logger.Style.YELLOW + text + Logger.Style.RESET

    @classmethod
    def text_blue(self, text):
        return Logger.Style.BLUE + text + Logger.Style.RESET

    @classmethod
    def text_magenta(self, text):
        return Logger.Style.MAGENTA + text + Logger.Style.RESET

    @classmethod
    def text_cyan(self, text):
        return Logger.Style.CYAN + text + Logger.Style.RESET

    @classmethod
    def text_red_background(self, text):
        return Logger.Style.RED_BACKGROUND + text + Logger.Style.RESET

    @classmethod
    def text_green_background(self, text):
        return Logger.Style.GREEN_BACKGROUND + text + Logger.Style.RESET

    @classmethod
    def text_yellow_background(self, text):
        return Logger.Style.YELLOW_BACKGROUND + text + Logger.Style.RESET

    @classmethod
    def text_blue_background(self, text):
        return Logger.Style.BLUE_BACKGROUND + text + Logger.Style.RESET

    @classmethod
    def text_magenta_background(self, text):
        return Logger.Style.MAGENTA_BACKGROUND + text + Logger.Style.RESET

    @classmethod
    def text_cyan_background(self, text):
        return Logger.Style.CYAN_BACKGROUND + text + Logger.Style.RESET

    @classmethod
    def text_italic(self, text):
        return Logger.Style.ITALIC + text + Logger.Style.RESET

    @classmethod
    def text_underline(self, text):
        return Logger.Style.UNDERLINE + text + Logger.Style.RESET

    @classmethod
    def text_crossed_out(self, text):
        return Logger.Style.CROSSED_OUT + text + Logger.Style.RESET


log = Logger()

if __name__ == "__main__":
    # log.is_show_time_in_console = False
    log.error("Test me 1")
    log.info("Test {} 2".format(Logger.text_normal("me")))
    log.info("Test {} 2".format(Logger.text_yellow("me")))
    log.info("Test {} 2".format(Logger.text_green("me")))
    log.info("Test {} 2".format(Logger.text_red("me")))
    log.info("Test {} 2".format(Logger.text_red_background("me")))
    log.info("Test me 3")

    print("\x1b[0m Normal \x1b[0m")
    print("\x1b[31m Red foreground\x1b[0m")
    print("\x1b[32m Green foreground\x1b[0m")
    print("\x1b[33m Yellow foreground\x1b[0m")
    print("\x1b[34m Blue foreground\x1b[0m")
    print("\x1b[35m Magenta foreground\x1b[0m")
    print("\x1b[36m Cyan foreground\x1b[0m")
    print("\x1b[41m Red background\x1b[0m")
    print("\x1b[42m Green background\x1b[0m")
    print("\x1b[43m Yellow background\x1b[0m")
    print("\x1b[44m Blue background\x1b[0m")
    print("\x1b[45m Magenta background\x1b[0m")
    print("\x1b[46m Cyan background\x1b[0m")
    print("\x1b[3m Italic \x1b[0m")
    print("\x1b[4m Underline \x1b[0m")
    print("\x1b[9m Crossed-out \x1b[0m")
