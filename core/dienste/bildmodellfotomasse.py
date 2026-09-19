# -*- coding: utf-8 -*-
"""Bildmodellfotomasse — die Proportionen der Fotos als Ziel der Formung.

Edgar (19.09.2026, Testfall Ursula): „versuchst du aus dem Genesis9 Modell das
Ursula Modell zu erstellen." Der erste Lauf traf Kopf und Breiten, aber Hüfte
34,6 statt 38,4 cm und jede Tiefe 3–5 cm zu klein — das Modell folgte dem
Zielnetz auf 0,8 mm, und das Zielnetz war die Schätzung von SMPLest-X. Die
Silhouette der Fotos hatte die Maße die ganze Zeit (`ergebnis.masse.foto`:
Hüfte 37,9 cm), sie formten nur nichts.

Hier misst `G9fotoproportionen` jedes formtaugliche Hauptbild in neutraler
Haltung (vorn, hinten, Seite) und der Median je Maß wird — in cm über die
Körperhöhe des Zielnetzes — zum Ziel von `Bildmodellzielproportionen`, wo der
Nutzer nichts eingegeben hat. Option `fotomasse` (Schritt Zielnetz): `an`
(Vorgabe) oder `aus` (nur Eingaben, das Ziel bleibt der Schätzer).

Gemessen an Ursulas gerenderten Ansichten gegen ihren echten Käfig: Hüfte
37,9 (38,4), Oberschenkel 16,9 (17,0), Wade 12,0 (12,0), Brusttiefe 26,0
(26,1), Gesäß 23,6 (22,8), Bauch 19,6 (18,6), Brustvorsprung 4,8 (4,2),
Taille 24,0 (22,7) — die YOLO-Maske ist an schmalen Stellen etwas zu breit.
"""

import logging

import numpy as np

from .bildmodellbildtypen import Bildmodellbildtypen

logger = logging.getLogger('core')

__all__ = ['Bildmodellfotomasse']


class Bildmodellfotomasse:
    """Median der Fotoproportionen über die Hauptbilder, in cm."""

    OPTION = 'fotomasse'
    ANSICHTEN = ('vorne', 'hinten', 'seite')

    def __init__(self, job, hoehe_cm):
        self.job = job
        self.hoehe_cm = float(hoehe_cm) if hoehe_cm else None

    @classmethod
    def an(cls, optionen, job=None):
        """Wahr, wenn die Fotomaße formen sollen (Vorgabe an)."""
        wert = (optionen or {}).get(cls.OPTION)
        if wert is None and job is not None:
            wert = (job.optionen or {}).get(cls.OPTION)
        return (wert or 'an') != 'aus'

    def bilder(self):
        """Hauptbilder des Körpers, neutral stehend, für die Form gewählt."""
        return [
            b for b in self.job.bilder
            if b.get('kategorie') == 'koerper' and b.get('ansicht') in self.ANSICHTEN
            and b.get('haltung') == 'neutral' and Bildmodellbildtypen.fuer_form(b)
        ]

    def messen(self):
        """`{'cm': {schluessel: cm}, 'bilder': {schluessel: n}, 'anzahl': n}` — leer ohne Höhe."""
        if not self.hoehe_cm:
            return {'cm': {}, 'bilder': {}, 'anzahl': 0}
        from Genesis9.fotoproportionen import G9fotoproportionen

        werte = {}
        bilder = self.bilder()
        for b in bilder:
            for k, v in G9fotoproportionen(b).messen().items():
                werte.setdefault(k, []).append(float(v))
        cm = {k: round(float(np.median(v)) * self.hoehe_cm, 1) for k, v in werte.items()}
        anzahl = {k: len(v) for k, v in werte.items()}
        logger.info('Bildmodell %s: Fotomaße aus %d Bildern: %s', self.job.kennung, len(bilder), cm)
        return {'cm': cm, 'bilder': anzahl, 'anzahl': len(bilder)}
