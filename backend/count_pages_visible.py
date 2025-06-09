"""
Script pour compter les pages avec navigateur visible
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from config import BASE_URL, SEARCH_PARAMS

def count_pages_visible():
    """
    Compte les pages avec navigateur visible pour debug
    """
    print("🚀 Configuration du navigateur visible...")
    chrome_options = Options()
    # Pas de headless pour voir ce qui se passe
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}"
        print(f"🔍 Ouverture de : {url}")
        
        driver.get(url)
        time.sleep(5)  # Laisse plus de temps pour charger
        
        print("📊 Analyse de la page...")
        
        # Prendre une capture d'écran pour debug
        driver.save_screenshot("data/debug_page.png")
        print("📸 Capture d'écran sauvée : data/debug_page.png")
        
        # Chercher tous les liens
        all_links = driver.find_elements(By.TAG_NAME, "a")
        association_links = [link for link in all_links if 'association' in link.get_attribute('href') or '']
        
        print(f"🔗 {len(all_links)} liens trouvés au total")
        print(f"🏫 {len(association_links)} liens d'associations trouvés")
        
        # Afficher quelques liens pour debug
        print("\n📋 Premiers liens d'associations :")
        for i, link in enumerate(association_links[:5]):
            href = link.get_attribute('href')
            text = link.text.strip()
            print(f"  {i+1}. {text} -> {href}")
        
        # Chercher les éléments de pagination
        print("\n📄 Recherche de pagination...")
        all_text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'page') or contains(text(), 'Page') or contains(text(), 'suivant') or contains(text(), 'Suivant')]")
        
        for elem in all_text_elements:
            print(f"📝 Élément trouvé : '{elem.text.strip()}'")
        
        # Chercher des boutons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n🔘 {len(buttons)} boutons trouvés")
        for i, button in enumerate(buttons[:10]):  # Limite à 10 pour ne pas spammer
            text = button.text.strip()
            if text:
                print(f"  Bouton {i+1}: '{text}'")
        
        print("\n⏳ Attente de 10 secondes pour que tu puisses voir la page...")
        time.sleep(10)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    count_pages_visible() 