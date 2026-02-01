import logging
from datetime import datetime

from elasticsearch import Elasticsearch

from hermes.config import settings

logger = logging.getLogger(__name__)

class Storage:
    """
    Elasticsearch wrapper for storing results.
    """
    def __init__(self, es_url: str = settings.elasticsearch_url):
        self.client = Elasticsearch(es_url)

    def save(self, index: str, document: dict):
        """
        Index a document.
        """
        try:
            document["timestamp"] = datetime.utcnow().isoformat()
            resp = self.client.index(index=index, document=document)
            logger.info(f"Saved document to {index}: {resp['_id']}")
            return resp['_id']
        except Exception as e:
            logger.error(f"Failed to save to {index}: {e}")
            raise
