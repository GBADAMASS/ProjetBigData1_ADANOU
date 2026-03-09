"""
Extraction du type de bien et de la surface (m²) depuis la description ou autres champs.
Utilise des expressions régulières pour détecter les patterns courants.
"""
import re
from typing import Tuple, Optional, Any

# Types de biens courants (ordre important: plus spécifique en premier)
PROPERTY_TYPES = [
    "Studio meublé", "Studio meuble", "Studio",
    "Villa duplex", "Villa meublée", "Villa meublee", "Villa duplex",
    "Appartement meublé", "Appartement meuble", "Appartement",
    "Maison / Villa avec piscine", "Maison / Villa moderne", "Maison / Villa plein pied",
    "Maison / Villa", "Villa", "Maison",
    "Duplex semi-détaché", "Duplex",
    "Terrain", "Commercial office", "Bureau",
]

# Patterns pour la surface (m², m2, m carrés, etc.)
SURFACE_PATTERNS = [
    r"(?:surface|superficie|de)\s*(?:de\s*)?(\d+[,.]?\d*)\s*(?:m²|m2|m\s*carrés?|mètres?\s*carrés?|m\s*carr)",
    r"(\d+)\s*(?:m²|m2|m\s*carrés?|mètres?\s*carrés?)",
    r"(\d+)\s*lots?\b",  # "1 lot" = ~300m² souvent au Togo
    r"(\d+)\s*(?:a|ares?)\s*(?:ca)?",  # 2a = 200m²
    r"surface[:\s]+(\d+)",
]


def extract_surface(text: str) -> Optional[float]:
    """Extrait la surface en m² depuis un texte."""
    if not text:
        return None
    text = str(text)
    for pattern in SURFACE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m and m.lastindex and m.group(1) is not None:
            try:
                val = float(str(m.group(1)).replace(",", "."))
                # Si c'est en ares (a), 1a = 100 m²
                if "a" in pattern.lower() or "are" in pattern.lower():
                    val *= 100
                if 1 <= val <= 50000:  # Plage raisonnable
                    return val
            except (ValueError, IndexError):
                pass
    return None


def extract_property_type(text: str) -> Optional[str]:
    """Extrait le type de bien depuis un texte."""
    if not text:
        return None
    text = str(text)
    for pt in PROPERTY_TYPES:
        if re.search(re.escape(pt), text, re.IGNORECASE):
            return pt
    return None


def extract_from_record(record: dict) -> Tuple[Optional[float], Optional[str]]:
    """
    Extrait surface_m2 et property_type depuis un enregistrement.
    Utilise description, property_type natif, etc.
    """
    surface = None
    ptype = None

    # Surface : priorité aux champs natifs
    for key in ("surface_m2", "surface_area", "square_footage"):
        v = record.get(key)
        if v is not None:
            try:
                surface = float(v)
                if surface <= 0 or surface > 50000:
                    surface = None
                else:
                    break
            except (TypeError, ValueError):
                pass

    if surface is None:
        desc = record.get("description") or ""
        surf_from_desc = extract_surface(desc)
        if surf_from_desc:
            surface = surf_from_desc

    # Type : priorité aux champs natifs
    ptype = record.get("property_type")
    if not ptype:
        desc = record.get("description") or ""
        ptype = extract_property_type(desc)
    if ptype and isinstance(ptype, str) and len(ptype) > 50:
        ptype = ptype[:50]  # Limiter la longueur

    return surface, ptype
