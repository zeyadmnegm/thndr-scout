"""
The stock universe this scanner ranks.

There is no public API for THNDR's exact tradable catalog, so this is a
curated list of liquid, well-known EGX-listed names (roughly the EGX30 +
notable EGX70 constituents) that are commonly available on THNDR. Yahoo
Finance tickers use the ".CA" suffix for Cairo-listed stocks.

>>> IMPORTANT: cross-check this list against what actually shows up in your
>>> THNDR app and edit freely. Adding/removing a row here is the only change
>>> needed for the scanner to pick it up.
"""

UNIVERSE = [
    {"ticker": "COMI.CA", "name": "Commercial International Bank", "sector": "Banks"},
    {"ticker": "HRHO.CA", "name": "EFG Hermes Holding", "sector": "Financial Services"},
    {"ticker": "TMGH.CA", "name": "Talaat Moustafa Group", "sector": "Real Estate"},
    {"ticker": "SWDY.CA", "name": "Elsewedy Electric", "sector": "Industrials"},
    {"ticker": "EAST.CA", "name": "Eastern Company", "sector": "Consumer Goods"},
    {"ticker": "ETEL.CA", "name": "Telecom Egypt", "sector": "Telecom"},
    {"ticker": "ABUK.CA", "name": "Abu Qir Fertilizers", "sector": "Chemicals"},
    {"ticker": "MFPC.CA", "name": "Misr Fertilizers Production (MOPCO)", "sector": "Chemicals"},
    {"ticker": "EFIH.CA", "name": "e-Finance Investment Group", "sector": "Fintech"},
    {"ticker": "FWRY.CA", "name": "Fawry for Banking Technology", "sector": "Fintech"},
    {"ticker": "EKHO.CA", "name": "Egypt Kuwait Holding", "sector": "Holding"},
    {"ticker": "CIEB.CA", "name": "Credit Agricole Egypt", "sector": "Banks"},
    {"ticker": "ADIB.CA", "name": "Abu Dhabi Islamic Bank Egypt", "sector": "Banks"},
    {"ticker": "SKPC.CA", "name": "Sidi Kerir Petrochemicals", "sector": "Chemicals"},
    {"ticker": "ISPH.CA", "name": "Ibnsina Pharma", "sector": "Healthcare"},
    {"ticker": "EGAL.CA", "name": "Egypt Aluminum", "sector": "Materials"},
    {"ticker": "QALAA.CA", "name": "Qalaa Holdings", "sector": "Holding"},
    {"ticker": "JUFO.CA", "name": "Juhayna Food Industries", "sector": "Consumer Goods"},
    {"ticker": "EFID.CA", "name": "Edita Food Industries", "sector": "Consumer Goods"},
    {"ticker": "RAYA.CA", "name": "Raya Holding", "sector": "Technology"},
    {"ticker": "PHDC.CA", "name": "Palm Hills Developments", "sector": "Real Estate"},
    {"ticker": "AMOC.CA", "name": "Alexandria Mineral Oils Company", "sector": "Energy"},
    {"ticker": "HELI.CA", "name": "Heliopolis Housing", "sector": "Real Estate"},
    {"ticker": "OCDI.CA", "name": "Sixth of October Development (SODIC)", "sector": "Real Estate"},
    {"ticker": "MNHD.CA", "name": "Madinet Nasr Housing", "sector": "Real Estate"},
    {"ticker": "ACGC.CA", "name": "Arabian Cement", "sector": "Materials"},
    {"ticker": "ESRS.CA", "name": "Ezz Steel", "sector": "Materials"},
    {"ticker": "MTIE.CA", "name": "MM Group for Industry and Trade", "sector": "Industrials"},
    {"ticker": "ORHD.CA", "name": "Orascom Development Egypt", "sector": "Real Estate"},
    {"ticker": "CCAP.CA", "name": "Citadel Capital", "sector": "Financial Services"},
]
