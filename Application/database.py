from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Application.models import Base

DATABASE_URL = "mysql+pymysql://root@localhost/scrapperDonnee_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Créer les tables si elles n'existent pas
Base.metadata.create_all(bind=engine)