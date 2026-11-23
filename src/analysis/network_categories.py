"""Categorías de las redes actuales, independientes de la anotación NER original.

KAS reúne conocimientos, actitudes y habilidades sin fusionar identidades
canónicas ni reescribir las fuentes o las ejecuciones históricas de clusters.
"""

from src.categories import ACTIVE_CATEGORIES

KAS_SOURCE_CATEGORIES = frozenset({"ATT", "KNOW", "SKILL"})
NETWORK_CATEGORIES = (ACTIVE_CATEGORIES - KAS_SOURCE_CATEGORIES) | {"KAS"}
KAS_DEFINITION = (
    "Categoría que reúne los saberes, las actitudes y valores, y las habilidades "
    "identificados en el texto. Conserva la evidencia de la clasificación original."
)


def network_category(category: str) -> str:
    return "KAS" if category in KAS_SOURCE_CATEGORIES else category
