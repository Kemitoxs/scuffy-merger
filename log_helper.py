import logging
import coloredlogs

log = logging.getLogger()


def configure_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Define your format and date format with proper spacing for the log level
    log_format = "%(asctime)s [%(levelname)-8s]: %(message)s"
    date_format = '%H:%M'

    # Specify colors for different log levels
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES.copy()
    level_styles['debug'] = {'color': 8}  # 'faint' makes the color appear as gray in many terminals

    # Install colored logs with custom format and colors
    coloredlogs.install(
        level='DEBUG',
        logger=logger,
        fmt=log_format,
        datefmt=date_format,
        level_styles=level_styles
    )
