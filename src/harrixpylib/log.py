"""
Colored logging class based on the standard python
[logging class](https://docs.python.org/3/library/logging.html).

The methods output logging messages to the console, the file `messages.log`,
and the file `errors.log` simultaneously. Output to a file or console can be disabled.

Messages are output to files without color.

## Usage example

```py
import harrixpylib as h

h.log.debug("Test message.")
```

```py
import harrixpylib as h

h.log.is_show_time_in_console = False
h.log.is_show_color_in_console = True
h.log.debug("Test message.")
h.log.info("Test message.")
h.log.warning("Test message.")
h.log.error("Test message.")
h.log.critical("Test message.")
```

![Colored text in the console without time](img/log_01.png)

```py
import harrixpylib as h

log.is_show_time_in_console = False
log.is_show_color_in_console = False
log.debug("Test message.")
log.info("Test message.")
log.warning("Test message.")
log.error("Test message.")
log.critical("Test message.")
```

![Text in the console without time and color](img/log_02.png)

```py
import harrixpylib as h

log.is_show_time_in_console = False
log.info("Message: {}. End of line".format(log.text_debug("x = 2")))
log.info("Message: {}. End of line".format(log.text_info("x = 2")))
log.info("Message: {}. End of line".format(log.text_warning("x = 2")))
log.info("Message: {}. End of line".format(log.text_error("x = 2")))
log.info("Message: {}. End of line".format(log.text_critical("x = 2")))
log.info("Message: {}. End of line".format(log.text_normal("x = 2")))
log.info("Message: {}. End of line".format(log.text_red("x = 2")))
log.info("Message: {}. End of line".format(log.text_green("x = 2")))
log.info("Message: {}. End of line".format(log.text_yellow("x = 2")))
log.info("Message: {}. End of line".format(log.text_blue("x = 2")))
log.info("Message: {}. End of line".format(log.text_magenta("x = 2")))
log.info("Message: {}. End of line".format(log.text_cyan("x = 2")))
log.info("Message: {}. End of line".format(log.text_red_background("x = 2")))
log.info("Message: {}. End of line".format(log.text_green_background("x = 2")))
log.info("Message: {}. End of line".format(log.text_yellow_background("x = 2")))
log.info("Message: {}. End of line".format(log.text_blue_background("x = 2")))
log.info("Message: {}. End of line".format(log.text_magenta_background("x = 2")))
log.info("Message: {}. End of line".format(log.text_cyan_background("x = 2")))
log.info("Message: {}. End of line".format(log.text_italic("x = 2")))
log.info("Message: {}. End of line".format(log.text_underline("x = 2")))
log.info("Message: {}. End of line".format(log.text_crossed_out("x = 2")))
```

![Info messages with formated text](img/log_03.png)

```py
import harrixpylib as h

log.is_show_time_in_console = False
log.error("Message: {}. End of line".format(log.text_debug("x = 2")))
log.error("Message: {}. End of line".format(log.text_info("x = 2")))
log.error("Message: {}. End of line".format(log.text_warning("x = 2")))
log.error("Message: {}. End of line".format(log.text_error("x = 2")))
log.error("Message: {}. End of line".format(log.text_critical("x = 2")))
log.error("Message: {}. End of line".format(log.text_normal("x = 2")))
log.error("Message: {}. End of line".format(log.text_red("x = 2")))
log.error("Message: {}. End of line".format(log.text_green("x = 2")))
log.error("Message: {}. End of line".format(log.text_yellow("x = 2")))
log.error("Message: {}. End of line".format(log.text_blue("x = 2")))
log.error("Message: {}. End of line".format(log.text_magenta("x = 2")))
log.error("Message: {}. End of line".format(log.text_cyan("x = 2")))
log.error("Message: {}. End of line".format(log.text_red_background("x = 2")))
log.error("Message: {}. End of line".format(log.text_green_background("x = 2")))
log.error("Message: {}. End of line".format(log.text_yellow_background("x = 2")))
log.error("Message: {}. End of line".format(log.text_blue_background("x = 2")))
log.error("Message: {}. End of line".format(log.text_magenta_background("x = 2")))
log.error("Message: {}. End of line".format(log.text_cyan_background("x = 2")))
log.error("Message: {}. End of line".format(log.text_italic("x = 2")))
log.error("Message: {}. End of line".format(log.text_underline("x = 2")))
log.error("Message: {}. End of line".format(log.text_crossed_out("x = 2")))
```

![Error messages with formated text](img/log_04.png)

```py
import harrixpylib as h

log.is_show_time_in_console = True
log.info(log.text_debug("x = 2"))
log.info(log.text_info("x = 2"))
log.info(log.text_warning("x = 2"))
log.info(log.text_error("x = 2"))
log.info(log.text_critical("x = 2"))
log.info(log.text_normal("x = 2"))
log.info(log.text_red("x = 2"))
log.info(log.text_green("x = 2"))
log.info(log.text_yellow("x = 2"))
log.info(log.text_blue("x = 2"))
log.info(log.text_magenta("x = 2"))
log.info(log.text_cyan("x = 2"))
log.info(log.text_red_background("x = 2"))
log.info(log.text_green_background("x = 2"))
log.info(log.text_yellow_background("x = 2"))
log.info(log.text_blue_background("x = 2"))
log.info(log.text_magenta_background("x = 2"))
log.info(log.text_cyan_background("x = 2"))
log.info(log.text_italic("x = 2"))
log.info(log.text_underline("x = 2"))
log.info(log.text_crossed_out("x = 2"))
```

![Info messages with formated text and time](img/log_05.png)

```py
import harrixpylib as h

h.log.is_log_file = True

log.info(log.text_debug("x = 2"))
log.info(log.text_info("x = 2"))
log.info(log.text_warning("x = 2"))
log.info(log.text_error("x = 2"))
log.info(log.text_critical("x = 2"))
log.info(log.text_normal("x = 2"))
log.info(log.text_red("x = 2"))
log.info(log.text_green("x = 2"))
log.info(log.text_yellow("x = 2"))
log.info(log.text_blue("x = 2"))
log.info(log.text_magenta("x = 2"))
log.info(log.text_cyan("x = 2"))
log.info(log.text_red_background("x = 2"))
log.info(log.text_green_background("x = 2"))
log.info(log.text_yellow_background("x = 2"))
log.info(log.text_blue_background("x = 2"))
log.info(log.text_magenta_background("x = 2"))
log.info(log.text_cyan_background("x = 2"))
log.info(log.text_italic("x = 2"))
log.info(log.text_underline("x = 2"))
log.info(log.text_crossed_out("x = 2"))
```

![Messages in file messages.log](img/log-file_01.png)

![Errors in file errors.log](img/log-file_02.png)
"""

