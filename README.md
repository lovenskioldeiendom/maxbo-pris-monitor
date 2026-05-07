# Maxbo prisovervåkning

Daglig sammenligning av priser hos Maxbo og fire konkurrenter (Byggmakker, Montér, Obs Bygg, XL-Bygg) på 14 standardvarer.

Kjøres automatisk hver morgen via GitHub Actions, og publiserer resultatet som et statisk dashbord på GitHub Pages.

## Komme i gang

### 1. Klon repoet og installer avhengigheter

```bash
git clone https://github.com/DITT-BRUKERNAVN/maxbo-pris-monitor.git
cd maxbo-pris-monitor
pip install -r requirements.txt
playwright install chromium
```

### 2. Fyll inn produkt-URLer

Åpne `products.py`. For hvert produkt og hver kjede må du legge inn URL-en til den faktiske produktsiden hos den kjeden.

Slik finner du URL-en:
1. Gå til kjedens nettside, søk etter produktet
2. Velg den produktvarianten som best matcher beskrivelsen
3. Kopier URL-en fra produktsiden
4. Lim inn i `products.py`

For produkter som ikke finnes hos en kjede (eller du ikke gidder å lete opp), la verdien stå som `None`. Scraperen logger det som "missing_url" og hopper over.

### 3. Test lokalt

```bash
# Test én kjede med synlig nettleser (for å se hva som skjer)
python run_scraper.py --competitor maxbo --no-headless

# Tørr-kjøring (ikke skriv til database)
python run_scraper.py --dry-run

# Full kjøring
python run_scraper.py

# Bygg dashbord
python build_dashboard.py

# Åpne dashboard/index.html i nettleser for å se resultatet
```

### 4. Tilpass CSS-selektorer

Første gangs kjøring vil sannsynligvis feile for noen kjeder fordi CSS-selektorene jeg har satt opp er kvalifiserte gjetninger. Slik fikser du:

1. Kjør med `--no-headless --competitor maxbo` (eller den kjeden som feiler)
2. Når nettleseren åpnes, høyreklikk på prisen → "Inspiser element"
3. Finn en CSS-selektor som er stabil (helst `data-testid` eller en klasse som ikke ser auto-generert ut)
4. Legg den til øverst i `price_selectors`-lista i `scrapers/MIN_KJEDE.py`

### 5. Sett opp GitHub Actions

1. Push repoet til GitHub
2. Gå til Settings → Actions → General → "Workflow permissions" → velg "Read and write permissions"
3. Gå til Settings → Pages → Source → velg "GitHub Actions"
4. Workflowen kjører automatisk hver morgen kl. 06:00. Du kan også trigge manuelt via "Actions"-fanen.

Etter første vellykkede kjøring publiseres dashbordet på `https://DITT-BRUKERNAVN.github.io/maxbo-pris-monitor/`.

## Filstruktur

```
maxbo-pris-monitor/
├── products.py             # Produktkatalog med URLer per kjede (rediger denne!)
├── database.py             # SQLite-håndtering
├── run_scraper.py          # Hovedskript
├── build_dashboard.py      # Genererer statisk HTML-dashbord
├── requirements.txt
├── pris_historikk.db       # SQLite-database (genereres ved første kjøring)
├── scrapers/
│   ├── base.py             # Felles scraper-logikk
│   ├── maxbo.py            # En modul per kjede
│   ├── byggmakker.py
│   ├── monter.py
│   ├── obs_bygg.py
│   └── xl_bygg.py
├── dashboard/
│   └── index.html          # Generert dashbord (publiseres på GitHub Pages)
└── .github/workflows/
    └── daily-scrape.yml    # GitHub Actions-konfigurasjon
```

## Vedlikehold

Scrapere er sårbare for endringer i nettsider. Forvent å måtte oppdatere CSS-selektorer 2-4 ganger i året per kjede. Når en kjede plutselig returnerer `null` for alle produkter, er det første du skal sjekke.

Hvis en kjede begynner å blokkere scraperen (Cloudflare-utfordring, CAPTCHAs), må du enten:
- Akseptere at den kjeden faller ut
- Implementere mer avansert anti-bot-omgåelse (residential proxies, stealth-plugins) — dette kan bryte deres ToS
- Switche til manuell prisregistrering for den kjeden

## Juridisk og etisk

Scraperen identifiserer seg som `MaxboPriceMonitor/1.0` i User-Agent. Den respekterer en pause på 3 sekunder mellom requests og henter bare offentlig tilgjengelige produktsider. Du bør lese hver kjedes brukervilkår før du kjører dette i lengre tid, særlig hvis du planlegger å bruke dataene kommersielt.

Verktøyet er laget for personlig prisoversikt og bør brukes deretter.
