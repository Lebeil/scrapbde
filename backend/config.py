"""
Configuration pour le scraping des BDE sur HelloAsso
Fichier de configuration centralisé pour un débutant
"""

# URL de base du site à scraper
BASE_URL = "https://www.helloasso.com/e/recherche/associations"
SEARCH_PARAMS = {
    "category_tags": "bde"
}

# Paramètres de scraping - Headers plus récents et réalistes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate", 
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

# Délais entre les requêtes (en secondes) - important pour être poli !
DELAY_BETWEEN_REQUESTS = 2

# Nom du fichier de sortie
OUTPUT_FILENAME = "bde_scraping_results"

# Colonnes à extraire
COLUMNS = [
    "nom_ecole",
    "nom_personne", 
    "prenom_personne",
    "adresse",
    "site_internet",
    "telephone",
    "email"
]

# Configuration Google Sheets (à remplir plus tard)
GOOGLE_SHEETS_CONFIG = {
    "spreadsheet_name": "BDE Scraping Results",
    "worksheet_name": "Données BDE"
} 