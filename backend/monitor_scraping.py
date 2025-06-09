"""
📊 MONITORING DU SCRAPING EN COURS
Script pour suivre l'avancement du scraping complet
"""

import os
import time
import pandas as pd
from datetime import datetime

def monitor_scraping():
    """
    Surveille l'avancement du scraping
    """
    print("📊 MONITORING DU SCRAPING EN COURS")
    print("=" * 50)
    
    # Répertoire des données
    data_dir = "data"
    
    # Chercher les fichiers de scraping récents
    if not os.path.exists(data_dir):
        print("❌ Répertoire data non trouvé")
        return
    
    files = os.listdir(data_dir)
    scraping_files = [f for f in files if f.startswith("bde_scraping_all_pages_")]
    
    if not scraping_files:
        print("❌ Aucun fichier de scraping en cours trouvé")
        return
    
    # Prendre le fichier le plus récent
    latest_file = max(scraping_files, key=lambda f: os.path.getctime(os.path.join(data_dir, f)))
    filepath = os.path.join(data_dir, latest_file)
    
    print(f"📁 Fichier surveillé : {latest_file}")
    print(f"🕐 Démarrage du monitoring à {datetime.now().strftime('%H:%M:%S')}")
    
    previous_count = 0
    monitoring_start = time.time()
    
    while True:
        try:
            # Lire le fichier CSV actuel
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                current_count = len(df)
                
                if current_count != previous_count:
                    elapsed = time.time() - monitoring_start
                    rate = current_count / elapsed * 60 if elapsed > 0 else 0
                    
                    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - Mise à jour !")
                    print(f"   🎯 BDE scrapés : {current_count}")
                    print(f"   ⏱️  Durée : {elapsed/60:.1f} minutes")
                    print(f"   📈 Vitesse : {rate:.1f} BDE/minute")
                    
                    # Estimation du temps restant
                    if rate > 0:
                        estimated_total = 30 * 31  # 30 pages × ~31 BDE par page
                        remaining = max(0, estimated_total - current_count)
                        eta_minutes = remaining / rate if rate > 0 else 0
                        print(f"   ⏳ ETA : {eta_minutes:.1f} minutes restantes")
                        print(f"   🎯 Progression : {current_count/estimated_total*100:.1f}%")
                    
                    previous_count = current_count
                
                # Vérifier si le fichier a été modifié récemment
                last_modified = os.path.getmtime(filepath)
                time_since_modified = time.time() - last_modified
                
                if time_since_modified > 300:  # 5 minutes sans modification
                    print(f"\n⚠️  Fichier non modifié depuis {time_since_modified/60:.1f} minutes")
                    print("   Le scraping pourrait être terminé ou bloqué")
                    break
            
            else:
                print("❌ Fichier non trouvé")
                break
            
            # Attendre avant la prochaine vérification
            time.sleep(30)  # Vérifier toutes les 30 secondes
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring arrêté par l'utilisateur")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {str(e)}")
            time.sleep(30)
    
    # Résumé final
    try:
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            total_elapsed = time.time() - monitoring_start
            
            print(f"\n🏁 RÉSUMÉ FINAL")
            print(f"   📊 Total BDE scrapés : {len(df)}")
            print(f"   ⏱️  Durée totale : {total_elapsed/60:.1f} minutes")
            print(f"   📈 Vitesse moyenne : {len(df)/(total_elapsed/60):.1f} BDE/minute")
            
            # Statistiques des données
            if len(df) > 0:
                emails_count = df['email'].notna().sum()
                sites_count = df['site_internet'].notna().sum()
                
                print(f"   📧 Emails récupérés : {emails_count} ({emails_count/len(df)*100:.1f}%)")
                print(f"   🌐 Sites web récupérés : {sites_count} ({sites_count/len(df)*100:.1f}%)")
    except:
        pass

if __name__ == "__main__":
    monitor_scraping() 