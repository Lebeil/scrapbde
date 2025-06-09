"""
🚀 SCRAPER BDE HELLOASSO - VERSION FORCÉE MULTI-PAGES
Auteur: Assistant IA
Description: Script pour scraper les BDE sur HelloAsso en forçant l'accès à toutes les pages
"""

import os
import time
import csv
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm

# Configuration
BASE_URL = "https://www.helloasso.com/associations"
SEARCH_PARAMS = {
    'category_tags': 'bde'
}
OUTPUT_FILENAME = "bde_scraping_results_forced"
DELAY_BETWEEN_REQUESTS = 2
MAX_PAGES_TO_TRY = 20  # On va essayer jusqu'à 20 pages

class BDEScraperForced:
    def __init__(self):
        self.driver = None
        self.bde_data = []
        self.current_page = 1
        
        # Création du dossier data
        os.makedirs('data', exist_ok=True)
    
    def setup_driver(self):
        """
        Configure le navigateur Chrome en mode headless
        """
        print("🔧 Configuration du navigateur...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Navigateur configuré avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de la configuration : {str(e)}")
            raise

    def get_page_url(self, page_number):
        """
        Génère l'URL pour une page spécifique
        """
        if page_number == 1:
            return f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}"
        else:
            # Différentes variations d'URL possible pour la pagination
            possible_urls = [
                f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}&page={page_number}",
                f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}&p={page_number}",
                f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}&offset={20*(page_number-1)}",
                f"{BASE_URL}/search?query=bde&page={page_number}",
                f"{BASE_URL}/search?q=bde&page={page_number}",
            ]
            return possible_urls
    
    def get_bde_links_from_page(self):
        """
        Extrait tous les liens des BDE présents sur la page actuelle
        """
        try:
            print("🔍 Recherche des BDE sur la page...")
            
            # Attendre que les éléments se chargent
            time.sleep(3)
            
            # Différents sélecteurs possibles pour les liens des BDE
            selectors = [
                "a[href*='/associations/']",
                ".association-card a",
                ".card a[href*='associations']",
                "a[href*='bde']",
                ".result-item a"
            ]
            
            all_links = []
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/associations/' in href and href not in all_links:
                            # Filtrer pour ne garder que les vrais liens de BDE
                            if any(keyword in href.lower() for keyword in ['bde', 'bureau', 'etudiant', 'eleve']):
                                all_links.append(href)
                except:
                    continue
            
            # Si on n'a pas trouvé avec les sélecteurs spécifiques, on prend tous les liens d'associations
            if not all_links:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']")
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and href not in all_links:
                            all_links.append(href)
                except:
                    pass
            
            print(f"🔗 {len(all_links)} liens trouvés sur cette page")
            return list(set(all_links))  # Supprimer les doublons
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des liens : {str(e)}")
            return []
    
    def extract_bde_details(self, bde_url):
        """
        Extrait les détails d'un BDE spécifique
        """
        try:
            print(f"📄 Extraction des détails pour : {bde_url}")
            self.driver.get(bde_url)
            time.sleep(2)
            
            # Structure de base des informations BDE
            bde_info = {
                'nom_ecole': '',
                'nom_personne': '',
                'prenom_personne': '',
                'adresse': '',
                'site_internet': '',
                'telephone': '',
                'email': '',
                'url_source': bde_url
            }
            
            # Extraction du nom de l'école/BDE
            try:
                selectors = ["h1", ".title", ".name", ".association-name", "title"]
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        name = elements[0].text.strip()
                        if name:
                            bde_info['nom_ecole'] = name
                            break
            except:
                pass
            
            # Extraction de l'email
            try:
                page_source = self.driver.page_source
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, page_source)
                if emails:
                    # Filtrer les emails valides et éviter les emails techniques
                    valid_emails = []
                    for email in emails:
                        if not any(x in email.lower() for x in ['noreply', 'no-reply', 'support', 'admin', 'info@helloasso']):
                            valid_emails.append(email)
                    if valid_emails:
                        bde_info['email'] = valid_emails[0]
            except:
                pass
            
            # Extraction du téléphone
            try:
                page_text = self.driver.page_source
                phone_patterns = [
                    r'(?:(?:\+33|0)[1-9](?:[0-9]{8}))',
                    r'(?:0[1-9](?:\s?\d{2}){4})',
                    r'(?:\+33\s?[1-9](?:\s?\d{2}){4})'
                ]
                
                for pattern in phone_patterns:
                    phone_matches = re.findall(pattern, page_text)
                    if phone_matches:
                        bde_info['telephone'] = phone_matches[0].strip()
                        break
            except:
                pass
            
            # Extraction du site internet
            try:
                external_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
                for link in external_links:
                    href = link.get_attribute('href')
                    if href and 'helloasso.com' not in href:
                        social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']
                        if not any(domain in href for domain in social_domains):
                            bde_info['site_internet'] = href
                            break
            except:
                pass
            
            # Extraction de l'adresse
            try:
                page_text = self.driver.page_source
                # Patterns pour adresses françaises
                address_patterns = [
                    r'\d+[,\s]+(?:rue|avenue|boulevard|place|impasse|allée)[^,\n]+(?:\d{5})[^,\n]*',
                    r'(?:rue|avenue|boulevard|place|impasse|allée)[^,\n]+(?:\d{5})[^,\n]*'
                ]
                
                for pattern in address_patterns:
                    addresses = re.findall(pattern, page_text, re.IGNORECASE)
                    if addresses:
                        bde_info['adresse'] = addresses[0].strip()
                        break
            except:
                pass
            
            # Affichage des informations extraites
            print(f"   ✅ Données extraites :")
            for key, value in bde_info.items():
                if value and key != 'url_source':
                    print(f"      {key}: {value}")
            
            return bde_info
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'extraction : {str(e)}")
            return None
    
    def check_page_exists(self, page_url):
        """
        Vérifie si une page existe et contient du contenu
        """
        try:
            self.driver.get(page_url)
            time.sleep(2)
            
            # Vérifier si la page contient des associations
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']")
            return len(elements) > 0
            
        except Exception as e:
            print(f"   ❌ Erreur lors de la vérification de la page : {str(e)}")
            return False
    
    def save_to_csv(self):
        """
        Sauvegarde les données en format CSV
        """
        if not self.bde_data:
            print("❌ Aucune donnée à sauvegarder")
            return False
            
        try:
            df = pd.DataFrame(self.bde_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/{OUTPUT_FILENAME}_{timestamp}.csv"
            
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"💾 Données sauvegardées dans : {filename}")
            print(f"📊 Total : {len(self.bde_data)} BDE scrapés")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {str(e)}")
            return False
    
    def run_forced_scraping(self, start_page=2, max_pages=MAX_PAGES_TO_TRY):
        """
        Lance le scraping forcé à partir d'une page donnée
        """
        print("🚀 DÉBUT DU SCRAPING FORCÉ DES BDE")
        print(f"📄 Pages {start_page} à {max_pages}")
        
        try:
            self.setup_driver()
            
            for page_num in range(start_page, max_pages + 1):
                print(f"\n📄 === PAGE {page_num} ===")
                
                # Essayer différentes variations d'URL pour cette page
                page_urls = self.get_page_url(page_num)
                
                # Si c'est la page 1, on a une seule URL
                if isinstance(page_urls, str):
                    page_urls = [page_urls]
                
                page_found = False
                bde_links = []
                
                for url in page_urls:
                    print(f"🔗 Tentative : {url}")
                    
                    if self.check_page_exists(url):
                        print("✅ Page trouvée !")
                        bde_links = self.get_bde_links_from_page()
                        if bde_links:
                            page_found = True
                            break
                    else:
                        print("❌ Page non trouvée ou vide")
                
                if not page_found or not bde_links:
                    print(f"📄 Page {page_num} : Aucun contenu trouvé")
                    continue
                
                # Traitement des BDE trouvés
                print(f"🔄 Traitement de {len(bde_links)} BDE...")
                
                for i, bde_url in enumerate(tqdm(bde_links, desc=f"Page {page_num}")):
                    print(f"\n   📄 BDE {i+1}/{len(bde_links)}")
                    
                    bde_info = self.extract_bde_details(bde_url)
                    if bde_info:
                        self.bde_data.append(bde_info)
                    
                    time.sleep(DELAY_BETWEEN_REQUESTS)
            
            # Sauvegarde finale
            print(f"\n💾 SAUVEGARDE DES DONNÉES")
            self.save_to_csv()
            
            print(f"\n✅ SCRAPING FORCÉ TERMINÉ !")
            print(f"📊 {len(self.bde_data)} BDE traités au total")
            
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE : {str(e)}")
            
        finally:
            if self.driver:
                print("\n🔒 Fermeture du navigateur...")
                self.driver.quit()

def main():
    """
    Fonction principale
    """
    print("=" * 60)
    print("🎓 SCRAPER BDE HELLOASSO - FORÇAGE MULTI-PAGES")
    print("=" * 60)
    
    scraper = BDEScraperForced()
    
    # Lancement du scraping forcé à partir de la page 2
    scraper.run_forced_scraping(start_page=2, max_pages=10)
    
    print("\n" + "=" * 60)
    print("✅ FIN DU PROGRAMME")
    print("=" * 60)

if __name__ == "__main__":
    main() 