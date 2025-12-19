import logging
class UvicornStyleFormatter(logging.Formatter):
    # ANSI color codes
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(levelname)s"+ reset +":     %(message)s" + reset,
        logging.INFO: green + "%(levelname)s"+ reset +":     %(message)s" + reset,
        logging.WARNING: yellow + "%(levelname)s"+ reset +":    %(message)s" + reset,
        logging.ERROR: red + "%(levelname)s"+ reset +":     %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(levelname)s"+ reset +":     %(message)s" + reset,
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)