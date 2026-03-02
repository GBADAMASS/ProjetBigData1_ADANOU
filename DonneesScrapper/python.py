"""
Scraper pour les annonces immobilières au Togo

Sources de données:
    1. OmniSoft API: https://devapi.omnisoft.africa/public/api/v2
    2. Intendance.tg: https://intendance.tg/
    3. Coin Afrique: https://tg.coinafrique.com/categorie/immobilier
    4. IGOE Immobilier: https://www.igoeimmobilier.com/
    
Ce module traite les fichiers JSON extraits et les prépare pour la base de données.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

def parse_price_to_float(price_str: str) -> float:
    """Convertir une chaîne de prix en float (exemple: '26 000 000 CFA' -> 26000000.0)"""
    try:
        # Enlever les espaces et la devise (CFA, etc.)
        price_cleaned = price_str.replace(" ", "").replace("CFA", "").strip()
        # Prendre les chiffres et le point décimal
        price_float = float(''.join(c for c in price_cleaned if c.isdigit() or c == '.'))
        return price_float
    except (ValueError, AttributeError):
        return None

def scrape_json_file(file_path: str, source_name: str) -> List[Dict[str, Any]]:
    """
    Scraper les données d'un fichier JSON
    
    Args:
        file_path: Chemin vers le fichier JSON
        source_name: Nom de la source (Coin-Afrique, igoe-immobilier, intendance-tg)
    
    Returns:
        List[Dict]: Liste des annonces formatées depuis ce fichier
    """
    data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Vérifier la structure (listings ou announcements ou autre)
        listings = json_data.get('listings', []) or json_data.get('announcements', []) or json_data
        
        if isinstance(listings, list):
            for idx, listing in enumerate(listings):
                # Créer un ID externe unique basé sur la source et l'index
                external_id = f"{source_name}_{Path(file_path).stem}_{idx}"
                
                # Extraire les images
                images = []
                if 'images' in listing and isinstance(listing['images'], list):
                    images = [img.get('value') for img in listing['images'] if img.get('value')]
                
                # Préparer les citations
                citations = {
                    'price_citation': listing.get('price_citation'),
                    'location_citation': listing.get('location_citation'),
                    'description_citation': listing.get('description_citation'),
                }
                
                record = {
                    'external_id': external_id,
                    'source': source_name,
                    'price': listing.get('price'),
                    'price_numeric': parse_price_to_float(listing.get('price', '')),
                    'location': listing.get('location'),
                    'description': listing.get('description'),
                    'images': images,
                    'source_url': listing.get('price_citation'),  # URL source
                    'citations': citations,
                }
                
                data.append(record)
    
    except Exception as e:
        print(f"Erreur lors du scraping de {file_path}: {str(e)}")
    
    return data

def scrape_source() -> List[Dict[str, Any]]:
    """
    Scraper tous les fichiers JSON du dossier DonneesScrapper
    
    Sources traités:
        - Coin-Afrique: https://tg.coinafrique.com/categorie/immobilier
        - IGOE Immobilier: https://www.igoeimmobilier.com/
        - Intendance.tg: https://intendance.tg/
        - OmniSoft API: https://devapi.omnisoft.africa/public/api/v2
    
    Returns:
        List[Dict]: Liste des annonces immobilières formatées
    """
    scrapper_dir = Path(__file__).parent
    all_data = []
    
    # Mapping des sources avec leurs fichiers JSON correspondants
    source_mapping = {
        'Coin-Afrique': {
            'file': 'extract-data-2026-02-21-Coin-Afrique.json',
            'url': 'https://tg.coinafrique.com/categorie/immobilier'
        },
        'igoe-immobilier': {
            'file': 'extract-data-2026-02-21-igoe-immobilier.json',
            'url': 'https://www.igoeimmobilier.com/'
        },
        'intendance-tg': {
            'file': 'extract-data-2026-02-21-intendance-tg.json',
            'url': 'https://intendance.tg/'
        },
    }
    
    # Scraper chaque fichier JSON
    for source_name, source_info in source_mapping.items():
        file_path = scrapper_dir / source_info['file']
        
        if file_path.exists():
            print(f"🔄 Scraping {source_name} depuis {source_info['file']}...")
            print(f"   Source: {source_info['url']}")
            data = scrape_json_file(str(file_path), source_name)
            all_data.extend(data)
            print(f"✅ {len(data)} annonces extraites de {source_name}")
        else:
            print(f"⚠️  Fichier non trouvé: {file_path}")
    
    print(f"\n📊 Total: {len(all_data)} annonces scrappées")
    return all_data
