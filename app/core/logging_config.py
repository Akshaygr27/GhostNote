import logging


def setup_logging(log_level: str):

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),

        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),

        datefmt="%Y-%m-%d %H:%M:%S"
    )


logger = logging.getLogger("app")