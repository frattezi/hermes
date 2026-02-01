import json
import os

import httpx
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed


class Scraper:
    """
    A class to scrape web pages using AI-based extraction.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the Scraper.

        Args:
            api_key: OpenAI API key. If None, it attempts to load from env.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def fetch_page(self, url: str) -> str:
        """
        Fetches the content of a URL.

        Args:
            url: The URL to fetch.

        Returns:
            The HTML content of the page.
        """
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def clean_html(self, html_content: str) -> str:
        """
        Cleans the HTML content to extract text.

        Args:
            html_content: The raw HTML content.

        Returns:
            The cleaned text content.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text(separator=" ")

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text

    async def scrape(self, url: str, rules: str) -> dict | str:
        """
        Scrapes data from a URL based on natural language rules.

        Args:
            url: The URL to scrape.
            rules: Natural language description of what to extract.

        Returns:
            The extracted data as a dictionary or string.
        """
        print(f"Fetching {url}...")
        try:
            html = await self.fetch_page(url)
        except Exception as e:
            return {"error": f"Failed to fetch page: {e}"}

        print("Cleaning HTML...")
        cleaned_text = self.clean_html(html)

        # Truncate if too long (simple heuristic for now)
        if len(cleaned_text) > 100000:
            cleaned_text = cleaned_text[:100000]

        if not self.api_key:
            return {
                "status": "mock_success",
                "message": "No API key provided. Skipping AI extraction.",
                "preview_text": cleaned_text[:500],
            }

        # Note: We use raw JSON extraction here because the rules are dynamic.
        # For fixed schemas, we should use Pydantic models.
        print("Extracting data with AI...")
        client = AsyncOpenAI(api_key=self.api_key)

        prompt = f"""
        You are an expert web scraper.
        Extract the information described by the rules below from the provided text.
        Return the result as a valid JSON object.

        Rules:
        {rules}

        Text:
        {cleaned_text}
        """

        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that extracts data "
                            "from text and returns JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
            else:
                return {"error": "Empty response from AI"}
        except Exception as e:
            return {"error": f"AI extraction failed: {e}"}
