import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from hermes.scraper import Scraper


def test_scraper_instantiation():
    scraper = Scraper(api_key="test", base_url="http://localhost:11434/v1", model="llama3")
    assert scraper.api_key == "test"
    assert scraper.base_url == "http://localhost:11434/v1"
    assert scraper.model == "llama3"


def test_scraper_instantiation_defaults():
    scraper = Scraper()
    assert scraper.model == "gpt-3.5-turbo"
    assert scraper.base_url is None


@pytest.mark.asyncio
async def test_scrape_with_ollama_config():
    # Mock content
    html_content = "<html>Pricing: $10, Name: Product A</html>"

    # Mock AsyncOpenAI response
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"Pricing": "$10", "Names": ["Product A"]}'
    mock_client.chat.completions.create.return_value = mock_response

    with patch("hermes.scraper.Scraper.fetch_page", new_callable=AsyncMock) as mock_fetch, \
         patch("hermes.scraper.AsyncOpenAI", return_value=mock_client) as mock_openai_cls:

        mock_fetch.return_value = html_content

        # Setup Scraper
        scraper = Scraper(api_key="ollama", base_url="http://localhost:11434/v1", model="llama3")

        # Run scrape
        result = await scraper.scrape("http://example.com", "Extract Pricing and Names")

        # Assertions
        assert result == {"Pricing": "$10", "Names": ["Product A"]}

        # Verify OpenAI client init
        mock_openai_cls.assert_called_with(api_key="ollama", base_url="http://localhost:11434/v1")

        # Verify chat completion call
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "llama3"
        assert "Extract Pricing and Names" in call_args.kwargs["messages"][1]["content"]
