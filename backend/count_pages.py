"""
Script pour compter le nombre total de pages de BDE sur HelloAsso
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from config import BASE_URL, SEARCH_PARAMS

def setup_driver():
    """Configure le navigateur Chrome"""
    print("🚀 Configuration du navigateur...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode invisible pour aller plus vite
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def count_total_pages():
    """
    Compte le nombre total de pages disponibles
    """
    driver = setup_driver()
    
    try:
        # Construction de l'URL
        url = f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}"
        print(f"🔍 Analyse de : {url}")
        
        driver.get(url)
        time.sleep(3)
        
        # Chercher les informations de pagination
        print("📊 Recherche des informations de pagination...")
        
        # Méthode 1: Chercher le texte "résultats" ou "associations"
        try:
            # Cherche différents sélecteurs possibles pour le nombre de résultats
            selectors_to_try = [
                "[data-testid*='result']",
                "[class*='result']", 
                "[class*='count']",
                "p:contains('association')",
                "span:contains('résultat')",
                ".pagination",
                "[class*='pagination']"
            ]
            
            results_info = ""
            for selector in selectors_to_try:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and ('association' in text.lower() or 'résultat' in text.lower() or 'page' in text.lower()):
                            results_info += f"{text} | "
                except:
                    continue
                    
            print(f"📝 Textes trouvés : {results_info}")
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la recherche des résultats : {e}")
        
        # Méthode 2: Compter les liens d'associations sur la première page
        association_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='association']")
        results_per_page = len(association_links)
        print(f"📄 {results_per_page} associations trouvées sur la première page")
        
        # Méthode 3: Chercher les boutons de pagination
        try:
            pagination_elements = driver.find_elements(By.CSS_SELECTOR, "button, a")
            page_numbers = []
            
            for elem in pagination_elements:
                text = elem.text.strip()
                if text.isdigit():
                    page_numbers.append(int(text))
                elif "suivant" in text.lower() or "next" in text.lower():
                    print(f"✅ Bouton 'Suivant' trouvé : {text}")
                elif "précédent" in text.lower() or "prev" in text.lower():
                    print(f"✅ Bouton 'Précédent' trouvé : {text}")
            
            if page_numbers:
                max_page_visible = max(page_numbers)
                print(f"📄 Plus grand numéro de page visible : {max_page_visible}")
            else:
                print("📄 Aucun numéro de page trouvé dans la pagination")
                
        except Exception as e:
            print(f"⚠️  Erreur lors de l'analyse de la pagination : {e}")
        
        # Méthode 4: Test de navigation pour compter réellement
        print("\n🔍 Test de navigation pour compter les pages...")
        page_count = 1
        
        while page_count <= 10:  # Limite à 10 pour éviter les boucles infinies
            print(f"📄 Page {page_count} - {len(driver.find_elements(By.CSS_SELECTOR, 'a[href*=\"association\"]'))} associations")
            
            # Cherche le bouton "Suivant"
            try:
                next_button = None
                buttons = driver.find_elements(By.CSS_SELECTOR, "button, a")
                
                for button in buttons:
                    text = button.text.strip().lower()
                    if "suivant" in text or "next" in text or ">" in text:
                        if button.is_enabled() and button.is_displayed():
                            next_button = button
                            break
                
                if next_button:
                    print(f"✅ Bouton suivant trouvé, navigation vers page {page_count + 1}")
                    next_button.click()
                    time.sleep(3)
                    page_count += 1
                else:
                    print("🏁 Aucun bouton 'Suivant' actif trouvé - fin de la pagination")
                    break
                    
            except Exception as e:
                print(f"⚠️  Erreur lors de la navigation : {e}")
                break
        
        total_associations_estimated = results_per_page * page_count
        print(f"\n📊 RÉSUMÉ :")
        print(f"📄 Nombre de pages trouvées : {page_count}")
        print(f"🏫 Associations par page : ~{results_per_page}")
        print(f"🎯 Total estimé d'associations BDE : ~{total_associations_estimated}")
        
        return page_count, results_per_page, total_associations_estimated
        
    finally:
        driver.quit()

if __name__ == "__main__":
    count_total_pages() 