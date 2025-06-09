"""
Script d'export vers Google Sheets
Export automatique des données de BDE scrapées
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import glob
import json
import os
from datetime import datetime

class GoogleSheetsExporter:
    """
    Classe pour exporter les données vers Google Sheets
    """
    
    def __init__(self):
        self.gc = None
        self.worksheet = None
        
    def setup_credentials(self):
        """
        Configure l'authentification Google Sheets
        """
        print("🔐 Configuration de l'authentification Google...")
        
        # Vérifier si le fichier de credentials existe
        creds_file = "data/google_credentials.json"
        
        if not os.path.exists(creds_file):
            print(f"❌ Fichier de credentials non trouvé : {creds_file}")
            print("📝 Pour configurer Google Sheets :")
            print("   1. Va sur https://console.cloud.google.com/")
            print("   2. Crée un nouveau projet ou sélectionne un projet existant")
            print("   3. Active l'API Google Sheets")
            print("   4. Crée un compte de service")
            print("   5. Télécharge le fichier JSON des credentials")
            print(f"   6. Renomme-le en 'google_credentials.json' et place-le dans {os.path.abspath('data/')}")
            return False
        
        try:
            # Scopes nécessaires pour Google Sheets
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Chargement des credentials
            credentials = Credentials.from_service_account_file(creds_file, scopes=scope)
            self.gc = gspread.authorize(credentials)
            
            print("✅ Authentification Google réussie !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur d'authentification : {e}")
            return False
    
    def create_or_open_spreadsheet(self, spreadsheet_name="BDE Scraping Results"):
        """
        Crée ou ouvre une feuille Google Sheets
        """
        try:
            print(f"📊 Recherche de la feuille '{spreadsheet_name}'...")
            
            try:
                # Essaie d'ouvrir la feuille existante
                spreadsheet = self.gc.open(spreadsheet_name)
                print(f"✅ Feuille existante trouvée : {spreadsheet_name}")
                
            except gspread.SpreadsheetNotFound:
                # Crée une nouvelle feuille
                print(f"📄 Création d'une nouvelle feuille : {spreadsheet_name}")
                spreadsheet = self.gc.create(spreadsheet_name)
                
                # Rend la feuille publique en lecture (optionnel)
                spreadsheet.share('', perm_type='anyone', role='reader')
                
            # Sélectionne la première feuille
            self.worksheet = spreadsheet.sheet1
            
            # URL de la feuille pour l'utilisateur
            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            print(f"🔗 URL de ta feuille Google Sheets : {sheet_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création/ouverture de la feuille : {e}")
            return False
    
    def export_csv_to_sheets(self, csv_file):
        """
        Exporte un fichier CSV vers Google Sheets
        """
        try:
            print(f"📁 Lecture du fichier : {csv_file}")
            
            # Lecture du CSV
            df = pd.read_csv(csv_file)
            print(f"📊 {len(df)} lignes à exporter")
            
            # Vide la feuille existante
            self.worksheet.clear()
            
            # Prépare les données avec les headers
            data_to_upload = [df.columns.tolist()] + df.values.tolist()
            
            # Upload vers Google Sheets
            print("⬆️  Upload des données vers Google Sheets...")
            self.worksheet.update('A1', data_to_upload)
            
            # Mise en forme basique
            print("🎨 Application du formatage...")
            
            # Header en gras
            self.worksheet.format('1:1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            # Auto-resize des colonnes
            self.worksheet.columns_auto_resize(0, len(df.columns))
            
            # Ajoute un timestamp
            timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
            self.worksheet.update('A{}'.format(len(df) + 3), f"Dernière mise à jour : {timestamp}")
            
            print("✅ Export vers Google Sheets réussi !")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'export : {e}")
            return False
    
    def find_latest_csv(self):
        """
        Trouve le fichier CSV le plus récent
        """
        # Cherche les fichiers CSV clean en premier
        clean_files = glob.glob("data/bde_clean_data_*.csv")
        if clean_files:
            latest_file = max(clean_files, key=os.path.getctime)
            print(f"📁 Fichier clean trouvé : {latest_file}")
            return latest_file
        
        # Sinon cherche les fichiers bruts
        raw_files = glob.glob("data/bde_scraping_results_*.csv")
        if raw_files:
            latest_file = max(raw_files, key=os.path.getctime)
            print(f"📁 Fichier brut trouvé : {latest_file}")
            return latest_file
        
        return None
    
    def export_to_google_sheets(self, csv_file=None):
        """
        Fonction principale d'export
        """
        print("🚀 DÉBUT DE L'EXPORT VERS GOOGLE SHEETS")
        print("=" * 50)
        
        # Configuration des credentials
        if not self.setup_credentials():
            return False
        
        # Trouve le fichier CSV si non spécifié
        if not csv_file:
            csv_file = self.find_latest_csv()
            if not csv_file:
                print("❌ Aucun fichier CSV trouvé")
                return False
        
        # Crée/ouvre la feuille Google Sheets
        if not self.create_or_open_spreadsheet():
            return False
        
        # Export des données
        if not self.export_csv_to_sheets(csv_file):
            return False
        
        print("=" * 50)
        print("✅ EXPORT GOOGLE SHEETS TERMINÉ !")
        
        return True

def create_credentials_template():
    """
    Crée un template de fichier credentials pour aider l'utilisateur
    """
    template = {
        "type": "service_account",
        "project_id": "TON_PROJECT_ID",
        "private_key_id": "TON_PRIVATE_KEY_ID", 
        "private_key": "-----BEGIN PRIVATE KEY-----\\nTON_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
        "client_email": "TON_SERVICE_ACCOUNT@TON_PROJECT.iam.gserviceaccount.com",
        "client_id": "TON_CLIENT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/TON_SERVICE_ACCOUNT%40TON_PROJECT.iam.gserviceaccount.com"
    }
    
    template_file = "data/google_credentials_template.json"
    with open(template_file, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"📋 Template créé : {template_file}")
    print("💡 Remplace les valeurs 'TON_*' par tes vraies credentials Google")

def main():
    """
    Fonction principale
    """
    print("🎓 EXPORT BDE VERS GOOGLE SHEETS")
    print("=" * 60)
    
    # Crée le template si nécessaire
    if not os.path.exists("data/google_credentials.json"):
        print("📋 Création du template de credentials...")
        create_credentials_template()
        print("\n⚠️  Configure d'abord tes credentials Google puis relance ce script")
        return
    
    # Lance l'export
    exporter = GoogleSheetsExporter()
    exporter.export_to_google_sheets()

if __name__ == "__main__":
    main() 