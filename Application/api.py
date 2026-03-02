from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from Application.database import SessionLocal
from Application.models import (
    RealEstateAnnouncement,
    CoinAfriqueAnnouncement,
    IgoeAnnouncement,
    IntendanceAnnouncement,
    Image,
)

app = FastAPI(title="Immobilier Scraper API")

class Announcement(BaseModel):
    id: int
    external_id: str
    source: str
    price: Optional[str]
    price_numeric: Optional[float]
    location: Optional[str]
    description: Optional[str]
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
    "generic": RealEstateAnnouncement,
}

@app.get("/announcements", response_model=AnnouncementsResponse)
def get_announcements(
    source: Optional[str] = Query(None, description="filter by source"),
    page: int = Query(1, ge=1, description="page number starting at 1"),
    per_page: int = Query(20, ge=1, le=100, description="items per page"),
    min_price: Optional[float] = Query(None, description="minimum numeric price"),
    max_price: Optional[float] = Query(None, description="maximum numeric price"),
    q: Optional[str] = Query(None, description="full text query (description/location)"),
):
    db = SessionLocal()
    try:
        query = db.query(RealEstateAnnouncement)
        if source:
            model = SOURCE_TABLES.get(source)
            if model:
                query = db.query(model)
            else:
                raise HTTPException(status_code=400, detail="Unknown source")
        if min_price is not None:
            query = query.filter(RealEstateAnnouncement.price_numeric >= min_price)
        if max_price is not None:
            query = query.filter(RealEstateAnnouncement.price_numeric <= max_price)
        if q:
            pattern = f"%{q}%"
            query = query.filter(
                RealEstateAnnouncement.description.ilike(pattern) |
                RealEstateAnnouncement.location.ilike(pattern)
            )
        total = query.count()
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()
        items = [Announcement(**r.__dict__) for r in results]
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
                return Announcement(**ann.__dict__)
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
