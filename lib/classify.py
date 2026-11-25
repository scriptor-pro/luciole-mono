"""Classement des glyphes selon leur largeur d'origine."""


def classify(width: int, cell: int, tol: float) -> str:
    """Renvoie "near", "wide" ou "narrow" par rapport à la cellule."""
    if abs(width - cell) <= tol * cell:
        return "near"
    return "wide" if width > cell else "narrow"
