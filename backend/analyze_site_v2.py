"""
Script d'analyse amélioré pour HelloAsso
Version 2 avec gestion des sessions et contournement des blocages
"""

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import time
import json
from config import BASE_URL, SEARCH_PARAMS, HEADERS

def create_session():
    """
    Crée une session HTTP avec retry et cookies
    """
    session = requests.Session()
    
    # Configuration des tentatives automatiques en cas d'échec
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Application des headers
    session.headers.update(HEADERS)
    
    return session

def analyser_page_helloasso_v2():
    """
    Analyse améliorée de la page HelloAsso avec différentes stratégies
    """
    print("🔍 Analyse améliorée de la page HelloAsso...")
    
    # Création d'une session pour maintenir les cookies
    session = create_session()
    
    try:
        # Stratégie 1 : Visiter d'abord la page d'accueil pour récupérer les cookies
        print("📌 Étape 1 : Visite de la page d'accueil...")
        home_response = session.get("https://www.helloasso.com", timeout=10)
        print(f"   Statut page d'accueil : {home_response.status_code}")
        
        # Attendre un peu comme un vrai utilisateur
        time.sleep(2)
        
        # Stratégie 2 : Essayer l'URL de recherche
        url = f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}"
        print(f"\n📌 Étape 2 : Accès à la page de recherche...")
        print(f"URL : {url}")
        
        response = session.get(url, timeout=10)
        print(f"✅ Statut de la réponse : {response.status_code}")
        
        if response.status_code == 200:
            # Analyse du contenu
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"\n📊 INFORMATIONS GÉNÉRALES :")
            print(f"   - Titre : {soup.title.text if soup.title else 'Non trouvé'}")
            print(f"   - Taille HTML : {len(response.content)} caractères")
            
            # Recherche de contenu JavaScript (souvent les sites modernes sont en SPA)
            scripts = soup.find_all('script')
            print(f"   - Nombre de scripts JS : {len(scripts)}")
            
            # Recherche de données JSON dans les scripts
            print("\n🔍 RECHERCHE DE DONNÉES JSON :")
            for i, script in enumerate(scripts[:10]):  # Limite aux 10 premiers
                if script.string and ('association' in script.string.lower() or 'data' in script.string.lower()):
                    script_content = script.string[:500]  # Limite pour affichage
                    print(f"   Script {i+1} contient potentiellement des données :")
                    print(f"   {script_content}...")
            
            # Recherche d'éléments contenant des associations
            print("\n🔍 RECHERCHE D'ÉLÉMENTS D'ASSOCIATIONS :")
            
            # Sélecteurs plus spécifiques à HelloAsso
            selectors = [
                "div[class*='SearchResult']",
                "div[class*='AssociationCard']", 
                "div[class*='Organization']",
                "div[class*='Card']",
                "article",
                "[data-testid*='association']",
                "[data-testid*='organization']",
                "div[class*='result']"
            ]
            
            associations_trouvees = []
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"   ✅ {len(elements)} éléments trouvés avec : {selector}")
                    associations_trouvees.extend(elements)
                    
                    # Analyse du premier élément
                    if elements:
                        premier = elements[0]
                        print(f"      Classes CSS : {premier.get('class', [])}")
                        texte = premier.get_text()[:200].replace('\n', ' ').strip()
                        print(f"      Texte (extrait) : {texte}...")
            
            # Recherche de liens d'associations
            print("\n🔗 RECHERCHE DE LIENS :")
            links = soup.find_all('a', href=True)
            association_links = []
            
            for link in links:
                href = link.get('href', '')
                if any(keyword in href.lower() for keyword in ['association', 'organization', 'bde']):
                    association_links.append({
                        'url': href,
                        'text': link.get_text().strip()[:100]
                    })
            
            print(f"   📄 {len(association_links)} liens d'associations trouvés")
            for i, link in enumerate(association_links[:5]):  # Affiche les 5 premiers
                print(f"      {i+1}. {link['url']} - {link['text']}")
            
            # Sauvegarde pour analyse manuelle
            with open('backend/data/page_analysis_v2.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"\n💾 HTML sauvegardé dans : backend/data/page_analysis_v2.html")
            
            # Sauvegarde des informations structurées
            analysis_data = {
                'status_code': response.status_code,
                'title': soup.title.text if soup.title else None,
                'content_length': len(response.content),
                'scripts_count': len(scripts),
                'associations_found': len(associations_trouvees),
                'links_found': len(association_links),
                'selectors_working': [sel for sel in selectors if soup.select(sel)]
            }
            
            with open('backend/data/analysis_results.json', 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Résultats d'analyse sauvegardés dans : backend/data/analysis_results.json")
            
        elif response.status_code == 403:
            print("❌ Accès refusé (403) - Le site bloque notre requête")
            print("💡 Suggestions :")
            print("   - Le site détecte probablement le scraping")
            print("   - Utilisation de Selenium recommandée")
            print("   - Ou recherche d'une API publique")
            
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Le site met trop de temps à répondre")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête : {str(e)}")
    except Exception as e:
        print(f"❌ Erreur inattendue : {str(e)}")
    
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Analyse avancée du site HelloAsso")
    analyser_page_helloasso_v2()
    print("✅ Analyse terminée !") 