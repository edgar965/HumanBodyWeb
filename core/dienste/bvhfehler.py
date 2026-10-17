# -*- coding: utf-8 -*-
"""BvhFehler — Ablehnung der BVH-Verwaltung.

Eigene Datei, damit `Bvhverwaltung` (Dateien) und `Bvhordner` (Ordner) sie
teilen, ohne sich gegenseitig zu importieren. `bvhverwaltung` fuehrt den Namen
weiter, die bisherigen Importe (`from ..dienste.bvhverwaltung import BvhFehler`)
gelten unveraendert.
"""

from .dienstfehler import DienstFehler


class BvhFehler(DienstFehler):
    """Ablehnung der BVH-Verwaltung. Rumpf und Kennzahl siehe `DienstFehler`.

    Eigene Klasse, damit ein `except BvhFehler` nicht die Kleiderverwaltung
    mitfaengt — aber ohne den Rumpf noch einmal zu schreiben (Befund
    `doppelrumpf`, 17.08.2026: derselbe Rumpf und dasselbe `__init__` lagen
    zweimal im Projekt)."""
