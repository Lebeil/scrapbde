"""
Analyse de HelloAsso avec Selenium
Script pour débutant utilisant un navigateur automatisé
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
from config import BASE_URL, SEARCH_PARAMS

def setup_driver():
    """
    Configure et lance le navigateur Chrome avec Selenium
    """
    print("🚀 Configuration du navigateur Chrome...")
    
    # Options pour Chrome (pour optimiser et éviter la détection)
    chrome_options = Options()
    
    # Désactive certaines fonctionnalités pour être plus discret
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Headers réalistes
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Désactive les notifications et popups
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Pour éviter les problèmes de certificats
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Installation automatique du driver Chrome
    service = Service(ChromeDriverManager().install())
    
    # Création du driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Supprime la bannière "Chrome est contrôlé par un logiciel automatisé"
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("✅ Navigateur Chrome configuré avec succès !")
    return driver

def analyser_helloasso_selenium():
    """
    Analyse HelloAsso avec Selenium pour comprendre la structure
    """
    driver = None
    
    try:
        # Configuration du navigateur
        driver = setup_driver()
        
        # Construction de l'URL
        url = f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}"
        print(f"\n📌 Accès à la page : {url}")
        
        # Navigation vers la page
        driver.get(url)
        print("✅ Page chargée avec succès !")
        
        # Attendre que la page se charge complètement
        print("⏳ Attente du chargement de la page...")
        time.sleep(5)  # Attendre 5 secondes pour que le JavaScript se charge
        
        # Récupérer des informations sur la page
        page_title = driver.title
        current_url = driver.current_url
        page_source_length = len(driver.page_source)
        
        print(f"\n📊 INFORMATIONS DE LA PAGE :")
        print(f"   - Titre : {page_title}")
        print(f"   - URL actuelle : {current_url}")
        print(f"   - Taille du HTML : {page_source_length} caractères")
        
        # Recherche d'éléments d'associations avec différents sélecteurs
        print(f"\n🔍 RECHERCHE D'ÉLÉMENTS D'ASSOCIATIONS :")
        
        selectors_to_test = [
            # Sélecteurs CSS communs pour HelloAsso
            "div[class*='association']",
            "div[class*='card']",
            "div[class*='result']", 
            "div[class*='organization']",
            "article",
            ".card",
            "[data-testid*='association']",
            "[data-testid*='organization']",
            "a[href*='association']"
        ]
        
        elements_found = {}
        
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    elements_found[selector] = len(elements)
                    print(f"   ✅ {len(elements)} éléments trouvés avec : {selector}")
                    
                    # Analyse du premier élément
                    if elements:
                        first_element = elements[0]
                        element_text = first_element.text[:200].replace('\n', ' ').strip()
                        element_classes = first_element.get_attribute('class')
                        print(f"      Classes CSS : {element_classes}")
                        print(f"      Texte (extrait) : {element_text}...")
                else:
                    print(f"   ❌ Aucun élément avec : {selector}")
                    
            except Exception as e:
                print(f"   ⚠️ Erreur avec le sélecteur {selector}: {str(e)}")
        
        # Recherche de liens vers des pages d'associations
        print(f"\n🔗 RECHERCHE DE LIENS D'ASSOCIATIONS :")
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            association_links = []
            
            for link in all_links:
                href = link.get_attribute('href')
                if href and any(keyword in href.lower() for keyword in ['association', 'organization', 'bde']):
                    link_text = link.text.strip()[:100]
                    association_links.append({
                        'url': href,
                        'text': link_text
                    })
            
            print(f"   📄 {len(association_links)} liens d'associations trouvés")
            
            # Affichage des premiers liens
            for i, link in enumerate(association_links[:5]):
                print(f"      {i+1}. {link['url']} - {link['text']}")
                
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la recherche de liens : {str(e)}")
        
        # Recherche de pagination ou bouton "Voir plus"
        print(f"\n📄 RECHERCHE DE PAGINATION :")
        pagination_selectors = [
            "nav[class*='pagination']",
            "button[class*='load']",
            "button[class*='more']", 
            "button[class*='next']",
            ".pagination"
        ]
        
        for selector in pagination_selectors:
            try:
                pagination_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if pagination_elements:
                    print(f"   ✅ Pagination trouvée avec : {selector}")
                    print(f"      Nombre d'éléments : {len(pagination_elements)}")
            except Exception as e:
                print(f"   ⚠️ Erreur pagination avec {selector}: {str(e)}")
        
        # Sauvegarde du HTML pour analyse manuelle
        with open('data/selenium_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"\n💾 HTML sauvegardé dans : data/selenium_page_source.html")
        
        # Sauvegarde des résultats d'analyse
        analysis_results = {
            'page_title': page_title,
            'current_url': current_url,
            'page_source_length': page_source_length,
            'elements_found': elements_found,
            'association_links_count': len(association_links) if 'association_links' in locals() else 0,
            'timestamp': time.time()
        }
        
        with open('data/selenium_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        print(f"💾 Résultats sauvegardés dans : data/selenium_analysis.json")
        
        # Faire une capture d'écran pour vérification visuelle
        driver.save_screenshot('data/helloasso_screenshot.png')
        print(f"📸 Capture d'écran sauvegardée : data/helloasso_screenshot.png")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {str(e)}")
        return False
        
    finally:
        # Fermeture du navigateur
        if driver:
            print("\n🔒 Fermeture du navigateur...")
            driver.quit()

if __name__ == "__main__":
    print("🚀 Analyse HelloAsso avec Selenium")
    print("⚠️ Un navigateur Chrome va s'ouvrir automatiquement")
    
    success = analyser_helloasso_selenium()
    
    if success:
        print("✅ Analyse terminée avec succès !")
        print("📁 Vérifiez les fichiers dans backend/data/ pour les résultats")
    else:
        print("❌ Analyse échouée - vérifiez les erreurs ci-dessus") 