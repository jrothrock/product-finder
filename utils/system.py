"""System module for cleaning up resources used by package."""
import logging

import database.db
import scraper.core.drivers


def cleanup(func):
    """Cleanup any instances we may have to prevent resource leakage."""

    def wrapper(*args, **kwargs):
        """Will return a wrapper to be called by celery."""
        try:
          func(*args, **kwargs)
        except Exception as e:
          logging.exception(f"Exception in task: {e.__dict__}")

        database.db.database_instance.cleanup()
        scraper.core.drivers.driver_instance.cleanup()

    return wrapper
