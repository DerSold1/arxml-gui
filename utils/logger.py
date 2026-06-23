"""Logging utilities"""

import logging
from pathlib import Path
from datetime import datetime


class Logger:
    """Logging handler for the application"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if Logger._logger is None:
            Logger._logger = self._setup_logger()

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Setup logger configuration"""
        logger = logging.getLogger('arxml_gui')
        logger.setLevel(logging.DEBUG)

        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # File handler
        log_file = log_dir / f"arxml_gui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def debug(self, message: str) -> None:
        """Log debug message"""
        Logger._logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message"""
        Logger._logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message"""
        Logger._logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message"""
        Logger._logger.error(message)

    def critical(self, message: str) -> None:
        """Log critical message"""
        Logger._logger.critical(message)


def get_logger() -> Logger:
    """Get logger instance"""
    return Logger()