import logging
from logging.handlers import RotatingFileHandler
from enum import Enum
import hashlib


class Log(object):
    """Colored logging."""

    __TEMP_STYLE = hashlib.md5("__TEMP_STYLE".encode()).hexdigest()
    __START_COLOR_SYMBOLS = "\x1b["
    __FILENAME_LOG = "messages.log"
    __FILENAME_ERROR_LOG = "errors.log"
    __REVERSE_DOMAIN = "dev.harrix"

    class _Format(str, Enum):
        TIME = "[%(levelname)s] %(asctime)s - %(message)s"
        NO_TIME = "[%(levelname)s] %(message)s"

    class _Style(str, Enum):
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

        @staticmethod
        def list():
            return list(map(lambda c: c.value, Log._Style))

    class _StyleFormatter(logging.Formatter):
        def __init__(self, format):
            super().__init__()
            self.__format = format

            self.FORMATS = {
                logging.DEBUG: Log._Style.DEBUG + self.__format + Log._Style.RESET,
                logging.INFO: Log._Style.INFO + self.__format + Log._Style.RESET,
                logging.WARNING: Log._Style.WARNING + self.__format + Log._Style.RESET,
                logging.ERROR: Log._Style.ERROR + self.__format + Log._Style.RESET,
                logging.CRITICAL: Log._Style.CRITICAL
                + self.__format
                + Log._Style.RESET,
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
        """If the parameter is `True`, the messages are displayed in the console.
        Defaults to `True`. Example:

        ```py
        import harrixpylib as h

        h.log.is_log_console = False
        h.log.error("Test message.")
        # The message will appear only in log files
        ```
        """

        self.is_log_file = False
        """If the parameter is `True`, the messages are displayed in log files.
        Defaults to `False`. Example:

        ```py
        import harrixpylib as h

        h.log.is_log_file = True
        h.log.error("Test message.")
        # The message will appear in log files and the console
        ```
        """
        self._is_show_time_in_console = False
        self._is_show_color_in_console = True
        self._filename_log = Log.__FILENAME_LOG
        self._filename_error_log = Log.__FILENAME_ERROR_LOG
        self._reverse_domain = Log.__REVERSE_DOMAIN

        self.__create_log_console()
        self.__create_log_file()
        self.__create_log_file_error()

    def __create_log_console(self):
        self.__handler_console = logging.StreamHandler()
        self.__handler_console.setFormatter(Log._StyleFormatter(Log._Format.NO_TIME))
        self.__handler_console.setLevel(logging.DEBUG)
        self.__log_console = logging.getLogger(f"{self._reverse_domain}.log.console")
        self.__log_console.setLevel(logging.DEBUG)
        self.__log_console.addHandler(self.__handler_console)

    def __create_log_file(self):
        self.__handler_file = RotatingFileHandler(
            self._filename_log, maxBytes=104857600, backupCount=100, encoding="utf-8"
        )
        self.__handler_file.setFormatter(logging.Formatter(Log._Format.TIME))
        self.__handler_file.setLevel(logging.DEBUG)
        self.__log_file = logging.getLogger(
            f"log.file.{self._filename_log}.{self._reverse_domain}"
        )
        self.__log_file.setLevel(logging.DEBUG)
        self.__log_file.addHandler(self.__handler_file)

    def __create_log_file_error(self):
        self.__handler_file_error = RotatingFileHandler(
            self._filename_error_log,
            maxBytes=104857600,
            backupCount=100,
            encoding="utf-8",
        )
        self.__handler_file_error.setFormatter(logging.Formatter(Log._Format.TIME))
        self.__handler_file_error.setLevel(logging.ERROR)
        self.__log_file_error = logging.getLogger(
            f"log.file.error.{self._filename_error_log}.{self._reverse_domain}"
        )
        self.__log_file_error.setLevel(logging.ERROR)
        self.__log_file_error.addHandler(self.__handler_file_error)

    @property
    def reverse_domain(self):
        """Reverse domain for
        [getLogger](https://docs.python.org/3/library/logging.html#logging.getLogger).
        This parameter can not be changed. Defaults to `dev.harrix`. Example:

        ```py
        import harrixpylib as h

        h.log.reverse_domain = "com.my-domain"
        h.log.debug("Test message.")
        ```
        """
        return self._reverse_domain

    @reverse_domain.setter
    def reverse_domain(self, value):
        self._reverse_domain = value
        self.__create_log_console()
        self.__create_log_file()
        self.__create_log_file_error()

    @reverse_domain.deleter
    def reverse_domain(self):
        del self._reverse_domain

    @property
    def filename_log(self):
        """Filename for log file. The variable `is_log_file` must be `True`.
        Defaults to `messages.log`. Example:

        ```py
        import harrixpylib as h

        h.log.is_log_file = True
        h.log.filename_log = "my-messages.log"
        h.log.debug("Test message.")
        ```
        """
        return self._filename_log

    @filename_log.setter
    def filename_log(self, value):
        self._filename_log = value
        self.__create_log_file()

    @filename_log.deleter
    def filename_log(self):
        del self._filename_log

    @property
    def filename_error_log(self):
        """Filename for log file. The variable `is_log_file` must be `True`.
        Defaults to `messages.log`. Example:

        ```py
        import harrixpylib as h

        h.log.is_log_file = True
        h.log.filename_error_log = "my-errors.log"
        h.log.error("Test message.")
        ```
        """
        return self._filename_error_log

    @filename_error_log.setter
    def filename_error_log(self, value):
        self._filename_error_log = value
        self.__create_log_file_error()

    @filename_error_log.deleter
    def filename_error_log(self):
        del self._filename_error_log

    @property
    def is_show_time_in_console(self):
        """If the parameter is `True`, then the time is displayed in the console.
        Defaults to `False`. Example:

        ```py
        import harrixpylib as h

        h.log.error("Test message.")
        # [ERROR] Test message.
        h.log.is_show_time_in_console = True
        h.log.error("Test message.")
        # [ERROR] 2022-04-03 21:56:49,570 - Test message.
        ```
        """
        return self._is_show_time_in_console

    @is_show_time_in_console.setter
    def is_show_time_in_console(self, value):
        self._is_show_time_in_console = value
        if self._is_show_time_in_console:
            if self._is_show_color_in_console:
                self.__handler_console.setFormatter(
                    Log._StyleFormatter(Log._Format.TIME)
                )
            else:
                self.__handler_console.setFormatter(logging.Formatter(Log._Format.TIME))
        else:
            if self._is_show_color_in_console:
                self.__handler_console.setFormatter(
                    Log._StyleFormatter(Log._Format.NO_TIME)
                )
            else:
                self.__handler_console.setFormatter(
                    logging.Formatter(Log._Format.NO_TIME)
                )

    @is_show_time_in_console.deleter
    def is_show_time_in_console(self):
        del self._is_show_time_in_console

    @property
    def is_show_color_in_console(self):
        """If the parameter is `True`, then the color is displayed in the console.
        Defaults to `True`. Example:

        ```py
        import harrixpylib as h

        h.log.is_show_color_in_console = False
        h.log.error("Test message.")
        ```
        """
        return self._is_show_color_in_console

    @is_show_color_in_console.setter
    def is_show_color_in_console(self, value):
        self._is_show_color_in_console = value
        if self._is_show_color_in_console:
            if self._is_show_time_in_console:
                self.__handler_console.setFormatter(
                    Log._StyleFormatter(Log._Format.TIME)
                )
            else:
                self.__handler_console.setFormatter(
                    Log._StyleFormatter(Log._Format.NO_TIME)
                )
        else:
            if self._is_show_time_in_console:
                self.__handler_console.setFormatter(logging.Formatter(Log._Format.TIME))
            else:
                self.__handler_console.setFormatter(
                    logging.Formatter(Log._Format.NO_TIME)
                )

    @is_show_color_in_console.deleter
    def is_show_color_in_console(self):
        del self._is_show_color_in_console

    def __write_log(self, method, text):
        text = str(text)
        if self.is_log_console:
            if Log.__TEMP_STYLE in text:
                text = text.replace(
                    Log.__TEMP_STYLE, getattr(Log._Style, method.upper())
                )
            getattr(self.__log_console, method)(text)
        if self.is_log_file:
            if Log.__START_COLOR_SYMBOLS in text:
                for symbol in Log._Style.list():
                    text = text.replace(symbol, "")
            getattr(self.__log_file, method)(text)
            getattr(self.__log_file_error, method)(text)

    def debug(self, text):
        """Method outputs a debug message to the console and log files.

        Args:
            text (str): Message for logging.

        Returns:
            None.

        Example:
        ```py
        import harrixpylib as h

        x = 2
        h.log.debug(f"x = {x}")
        ```
        """
        self.__write_log("debug", text)

    def info(self, text):
        """Method outputs a info message to the console and log files.

        Args:
            text (str): Message for logging.

        Returns:
            None.

        Example:
        ```py
        import harrixpylib as h

        x = 2
        h.log.info(f"x = {x}")
        ```
        """
        self.__write_log("info", text)

    def warning(self, text):
        """Method outputs a warning message to the console and log files.

        Args:
            text (str): Message for logging.

        Returns:
            None.

        Example:
        ```py
        import harrixpylib as h

        x = 2
        h.log.warning(f"x = {x}")
        ```
        """
        self.__write_log("warning", text)

    def error(self, text):
        """Method outputs a error message to the console and log files.

        Args:
            text (str): Message for logging.

        Returns:
            None.

        Example:
        ```py
        import harrixpylib as h

        x = 2
        h.log.error(f"x = {x}")
        ```
        """
        self.__write_log("error", text)

    def critical(self, text):
        """Method outputs a critical message to the console and log files.

        Args:
            text (str): Message for logging.

        Returns:
            None.

        Example:
        ```py
        import harrixpylib as h

        x = 2
        h.log.critical(f"x = {x}")
        ```
        """
        self.__write_log("critical", text)

    def __text_style(self, style: _Style, text):
        if self._is_show_color_in_console:
            return (
                Log._Style.RESET
                + style
                + str(text)
                + Log._Style.RESET
                + Log.__TEMP_STYLE
            )
        return str(text)

    def text_debug(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is debug text (**cyan** text) in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_debug("Message"))
        ```
        """
        return self.__text_style(Log._Style.DEBUG, text)

    def text_info(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is info text (**normal** text) in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_info("Message"))
        ```
        """
        return self.__text_style(Log._Style.DEBUG, text)

    def text_warning(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is warning text (**yellow** text) in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_warning("Message"))
        ```
        """
        return self.__text_style(Log._Style.WARNING, text)

    def text_error(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is error text (**red** text) in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_error("Message"))
        ```
        """
        return self.__text_style(Log._Style.ERROR, text)

    def text_critical(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is critical text (text with **red background**) in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_critical("Message"))
        ```
        """
        return self.__text_style(Log._Style.CRITICAL, text)

    def text_normal(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is **normal** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_normal("Message"))
        ```
        """
        return self.__text_style(Log._Style.NORMAL, text)

    def text_red(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is **red** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_red("Message"))
        ```
        """
        return self.__text_style(Log._Style.RED, text)

    def text_green(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is **green** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_green("Message"))
        ```
        """
        return self.__text_style(Log._Style.GREEN, text)

    def text_yellow(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is **yellow** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_yellow("Message"))
        ```
        """
        return self.__text_style(Log._Style.YELLOW, text)

    def text_blue(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is **blue** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_blue("Message"))
        ```
        """
        return self.__text_style(Log._Style.BLUE, text)

    def text_magenta(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is **magenta** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_magenta("Message"))
        ```
        """
        return self.__text_style(Log._Style.MAGENTA, text)

    def text_cyan(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is **cyan** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_cyan("Message"))
        ```
        """
        return self.__text_style(Log._Style.CYAN, text)

    def text_red_background(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is black with **red background** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_red_background("Message"))
        ```
        """
        return self.__text_style(Log._Style.RED_BACKGROUND, " " + str(text) + " ")

    def text_green_background(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is black with **green background** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_green_background("Message"))
        ```
        """
        return self.__text_style(Log._Style.GREEN_BACKGROUND, " " + str(text) + " ")

    def text_yellow_background(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is black with **yellow background** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_yellow_background("Message"))
        ```
        """
        return self.__text_style(Log._Style.YELLOW_BACKGROUND, " " + str(text) + " ")

    def text_blue_background(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is black with **blue background** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_blue_background("Message"))
        ```
        """
        return self.__text_style(Log._Style.BLUE_BACKGROUND, " " + str(text) + " ")

    def text_magenta_background(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is black with **magenta background** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_magenta_background("Message"))
        ```
        """
        return self.__text_style(Log._Style.MAGENTA_BACKGROUND, " " + str(text) + " ")

    def text_cyan_background(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is black with **cyan background** in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_cyan_background("Message"))
        ```
        """
        return self.__text_style(Log._Style.CYAN_BACKGROUND, " " + str(text) + " ")

    def text_italic(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is text in italics in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_italic("Message"))
        ```
        """
        return self.__text_style(Log._Style.ITALIC, text)

    def text_underline(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is underlined text in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_underlined("Message"))
        ```
        """
        return self.__text_style(Log._Style.UNDERLINE, text)

    def text_crossed_out(self, text):
        """Frame the text with
        [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
        so that it is crossed out text in the console.

        Args:
            text (str): Message for logging.

        Returns:
            Returns framed text.

        Example:
        ```py
        import harrixpylib as h

        h.log.info("x = " + h.log.text_crossed_out("Message"))
        ```
        """
        return self.__text_style(Log._Style.CROSSED_OUT, text)


log = Log()

if __name__ == "__main__":
    log.is_log_file = True

    log.is_show_time_in_console = False
    log.is_show_color_in_console = False
    log.debug("Test message.")
    log.info("Test message.")
    log.warning("Test message.")
    log.error("Test message.")
    log.critical("Test message.")

    print()

    log.is_show_time_in_console = True
    log.is_show_color_in_console = True
    log.debug("Test message.")
    log.info("Test message.")
    log.warning("Test message.")
    log.error("Test message.")
    log.critical("Test message.")

    print()

    log.is_show_time_in_console = False
    log.info("Message: {}. End of line".format(log.text_debug("x = 2")))
    log.info("Message: {}. End of line".format(log.text_info("x = 2")))
    log.info("Message: {}. End of line".format(log.text_warning("x = 2")))
    log.info("Message: {}. End of line".format(log.text_error("x = 2")))
    log.info("Message: {}. End of line".format(log.text_critical("x = 2")))
    log.info("Message: {}. End of line".format(log.text_normal("x = 2")))
    log.info("Message: {}. End of line".format(log.text_red("x = 2")))
    log.info("Message: {}. End of line".format(log.text_green("x = 2")))
    log.info("Message: {}. End of line".format(log.text_yellow("x = 2")))
    log.info("Message: {}. End of line".format(log.text_blue("x = 2")))
    log.info("Message: {}. End of line".format(log.text_magenta("x = 2")))
    log.info("Message: {}. End of line".format(log.text_cyan("x = 2")))
    log.info("Message: {}. End of line".format(log.text_red_background("x = 2")))
    log.info("Message: {}. End of line".format(log.text_green_background("x = 2")))
    log.info("Message: {}. End of line".format(log.text_yellow_background("x = 2")))
    log.info("Message: {}. End of line".format(log.text_blue_background("x = 2")))
    log.info("Message: {}. End of line".format(log.text_magenta_background("x = 2")))
    log.info("Message: {}. End of line".format(log.text_cyan_background("x = 2")))
    log.info("Message: {}. End of line".format(log.text_italic("x = 2")))
    log.info("Message: {}. End of line".format(log.text_underline("x = 2")))
    log.info("Message: {}. End of line".format(log.text_crossed_out("x = 2")))

    print()

    log.is_show_time_in_console = False
    log.error("Message: {}. End of line".format(log.text_debug("x = 2")))
    log.error("Message: {}. End of line".format(log.text_info("x = 2")))
    log.error("Message: {}. End of line".format(log.text_warning("x = 2")))
    log.error("Message: {}. End of line".format(log.text_error("x = 2")))
    log.error("Message: {}. End of line".format(log.text_critical("x = 2")))
    log.error("Message: {}. End of line".format(log.text_normal("x = 2")))
    log.error("Message: {}. End of line".format(log.text_red("x = 2")))
    log.error("Message: {}. End of line".format(log.text_green("x = 2")))
    log.error("Message: {}. End of line".format(log.text_yellow("x = 2")))
    log.error("Message: {}. End of line".format(log.text_blue("x = 2")))
    log.error("Message: {}. End of line".format(log.text_magenta("x = 2")))
    log.error("Message: {}. End of line".format(log.text_cyan("x = 2")))
    log.error("Message: {}. End of line".format(log.text_red_background("x = 2")))
    log.error("Message: {}. End of line".format(log.text_green_background("x = 2")))
    log.error("Message: {}. End of line".format(log.text_yellow_background("x = 2")))
    log.error("Message: {}. End of line".format(log.text_blue_background("x = 2")))
    log.error("Message: {}. End of line".format(log.text_magenta_background("x = 2")))
    log.error("Message: {}. End of line".format(log.text_cyan_background("x = 2")))
    log.error("Message: {}. End of line".format(log.text_italic("x = 2")))
    log.error("Message: {}. End of line".format(log.text_underline("x = 2")))
    log.error("Message: {}. End of line".format(log.text_crossed_out("x = 2")))

    print()

    log.is_show_time_in_console = True
    log.info(log.text_debug("x = 2"))
    log.info(log.text_info("x = 2"))
    log.info(log.text_warning("x = 2"))
    log.info(log.text_error("x = 2"))
    log.info(log.text_critical("x = 2"))
    log.info(log.text_normal("x = 2"))
    log.info(log.text_red("x = 2"))
    log.info(log.text_green("x = 2"))
    log.info(log.text_yellow("x = 2"))
    log.info(log.text_blue("x = 2"))
    log.info(log.text_magenta("x = 2"))
    log.info(log.text_cyan("x = 2"))
    log.info(log.text_red_background("x = 2"))
    log.info(log.text_green_background("x = 2"))
    log.info(log.text_yellow_background("x = 2"))
    log.info(log.text_blue_background("x = 2"))
    log.info(log.text_magenta_background("x = 2"))
    log.info(log.text_cyan_background("x = 2"))
    log.info(log.text_italic("x = 2"))
    log.info(log.text_underline("x = 2"))
    log.info(log.text_crossed_out("x = 2"))
