import asyncio
import os

from dotenv import load_dotenv

from hermes.scraper import Scraper

load_dotenv()


async def main():
    """
    Main entry point for the Hermes scraper POC.
    """
    print("Starting Hermes Scraper POC...")

    url = "https://example.com"
    rules = "Extract Pricing and Names."

    # Configuration for Ollama or other LLMs
    # For Ollama, set LLM_BASE_URL="http://localhost:11434/v1" and LLM_API_KEY="ollama"
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    api_key = os.getenv("LLM_API_KEY")

    scraper = Scraper(api_key=api_key, base_url=base_url, model=model)

    print(f"Target URL: {url}")
    print(f"Rules: {rules}")
    print(f"Model: {model}")
    if base_url:
        print(f"Base URL: {base_url}")

    result = await scraper.scrape(url, rules)

    print("\n--- Scrape Result ---")
    print(result)
    print("---------------------")

if __name__ == "__main__":
    asyncio.run(main())
