"""
Script pour nettoyer le fichier final avec les 879 BDE
"""

from data_cleaner import clean_csv_data, display_sample_data
from datetime import datetime

def main():
    # Fichier source (le gros fichier avec 879 BDE)
    input_file = 'data/bde_scraping_all_pages_20250609_151849.csv'
    
    # Fichier de sortie nettoyé
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/bde_clean_data_final_{timestamp}.csv'
    
    print("🚀 NETTOYAGE DU FICHIER FINAL")
    print("=" * 50)
    print(f"📁 Fichier source : {input_file}")
    print(f"📁 Fichier de sortie : {output_file}")
    
    # Nettoie les données
    if clean_csv_data(input_file, output_file):
        print("\n🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS !")
        display_sample_data(output_file, 10)
        
        # Statistiques finales
        import pandas as pd
        df = pd.read_csv(output_file)
        emails_count = df['email'].notna().sum()
        sites_count = df['site_internet'].notna().sum()
        
        print(f"\n📊 STATISTIQUES FINALES")
        print("=" * 50)
        print(f"📈 Total BDE : {len(df)}")
        print(f"📧 Emails récupérés : {emails_count} ({emails_count/len(df)*100:.1f}%)")
        print(f"🌐 Sites web récupérés : {sites_count} ({sites_count/len(df)*100:.1f}%)")
        print(f"📁 Fichier final : {output_file}")
    else:
        print("❌ Erreur lors du nettoyage")

if __name__ == "__main__":
    main() 