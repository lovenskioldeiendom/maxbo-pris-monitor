"""
Hovedskript. Kjører alle scrapere mot alle produkter, lagrer i SQLite.

Kjøring:
    python run_scraper.py              # alle kjeder, alle produkter
    python run_scraper.py --dry-run    # ikke skriv til DB
    python run_scraper.py --competitor maxbo  # bare én kjede
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Legg til prosjektmappen i path så imports virker
sys.path.insert(0, str(Path(__file__).parent))

from products import PRODUCTS, COMPETITORS
from database import init_db, save_price
from scrapers.base import run_scraper
from scrapers.maxbo import MaxboScraper
from scrapers.byggmakker import ByggmakkerScraper
from scrapers.monter import MonterScraper
from scrapers.obs_bygg import ObsByggScraper
from scrapers.xl_bygg import XLByggScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

SCRAPER_CLASSES = {
    "maxbo": MaxboScraper,
    "byggmakker": ByggmakkerScraper,
    "monter": MonterScraper,
    "obs_bygg": ObsByggScraper,
    "xl_bygg": XLByggScraper,
}


async def main(competitors: list[str], dry_run: bool, headless: bool):
    init_db()
    # Skriv en placeholder så databasen alltid har minst én rad
    save_price("_init", "_init", None, status="ok")
    summary = {"ok": 0, "missing_url": 0, "scrape_error": 0}

    for competitor in competitors:
        scraper_class = SCRAPER_CLASSES[competitor]
        scraper = scraper_class(headless=headless)

        # Bygg liste med (product_id, url)-par der URL ikke er None
        urls = []
        for p in PRODUCTS:
            url = p["urls"].get(competitor)
            if url:
                urls.append((p["id"], url))
            else:
                if not dry_run:
                    save_price(p["id"], competitor, None,
                              status="missing_url",
                              error_msg="URL not configured")
                summary["missing_url"] += 1

        if not urls:
            logger.info(f"[{competitor}] ingen URLer konfigurert, hopper over")
            continue

        logger.info(f"[{competitor}] starter scraping av {len(urls)} produkter")
        results = await run_scraper(scraper, urls)

        for r in results:
            if not dry_run:
                save_price(
                    product_id=r["product_id"],
                    competitor=r["competitor"],
                    price=r["price"],
                    url=r["url"],
                    status=r["status"],
                )
            summary[r["status"]] = summary.get(r["status"], 0) + 1

        logger.info(f"[{competitor}] ferdig")

    logger.info(f"Totalt: {summary}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--competitor", choices=COMPETITORS, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-headless", action="store_true",
                       help="Vis nettleser (for debug)")
    args = parser.parse_args()

    competitors = [args.competitor] if args.competitor else COMPETITORS
    asyncio.run(main(competitors, args.dry_run, headless=not args.no_headless))
