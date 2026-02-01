import asyncio

from dotenv import load_dotenv

from hermes.scraper import Scraper

load_dotenv()

async def main():
    """
    Main entry point for the Hermes scraper POC.
    """
    print("Starting Hermes Scraper POC...")

    # POC Configuration
    url = "https://example.com"
    rules = "Extract the page title and the main heading."

    scraper = Scraper()

    print(f"Target URL: {url}")
    print(f"Rules: {rules}")

    result = await scraper.scrape(url, rules)

    print("\n--- Scrape Result ---")
    print(result)
    print("---------------------")

if __name__ == "__main__":
    asyncio.run(main())
