"""
Base for alle scrapere. Hver konkurrent-modul (maxbo.py, byggmakker.py, ...)
arver fra BaseScraper og overstyrer extract_price().

Strategi:
- Bruker Playwright med chromium (headless)
- Venter på network-idle for å la JavaScript laste prisen
- Prøver flere CSS-selektorer i prioritert rekkefølge
- Returnerer None hvis ingen pris finnes (logges som feil)
"""

import asyncio
import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeout

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (compatible; MaxboPriceMonitor/1.0; "
    "+https://github.com/yourusername/maxbo-pris-monitor)"
)
PAGE_TIMEOUT_MS = 20_000
DELAY_BETWEEN_REQUESTS_S = 3


def parse_price(text: str) -> Optional[float]:
    """
    Henter ut et tall fra tekst som '47,90 kr', 'kr 1 495,-', '129.-', '12 990 kr'.
    Returnerer None hvis ingen pris finnes.
    """
    if not text:
        return None
    # Fjern kr, "Fra", whitespace, NBSP
    cleaned = text.replace("\xa0", " ").replace("kr", "").replace("Kr", "").replace("KR", "")
    # Match tall med komma eller punkt som desimalskille
    m = re.search(r"(\d{1,3}(?:[ .]\d{3})*(?:[,.]\d{1,2})?)", cleaned)
    if not m:
        return None
    raw = m.group(1).replace(" ", "").replace(".", "").replace(",", ".")
    # Hvis det opprinnelig var komma som desimal: "12.990,50" → "12990.50". Vi har erstattet
    # punkt med ingenting og komma med punkt, så det blir "12990.50" — riktig.
    # Hvis det var punkt som tusenskille: "12.990" → "12990" — riktig.
    # Hvis det var punkt som desimal: "129.50" → "12950" — feil!
    # Heuristikk: hvis det fjernede punktet hadde 3 sifre etter, var det tusenskille.
    # Enklere: hvis prisen virker urealistisk høy (>100 000 kr), prøv på nytt med .  som desimal.
    try:
        val = float(raw)
        if val > 100_000:
            # Sannsynlig at vi har feiltolket. Prøv original med . som desimal.
            alt = m.group(1).replace(" ", "").replace(",", "")
            val = float(alt)
        return round(val, 2)
    except ValueError:
        return None


class BaseScraper(ABC):
    """Base for alle konkurrent-scrapere."""

    competitor_id: str = ""
    competitor_name: str = ""

    # CSS-selektorer i prioritert rekkefølge. Første match vinner.
    # Override i subklasse.
    price_selectors: list[str] = []

    # Hvis siden krever ekstra ventetid for prisen
    extra_wait_ms: int = 1000

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def scrape(self, page: Page, url: str) -> Optional[float]:
        """
        Henter pris fra en URL. Returnerer pris i NOK, eller None hvis ikke funnet.
        Subklasser kan overstyre extract_price() for kjedespesifikk logikk.
        """
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            # Vent litt ekstra for at JS skal laste prisen
            await page.wait_for_timeout(self.extra_wait_ms)
            return await self.extract_price(page)
        except PWTimeout:
            logger.warning(f"[{self.competitor_id}] timeout på {url}")
            return None
        except Exception as e:
            logger.warning(f"[{self.competitor_id}] feil på {url}: {e}")
            return None

    async def extract_price(self, page: Page) -> Optional[float]:
        """Standard implementasjon: prøv selektorer i rekkefølge."""
        for selector in self.price_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    price = parse_price(text)
                    if price is not None:
                        return price
            except Exception:
                continue
        return None


async def run_scraper(scraper: BaseScraper, urls: list[tuple[str, str]],
                      progress_callback=None) -> list[dict]:
    """
    Kjør en scraper mot en liste (product_id, url)-par.
    Returnerer liste med resultater.
    """
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=scraper.headless)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            locale="nb-NO",
        )
        page = await context.new_page()
        # Blokker bilder/fonter for raskere lasting
        await page.route("**/*", lambda route: (
            route.abort() if route.request.resource_type in ("image", "font", "media")
            else route.continue_()
        ))

        for i, (product_id, url) in enumerate(urls):
            logger.info(f"[{scraper.competitor_id}] {i+1}/{len(urls)}: {product_id}")
            price = await scraper.scrape(page, url)
            results.append({
                "product_id": product_id,
                "competitor": scraper.competitor_id,
                "url": url,
                "price": price,
                "status": "ok" if price is not None else "scrape_error",
            })
            if progress_callback:
                progress_callback(i + 1, len(urls))
            # Snill mot serveren: vent litt mellom requests
            if i < len(urls) - 1:
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS_S)

        await context.close()
        await browser.close()

    return results
