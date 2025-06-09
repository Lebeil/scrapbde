"""
Script de nettoyage des données scrapées
Nettoie le fichier CSV pour enlever le CSS et garder seulement les données utiles
"""

import pandas as pd
import re
from datetime import datetime

def clean_address_field(address_text):
    """
    Nettoie le champ adresse en supprimant le CSS et les styles
    """
    if pd.isna(address_text) or address_text == "":
        return ""
    
    # Supprime tout le CSS (commence par @font-face ou contient des propriétés CSS)
    if address_text.startswith("100%;font-style") or "@font-face" in address_text:
        return ""
    
    # Supprime les balises HTML
    clean_text = re.sub(r'<[^>]+>', '', str(address_text))
    
    # Supprime les propriétés CSS restantes
    clean_text = re.sub(r'[a-zA-Z-]+:[^;]+;', '', clean_text)
    
    # Supprime les URL
    clean_text = re.sub(r'https?://[^\s]+', '', clean_text)
    
    # Supprime les caractères spéciaux répétitifs
    clean_text = re.sub(r'[{}%\[\]@#]+', '', clean_text)
    
    # Supprime les espaces multiples
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text.strip()

def clean_website_field(website_text):
    """
    Nettoie et valide les URLs de sites web
    """
    if pd.isna(website_text) or website_text == "":
        return ""
    
    # Cherche une URL valide dans le texte
    url_pattern = r'https?://[^\s,;)]+[a-zA-Z0-9/]'
    urls = re.findall(url_pattern, str(website_text))
    
    if urls:
        # Prend la première URL trouvée et la nettoie
        clean_url = urls[0].rstrip('.,;)')
        # Vérifie que ce n'est pas une URL de HelloAsso ou d'API
        if 'helloasso.com' not in clean_url and 'api.api-engagement' not in clean_url:
            return clean_url
    
    return ""

def clean_csv_data(input_file, output_file):
    """
    Fonction principale pour nettoyer le fichier CSV
    """
    print(f"🧹 Nettoyage du fichier : {input_file}")
    
    try:
        # Lit le fichier CSV
        df = pd.read_csv(input_file)
        print(f"📊 {len(df)} lignes trouvées")
        
        # Nettoie chaque colonne
        print("🔧 Nettoyage des adresses...")
        df['adresse'] = df['adresse'].apply(clean_address_field)
        
        print("🔧 Nettoyage des sites web...")
        df['site_internet'] = df['site_internet'].apply(clean_website_field)
        
        # Supprime les lignes où l'école est vide
        df = df[df['nom_ecole'].notna() & (df['nom_ecole'] != "")]
        
        # Réorganise les colonnes dans un ordre plus logique
        columns_order = ['nom_ecole', 'email', 'telephone', 'site_internet', 'adresse', 'nom_personne', 'prenom_personne', 'url_source']
        df = df[columns_order]
        
        # Sauvegarde le fichier nettoyé
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Fichier nettoyé sauvegardé : {output_file}")
        print(f"📊 {len(df)} BDE dans le fichier final")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage : {e}")
        return False

def display_sample_data(file_path, num_rows=5):
    """
    Affiche un échantillon des données nettoyées
    """
    try:
        df = pd.read_csv(file_path)
        print(f"\n📋 Aperçu des {num_rows} premiers BDE :")
        print("="*80)
        
        for i, row in df.head(num_rows).iterrows():
            print(f"🏫 École : {row['nom_ecole']}")
            print(f"📧 Email : {row['email']}")
            print(f"📞 Téléphone : {row['telephone']}")
            print(f"🌐 Site web : {row['site_internet']}")
            print(f"📍 Adresse : {row['adresse'][:100]}{'...' if len(str(row['adresse'])) > 100 else ''}")
            print("-"*80)
            
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage : {e}")

if __name__ == "__main__":
    # Trouve le fichier CSV le plus récent
    import glob
    csv_files = glob.glob("data/bde_scraping_results_*.csv")
    if csv_files:
        latest_file = max(csv_files)
        
        # Génère le nom du fichier nettoyé
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_file = f"data/bde_clean_data_{timestamp}.csv"
        
        # Nettoie les données
        if clean_csv_data(latest_file, clean_file):
            display_sample_data(clean_file)
        
    else:
        print("❌ Aucun fichier de scraping trouvé dans le dossier data/") 