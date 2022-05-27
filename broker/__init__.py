"""Subpackage used for instantiating broker."""
import os

import redis as redis_import

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


def redis():
    """Will return the redis instance."""
    return redis_import.from_url(REDIS_URL)
