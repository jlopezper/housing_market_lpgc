import logging


def init_logger():
    # logger
    logger = logging.getLogger("__name__")
    logger.setLevel(logging.INFO)
    # file handler
    fh = logging.FileHandler("log/logging.log", "w")
    fh.setLevel(logging.INFO)
    # level handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # format
    log_format = "%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s"
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
