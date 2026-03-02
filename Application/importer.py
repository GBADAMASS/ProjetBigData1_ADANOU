"""
Exemples d'utilisation du système de scraping immobilier
"""

from Application.database import SessionLocal
from Application.models import RealEstateAnnouncement
from sqlalchemy import desc, and_

def example_get_all_announcements():
    """Récupérer toutes les annonces"""
    db = SessionLocal()
    try:
        announcements = db.query(RealEstateAnnouncement).all()
        print(f"Total annonces: {len(announcements)}")
        for ann in announcements[:5]:
            print(f"  - {ann.source}: {ann.location} - {ann.price}")
    finally:
        db.close()

def example_get_by_source(source: str):
    """Récupérer les annonces d'une source spécifique"""
    db = SessionLocal()
    try:
        announcements = db.query(RealEstateAnnouncement).filter(
            RealEstateAnnouncement.source == source
        ).all()
        print(f"\n{source}: {len(announcements)} annonces")
        for ann in announcements[:3]:
            print(f"  - {ann.location}: {ann.price}")
    finally:
        db.close()

def example_get_by_location(location_keyword: str):
    """Rechercher les annonces par localisation"""
    db = SessionLocal()
    try:
        announcements = db.query(RealEstateAnnouncement).filter(
            RealEstateAnnouncement.location.ilike(f"%{location_keyword}%")
        ).all()
        print(f"\nAnnonces pour '{location_keyword}': {len(announcements)}")
        for ann in announcements:
            print(f"  - {ann.location}: {ann.price}")
    finally:
        db.close()

def example_get_expensive_announcements(min_price: float):
    """Récupérer les annonces au-dessus d'un certain prix"""
    db = SessionLocal()
    try:
        announcements = db.query(RealEstateAnnouncement).filter(
            RealEstateAnnouncement.price_numeric >= min_price
        ).order_by(desc(RealEstateAnnouncement.price_numeric)).all()
        
        print(f"\nAnnonces au-dessus de {min_price:,.0f} CFA: {len(announcements)}")
        for ann in announcements[:10]:
            print(f"  - {ann.location}: {ann.price}")
    finally:
        db.close()

def example_get_latest_announcements(limit: int = 10):
    """Récupérer les annonces les plus récentes"""
    db = SessionLocal()
    try:
        announcements = db.query(RealEstateAnnouncement).order_by(
            desc(RealEstateAnnouncement.scraped_at)
        ).limit(limit).all()
        
        print(f"\nDernières {limit} annonces scrappées:")
        for ann in announcements:
            print(f"  - {ann.source}: {ann.location} ({ann.scraped_at.strftime('%Y-%m-%d %H:%M')})")
    finally:
        db.close()

def example_get_statistics():
    """Afficher les statistiques complètes"""
    db = SessionLocal()
    try:
        total = db.query(RealEstateAnnouncement).count()
        
        # Par source
        by_source = db.query(
            RealEstateAnnouncement.source,
            RealEstateAnnouncement.id.count()
        ).group_by(RealEstateAnnouncement.source).all()
        
        # Statistiques de prix
        stats = db.query(
            RealEstateAnnouncement.price_numeric.label("min"),
        ).all()
        
        print(f"\n📊 STATISTIQUES COMPLÈTES")
        print(f"Total annonces: {total}")
        print(f"\nPar source:")
        for source, count in by_source:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  - {source}: {count} ({percentage:.1f}%)")
        
    finally:
        db.close()

def example_complex_query():
    """Requête complexe: annonces récentes par source"""
    db = SessionLocal()
    try:
        # Annonces de Coin-Afrique scrappées dans les 7 derniers jours
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        announcements = db.query(RealEstateAnnouncement).filter(
            and_(
                RealEstateAnnouncement.source == "Coin-Afrique",
                RealEstateAnnouncement.scraped_at >= seven_days_ago,
                RealEstateAnnouncement.price_numeric.isnot(None)
            )
        ).order_by(desc(RealEstateAnnouncement.price_numeric)).all()
        
        print(f"\n🔍 Annonces Coin-Afrique de moins de 7 jours (avec prix):")
        print(f"Résultats: {len(announcements)}")
        for ann in announcements[:5]:
            print(f"  - {ann.location}: {ann.price} ({ann.scraped_at.strftime('%Y-%m-%d')})")
            
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLES D'UTILISATION - Système de Scraping Immobilier")
    print("=" * 60)
    
    try:
        # Exécuter les exemples
        example_get_all_announcements()
        example_get_by_source("Coin-Afrique")
        example_get_by_location("Lomé")
        example_get_expensive_announcements(50_000_000)
        example_get_latest_announcements(5)
        example_get_statistics()
        example_complex_query()
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        print("Assurez-vous que PostgreSQL est démarré et les données sont chargées.")
    
    print("\n" + "=" * 60)
