import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import ollama

from hermes.config import settings
from hermes.gliner_scraper import GlinerScraper
from hermes.queue import JobQueue
from hermes.storage import Storage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Queues
SCRAPE_QUEUE = "scrape_queue"
ANALYZE_QUEUE = "analyze_queue"
EXTRACT_QUEUE = "extract_queue"

# Storage Indices
RESULT_INDEX = "hermes_results"

class Worker:
    def __init__(self):
        self.queue = JobQueue()
        self.storage = Storage()
        self.scraper = GlinerScraper(model_name=settings.gliner_model)
        # We can re-use the scraper instance for fetching as well,
        # or have a dedicated fetcher if we want to split concerns cleanly.
        # For this POC, GlinerScraper inherits from Scraper so it has fetch_page.

        # Ollama client configuration (if using python lib)
        # Note: ollama lib connects to localhost:11434 by default.
        # If we need to change host: ollama.Client(host=settings.ollama_url)
        self.ollama_client = ollama.Client(host=settings.ollama_url)

    async def run(self):
        """
        Main worker loop.
        In a real system, these would likely be separate processes/pods.
        Here we run them as concurrent async tasks.
        """
        logger.info("Starting Worker Loop...")
        await asyncio.gather(
            self.process_scrape_queue(),
            self.process_analyze_queue(),
            self.process_extract_queue()
        )

    async def process_scrape_queue(self):
        """
        Step 2: Pulls from scrape_queue -> Fetches HTML -> Pushes to analyze_queue
        """
        logger.info("Listening on scrape_queue...")
        while True:
            job = self.queue.pop(SCRAPE_QUEUE)
            if not job:
                await asyncio.sleep(1)
                continue

            logger.info(f"[Scrape] Processing: {job}")
            url = job.get("url")
            user_query = job.get("query")

            try:
                # 1. Fetch Page
                html = await self.scraper.fetch_page(url)

                # 2. Clean HTML
                cleaned_text = self.scraper.clean_html(html)
                # Truncate for analysis context
                truncated_text = cleaned_text[:10000]

                # 3. Push to next stage
                next_job = {
                    "url": url,
                    "query": user_query,
                    "text_content": truncated_text
                }
                self.queue.push(ANALYZE_QUEUE, next_job)

            except Exception as e:
                logger.error(f"[Scrape] Failed: {e}")

    async def process_analyze_queue(self):
        """
        Step 3: Pulls from analyze_queue -> Calls Ollama to get labels
        -> Pushes to extract_queue
        """
        logger.info("Listening on analyze_queue...")
        while True:
            job = self.queue.pop(ANALYZE_QUEUE)
            if not job:
                await asyncio.sleep(1)
                continue

            logger.info(f"[Analyze] Processing: {job.get('url')}")
            text_preview = job.get("text_content")[:500]
            user_query = job.get("query")

            try:
                # Call Ollama to deduce labels
                prompt = (
                    f"User wants to know: '{user_query}'.\n"
                    f"Based on this text preview: '{text_preview}...'\n"
                    "What are the best short entity labels (comma separated) "
                    "for a Named Entity Recognition model "
                    "to extract the relevant information?\n"
                    "Output ONLY the comma separated labels "
                    "(e.g. price, product_name, vendor). Do not add extra text."
                )

                # Blocking call, offload to thread
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    response = await loop.run_in_executor(
                        pool,
                        lambda: self.ollama_client.generate(
                            model=settings.ollama_model, prompt=prompt
                        ),
                    )

                labels_str = response['response'].strip()
                # Simple cleanup
                labels = [label.strip() for label in labels_str.split(",")]
                logger.info(f"[Analyze] Derived labels: {labels}")

                # Push to next stage
                next_job = {
                    "url": job.get("url"),
                    "query": user_query,
                    "text_content": job.get("text_content"),
                    "labels": labels
                }
                self.queue.push(EXTRACT_QUEUE, next_job)

            except Exception as e:
                logger.error(f"[Analyze] Failed: {e}")

    async def process_extract_queue(self):
        """
        Step 4: Pulls from extract_queue -> Calls GLiNER
        -> Pushes results to Elasticsearch
        """
        logger.info("Listening on extract_queue...")
        while True:
            job = self.queue.pop(EXTRACT_QUEUE)
            if not job:
                await asyncio.sleep(1)
                continue

            logger.info(f"[Extract] Processing: {job.get('url')}")
            text_content = job.get("text_content")
            labels = job.get("labels")

            try:
                # Call GLiNER (already async-wrapped in gliner_scraper logic
                # if we used scrape(), but here we have the text already,
                # so we call extract() which is sync.
                # GlinerScraper.extract is sync, so offload it.

                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as pool:
                    extraction_result = await loop.run_in_executor(
                        pool,
                        self.scraper.extract,
                        text_content,
                        labels
                    )

                # Save to ES
                doc = {
                    "url": job.get("url"),
                    "query": job.get("query"),
                    "extracted_data": extraction_result
                }
                self.storage.save(RESULT_INDEX, doc)
                logger.info(f"[Extract] Finished processing {job.get('url')}")

            except Exception as e:
                logger.error(f"[Extract] Failed: {e}")

if __name__ == "__main__":
    worker = Worker()
    asyncio.run(worker.run())
