"""
🚀 SCRAPER BDE HELLOASSO - TOUTES LES PAGES (0 à 29)
Utilise l'URL correcte trouvée par l'utilisateur
URL: https://www.helloasso.com/e/recherche/associations?page={i}&category_tags=bde
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
BASE_URL = "https://www.helloasso.com/e/recherche/associations"
SEARCH_PARAMS = "category_tags=bde"
OUTPUT_FILENAME = "bde_scraping_all_pages"
DELAY_BETWEEN_REQUESTS = 2
TOTAL_PAGES = 30  # Pages 0 à 29 = 30 pages

class BDEScraperAllPages:
    def __init__(self):
        self.driver = None
        self.bde_data = []
        
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
        Génère l'URL pour une page spécifique (0 à 29)
        """
        return f"{BASE_URL}?page={page_number}&{SEARCH_PARAMS}"
    
    def get_bde_links_from_page(self, page_number):
        """
        Extrait tous les liens des BDE présents sur la page spécifiée
        """
        try:
            url = self.get_page_url(page_number)
            print(f"🔗 Accès à la page {page_number} : {url}")
            
            self.driver.get(url)
            time.sleep(3)
            
            # Différents sélecteurs possibles pour les liens des BDE
            selectors = [
                "a[href*='/associations/']",
                ".association-card a",
                ".card a[href*='associations']",
                "a[href*='bde']",
                ".result-item a",
                ".search-result a"
            ]
            
            all_links = []
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and '/associations/' in href and href not in all_links:
                            all_links.append(href)
                except:
                    continue
            
            # Supprimer les doublons et filtrer
            unique_links = list(set(all_links))
            
            print(f"🔗 {len(unique_links)} liens BDE uniques trouvés sur la page {page_number}")
            return unique_links
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des liens page {page_number} : {str(e)}")
            return []
    
    def extract_bde_details(self, bde_url):
        """
        Extrait les détails d'un BDE spécifique
        """
        try:
            print(f"📄 Extraction : {bde_url}")
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
                        if name and name != "HelloAsso":
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
                    # Filtrer les emails valides
                    valid_emails = []
                    for email in emails:
                        if not any(x in email.lower() for x in ['noreply', 'no-reply', 'support', 'admin', 'info@helloasso', 'contact@helloasso']):
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
            print(f"   ✅ {bde_info.get('nom_ecole', 'Nom non trouvé')}")
            if bde_info.get('email'):
                print(f"   📧 {bde_info['email']}")
            
            return bde_info
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'extraction : {str(e)}")
            return None
    
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
            
            return filename
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {str(e)}")
            return False
    
    def run_scraping_all_pages(self, start_page=0, end_page=29):
        """
        Lance le scraping de toutes les pages
        """
        print("🚀 DÉBUT DU SCRAPING COMPLET DES BDE")
        print(f"📄 Scraping des pages {start_page} à {end_page} ({end_page - start_page + 1} pages)")
        print(f"🔗 URL de base : {BASE_URL}?page={{i}}&{SEARCH_PARAMS}")
        
        try:
            self.setup_driver()
            
            total_scraped = 0
            
            for page_num in range(start_page, end_page + 1):
                print(f"\n📄 === PAGE {page_num} ===")
                
                # Extraction des liens de la page courante
                bde_links = self.get_bde_links_from_page(page_num)
                
                if not bde_links:
                    print(f"❌ Aucun BDE trouvé sur la page {page_num}")
                    continue
                
                # Traitement de chaque BDE
                print(f"🔄 Traitement de {len(bde_links)} BDE...")
                
                for i, bde_url in enumerate(tqdm(bde_links, desc=f"Page {page_num}")):
                    print(f"\n   📄 BDE {i+1}/{len(bde_links)}")
                    
                    # Extraction des détails
                    bde_info = self.extract_bde_details(bde_url)
                    if bde_info:
                        self.bde_data.append(bde_info)
                        total_scraped += 1
                    
                    # Délai entre les requêtes
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                
                print(f"✅ Page {page_num} terminée - {len(bde_links)} BDE traités")
                print(f"📊 Total cumulé : {total_scraped} BDE")
            
            # Sauvegarde des données
            print(f"\n💾 SAUVEGARDE DES DONNÉES")
            filename = self.save_to_csv()
            
            print(f"\n✅ SCRAPING COMPLET TERMINÉ !")
            print(f"📊 {len(self.bde_data)} BDE traités au total")
            print(f"📁 Fichier généré : {filename}")
            
            return filename
            
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE : {str(e)}")
            
        finally:
            # Fermeture du navigateur
            if self.driver:
                print("\n🔒 Fermeture du navigateur...")
                self.driver.quit()

def main():
    """
    Fonction principale
    """
    print("=" * 60)
    print("🎓 SCRAPER BDE HELLOASSO - TOUTES LES PAGES")
    print("=" * 60)
    
    # Création et lancement du scraper
    scraper = BDEScraperAllPages()
    
    # Lancement du scraping complet (pages 0 à 29)
    scraper.run_scraping_all_pages(start_page=0, end_page=29)
    
    print("\n" + "=" * 60)
    print("✅ FIN DU PROGRAMME")
    print("=" * 60)

if __name__ == "__main__":
    main() 