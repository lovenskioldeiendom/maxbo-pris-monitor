"""SQLite-database for prishistorikk."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path(__file__).parent / "pris_historikk.db"


def _ensure_table(conn):
    """Lager tabellen hvis den ikke finnes. Kjøres ved hver tilkobling."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_id TEXT NOT NULL,
            competitor TEXT NOT NULL,
            price REAL,
            currency TEXT DEFAULT 'NOK',
            url TEXT,
            status TEXT DEFAULT 'ok',
            error_msg TEXT,
            scraped_at TEXT NOT NULL,
            UNIQUE(date, product_id, competitor)
        );
        CREATE INDEX IF NOT EXISTS idx_prices_date ON prices(date);
        CREATE INDEX IF NOT EXISTS idx_prices_product ON prices(product_id);
    """)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _ensure_table(conn)  # Garanterer at tabellen finnes
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        pass  # _ensure_table kjøres allerede i get_conn


def save_price(product_id: str, competitor: str, price: float | None,
               url: str | None = None, status: str = "ok",
               error_msg: str | None = None):
    today = date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO prices (date, product_id, competitor, price, url, status, error_msg, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date, product_id, competitor) DO UPDATE SET
                price = excluded.price,
                url = excluded.url,
                status = excluded.status,
                error_msg = excluded.error_msg,
                scraped_at = excluded.scraped_at
        """, (today, product_id, competitor, price, url, status, error_msg, now))


def get_latest_prices() -> list[dict]:
    with get_conn() as conn:
        latest_date = conn.execute("SELECT MAX(date) FROM prices").fetchone()[0]
        if not latest_date:
            return []
        rows = conn.execute(
            "SELECT * FROM prices WHERE date = ? ORDER BY product_id, competitor",
            (latest_date,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_history(product_id: str, days: int = 30) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT date, competitor, price, status
            FROM prices
            WHERE product_id = ?
              AND date >= date('now', ?)
            ORDER BY date, competitor
        """, (product_id, f"-{days} days")).fetchall()
        return [dict(r) for r in rows]


def get_all_dates() -> list[str]:
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT date FROM prices ORDER BY date").fetchall()
        return [r[0] for r in rows]
