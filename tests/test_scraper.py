from hermes.scraper import Scraper


def test_scraper_instantiation():
    scraper = Scraper(api_key="test")
    assert scraper.api_key == "test"
