from .base import BaseScraper


class ObsByggScraper(BaseScraper):
    competitor_id = "obs_bygg"
    competitor_name = "Obs Bygg"

    price_selectors = [
        '[data-testid="price"]',
        '.product-price__amount',
        '.price-amount',
        '[class*="price"]',
    ]

    extra_wait_ms = 2000
