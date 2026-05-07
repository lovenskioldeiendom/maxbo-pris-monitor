from .base import BaseScraper


class ByggmakkerScraper(BaseScraper):
    competitor_id = "byggmakker"
    competitor_name = "Byggmakker"

    price_selectors = [
        '[data-testid="price"]',
        '.product-price',
        '.price-current',
        '[class*="Price"]',
    ]

    extra_wait_ms = 2000
