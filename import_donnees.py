#!/usr/bin/env python
"""
Script d'import des données scrapées (igoe-immobilier, intendance-tg, Coin-Afrique)
vers les tables de la base de données.

Exécuter depuis la racine du projet :
    python import_donnees.py
"""
import sys
from pathlib import Path

# S'assurer que le projet est dans le PYTHONPATH
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from DonneesScrapper.Scheduler import job

if __name__ == "__main__":
    print("=" * 60)
    print("Import des données vers la base de données")
    print("=" * 60)
    job()
    print("\nImport terminé. Vous pouvez maintenant afficher les données dans Streamlit.")
