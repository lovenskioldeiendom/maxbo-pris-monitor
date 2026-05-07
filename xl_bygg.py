from .base import BaseScraper


class XLByggScraper(BaseScraper):
    competitor_id = "xl_bygg"
    competitor_name = "XL-Bygg"

    price_selectors = [
        '[data-testid="product-price"]',
        '.product-price',
        '.price__value',
        '[class*="Price"]',
    ]

    extra_wait_ms = 2000
