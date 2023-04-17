import logging

default_format: str = "%(asctime)s " "[%(levelname)s] " "%(module)s | " "%(message)s"

logging.basicConfig(
    level=logging.INFO, format=default_format, datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()
