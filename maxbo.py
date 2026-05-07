from .base import BaseScraper


class MaxboScraper(BaseScraper):
    competitor_id = "maxbo"
    competitor_name = "Maxbo"

    # Maxbo bruker Gatsby (JS-rendret). Pris er typisk i en data-attribute eller en .price-klasse.
    # Disse er kvalifiserte gjetninger — verifiser ved å åpne devtools på en produktside.
    price_selectors = [
        '[data-testid="product-price"]',
        '.product-price__current',
        '.price__value',
        '[class*="ProductPrice"]',
        '[class*="price"]',
    ]

    extra_wait_ms = 2000  # Maxbo trenger litt tid for å hydrere
