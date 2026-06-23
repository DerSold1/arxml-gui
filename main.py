"""Main entry point for ARXML GUI Generator"""

import tkinter as tk
from gui.main_window import MainWindow
from utils.logger import get_logger


def main():
    """Main application entry point"""
    logger = get_logger()
    logger.info("Starting ARXML GUI Generator")

    root = tk.Tk()
    app = MainWindow(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        raise
    finally:
        logger.info("Application closed")


if __name__ == "__main__":
    main()
