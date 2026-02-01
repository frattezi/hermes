import asyncio
from concurrent.futures import ThreadPoolExecutor

from gliner import GLiNER

from hermes.scraper import Scraper


class GlinerScraper(Scraper):
    """
    A scraper that uses GLiNER for entity extraction.
    """

    def __init__(
        self,
        model_name: str = "urchade/gliner_small-v2.1",
        api_key: str | None = None
    ):
        """
        Initialize the GlinerScraper.

        Args:
            model_name: The name of the GLiNER model to use.
            api_key: Not used for GLiNER, but kept for compatibility.
        """
        super().__init__(api_key=api_key)
        self.model = GLiNER.from_pretrained(model_name)

    def extract(self, text: str, labels: list[str]) -> dict:
        """
        Extract entities from text using GLiNER.

        Args:
            text: The text to extract from.
            labels: The list of labels to extract (e.g., ["price", "person"]).

        Returns:
            A dictionary of extracted entities grouped by label.
        """
        entities = self.model.predict_entities(text, labels)

        result = {label: [] for label in labels}
        for entity in entities:
            result[entity["label"]].append(entity["text"])

        return result

    async def scrape(self, url: str, rules: str = "") -> dict | str:
        """
        Scrapes data from a URL using GLiNER.

        Note: 'rules' here is treated as a comma-separated list of labels
        if provided, otherwise defaults to ["price", "person"].
        """
        print(f"Fetching {url}...")
        try:
            html = await self.fetch_page(url)
        except Exception as e:
            return {"error": f"Failed to fetch page: {e}"}

        print("Cleaning HTML...")
        cleaned_text = self.clean_html(html)

        # Truncate to avoid excessive processing time/memory
        if len(cleaned_text) > 10000:
            cleaned_text = cleaned_text[:10000]

        print("Extracting entities with GLiNER...")

        # Parse rules into labels
        # If rules are provided as natural language, we might need to be smarter,
        # but for this POC we assume they map to labels.
        if rules:
             # Heuristic: split by comma if it looks like a list
             labels = [r.strip() for r in rules.split(",")]
        else:
             labels = ["price", "person"]

        # Offload blocking inference to a thread
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool, self.extract, cleaned_text, labels
            )
        return result
