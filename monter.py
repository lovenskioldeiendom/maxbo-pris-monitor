from .base import BaseScraper


class MonterScraper(BaseScraper):
    competitor_id = "monter"
    competitor_name = "Montér"

    price_selectors = [
        '[data-testid="product-price"]',
        '.product-price',
        '.price',
        '[class*="price"]',
    ]

    extra_wait_ms = 2000
