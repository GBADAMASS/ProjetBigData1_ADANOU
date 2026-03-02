from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime
import logging

from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
)
from DonneesScrapper.python import scrape_source

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def save_data_to_db(data, db):
    """Sauvegarder ou mettre à jour les annonces en base de données"""
    saved_count = 0
    updated_count = 0
    error_count = 0
    
    # mapper source -> model
    source_model_map = {
        'Coin-Afrique': CoinAfriqueAnnouncement,
        'igoe-immobilier': IgoeAnnouncement,
        'intendance-tg': IntendanceAnnouncement,
    }

    for record in data:
        try:
            # Choisir le modèle en fonction de la source (fallback: RealEstateAnnouncement)
            model = source_model_map.get(record.get('source'), RealEstateAnnouncement)

            # Vérifier si l'annonce existe déjà dans le modèle choisi
            existing = db.query(model).filter(model.external_id == record['external_id']).first()

            if existing:
                # Mettre à jour l'annonce existante
                existing.price = record['price']
                existing.price_numeric = record['price_numeric']
                existing.location = record['location']
                existing.description = record['description']
                existing.images = record['images']
                existing.source_url = record['source_url']
                existing.citations = record['citations']
                existing.updated_at = datetime.utcnow()
                db.commit()
                updated_count += 1
            else:
                # Créer une nouvelle annonce dans la table correspondante
                announcement = model(
                    external_id=record['external_id'],
                    source=record['source'],
                    price=record['price'],
                    price_numeric=record['price_numeric'],
                    location=record['location'],
                    description=record['description'],
                    images=record['images'],
                    source_url=record['source_url'],
                    citations=record['citations'],
                )
                db.add(announcement)
                db.commit()
                saved_count += 1
                
        except IntegrityError:
            db.rollback()
            error_count += 1
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la sauvegarde de {record.get('external_id')}: {str(e)}")
            error_count += 1
    
    return saved_count, updated_count, error_count

def job():
    """Tâche planifiée: scraper et sauvegarder les données"""
    db = SessionLocal()
    try:
        logger.info("=" * 50)
        logger.info(f"🚀 Démarrage du scraping - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
        # Scraper les données
        data = scrape_source()
        
        if data:
            # Sauvegarder en base de données
            saved, updated, errors = save_data_to_db(data, db)
            
            logger.info(f"\n Résultats de la synchronisation:")
            logger.info(f"    Annonces créées: {saved}")
            logger.info(f"    Annonces mises à jour: {updated}")
            logger.info(f"    Erreurs: {errors}")
            logger.info(f"    Total traité: {saved + updated + errors}")
            
            # Afficher statistiques
            stats = db.query(RealEstateAnnouncement).with_entities(
                RealEstateAnnouncement.source,
                func.count(RealEstateAnnouncement.id)
            ).group_by(RealEstateAnnouncement.source).all()
            
            logger.info(f"\n Annonces par source:")
            for source, count in stats:
                logger.info(f"   {source}: {count}")
        else:
            logger.warning(" Aucune donnée scrappée")
            
    except Exception as e:
        logger.error(f" Erreur dans la tâche planifiée: {str(e)}", exc_info=True)
    finally:
        db.close()
        logger.info("=" * 50 + "\n")

# Ajouter la tâche au scheduler - s'exécute toutes les 20 minutes
scheduler.add_job(job, "interval", minutes=20, id="scraper_job", replace_existing=True)

# Exécuter la tâche une fois au démarrage
def start_scheduler():
    """Démarrer le scheduler et exécuter le job une première fois"""
    logger.info("Exécution initiale du scraper...")
    job()
    
    logger.info("Démarrage du scheduler...")
    scheduler.start()
    logger.info(" Scheduler démarré avec succès!")

if __name__ == "__main__":
    start_scheduler()