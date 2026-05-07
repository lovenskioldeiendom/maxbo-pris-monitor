"""
Produktkatalog. En entry per produkt, med URL eller søkebegrep per kjede.

Når noe er None, hopper scraperen over den kombinasjonen og logger den som "manglende".
Du fyller inn etter hvert som du finner produktene hos hver kjede.

Tips for å finne URLer:
1. Gå til kjedens nettside, søk etter produktet, kopier URL fra produktsiden
2. Hvis kjeden krever postnummer, lagre URL som inkluderer postnummeret
3. Test scraperen lokalt med "python -m scrapers.maxbo TERRASSEBORD" før du commiter
"""

PRODUCTS = [
    {
        "id": "virke-48x98-c24",
        "category": "Trelast",
        "name": "Konstruksjonsvirke C24 48x98 ubehandlet gran",
        "unit": "lm",
        "urls": {
            "maxbo": "https://www.maxbo.no/konstruksjonsvirke-ubehandlet-gran-p914628/",       # TODO: finn på maxbo.no
            "byggmakker": "https://www.byggmakker.no/produkt/gran-48x098-k-virke-c24/7070276013922",  # TODO
            "monter": "https://www.monter.no/trelast/konstruksjonsvirke/ubehandlet-konstruksjonsvirke/konstruksjonsvirke-c24-gran-ubehandlet-48x98-mm",      # TODO
            "obs_bygg": "https://www.obsbygg.no/trelast-og-tyngre-byggevarer/treverk/konstruksjonsvirke/ubehandlet-konstruksjonsvirke/3019536?v=ObsBygg-7040431808410",    # TODO
            "xl_bygg": "https://www.xl-bygg.no/product/moelven-gran-48x098-k-virke-c24-54262933",     # TODO
        },
    },
    {
        "id": "terrassebord-28x120-royal-brun",
        "category": "Trelast",
        "name": "Terrassebord 28x120 royalimpregnert brun",
        "unit": "stk",
        "urls": {
            # Disse fant jeg ved web-søk; de er sannsynlig riktige men bør verifiseres
            "maxbo": "https://www.maxbo.no/terrassebord-royal-oljet-furu-p450302/",
            "byggmakker": "https://www.byggmakker.no/produkt/terrassebord-furu-28x120-duo-brun-royal-moreroyal/7071536012945",
            "monter": None,      # TODO
            "obs_bygg": None,    # TODO
            "xl_bygg": None,     # TODO
        },
    },
    {
        "id": "gipsplate-13mm",
        "category": "Trelast",
        "name": "Gipsplate 13mm 1200x2400",
        "unit": "stk",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "osb-12mm",
        "category": "Trelast",
        "name": "OSB-plate 12mm 1200x2400",
        "unit": "stk",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "stolpe-98x98-tryk",
        "category": "Trelast",
        "name": "Trykkimpregnert stolpe 98x98 3,0m",
        "unit": "stk",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "mineralull-70mm",
        "category": "Isolasjon",
        "name": "Mineralull 70mm glassull",
        "unit": "pakke",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "sement-25kg",
        "category": "Tørrvarer",
        "name": "Norcem Standardsement 25kg",
        "unit": "sekk",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "skruer-terrasse-a4",
        "category": "Skruer",
        "name": "Terrasseskruer A4 4,2x55, 250 stk",
        "unit": "eske",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "skruer-trekonstr-6x80",
        "category": "Skruer",
        "name": "Trekonstruksjonsskruer 6,0x80, 100 stk",
        "unit": "eske",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "maling-uten-10l",
        "category": "Maling",
        "name": "Utendørsmaling 10L hvit",
        "unit": "spann",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "maling-innen-10l",
        "category": "Maling",
        "name": "Innendørsmaling 10L glans 7",
        "unit": "spann",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "terrasseolje-3l",
        "category": "Olje",
        "name": "Terrasseolje 3L klar",
        "unit": "spann",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "drill-18v",
        "category": "Verktøy",
        "name": "Drill-kit 18V Bosch/Makita m/2 batt",
        "unit": "sett",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
    {
        "id": "gressklipper-bensin-46cm",
        "category": "Hage",
        "name": "Gressklipper bensin selvgående 46cm",
        "unit": "stk",
        "urls": {k: None for k in ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]},
    },
]

COMPETITORS = ["maxbo", "byggmakker", "monter", "obs_bygg", "xl_bygg"]
COMPETITOR_NAMES = {
    "maxbo": "Maxbo",
    "byggmakker": "Byggmakker",
    "monter": "Montér",
    "obs_bygg": "Obs Bygg",
    "xl_bygg": "XL-Bygg",
}
