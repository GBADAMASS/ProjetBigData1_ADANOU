from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class RealEstateAnnouncement(Base):
    """Modèle pour les annonces immobilières scrappées"""
    __tablename__ = "real_estate_announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(100), nullable=False)  # Coin-Afrique, igoe-immobilier, intendance-tg
    price = Column(String(100), nullable=True)
    price_numeric = Column(Float, nullable=True)  # Pour les recherches numériques
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)  # Liste des URLs d'images
    source_url = Column(String(500), nullable=True)
    citations = Column(JSON, nullable=True)  # URLs de citation des données
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RealEstateAnnouncement(id={self.id}, source={self.source}, location={self.location})>"


class CoinAfriqueAnnouncement(Base):
    __tablename__ = "coinafrique_announcements"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(100), nullable=False, default="Coin-Afrique")
    price = Column(String(100), nullable=True)
    price_numeric = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)
    source_url = Column(String(500), nullable=True)
    citations = Column(JSON, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IgoeAnnouncement(Base):
    __tablename__ = "igoe_announcements"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(100), nullable=False, default="igoe-immobilier")
    price = Column(String(100), nullable=True)
    price_numeric = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)
    source_url = Column(String(500), nullable=True)
    citations = Column(JSON, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IntendanceAnnouncement(Base):
    __tablename__ = "intendance_announcements"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(100), nullable=False, default="intendance-tg")
    price = Column(String(100), nullable=True)
    price_numeric = Column(Float, nullable=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)
    source_url = Column(String(500), nullable=True)
    citations = Column(JSON, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), nullable=True, index=True)
    source = Column(String(100), nullable=True)
    url = Column(String(1000), nullable=False)
    position = Column(Integer, nullable=True)  # index in the images list
    citations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Image(id={self.id}, source={self.source}, url={self.url})>"

