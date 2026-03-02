"""
Application principale - Point d'entrée pour le scraper et scheduler
"""

from DonneesScrapper.Scheduler import start_scheduler
from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def display_statistics():
    """Afficher les statistiques des annonces en base de données"""
    db = SessionLocal()
    try:
        # Compter par table/source
        total_generic = db.query(RealEstateAnnouncement).count()
        total_coinafrique = db.query(CoinAfriqueAnnouncement).count()
        total_igoe = db.query(IgoeAnnouncement).count()
        total_intendance = db.query(IntendanceAnnouncement).count()
        total = total_generic + total_coinafrique + total_igoe + total_intendance

        logger.info("\n" + "=" * 50)
        logger.info("📊 STATISTIQUES DE LA BASE DE DONNÉES")
        logger.info("=" * 50)
        logger.info(f"Total annonces (toutes tables): {total}\n")
        logger.info(f"  real_estate_announcements: {total_generic}")
        logger.info(f"  coinafrique_announcements: {total_coinafrique}")
        logger.info(f"  igoe_announcements: {total_igoe}")
        logger.info(f"  intendance_announcements: {total_intendance}")

        logger.info("=" * 50 + "\n")

    finally:
        db.close()

def main():
    """Fonction principale"""
    logger.info("🏠 Démarrage du système de scraping immobilier")
    logger.info("📍 Régions couvertes: Togo (Lomé et environs)")
    logger.info("📚 Sources: Coin-Afrique, IGOE Immobilier, Intendance.tg\n")
    
    # Afficher les statistiques actuelles
    display_statistics()
    
    # Démarrer le scheduler
    start_scheduler()

if __name__ == "__main__":
    main()
