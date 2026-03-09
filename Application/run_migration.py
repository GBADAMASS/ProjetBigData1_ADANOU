"""Applique la migration: surface_m2, property_type, table immoask_announcements"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from Application.database import engine
from Application.models import Base

def run():
    with engine.connect() as conn:
        tables_cols = [
            ("real_estate_announcements", ["surface_m2", "property_type"]),
            ("coinafrique_announcements", ["surface_m2", "property_type"]),
            ("igoe_announcements", ["surface_m2", "property_type"]),
            ("intendance_announcements", ["surface_m2", "property_type"]),
        ]
        for table, cols in tables_cols:
            for col in cols:
                try:
                    dtype = "FLOAT" if col == "surface_m2" else "VARCHAR(100)"
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {dtype} NULL"))
                    conn.commit()
                    print(f"  + {table}.{col}")
                except Exception as e:
                    if "Duplicate column" in str(e):
                        print(f"  - {table}.{col} (deja present)")
                    else:
                        raise
    Base.metadata.create_all(bind=engine)
    print("Table immoask_announcements creee si necessaire.")

if __name__ == "__main__":
    print("Migration add_surface_property_immoask...")
    run()
    print("Termine.")
