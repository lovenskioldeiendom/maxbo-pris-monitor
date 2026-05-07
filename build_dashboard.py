"""
Genererer statisk index.html fra databasen.
Kjøres etter scraperen, før commit/push til GitHub Pages.

Kjøring:
    python build_dashboard.py
"""

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from products import PRODUCTS, COMPETITORS, COMPETITOR_NAMES
from database import init_db, get_latest_prices, get_history, get_all_dates

OUT_DIR = Path(__file__).parent / "dashboard"
OUT_FILE = OUT_DIR / "index.html"


def build_data():
    """Bygger en JSON-struktur med dagens priser + historikk per produkt."""
    latest = get_latest_prices()
    latest_date = latest[0]["date"] if latest else date.today().isoformat()

    # Indekser dagens priser per (product_id, competitor)
    today_lookup = {(r["product_id"], r["competitor"]): r for r in latest}

    products_out = []
    for p in PRODUCTS:
        prices = []
        for comp in COMPETITORS:
            row = today_lookup.get((p["id"], comp))
            if row and row["price"] is not None:
                prices.append(row["price"])
            else:
                prices.append(None)

        # Historikk siste 30 dager
        history_rows = get_history(p["id"], days=30)
        hist_by_date = defaultdict(dict)
        for r in history_rows:
            if r["price"] is not None:
                hist_by_date[r["date"]][r["competitor"]] = r["price"]

        history = sorted([
            {"date": d, **{c: hist_by_date[d].get(c) for c in COMPETITORS}}
            for d in hist_by_date
        ], key=lambda x: x["date"])

        products_out.append({
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "unit": p["unit"],
            "prices": prices,
            "history": history,
        })

    return {
        "updated": latest_date,
        "competitors": COMPETITORS,
        "competitor_names": [COMPETITOR_NAMES[c] for c in COMPETITORS],
        "products": products_out,
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Maxbo prissammenligning</title>
<style>
  :root {
    --bg: #ffffff;
    --bg-secondary: #f5f4ee;
    --text: #1a1a1a;
    --text-muted: #6b6b6b;
    --text-faint: #999;
    --border: #e5e3dc;
    --success: #0f6e56;
    --warning: #854f0b;
    --danger: #a32d2d;
    --accent: #185fa5;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1a1a1a;
      --bg-secondary: #252525;
      --text: #e8e8e8;
      --text-muted: #a0a0a0;
      --text-faint: #707070;
      --border: #353535;
      --success: #5DCAA5;
      --warning: #EF9F27;
      --danger: #F09595;
      --accent: #85B7EB;
    }
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 1.5rem;
    line-height: 1.5;
  }
  .container { max-width: 1100px; margin: 0 auto; }
  h1 { font-size: 22px; font-weight: 500; margin: 0; }
  h2 { font-size: 16px; font-weight: 500; margin: 0 0 12px; }
  .header { display: flex; align-items: baseline; justify-content: space-between;
            margin-bottom: 1.5rem; flex-wrap: wrap; gap: 8px; }
  .updated { font-size: 13px; color: var(--text-muted); margin: 4px 0 0; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
           gap: 12px; margin-bottom: 1.5rem; }
  .stat { background: var(--bg-secondary); border-radius: 8px; padding: 1rem; }
  .stat-label { font-size: 13px; color: var(--text-muted); margin: 0; }
  .stat-value { font-size: 24px; font-weight: 500; margin: 4px 0 0; }
  .card { background: var(--bg); border: 1px solid var(--border); border-radius: 12px;
          padding: 1rem 1.25rem; margin-bottom: 1.5rem; }
  table { width: 100%; font-size: 13px; border-collapse: collapse; }
  th { text-align: left; padding: 8px 4px; font-weight: 500; color: var(--text-muted);
       border-bottom: 1px solid var(--border); font-size: 12px; text-transform: uppercase;
       letter-spacing: 0.04em; }
  th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }
  td { padding: 8px 4px; border-bottom: 1px solid var(--border); }
  td.cat { font-size: 11px; color: var(--text-faint); text-transform: uppercase;
           letter-spacing: 0.04em; }
  .min { color: var(--success); font-weight: 500; }
  .diff-cheap { color: var(--success); font-weight: 500; }
  .diff-mid { color: var(--warning); font-weight: 500; }
  .diff-high { color: var(--danger); font-weight: 500; }
  .missing { color: var(--text-faint); }
  .controls { display: flex; align-items: baseline; justify-content: space-between;
              flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
  select { font-size: 13px; padding: 6px 10px; background: var(--bg-secondary);
           color: var(--text); border: 1px solid var(--border); border-radius: 6px; }
  .legend { display: flex; flex-wrap: wrap; gap: 16px; margin: 8px 0;
            font-size: 12px; color: var(--text-muted); }
  .legend-item { display: flex; align-items: center; gap: 4px; }
  .swatch { width: 10px; height: 10px; border-radius: 2px; }
  .chart-wrap { position: relative; width: 100%; height: 280px; }
  .footer { font-size: 12px; color: var(--text-faint); margin-top: 2rem; text-align: center; }
  .empty { color: var(--text-muted); padding: 1rem; text-align: center; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>Maxbo prissammenligning</h1>
      <p class="updated">Sist oppdatert: <span id="updated-date"></span></p>
    </div>
  </div>

  <div class="stats" id="stats"></div>

  <div class="card">
    <h2>Dagens priser</h2>
    <div style="overflow-x: auto;">
      <table>
        <thead><tr id="price-head"></tr></thead>
        <tbody id="price-body"></tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <div class="controls">
      <h2 style="margin: 0;">Prishistorikk</h2>
      <select id="product-select"></select>
    </div>
    <div class="legend" id="legend"></div>
    <div class="chart-wrap">
      <canvas id="chart" role="img" aria-label="Prishistorikk per konkurrent">
        Prishistorikk siste 30 dager.
      </canvas>
    </div>
  </div>

  <p class="footer">
    Generert automatisk fra <a href="https://github.com/">prisovervåkningssystemet</a>.
    Priser hentes fra konkurrentenes nettsider.
  </p>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
const DATA = __DATA_PLACEHOLDER__;

const COLORS = ['#378ADD', '#1D9E75', '#BA7517', '#7F77DD', '#D4537E'];
const DASHES = [[], [6,4], [2,3], [10,4], [8,4,2,4]];
const POINT_STYLES = ['circle', 'rect', 'triangle', 'crossRot', 'rectRot'];

function fmt(n) {
  if (n === null || n === undefined) return '–';
  return new Intl.NumberFormat('nb-NO').format(Math.round(n));
}

function init() {
  document.getElementById('updated-date').textContent = DATA.updated;

  // Stats
  const totalProducts = DATA.products.length;
  let maxboBest = 0;
  let totalDiff = 0;
  let validCount = 0;
  for (const p of DATA.products) {
    const valid = p.prices.filter(x => x !== null);
    if (valid.length === 0) continue;
    const min = Math.min(...valid);
    const maxboPrice = p.prices[0]; // Maxbo er alltid første konkurrent
    if (maxboPrice !== null) {
      if (maxboPrice === min) maxboBest++;
      const diff = (maxboPrice - min) / min * 100;
      totalDiff += diff;
      validCount++;
    }
  }
  const avgDiff = validCount > 0 ? totalDiff / validCount : 0;
  const diffColor = avgDiff < 1 ? 'var(--success)' : avgDiff < 5 ? 'var(--warning)' : 'var(--danger)';

  document.getElementById('stats').innerHTML = `
    <div class="stat"><p class="stat-label">Produkter</p><p class="stat-value">${totalProducts}</p></div>
    <div class="stat"><p class="stat-label">Maxbo billigst</p><p class="stat-value" style="color: var(--success);">${maxboBest} / ${totalProducts}</p></div>
    <div class="stat"><p class="stat-label">Snitt vs. billigste</p><p class="stat-value" style="color: ${diffColor};">${avgDiff > 0 ? '+' : ''}${avgDiff.toFixed(1)} %</p></div>
    <div class="stat"><p class="stat-label">Konkurrenter</p><p class="stat-value">${DATA.competitors.length}</p></div>
  `;

  // Tabell-header
  const head = document.getElementById('price-head');
  head.innerHTML = '<th>Produkt</th>' +
    DATA.competitor_names.map(n => `<th class="num">${n}</th>`).join('') +
    '<th class="num">Maxbo vs. min.</th>';

  // Tabell-body
  const body = document.getElementById('price-body');
  for (const p of DATA.products) {
    const valid = p.prices.filter(x => x !== null);
    const min = valid.length > 0 ? Math.min(...valid) : null;
    const cells = p.prices.map(px => {
      if (px === null) return '<td class="num missing">–</td>';
      const isMin = px === min;
      return `<td class="num ${isMin ? 'min' : ''}">${fmt(px)}</td>`;
    }).join('');

    let diffCell;
    const maxboPrice = p.prices[0];
    if (maxboPrice === null || min === null) {
      diffCell = '<td class="num missing">–</td>';
    } else if (maxboPrice === min) {
      diffCell = '<td class="num diff-cheap">Billigst</td>';
    } else {
      const diff = (maxboPrice - min) / min * 100;
      const cls = diff > 5 ? 'diff-high' : 'diff-mid';
      diffCell = `<td class="num ${cls}">+${diff.toFixed(1)} %</td>`;
    }

    body.insertAdjacentHTML('beforeend', `
      <tr>
        <td><div class="cat">${p.category}</div>${p.name}</td>
        ${cells}
        ${diffCell}
      </tr>
    `);
  }

  // Legend
  const legend = document.getElementById('legend');
  legend.innerHTML = DATA.competitor_names.map((n, i) =>
    `<span class="legend-item"><span class="swatch" style="background:${COLORS[i]};"></span>${n}</span>`
  ).join('');

  // Produkt-select
  const sel = document.getElementById('product-select');
  for (const p of DATA.products) {
    sel.insertAdjacentHTML('beforeend', `<option value="${p.id}">${p.name}</option>`);
  }

  let chart;
  function render(productId) {
    const p = DATA.products.find(x => x.id === productId);
    if (!p) return;
    const labels = p.history.map(h => {
      const [y, m, d] = h.date.split('-');
      return `${parseInt(d)}.${parseInt(m)}`;
    });
    const datasets = DATA.competitors.map((c, i) => ({
      label: DATA.competitor_names[i],
      data: p.history.map(h => h[c] ?? null),
      borderColor: COLORS[i],
      backgroundColor: COLORS[i],
      borderDash: DASHES[i],
      pointStyle: POINT_STYLES[i],
      spanGaps: true,
    }));

    if (chart) chart.destroy();
    chart = new Chart(document.getElementById('chart'), {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: c => c.dataset.label + ': ' + fmt(c.parsed.y) + ' kr' } }
        },
        scales: {
          x: { ticks: { font: { size: 11 } }, grid: { display: false } },
          y: { ticks: { font: { size: 11 }, callback: v => fmt(v) + ' kr' },
               grid: { color: 'rgba(128,128,128,0.1)' } }
        },
        elements: { point: { radius: 2, hoverRadius: 5 }, line: { borderWidth: 2, tension: 0.2 } }
      }
    });
  }

  sel.addEventListener('change', e => render(e.target.value));
  if (DATA.products.length > 0) render(DATA.products[0].id);
}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
"""


def main():
    OUT_DIR.mkdir(exist_ok=True)
    init_db()
    data = build_data()
    html = HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", json.dumps(data, ensure_ascii=False))
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"Skrev {OUT_FILE} ({OUT_FILE.stat().st_size:,} bytes)")
    print(f"Oppsummering: {len(data['products'])} produkter, oppdatert {data['updated']}")


if __name__ == "__main__":
    main()
