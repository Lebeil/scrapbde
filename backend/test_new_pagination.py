"""
🧪 TEST DE LA NOUVELLE PAGINATION
Test des pages 0, 1, 2 pour valider l'approche
"""

from scraper_all_pages import BDEScraperAllPages

def test_pagination():
    """
    Teste les 3 premières pages pour valider l'approche
    """
    print("🧪 TEST DE LA NOUVELLE PAGINATION")
    print("=" * 50)
    print("📄 Test des pages 0, 1, 2")
    
    scraper = BDEScraperAllPages()
    
    # Test sur les 3 premières pages seulement
    filename = scraper.run_scraping_all_pages(start_page=0, end_page=2)
    
    if filename:
        print(f"\n🎯 RÉSULTAT DU TEST")
        print(f"📁 Fichier généré : {filename}")
        print(f"📊 Total BDE récupérés : {len(scraper.bde_data)}")
        
        if len(scraper.bde_data) > 0:
            print("✅ LA NOUVELLE PAGINATION FONCTIONNE !")
            print("🚀 Prêt pour le scraping complet des 30 pages")
        else:
            print("❌ Aucun BDE récupéré - vérifier l'URL")
    else:
        print("❌ Erreur lors du test")

if __name__ == "__main__":
    test_pagination() 