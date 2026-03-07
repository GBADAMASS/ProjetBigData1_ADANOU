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

def parse_price_to_float(price_val) -> float:
    """Convertir une chaîne ou un nombre en float (exemple: '26 000 000 CFA' -> 26000000.0)"""
    if price_val is None:
        return None
    if isinstance(price_val, (int, float)):
        return float(price_val)
    try:
        price_str = str(price_val)
        price_cleaned = price_str.replace(" ", "").replace("CFA", "").strip()
        price_float = float(''.join(c for c in price_cleaned if c.isdigit() or c == '.'))
        return price_float
    except (ValueError, AttributeError):
        return None


def _get_listings_from_json(json_data: dict) -> list:
    """Extraire la liste des annonces depuis différentes structures JSON."""
    listings = json_data.get('listings') or json_data.get('announcements')
    if listings and isinstance(listings, list):
        return listings
    # Clés spécifiques par source
    for key in ('igoeimmobilier_listings', 'intendance_tg_listings'):
        listings = json_data.get(key)
        if listings and isinstance(listings, list):
            return listings
    # Fallback : première valeur qui est une liste de dicts
    if isinstance(json_data, dict):
        for val in json_data.values():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                return val
    return []


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
        
        listings = _get_listings_from_json(json_data)
        
        if isinstance(listings, list):
            for idx, listing in enumerate(listings):
                # external_id unique : utiliser l'URL si disponible, sinon index
                source_url = listing.get('link') or listing.get('price_citation') or listing.get('link_citation')
                if source_url:
                    slug = str(source_url).rstrip('/').split('/')[-1] or str(idx)
                    external_id = f"{source_name}_{slug}_{idx}"
                else:
                    external_id = f"{source_name}_{Path(file_path).stem}_{idx}"
                
                # Extraire les images
                images = []
                if 'images' in listing and isinstance(listing['images'], list):
                    images = [img.get('value') if isinstance(img, dict) else img for img in listing['images'] if img]
                    images = [u for u in images if u and isinstance(u, str)]
                
                # Description : Intendance n'a pas de description, construire depuis property_type + specifications
                description = listing.get('description')
                if not description and 'property_type' in listing:
                    desc_parts = [listing.get('property_type', '')]
                    if 'specifications' in listing and isinstance(listing['specifications'], list):
                        specs = [s.get('value', s) if isinstance(s, dict) else str(s) for s in listing['specifications'][:5]]
                        desc_parts.extend(specs)
                    description = '. '.join(str(p) for p in desc_parts if p)
                
                # Location : Intendance n'a pas de location au même format
                location = listing.get('location')
                
                # Prix : formater en chaîne si numérique (pour affichage)
                price_raw = listing.get('price')
                price_str = f"{price_raw:,.0f} FCFA" if isinstance(price_raw, (int, float)) else price_raw
                
                citations = {
                    'price_citation': listing.get('price_citation'),
                    'location_citation': listing.get('location_citation'),
                    'description_citation': listing.get('description_citation'),
                }
                
                record = {
                    'external_id': external_id,
                    'source': source_name,
                    'price': price_str,
                    'price_numeric': parse_price_to_float(price_raw),
                    'location': location,
                    'description': description,
                    'images': images,
                    'source_url': source_url,
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
            print(f"[*] Scraping {source_name} depuis {source_info['file']}...")
            print(f"    Source: {source_info['url']}")
            data = scrape_json_file(str(file_path), source_name)
            all_data.extend(data)
            print(f"[OK] {len(data)} annonces extraites de {source_name}")
        else:
            print(f"[!] Fichier non trouve: {file_path}")
    
    print(f"\nTotal: {len(all_data)} annonces scrappees")
    return all_data
