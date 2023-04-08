import logging

default_format: str = (
    "%(asctime)s "
    "[%(levelname)s] "
    "%(name)s | "
    "%(message)s"
)

handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
handler.setFormatter(logging.Formatter(default_format, datefmt="%Y-%m-%d %H:%M:%S"))
logger = logging.getLogger()
logger.addHandler(handler)
