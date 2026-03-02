from sqlalchemy import func
from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
    Image,
)

MODEL_SOURCE_MAP = [
    (CoinAfriqueAnnouncement, 'Coin-Afrique'),
    (IgoeAnnouncement, 'igoe-immobilier'),
    (IntendanceAnnouncement, 'intendance-tg'),
    (RealEstateAnnouncement, 'generic'),
]


def normalize_images(db):
    inserted = 0
    for model, source in MODEL_SOURCE_MAP:
        rows = db.query(model).all()
        for r in rows:
            imgs = getattr(r, 'images', None)
            citations = getattr(r, 'citations', None)
            if not imgs:
                continue
            if isinstance(imgs, str):
                # Attempt to parse JSON string
                try:
                    import json
                    imgs = json.loads(imgs)
                except Exception:
                    imgs = [imgs]
            for idx, url in enumerate(imgs):
                if not url:
                    continue
                # avoid duplicates
                exists = db.query(Image).filter(
                    Image.external_id == getattr(r, 'external_id', None),
                    Image.url == url
                ).first()
                if exists:
                    continue
                img = Image(
                    external_id=getattr(r, 'external_id', None),
                    source=source,
                    url=url,
                    position=idx,
                    citations=citations,
                )
                db.add(img)
                inserted += 1
        db.commit()
    return inserted


def generate_report(db):
    report = {}
    # Per-table counts
    report['counts'] = {
        'real_estate_announcements': db.query(RealEstateAnnouncement).count(),
        'coinafrique_announcements': db.query(CoinAfriqueAnnouncement).count(),
        'igoe_announcements': db.query(IgoeAnnouncement).count(),
        'intendance_announcements': db.query(IntendanceAnnouncement).count(),
        'images': db.query(Image).count(),
    }

    # Price statistics per source (using numeric where available)
    stats = {}
    for model, source in MODEL_SOURCE_MAP:
        q = db.query(
            func.count(model.id),
            func.avg(model.price_numeric),
            func.min(model.price_numeric),
            func.max(model.price_numeric),
        )
        res = q.one()
        stats[source] = {
            'count': int(res[0] or 0),
            'avg_price': float(res[1]) if res[1] is not None else None,
            'min_price': float(res[2]) if res[2] is not None else None,
            'max_price': float(res[3]) if res[3] is not None else None,
        }
    report['price_stats'] = stats
    return report


def main():
    db = SessionLocal()
    try:
        print('Normalizing images into `images` table...')
        inserted = normalize_images(db)
        print(f'Inserted {inserted} image rows into images table.')

        print('\nGenerating report...')
        report = generate_report(db)

        print('\nCounts:')
        for k, v in report['counts'].items():
            print(f'  {k}: {v}')

        print('\nPrice statistics:')
        for source, s in report['price_stats'].items():
            print(f"  Source: {source}")
            print(f"    count: {s['count']}")
            print(f"    avg_price: {s['avg_price']}")
            print(f"    min_price: {s['min_price']}")
            print(f"    max_price: {s['max_price']}")

    finally:
        db.close()


if __name__ == '__main__':
    main()
