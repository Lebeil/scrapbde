"""
Script d'analyse pour comprendre la structure du site HelloAsso
Étape 3 : Analyse avant scraping
"""

import requests
from bs4 import BeautifulSoup
import time
from config import BASE_URL, SEARCH_PARAMS, HEADERS

def analyser_page_helloasso():
    """
    Fonction pour analyser la structure de la page HelloAsso
    """
    print("🔍 Analyse de la page HelloAsso en cours...")
    
    try:
        # Construction de l'URL complète
        url = f"{BASE_URL}?category_tags={SEARCH_PARAMS['category_tags']}"
        print(f"📌 URL à analyser : {url}")
        
        # Requête HTTP avec nos headers
        response = requests.get(url, headers=HEADERS)
        print(f"✅ Statut de la réponse : {response.status_code}")
        
        # Vérification que la requête a réussi
        if response.status_code == 200:
            # Analyse du HTML avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print("\n📊 INFORMATIONS GÉNÉRALES SUR LA PAGE :")
            print(f"   - Titre de la page : {soup.title.text if soup.title else 'Non trouvé'}")
            print(f"   - Taille du contenu HTML : {len(response.content)} caractères")
            
            # Recherche des éléments qui pourraient contenir les associations
            print("\n🔍 RECHERCHE DES STRUCTURES D'ASSOCIATIONS :")
            
            # Recherche de différents sélecteurs possibles
            selectors_a_tester = [
                "div[class*='association']",
                "div[class*='card']", 
                "div[class*='result']",
                "article",
                ".association-card",
                ".search-result",
                "div[data-testid*='association']"
            ]
            
            for selector in selectors_a_tester:
                elements = soup.select(selector)
                if elements:
                    print(f"   ✅ Trouvé {len(elements)} éléments avec le sélecteur : {selector}")
                    # Affichage du premier élément pour analyse
                    if len(elements) > 0:
                        print(f"      Premier élément (extrait) : {str(elements[0])[:200]}...")
                else:
                    print(f"   ❌ Aucun élément trouvé avec : {selector}")
            
            # Recherche de liens vers les pages individuelles
            print("\n🔗 RECHERCHE DES LIENS VERS LES ASSOCIATIONS :")
            links = soup.find_all('a', href=True)
            association_links = [link for link in links if 'association' in link.get('href', '')]
            print(f"   📄 Trouvé {len(association_links)} liens contenant 'association'")
            
            if association_links:
                print("   🔍 Exemples de liens trouvés :")
                for i, link in enumerate(association_links[:3]):  # Affiche les 3 premiers
                    print(f"      {i+1}. {link.get('href')}")
            
            # Recherche de pagination
            print("\n📄 RECHERCHE DE LA PAGINATION :")
            pagination_selectors = [
                "nav[class*='pagination']",
                "div[class*='pagination']", 
                ".pagination",
                "button[class*='next']",
                "a[class*='page']"
            ]
            
            for selector in pagination_selectors:
                pagination = soup.select(selector)
                if pagination:
                    print(f"   ✅ Pagination trouvée avec : {selector}")
                    print(f"      Nombre d'éléments : {len(pagination)}")
                    
            # Sauvegarde du HTML pour analyse manuelle si nécessaire
            with open('backend/data/page_analysis.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print("\n💾 HTML de la page sauvegardé dans : backend/data/page_analysis.html")
            
        else:
            print(f"❌ Erreur : Impossible d'accéder à la page (Code {response.status_code})")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    print("🚀 Début de l'analyse du site HelloAsso")
    analyser_page_helloasso()
    print("✅ Analyse terminée !") 