# 🏠 Système de Scraping Immobilier - Togo

Système automatisé de scraping et de stockage des annonces immobilières togolaises dans une base de données PostgreSQL.

## 📍 Sources de données

### 1. **Coin Afrique** 
- Site: https://tg.coinafrique.com/categorie/immobilier
- Fichier: `extract-data-2026-02-21-Coin-Afrique.json`

### 2. **IGOE Immobilier**
- Site: https://www.igoeimmobilier.com/
- Fichier: `extract-data-2026-02-21-igoe-immobilier.json`

### 3. **Intendance.tg**
- Site: https://intendance.tg/
- Fichier: `extract-data-2026-02-21-intendance-tg.json`

### 4. **OmniSoft API** (optionnel)
- API: https://devapi.omnisoft.africa/public/api/v2
- Données disponibles pour intégration future

## 📋 Structure du projet

```
Application/
├── database.py        # Configuration PostgreSQL et sessions
├── models.py          # Modèle SQLAlchemy RealEstateAnnouncement
├── main.py            # Point d'entrée principal
└── importer.py        # Fonctions utilitaires d'import

DonneesScrapper/
├── python.py          # Logique de scraping des fichiers JSON
├── Scheduler.py       # Tâches planifiées (APScheduler)
└── *.json             # Fichiers de données scrappées
```

## 🔧 Configuration

### Prérequis
- Python 3.8+
- PostgreSQL 12+
- Packages Python:
  ```bash
  pip install sqlalchemy psycopg2-binary apscheduler
  ```

### Configuration PostgreSQL

Modifier `Application/database.py`:
```python
DATABASE_URL = "postgresql://username:password@localhost/database_name"
```

**Exemple:**
```python
DATABASE_URL = "postgresql://postgres:password@localhost/scraper_db"
```

### Créer la base de données

```bash
psql -U postgres
CREATE DATABASE scraper_db;
```

## 🚀 Utilisation

### Lancer le scraper
```bash
python -m Application.main
```

### API FastAPI

Démarrage du serveur :
```bash
uvicorn Application.api:app --reload --port 8000
```

Points d'accès disponibles :
- `GET /announcements` (paramètres `source`, `limit`, `min_price`, `max_price`, `q` pour recherche textuelle)
- `GET /announcements/{external_id}`
- `GET /images` (option `source`)
- `GET /statistics`

Exemple :
```bash
curl "http://localhost:8000/announcements?source=Coin-Afrique&limit=10"
```

### Visualisation avec Streamlit

Le fichier `streamlit_app.py` consomme l'API et permet d'interagir via une interface web.
Lancer avec :
```bash
streamlit run streamlit_app.py
```

Une fois les deux services actifs (API & Streamlit), utilisez l'interface pour récupérer les annonces, statistiques et images.

Cela va:
1. ✅ Créer les tables PostgreSQL si nécessaire
2. 🔄 Exécuter le scraping initial
3. ⏰ Démarrer le scheduler (exécution toutes les 20 minutes)

### Structure des données scrappées

Chaque annonce contient:
- **ID externe**: Identifiant unique basé sur la source
- **Source**: (Coin-Afrique, igoe-immobilier, intendance-tg)
- **Prix**: Prix affiché et valeur numérique en CFA
- **Localisation**: Quartier/région au Togo
- **Description**: Détails complets de l'annonce
- **Images**: Liste des URLs des images
- **Citations**: URLs sources des données
- **Timestamps**: Date de scraping et mise à jour

### Exemple d'annonce en base de données

```python
{
    "id": 1,
    "external_id": "Coin-Afrique_extract-data_0",
    "source": "Coin-Afrique",
    "price": "26 000 000 CFA",
    "price_numeric": 26000000.0,
    "location": "Lomé, Togo",
    "description": "Terrain à Agoè-Vakpossito...",
    "images": ["https://coinafrique-ads-photos.s3.amazonaws.com/..."],
    "source_url": "https://tg.coinafrique.com/annonce/...",
    "scraped_at": "2026-02-21T10:30:00",
    "updated_at": "2026-02-21T10:30:00"
}
```

## 📊 Scheduler

Le scheduler exécute automatiquement:
- **Fréquence**: Toutes les 20 minutes
- **Tâche**: Scraper les fichiers JSON et synchroniser la base de données
- **Comportement**:
  - Crée les nouvelles annonces
  - Met à jour les annonces existantes
  - Affiche les statistiques de synchronisation

**Logs du scheduler:**
```
==================================================
🚀 Démarrage du scraping - 2026-02-21 10:30:00
==================================================
🔄 Scraping Coin-Afrique depuis extract-data-2026-02-21-Coin-Afrique.json...
   Source: https://tg.coinafrique.com/categorie/immobilier
✅ 25 annonces extraites de Coin-Afrique
...
📈 Résultats de la synchronisation:
   ✅ Annonces créées: 15
   🔄 Annonces mises à jour: 10
   ❌ Erreurs: 0
```

## 🔄 Flux de mise à jour

```
Fichiers JSON (sources) 
       ↓
   python.py (parse JSON)
       ↓
  models.py (RealEstateAnnouncement)
       ↓
  Scheduler.py (APScheduler)
       ↓
  database.py (SessionLocal)
       ↓
  PostgreSQL (Stockage)
```

## 🛠️ Maintenance

### Ajouter une nouvelle source

1. Ajouter le fichier JSON au dossier `DonneesScrapper/`
2. Modifier `DonneesScrapper/python.py` - mettre à jour `source_mapping`:
```python
source_mapping = {
    'NouvelleSource': {
        'file': 'extract-data-nouvelle-source.json',
        'url': 'https://exemple.com/'
    }
}
```

### Requêtes SQL utiles

```sql
-- Statistiques par source
SELECT source, COUNT(*) as count FROM real_estate_announcements GROUP BY source;

-- Annonces les plus chères
SELECT location, price, price_numeric FROM real_estate_announcements 
ORDER BY price_numeric DESC LIMIT 10;

-- Dernières annonces
SELECT * FROM real_estate_announcements 
ORDER BY scraped_at DESC LIMIT 5;
```

## 📝 Notes

- Les annonces sont identifiées de manière unique par `external_id`
- Les doublets en base de données sont évités grâce à la clé unique
- Les prix sont extraits en format numérique pour faciliter les recherches
- Le système est tolérant aux erreurs (continue même si un fichier manque)

## 🐛 Troubleshooting

### Erreur de connexion PostgreSQL
```
Vérifier:
- PostgreSQL est démarré
- Les identifiants dans DATABASE_URL sont corrects
- La base de données existe
```

### Fichiers JSON non trouvés
```
Le système continuera sans ces fichiers (affichera ⚠️)
Vérifier que les fichiers sont dans DonneesScrapper/
```

### Pas de mises à jour
```
Vérifier les logs du scheduler
S'assurer que main.py est en cours d'exécution
```

---

**Dernière mise à jour**: 2026-02-21  
**Auteur**: INGGBAA  
**Version**: 1.0
