from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
)

MODELS = [
    (RealEstateAnnouncement, 'real_estate_announcements'),
    (CoinAfriqueAnnouncement, 'coinafrique_announcements'),
    (IgoeAnnouncement, 'igoe_announcements'),
    (IntendanceAnnouncement, 'intendance_announcements'),
]


def print_samples():
    db = SessionLocal()
    try:
        for model, name in MODELS:
            rows = db.query(model).limit(10).all()
            print('\n' + '=' * 60)
            print(f"Table: {name} - {len(rows)} rows returned (showing up to 10)")
            print('-' * 60)
            for r in rows:
                print({
                    'id': getattr(r, 'id', None),
                    'external_id': getattr(r, 'external_id', None),
                    'source': getattr(r, 'source', None),
                    'price': getattr(r, 'price', None),
                    'price_numeric': getattr(r, 'price_numeric', None),
                    'location': getattr(r, 'location', None),
                    'source_url': getattr(r, 'source_url', None),
                    'scraped_at': getattr(r, 'scraped_at', None),
                })
    finally:
        db.close()


if __name__ == '__main__':
    print_samples()
