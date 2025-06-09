"""
Script de test pour scraper toutes les pages et voir le total
"""

from scraper import BDEScraper

def test_full_scraping():
    """
    Teste le scraping complet de toutes les pages
    """
    print("🧪 TEST DU SCRAPING COMPLET")
    print("=" * 50)
    
    scraper = BDEScraper()
    
    # Lance le scraping de toutes les pages
    scraper.run_scraping(max_pages=None)
    
    print("=" * 50)
    print("🧪 FIN DU TEST")

if __name__ == "__main__":
    test_full_scraping() 