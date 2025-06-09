"""
Script principal de scraping des BDE sur HelloAsso
Scraper complet pour débutant avec Selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
from datetime import datetime
from tqdm import tqdm
from config import BASE_URL, SEARCH_PARAMS, DELAY_BETWEEN_REQUESTS, COLUMNS, OUTPUT_FILENAME

class BDEScraper:
    """
    Classe principale pour scraper les BDE sur HelloAsso
    """
    
    def __init__(self):
        """
        Initialisation du scraper
        """
        self.driver = None
        self.bde_data = []  # Liste pour stocker toutes les données
        self.processed_urls = set()  # Pour éviter les doublons
        
    def setup_driver(self):
        """
        Configure et lance le navigateur Chrome
        """
        print("🚀 Configuration du navigateur Chrome...")
        
        chrome_options = Options()
        
        # Options pour être plus discret
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent réaliste
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Désactive certaines fonctionnalités
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--ignore-certificate-errors")
        
        # Installation automatique du driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Supprime les signes d'automation
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Navigateur configuré avec succès !")
        
    def get_bde_links_from_page(self):
        """
        Extrait tous les liens des BDE depuis la page courante
        """
        print("🔍 Extraction des liens BDE de la page courante...")
        
        # Attendre que la page se charge
        time.sleep(3)
        
        # Recherche de tous les liens d'associations
        try:
            # Sélecteur pour les liens d'associations BDE
            association_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/associations/']")
            
            bde_links = []
            for link in association_links:
                href = link.get_attribute('href')
                if href and '/associations/' in href and href not in self.processed_urls:
                    # Récupérer le nom et la description depuis le lien
                    try:
                        link_text = link.text.strip()
                        # Éviter les liens vides ou de navigation
                        if link_text and len(link_text) > 10:
                            bde_links.append(href)
                            self.processed_urls.add(href)
                    except:
                        continue
            
            print(f"   📄 {len(bde_links)} nouveaux liens BDE trouvés")
            return bde_links
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'extraction des liens : {str(e)}")
            return []
    
    def extract_bde_details(self, bde_url):
        """
        Extrait les détails d'un BDE depuis sa page individuelle
        """
        print(f"📄 Extraction des détails pour : {bde_url}")
        
        try:
            # Navigation vers la page du BDE
            self.driver.get(bde_url)
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Respecter les délais
            
            # Initialisation des données
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
                # Différents sélecteurs possibles pour le nom
                name_selectors = [
                    "h1",
                    ".association-name",
                    "[data-testid*='name']",
                    ".title"
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if name_element and name_element.text.strip():
                            bde_info['nom_ecole'] = name_element.text.strip()
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️ Nom non trouvé : {str(e)}")
            
            # Extraction de l'adresse
            try:
                # Recherche d'éléments contenant une adresse
                address_patterns = [
                    r'\d+.*(?:rue|avenue|boulevard|place|impasse).*\d{5}.*',
                    r'\d{5}\s+[A-Za-z\s\-]+',
                    r'[A-Za-z\s\-]+\s+\(\d{5}\)'
                ]
                
                page_text = self.driver.page_source
                for pattern in address_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        bde_info['adresse'] = matches[0].strip()
                        break
                        
            except Exception as e:
                print(f"   ⚠️ Adresse non trouvée : {str(e)}")
            
            # Extraction de l'email
            try:
                # Pattern pour email
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                page_text = self.driver.page_source
                email_matches = re.findall(email_pattern, page_text)
                
                if email_matches:
                    # Filtrer les emails valides (éviter les emails génériques)
                    valid_emails = [email for email in email_matches if not any(generic in email.lower() for generic in ['noreply', 'admin', 'webmaster', 'contact@helloasso'])]
                    if valid_emails:
                        bde_info['email'] = valid_emails[0]
                    elif email_matches:
                        bde_info['email'] = email_matches[0]
                        
            except Exception as e:
                print(f"   ⚠️ Email non trouvé : {str(e)}")
            
            # Extraction du téléphone
            try:
                # Patterns pour téléphone français
                phone_patterns = [
                    r'(?:(?:\+33|0)[1-9](?:[0-9]{8}))',
                    r'(?:0[1-9](?:\s?\d{2}){4})',
                    r'(?:\+33\s?[1-9](?:\s?\d{2}){4})'
                ]
                
                page_text = self.driver.page_source
                for pattern in phone_patterns:
                    phone_matches = re.findall(pattern, page_text)
                    if phone_matches:
                        bde_info['telephone'] = phone_matches[0].strip()
                        break
                        
            except Exception as e:
                print(f"   ⚠️ Téléphone non trouvé : {str(e)}")
            
            # Extraction du site internet
            try:
                # Recherche de liens externes (sites web)
                external_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
                for link in external_links:
                    href = link.get_attribute('href')
                    if href and 'helloasso.com' not in href:
                        # Filtrer les réseaux sociaux courants
                        social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']
                        if not any(domain in href for domain in social_domains):
                            bde_info['site_internet'] = href
                            break
                            
            except Exception as e:
                print(f"   ⚠️ Site internet non trouvé : {str(e)}")
            
            # Extraction des noms de personnes (si disponibles)
            try:
                # Recherche de patterns de noms dans le texte
                name_patterns = [
                    r'(?:Président|Présidente|Contact|Responsable)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                    r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s*[-–]\s*(?:Président|Présidente|Contact))'
                ]
                
                page_text = self.driver.page_source
                for pattern in name_patterns:
                    name_matches = re.findall(pattern, page_text)
                    if name_matches:
                        full_name = name_matches[0].strip()
                        name_parts = full_name.split()
                        if len(name_parts) >= 2:
                            bde_info['prenom_personne'] = name_parts[0]
                            bde_info['nom_personne'] = ' '.join(name_parts[1:])
                        break
                        
            except Exception as e:
                print(f"   ⚠️ Noms de personnes non trouvés : {str(e)}")
            
            # Affichage des informations extraites
            print(f"   ✅ Données extraites :")
            for key, value in bde_info.items():
                if value and key != 'url_source':
                    print(f"      {key}: {value}")
            
            return bde_info
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'extraction : {str(e)}")
            return None
    
    def navigate_to_next_page(self):
        """
        Navigue vers la page suivante s'il y en a une
        """
        try:
            # Recherche du bouton "Suivant"
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[class*='next']:not([disabled])")
            if next_button:
                next_button.click()
                time.sleep(3)  # Attendre le chargement
                return True
        except:
            pass
        
        return False
    
    def save_to_csv(self):
        """
        Sauvegarde les données en format CSV
        """
        if not self.bde_data:
            print("❌ Aucune donnée à sauvegarder")
            return False
            
        try:
            # Création du DataFrame pandas
            df = pd.DataFrame(self.bde_data)
            
            # Nom du fichier avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/{OUTPUT_FILENAME}_{timestamp}.csv"
            
            # Sauvegarde
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"💾 Données sauvegardées dans : {filename}")
            print(f"📊 Total : {len(self.bde_data)} BDE scrapés")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {str(e)}")
            return False
    
    def run_scraping(self, max_pages=None):
        """
        Lance le scraping complet
        """
        print("🚀 DÉBUT DU SCRAPING DES BDE")
        if max_pages:
            print(f"📄 Scraping limité à {max_pages} pages maximum")
        else:
            print(f"📄 Scraping de TOUTES les pages disponibles")
        
        try:
            # Configuration du navigateur
            self.setup_driver()
            
            # Navigation vers la page de recherche
            url = f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}"
            print(f"\n📌 Accès à : {url}")
            self.driver.get(url)
            time.sleep(3)
            
            page_count = 0
            
            while max_pages is None or page_count < max_pages:
                page_count += 1
                print(f"\n📄 === PAGE {page_count} ===")
                
                # Extraction des liens de la page courante
                bde_links = self.get_bde_links_from_page()
                
                if not bde_links:
                    print("❌ Aucun lien trouvé sur cette page")
                    break
                
                # Traitement de chaque BDE
                print(f"🔄 Traitement de {len(bde_links)} BDE...")
                
                for i, bde_url in enumerate(tqdm(bde_links, desc=f"Page {page_count}")):
                    print(f"\n   📄 BDE {i+1}/{len(bde_links)}")
                    
                    # Extraction des détails
                    bde_info = self.extract_bde_details(bde_url)
                    if bde_info:
                        self.bde_data.append(bde_info)
                    
                    # Délai entre les requêtes
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                
                # Tentative de navigation vers la page suivante
                print(f"\n🔄 Tentative de passage à la page suivante...")
                if not self.navigate_to_next_page():
                    print("📄 Pas de page suivante - fin du scraping")
                    break
            
            # Sauvegarde des données
            print(f"\n💾 SAUVEGARDE DES DONNÉES")
            self.save_to_csv()
            
            print(f"\n✅ SCRAPING TERMINÉ AVEC SUCCÈS !")
            print(f"📊 {len(self.bde_data)} BDE traités au total")
            
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
    print("🎓 SCRAPER BDE HELLOASSO")
    print("=" * 60)
    
    # Création et lancement du scraper
    scraper = BDEScraper()
    
    # Lancement du scraping complet (toutes les pages)
    scraper.run_scraping(max_pages=None)
    
    print("\n" + "=" * 60)
    print("✅ FIN DU PROGRAMME")
    print("=" * 60)

if __name__ == "__main__":
    main() 