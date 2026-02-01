import logging
from datetime import datetime, timezone

from elasticsearch import AsyncElasticsearch

from hermes.config import settings

logger = logging.getLogger(__name__)

class Storage:
    """
    Elasticsearch wrapper for storing results (Async).
    """
    def __init__(self, es_url: str = settings.elasticsearch_url):
        self.client = AsyncElasticsearch(es_url)

    async def save(self, index: str, document: dict):
        """
        Index a document.
        """
        try:
            document["timestamp"] = datetime.now(timezone.utc).isoformat()
            resp = await self.client.index(index=index, document=document)
            logger.info(f"Saved document to {index}: {resp['_id']}")
            return resp['_id']
        except Exception as e:
            logger.error(f"Failed to save to {index}: {e}")
            raise
