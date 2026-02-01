import json
import logging

import redis

from hermes.config import settings

logger = logging.getLogger(__name__)

class JobQueue:
    """
    A simple Redis-based job queue.
    """
    def __init__(self, redis_url: str = settings.redis_url):
        self.client = redis.from_url(redis_url)

    def push(self, queue_name: str, payload: dict):
        """
        Push a job to the queue.
        """
        try:
            self.client.rpush(queue_name, json.dumps(payload))
            logger.info(f"Pushed job to {queue_name}: {payload}")
        except Exception as e:
            logger.error(f"Failed to push to {queue_name}: {e}")
            raise

    def pop(self, queue_name: str, timeout: int = 5) -> dict | None:
        """
        Pop a job from the queue (blocking).
        """
        try:
            # blpop returns (queue_name, data) or None
            result = self.client.blpop(queue_name, timeout=timeout)
            if result:
                return json.loads(result[1])
            return None
        except Exception as e:
            logger.error(f"Failed to pop from {queue_name}: {e}")
            return None
