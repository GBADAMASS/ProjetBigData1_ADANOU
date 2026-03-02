import csv
import json
from pathlib import Path

from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
)

EXPORT_DIR = Path(__file__).parent / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    (RealEstateAnnouncement, "real_estate_announcements"),
    (CoinAfriqueAnnouncement, "coinafrique_announcements"),
    (IgoeAnnouncement, "igoe_announcements"),
    (IntendanceAnnouncement, "intendance_announcements"),
]

FIELDS = [
    "id",
    "external_id",
    "source",
    "price",
    "price_numeric",
    "location",
    "description",
    "images",
    "citations",
    "source_url",
    "scraped_at",
    "updated_at",
]


def serialize_value(val):
    if val is None:
        return ""
    # JSON for lists/dicts
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def export_table(db, model, filename):
    rows = db.query(model).all()
    path = EXPORT_DIR / filename
    with path.open("w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in rows:
            row = {}
            for field in FIELDS:
                row[field] = serialize_value(getattr(r, field, None))
            writer.writerow(row)
    return path


def main():
    db = SessionLocal()
    try:
        exported = []
        for model, name in MODELS:
            filename = f"{name}.csv"
            path = export_table(db, model, filename)
            exported.append(str(path))
        print("Export completed:")
        for p in exported:
            print(" -", p)
    finally:
        db.close()


if __name__ == "__main__":
    main()
