# QUICKSTART

Guide rapide pour lancer le projet après un `git clone` et tester les endpoints API FastAPI.

## 1) Prérequis

- Python 3.8+
- MySQL 8+
- `pip`

## 2) Cloner et installer

```bash
git clone <URL_DU_REPO>
cd DEVOIR_ADANOU
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3) Préparer MySQL

Créer la base:

```sql
CREATE DATABASE scrapperDonnee_db;
```

Vérifier la connexion dans `Application/database.py`:

```python
DATABASE_URL = "mysql+pymysql://root@localhost/scrapperDonnee_db"
```

Adapte `root` / mot de passe selon ta machine.

## 4) Charger les données (scraping + scheduler)

```bash
python -m Application.main
```

Ce script:
- crée les tables si besoin,
- exécute un scraping initial,
- lance le scheduler (toutes les 20 minutes).

## 5) Lancer l'API FastAPI

Dans un autre terminal:

```bash
.venv\Scripts\activate
uvicorn Application.api:app --reload --port 8000
```

API FastAPI disponible sur:
- http://localhost:8000
- Documentation Swagger: http://localhost:8000/docs

## 6) (Optionnel) Lancer Streamlit

Dans un autre terminal:

```bash
.venv\Scripts\activate
streamlit run streamlit_app.py
```

Interface Streamlit:
- http://localhost:8501

## 7) Tester les endpoints API FastAPI

## Option A: Swagger (recommandé)

Ouvrir:
- http://localhost:8000/docs

Puis utiliser `Try it out`.

## Option B: curl

```bash
curl "http://localhost:8000/announcements?page=1&per_page=5"
curl "http://localhost:8000/announcements?source=Coin-Afrique&page=1&per_page=10"
curl "http://localhost:8000/announcements?q=Lome"
curl "http://localhost:8000/images?limit=5"
curl "http://localhost:8000/statistics"
```

## Option C: Postman / Insomnia

Configurer des requêtes `GET`:
- `/announcements`
- `/announcements/{external_id}`
- `/images`
- `/statistics`

Exemple URL:
- `http://localhost:8000/announcements?source=Coin-Afrique&page=1&per_page=10`

## 8) Endpoints disponibles

- `GET /announcements`
  - params: `source`, `page`, `per_page`, `min_price`, `max_price`, `q`
- `GET /announcements/{external_id}`
- `GET /images`
  - params: `source`, `limit`
- `GET /statistics`

## 9) Dépannage rapide

- Erreur DB:
  - vérifier MySQL démarré,
  - vérifier `DATABASE_URL`,
  - vérifier que `scrapperDonnee_db` existe.
- API FastAPI vide:
  - exécuter `python -m Application.main` pour alimenter les tables.
- Streamlit ne charge rien:
  - vérifier que l'API FastAPI tourne sur `http://localhost:8000`.

---

Projet: `DEVOIR_ADANOU`

