# -*- coding: utf-8 -*-
"""Einstieg fuer den Hintergrundfaden eines BVH-Auftrags.

`_run_processing` hatte 302 Zeilen mit vier Routen und einer fuenfmal
wiederholten Nachbereitung. Der Ablauf liegt jetzt in der Klasse `Auftragslauf`
(core/pipelines/auftragslauf.py); hier bleibt der Einsprungpunkt, den der Faden
in `core/api/auftraege.py` aufruft.
"""
from .auftragslauf import Auftragslauf


def _run_processing(job_id):
    """Einen Auftrag von Anfang bis Ende durchfuehren (laeuft im Faden)."""
    Auftragslauf(job_id).ausfuehren()
