"""
🔍 ANALYSE DE LA PAGINATION HELLOASSO
Script pour analyser la structure de pagination et comprendre pourquoi il n'y a qu'une page
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PaginationAnalyzer:
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
    
    def analyze_page_structure(self):
        """Analyse la structure de la page principale"""
        print("🔍 ANALYSE DE LA PAGE PRINCIPALE")
        print("=" * 50)
        
        url = "https://www.helloasso.com/associations?category_tags=bde"
        print(f"📌 URL analysée : {url}")
        
        self.driver.get(url)
        time.sleep(5)
        
        # 1. Compter le nombre total d'associations
        print("\n📊 COMPTAGE DES ASSOCIATIONS")
        association_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']")
        print(f"   Total de liens d'associations trouvés : {len(association_links)}")
        
        # 2. Analyser les éléments de pagination
        print("\n🔄 ANALYSE DES ÉLÉMENTS DE PAGINATION")
        
        pagination_selectors = [
            "nav[aria-label*='pagination']",
            ".pagination",
            "button[aria-label*='next']",
            "button[aria-label*='suivant']",
            "a[aria-label*='next']",
            "a[aria-label*='suivant']",
            ".next-page",
            ".page-next",
            "[data-testid*='pagination']",
            ".btn-next"
        ]
        
        for selector in pagination_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ✅ Trouvé {len(elements)} éléments avec sélecteur '{selector}'")
                for i, elem in enumerate(elements):
                    try:
                        text = elem.text.strip()
                        href = elem.get_attribute('href')
                        disabled = elem.get_attribute('disabled')
                        print(f"      - Élément {i+1}: text='{text}', href='{href}', disabled='{disabled}'")
                    except:
                        print(f"      - Élément {i+1}: Erreur lors de la lecture des attributs")
            else:
                print(f"   ❌ Aucun élément trouvé avec sélecteur '{selector}'")
        
        # 3. Rechercher des indices de pagination dans le HTML
        print("\n🔍 RECHERCHE DANS LE CODE SOURCE")
        page_source = self.driver.page_source.lower()
        
        pagination_keywords = [
            'page', 'next', 'suivant', 'previous', 'précédent', 
            'pagination', 'load more', 'charger plus', 'voir plus',
            'offset', 'limit', 'per_page', 'page_size'
        ]
        
        for keyword in pagination_keywords:
            if keyword in page_source:
                print(f"   ✅ Mot-clé '{keyword}' trouvé dans le code source")
            else:
                print(f"   ❌ Mot-clé '{keyword}' NON trouvé")
        
        # 4. Analyser les scripts JavaScript pour la pagination
        print("\n📜 ANALYSE DES SCRIPTS JAVASCRIPT")
        script_elements = self.driver.find_elements(By.TAG_NAME, "script")
        
        js_pagination_keywords = [
            'pagination', 'loadMore', 'nextPage', 'offset', 'limit',
            'infiniteScroll', 'lazy', 'async'
        ]
        
        for i, script in enumerate(script_elements[:10]):  # Analyser les 10 premiers scripts
            try:
                script_content = script.get_attribute('innerHTML')
                if script_content:
                    for keyword in js_pagination_keywords:
                        if keyword.lower() in script_content.lower():
                            print(f"   ✅ Script {i+1}: Contient '{keyword}'")
                            break
            except:
                continue
        
        # 5. Vérifier s'il y a des paramètres d'URL existants
        print("\n🔗 ANALYSE DE L'URL ACTUELLE")
        current_url = self.driver.current_url
        print(f"   URL après chargement : {current_url}")
        
        if '?' in current_url:
            params = current_url.split('?')[1]
            print(f"   Paramètres actuels : {params}")
        else:
            print("   Aucun paramètre dans l'URL")
        
        # 6. Tester le scroll infini
        print("\n📜 TEST DU SCROLL INFINI")
        initial_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']"))
        print(f"   Nombre initial d'associations : {initial_count}")
        
        # Scroll vers le bas
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        after_scroll_count = len(self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']"))
        print(f"   Nombre après scroll : {after_scroll_count}")
        
        if after_scroll_count > initial_count:
            print("   ✅ Le scroll infini semble actif !")
        else:
            print("   ❌ Pas de scroll infini détecté")
        
        # 7. Analyser les boutons "Voir plus" ou "Charger plus"
        print("\n🔄 RECHERCHE DE BOUTONS 'VOIR PLUS'")
        load_more_selectors = [
            "button[data-testid*='load']",
            "button[data-testid*='more']",
            "button:contains('Voir plus')",
            "button:contains('Charger plus')",
            "button:contains('Load more')",
            ".load-more",
            ".btn-load-more",
            "[data-action*='load']"
        ]
        
        for selector in load_more_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"   ✅ Trouvé {len(elements)} boutons avec sélecteur '{selector}'")
                for elem in elements:
                    try:
                        text = elem.text.strip()
                        print(f"      - Texte du bouton : '{text}'")
                    except:
                        print("      - Erreur lors de la lecture du texte")
    
    def test_different_search_urls(self):
        """Teste différentes façons de chercher les BDE"""
        print("\n\n🔍 TEST DE DIFFÉRENTES APPROCHES DE RECHERCHE")
        print("=" * 50)
        
        search_urls = [
            "https://www.helloasso.com/associations?q=bde",
            "https://www.helloasso.com/associations?search=bde",
            "https://www.helloasso.com/associations?query=bde", 
            "https://www.helloasso.com/associations?tag=bde",
            "https://www.helloasso.com/associations?tags=bde",
            "https://www.helloasso.com/associations?category=bde",
            "https://www.helloasso.com/associations/search?q=bde",
            "https://www.helloasso.com/search?type=associations&q=bde"
        ]
        
        for url in search_urls:
            print(f"\n📌 Test : {url}")
            try:
                self.driver.get(url)
                time.sleep(3)
                
                association_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']")
                print(f"   Résultats : {len(association_links)} associations trouvées")
                
                if len(association_links) > 0:
                    # Vérifier si on a des BDE
                    bde_count = 0
                    for link in association_links[:5]:  # Vérifier les 5 premiers
                        href = link.get_attribute('href')
                        if href and any(keyword in href.lower() for keyword in ['bde', 'bureau', 'etudiant']):
                            bde_count += 1
                    print(f"   BDE potentiels : {bde_count}/5 dans les premiers résultats")
                
            except Exception as e:
                print(f"   ❌ Erreur : {str(e)}")
    
    def run_analysis(self):
        """Lance l'analyse complète"""
        try:
            self.setup_driver()
            self.analyze_page_structure()
            self.test_different_search_urls()
            
        except Exception as e:
            print(f"❌ Erreur critique : {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()

def main():
    print("=" * 60)
    print("🔍 ANALYSEUR DE PAGINATION HELLOASSO")
    print("=" * 60)
    
    analyzer = PaginationAnalyzer()
    analyzer.run_analysis()
    
    print("\n" + "=" * 60)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main() 