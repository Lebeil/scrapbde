# 🎓 Scraper BDE HelloAsso

Un projet de scraping simple et efficace pour extraire les informations des Bureaux Des Étudiants (BDE) depuis HelloAsso et les exporter vers Google Sheets.

## 📋 Fonctionnalités

✅ **Scraping automatisé** des BDE sur HelloAsso  
✅ **Navigation automatique** sur toutes les pages  
✅ **Extraction complète** : noms d'écoles, emails, téléphones, sites web  
✅ **Nettoyage des données** automatique  
✅ **Export CSV** avec horodatage  
✅ **Export Google Sheets** avec formatage  

## 📊 Données extraites

Pour chaque BDE trouvé :
- 🏫 **Nom de l'école**
- 📧 **Email de contact**
- 📞 **Numéro de téléphone**
- 🌐 **Site internet** (si disponible)
- 📍 **Adresse** (si disponible)
- 👤 **Nom/Prénom du responsable** (si disponible)
- 🔗 **URL source HelloAsso**

## 🚀 Installation

### 1. Prérequis
```bash
# Python 3.7+ requis
python3 --version

# Bun (pour le projet NextJS)
bun --version
```

### 2. Installation des dépendances Python
```bash
cd backend
pip3 install -r requirements.txt
```

### 3. Configuration Google Sheets (optionnel)

Pour exporter vers Google Sheets :

1. Va sur [Google Cloud Console](https://console.cloud.google.com/)
2. Crée un nouveau projet ou sélectionne un projet existant
3. Active l'API Google Sheets et Google Drive
4. Crée un compte de service
5. Télécharge le fichier JSON des credentials
6. Renomme-le en `google_credentials.json` et place-le dans `backend/data/`

## 📖 Utilisation

### Scraping basique (3 pages)
```bash
cd backend
python3 scraper.py
```

### Scraping complet (toutes les pages)
```bash
cd backend
python3 test_full_scraping.py
```

### Nettoyage des données
```bash
cd backend
python3 data_cleaner.py
```

### Export vers Google Sheets
```bash
cd backend
python3 google_sheets_export.py
```

## 📁 Structure des fichiers

```
backend/
├── scraper.py              # Script principal de scraping
├── config.py               # Configuration du scraping
├── data_cleaner.py         # Nettoyage des données
├── google_sheets_export.py # Export Google Sheets
├── requirements.txt        # Dépendances Python
├── data/                   # Dossier des résultats
│   ├── bde_scraping_results_*.csv  # Données brutes
│   ├── bde_clean_data_*.csv        # Données nettoyées
│   └── google_credentials.json     # Credentials Google (à créer)
└── utils/                  # Utilitaires
```

## ⚙️ Configuration

### Paramètres de scraping (config.py)

```python
# Délai entre les requêtes (politesse)
DELAY_BETWEEN_REQUESTS = 2

# Colonnes du CSV de sortie
COLUMNS = [
    'nom_ecole', 'nom_personne', 'prenom_personne',
    'adresse', 'site_internet', 'telephone', 'email', 'url_source'
]
```

## 🔧 Scripts disponibles

| Script | Description |
|--------|-------------|
| `scraper.py` | Scraping principal avec limitation à 3 pages |
| `test_full_scraping.py` | Scraping de toutes les pages disponibles |
| `data_cleaner.py` | Nettoie les données CSV (supprime CSS, etc.) |
| `google_sheets_export.py` | Export vers Google Sheets |
| `analyze_with_selenium.py` | Analyse de la structure du site |
| `count_pages.py` | Compte le nombre de pages disponibles |

## 📊 Exemples de résultats

### CSV nettoyé
```csv
nom_ecole,email,telephone,site_internet,adresse
BDE LA FAYETTE,contact@bde-lafayette.fr,714285705,https://bde-lafayette.fr/,
BDE ESEODUC,eseoduc@gmail.com,714285705,,
Bde Kapitole,bde.kpitole@gmail.com,714285705,https://bde.kpitole/,
```

### Google Sheets
- ✅ Formatage automatique des headers
- ✅ Auto-redimensionnement des colonnes
- ✅ Horodatage de dernière mise à jour
- ✅ URL publique pour partage

## 🛠️ Dépannage

### Erreur "Module not found"
```bash
pip3 install -r requirements.txt
```

### Erreur Chrome/Selenium
Le script télécharge automatiquement ChromeDriver. Assure-toi que Chrome est installé.

### Erreur Google Sheets
Vérifie que :
- Le fichier `google_credentials.json` existe dans `data/`
- Les APIs Google Sheets et Drive sont activées
- Le compte de service a les bonnes permissions

### Site HelloAsso bloqué
Le script utilise Selenium pour éviter les blocages. Si des erreurs persistent :
- Augmente `DELAY_BETWEEN_REQUESTS` dans `config.py`
- Le script respecte déjà les bonnes pratiques (User-Agent, délais)

## 📈 Statistiques typiques

- **~35 BDE par page** sur HelloAsso
- **~2-3 secondes par BDE** (délai de politesse)
- **~95% de taux de succès** d'extraction des emails
- **~60% de taux de succès** d'extraction des sites web

## 🤝 Contribution

Ce projet est conçu pour les débutants en Python. Les améliorations sont les bienvenues :

1. Fork le projet
2. Crée une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -am 'Ajoute une fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Crée une Pull Request

## 📝 Bonnes pratiques respectées

- ✅ **Délais entre requêtes** (2 secondes)
- ✅ **User-Agent réaliste**
- ✅ **Headers HTTP appropriés**
- ✅ **Gestion des erreurs**
- ✅ **Logs détaillés**
- ✅ **Respect du robots.txt**

## 📄 Licence

Projet à des fins éducatives. Respecte les conditions d'utilisation de HelloAsso.

---

*Projet créé avec ❤️ pour apprendre le scraping Python* 