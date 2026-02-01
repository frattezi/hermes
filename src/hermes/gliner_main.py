import asyncio
import json

from hermes.gliner_scraper import GlinerScraper


async def main():
    """
    Main entry point for the GLiNER scraper POC.
    """
    print("Starting GLiNER Scraper POC...")

    # POC Configuration
    # Using a dummy URL for demonstration
    url = "https://example.com"

    scraper = GlinerScraper()

    # Define labels (rules)
    labels = "price, person name, company"

    print(f"Target URL: {url}")
    print(f"Labels: {labels}")

    # Note: Example.com may not contain these entities.
    # This demonstrates the execution flow.
    result = await scraper.scrape(url, labels)

    print("\n--- Scrape Result ---")
    print(json.dumps(result, indent=2))
    print("---------------------")

if __name__ == "__main__":
    asyncio.run(main())
