from loguru import logger

logger.add("logs/logger.log", rotation="10 MB", retention="10 days", compression="zip", level="DEBUG", format="{time} | {level} | {message}")

log = logger