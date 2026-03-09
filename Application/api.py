from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
    ImmoaskAnnouncement,
    Image,
)

app = FastAPI(title="Immobilier Scraper API")


def _row_to_announcement_dict(row) -> dict:
    """Convert a SQLAlchemy row to a dict compatible with Announcement, handling datetime fields."""
    d = {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
    for key in ("scraped_at", "updated_at"):
        if key in d and d[key] is not None and isinstance(d[key], datetime):
            d[key] = d[key].isoformat()
    return d


class Announcement(BaseModel):
    id: int
    external_id: str
    source: str
    price: Optional[str]
    price_numeric: Optional[float]
    location: Optional[str]
    description: Optional[str]
    surface_m2: Optional[float]
    property_type: Optional[str]
    images: Optional[List[str]]
    source_url: Optional[str]
    citations: Optional[dict]
    scraped_at: Optional[str]
    updated_at: Optional[str]


class AnnouncementsResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[Announcement]

class ImageModel(BaseModel):
    id: int
    external_id: Optional[str]
    source: Optional[str]
    url: str
    position: Optional[int]
    citations: Optional[dict]
    created_at: Optional[str]

# utility
SOURCE_TABLES = {
    "Coin-Afrique": CoinAfriqueAnnouncement,
    "igoe-immobilier": IgoeAnnouncement,
    "intendance-tg": IntendanceAnnouncement,
    "Immoask": ImmoaskAnnouncement,
    "generic": RealEstateAnnouncement,
}

@app.get("/announcements", response_model=AnnouncementsResponse)
def get_announcements(
    source: Optional[str] = Query(None, description="filter by source"),
    page: int = Query(1, ge=1, description="page number starting at 1"),
    per_page: int = Query(20, ge=1, le=100, description="items per page"),
    min_price: Optional[float] = Query(None, description="minimum numeric price"),
    max_price: Optional[float] = Query(None, description="maximum numeric price"),
    min_surface: Optional[float] = Query(None, description="surface min en m²"),
    max_surface: Optional[float] = Query(None, description="surface max en m²"),
    property_type: Optional[str] = Query(None, description="type de bien (Villa, Appartement, etc.)"),
    q: Optional[str] = Query(None, description="full text query (description/location)"),
):
    db = SessionLocal()
    try:
        model = SOURCE_TABLES.get(source) if source else RealEstateAnnouncement
        if source and not model:
            raise HTTPException(status_code=400, detail="Unknown source")
        query = db.query(model)
        if min_price is not None:
            query = query.filter(model.price_numeric >= min_price)
        if max_price is not None:
            query = query.filter(model.price_numeric <= max_price)
        if min_surface is not None:
            query = query.filter(model.surface_m2 >= min_surface)
        if max_surface is not None:
            query = query.filter(model.surface_m2 <= max_surface)
        if property_type:
            query = query.filter(model.property_type.ilike(f"%{property_type}%"))
        if q:
            pattern = f"%{q}%"
            query = query.filter(
                (model.description.isnot(None) & model.description.ilike(pattern)) |
                (model.location.isnot(None) & model.location.ilike(pattern))
            )
        total = query.count()
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()
        items = [Announcement(**_row_to_announcement_dict(r)) for r in results]
        return AnnouncementsResponse(total=total, page=page, per_page=per_page, items=items)
    finally:
        db.close()

@app.get("/announcements/{external_id}", response_model=Announcement)
def get_announcement(external_id: str):
    db = SessionLocal()
    try:
        # search across all tables
        for model in SOURCE_TABLES.values():
            ann = db.query(model).filter(model.external_id == external_id).first()
            if ann:
                return Announcement(**_row_to_announcement_dict(ann))
        raise HTTPException(status_code=404, detail="Not found")
    finally:
        db.close()

@app.get("/images", response_model=List[ImageModel])
def get_images(source: Optional[str] = None, limit: int = 100):
    db = SessionLocal()
    try:
        query = db.query(Image)
        if source:
            query = query.filter(Image.source == source)
        return [ImageModel(**img.__dict__) for img in query.limit(limit).all()]
    finally:
        db.close()

@app.get("/statistics")
def stats():
    db = SessionLocal()
    try:
        data = {}
        for name, model in SOURCE_TABLES.items():
            count = db.query(model).count()
            data[name] = count
        data['images'] = db.query(Image).count()
        return data
    finally:
        db.close()


def _get_all_announcements_with_surface(db):
    """Récupère (location, price_numeric, surface_m2) de toutes les tables pour analytics."""
    rows = []
    for model in SOURCE_TABLES.values():
        if not hasattr(model, 'surface_m2'):
            continue
        q = db.query(model.location, model.price_numeric, model.surface_m2, model.source).filter(
            model.price_numeric.isnot(None),
            model.price_numeric > 0,
            model.surface_m2.isnot(None),
            model.surface_m2 > 0,
        )
        for r in q.all():
            if r.location:
                rows.append({
                    "quartier": r.location.strip().split(',')[0].strip() if r.location else "Non renseigné",
                    "location_full": r.location,
                    "price_numeric": r.price_numeric,
                    "surface_m2": r.surface_m2,
                    "source": r.source,
                })
    return rows


@app.get("/analytics/price-per-m2")
def get_price_per_m2_by_quartier():
    """
    Prix moyen au m² par quartier (zone géographique).
    Regroupe les annonces ayant prix et surface renseignés.
    """
    db = SessionLocal()
    try:
        rows = _get_all_announcements_with_surface(db)
        if not rows:
            return {"quartiers": [], "moyenne_globale": None}
        from collections import defaultdict
        by_quartier = defaultdict(list)
        for r in rows:
            q = r["quartier"] or "Non renseigné"
            pm2 = r["price_numeric"] / r["surface_m2"]
            by_quartier[q].append(pm2)
        result = []
        for quartier, prices in sorted(by_quartier.items()):
            avg = sum(prices) / len(prices)
            result.append({
                "quartier": quartier,
                "prix_m2_moyen": round(avg, 2),
                "nombre_annonces": len(prices),
            })
        all_prices = [r["price_numeric"] / r["surface_m2"] for r in rows]
        return {
            "quartiers": result,
            "moyenne_globale": round(sum(all_prices) / len(all_prices), 2),
            "total_annonces": len(rows),
        }
    finally:
        db.close()


@app.get("/analytics/indice-immobilier")
def get_indice_immobilier():
    """
    Indice Immobilier (ID Immobilier): indicateur synthétique base 100.
    - Compare les zones (quartiers) à la moyenne globale
    - < 100 = sous-évalué, > 100 = surévalué
    - Permet de suivre l'évolution et comparer les zones
    """
    db = SessionLocal()
    try:
        rows = _get_all_announcements_with_surface(db)
        if not rows:
            return {"indices": [], "moyenne_reference": None}
        all_prices_m2 = [r["price_numeric"] / r["surface_m2"] for r in rows]
        moyenne_ref = sum(all_prices_m2) / len(all_prices_m2)
        from collections import defaultdict
        by_quartier = defaultdict(list)
        for r in rows:
            q = r["quartier"] or "Non renseigné"
            by_quartier[q].append(r["price_numeric"] / r["surface_m2"])
        result = []
        for quartier, prices in sorted(by_quartier.items()):
            avg = sum(prices) / len(prices)
            indice = round(100 * avg / moyenne_ref, 1) if moyenne_ref else 100
            statut = "sous-évalué" if indice < 95 else ("surévalué" if indice > 105 else "dans la moyenne")
            result.append({
                "quartier": quartier,
                "indice": indice,
                "prix_m2_moyen": round(avg, 2),
                "statut": statut,
                "nombre_annonces": len(prices),
            })
        return {
            "indices": result,
            "moyenne_reference": round(moyenne_ref, 2),
            "base": 100,
        }
    finally:
        db.close()


@app.get("/analytics/property-types")
def get_property_types():
    """Liste des types de biens disponibles pour filtrage."""
    db = SessionLocal()
    try:
        seen = set()
        for model in SOURCE_TABLES.values():
            if not hasattr(model, 'property_type'):
                continue
            for row in db.query(model.property_type).distinct().all():
                if row.property_type and row.property_type.strip():
                    seen.add(row.property_type.strip())
        return {"property_types": sorted(seen)}
    finally:
        db.close()
