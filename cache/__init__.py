"""Subpackage used for instantiating caching."""
import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_instance = redis.from_url(REDIS_URL)
