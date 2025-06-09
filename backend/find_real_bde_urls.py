"""
🔍 RECHERCHE DES VRAIES URLs DE BDE SUR HELLOASSO
Script pour trouver les bonnes URLs et méthodes de recherche
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class BDEUrlFinder:
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        """Configure le navigateur"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def test_main_helloasso_site(self):
        """Test le site principal HelloAsso"""
        print("🔍 TEST DU SITE PRINCIPAL HELLOASSO")
        print("=" * 50)
        
        urls_to_test = [
            "https://www.helloasso.com",
            "https://helloasso.com",
            "https://www.helloasso.com/associations",
            "https://www.helloasso.com/associations/bde",
            "https://www.helloasso.com/discover",
            "https://www.helloasso.com/explorer",
            "https://www.helloasso.com/search"
        ]
        
        for url in urls_to_test:
            print(f"\n📌 Test : {url}")
            try:
                self.driver.get(url)
                time.sleep(3)
                
                final_url = self.driver.current_url
                print(f"   Redirection vers : {final_url}")
                
                # Chercher des liens d'associations
                association_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='associations']")
                print(f"   Liens d'associations trouvés : {len(association_links)}")
                
                # Chercher un champ de recherche
                search_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='search'], input[placeholder*='recherch'], input[name*='search'], input[name*='query']")
                print(f"   Champs de recherche trouvés : {len(search_inputs)}")
                
                if search_inputs:
                    print("   ✅ Champ de recherche détecté - tentative de recherche BDE")
                    try:
                        search_input = search_inputs[0]
                        search_input.clear()
                        search_input.send_keys("BDE")
                        search_input.send_keys(Keys.RETURN)
                        time.sleep(3)
                        
                        results_url = self.driver.current_url
                        print(f"   URL des résultats : {results_url}")
                        
                        result_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='associations']")
                        print(f"   Résultats de recherche : {len(result_links)} liens trouvés")
                        
                        # Analyser quelques résultats
                        for i, link in enumerate(result_links[:5]):
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            print(f"      {i+1}. {text[:50]}... -> {href}")
                    
                    except Exception as e:
                        print(f"   ❌ Erreur lors de la recherche : {str(e)}")
                
            except Exception as e:
                print(f"   ❌ Erreur : {str(e)}")
    
    def test_direct_bde_search(self):
        """Test de recherche directe de BDE"""
        print("\n\n🔍 TEST DE RECHERCHE DIRECTE BDE")
        print("=" * 50)
        
        # Aller sur la page principale
        self.driver.get("https://www.helloasso.com")
        time.sleep(3)
        
        print(f"Page actuelle : {self.driver.current_url}")
        
        # Essayer différents termes de recherche
        search_terms = [
            "BDE",
            "Bureau des étudiants", 
            "Bureau des élèves",
            "Association étudiante",
            "École",
            "Université"
        ]
        
        for term in search_terms:
            print(f"\n🔍 Recherche pour : '{term}'")
            
            # Construire l'URL de recherche
            search_urls = [
                f"https://www.helloasso.com/associations?q={term.replace(' ', '+')}",
                f"https://www.helloasso.com/search?q={term.replace(' ', '+')}",
                f"https://www.helloasso.com/explorer?search={term.replace(' ', '+')}",
                f"https://www.helloasso.com/associations/search?query={term.replace(' ', '+')}"
            ]
            
            for search_url in search_urls:
                try:
                    print(f"   📌 Test URL : {search_url}")
                    self.driver.get(search_url)
                    time.sleep(3)
                    
                    final_url = self.driver.current_url
                    if final_url != search_url:
                        print(f"   → Redirection vers : {final_url}")
                    
                    # Chercher des résultats
                    result_selectors = [
                        "a[href*='/associations/']",
                        ".association",
                        ".result",
                        ".card a",
                        ".search-result a"
                    ]
                    
                    total_results = 0
                    for selector in result_selectors:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            total_results = max(total_results, len(elements))
                    
                    print(f"   Résultats trouvés : {total_results}")
                    
                    if total_results > 0:
                        print("   ✅ URL PROMETTEUSE !")
                        return search_url
                    
                except Exception as e:
                    print(f"   ❌ Erreur : {str(e)}")
        
        return None
    
    def test_known_bde_urls(self):
        """Test avec des URLs de BDE connus"""
        print("\n\n🔍 TEST AVEC DES BDE CONNUS")
        print("=" * 50)
        
        # URLs de BDE trouvées dans nos précédents scrapings
        known_bde_urls = [
            "https://www.helloasso.com/associations/bde-la-fayette",
            "https://www.helloasso.com/associations/bde-eseo",
            "https://www.helloasso.com/associations/bde-ecole-superieure-du-digital",
            "https://www.helloasso.com/associations/bde-epsi-montpellier"
        ]
        
        for url in known_bde_urls:
            print(f"\n📌 Test BDE connu : {url}")
            try:
                self.driver.get(url)
                time.sleep(2)
                
                final_url = self.driver.current_url
                
                if "404" in self.driver.page_source or "not found" in self.driver.page_source.lower():
                    print("   ❌ BDE non trouvé (404)")
                else:
                    print("   ✅ BDE accessible !")
                    print(f"   URL finale : {final_url}")
                    
                    # Récupérer le titre
                    try:
                        title = self.driver.find_element(By.TAG_NAME, "title").get_attribute("textContent")
                        print(f"   Titre : {title}")
                    except:
                        pass
                    
                    # Chercher des liens vers d'autres BDE
                    other_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']")
                    if other_links:
                        print(f"   Autres associations liées : {len(other_links)}")
                    
            except Exception as e:
                print(f"   ❌ Erreur : {str(e)}")
    
    def explore_helloasso_api(self):
        """Explore les possibilités d'API HelloAsso"""
        print("\n\n🔍 EXPLORATION API HELLOASSO")
        print("=" * 50)
        
        # Tester des endpoints d'API potentiels
        api_urls = [
            "https://api.helloasso.com/v5/organizations",
            "https://api.helloasso.com/organizations",
            "https://www.helloasso.com/api/associations",
            "https://www.helloasso.com/api/v1/associations",
            "https://www.helloasso.com/api/search"
        ]
        
        for url in api_urls:
            print(f"\n📌 Test API : {url}")
            try:
                self.driver.get(url)
                time.sleep(2)
                
                page_source = self.driver.page_source
                
                if "json" in page_source.lower() or "{" in page_source:
                    print("   ✅ Possible endpoint API détecté !")
                    print(f"   Contenu (100 premiers caractères) : {page_source[:100]}")
                else:
                    print("   ❌ Pas de données JSON détectées")
                    
            except Exception as e:
                print(f"   ❌ Erreur : {str(e)}")
    
    def run_analysis(self):
        """Lance l'analyse complète"""
        try:
            self.setup_driver()
            
            self.test_main_helloasso_site()
            promising_url = self.test_direct_bde_search()
            self.test_known_bde_urls()
            self.explore_helloasso_api()
            
            if promising_url:
                print(f"\n🎯 URL PROMETTEUSE TROUVÉE : {promising_url}")
            else:
                print("\n❌ Aucune URL prometteuse trouvée")
            
        except Exception as e:
            print(f"❌ Erreur critique : {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()

def main():
    print("=" * 60)
    print("🔍 RECHERCHE DES VRAIES URLs BDE HELLOASSO")
    print("=" * 60)
    
    finder = BDEUrlFinder()
    finder.run_analysis()
    
    print("\n" + "=" * 60)
    print("✅ RECHERCHE TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main() 