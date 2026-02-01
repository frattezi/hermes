import asyncio
import logging

from hermes.queue import JobQueue
from hermes.worker import SCRAPE_QUEUE

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """
    Submits a job to the Hermes system.
    In a real scenario, this would be an API endpoint (FastAPI).
    """
    queue = JobQueue()

    url = "https://example.com"
    query = "Find the main pricing and product name"

    logger.info(f"Submitting job: {url} -> {query}")

    payload = {
        "url": url,
        "query": query
    }

    queue.push(SCRAPE_QUEUE, payload)
    logger.info(
        "Job submitted! The Worker (run via `python src/hermes/worker.py`) "
        "will pick it up."
    )

if __name__ == "__main__":
    asyncio.run(main())
