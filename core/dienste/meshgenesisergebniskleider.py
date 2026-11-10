# -*- coding: utf-8 -*-
"""Meshgenesisergebniskleider — die Kleider aus der KI im Feld „Ergebnis“ einer Tripo-Jobseite (20.10.2026 nachts).

Edgar (19.10.2026, MannLaufen): „warum keine kleider im Ergebnis?“ → „baue die Ausgänge für Kleider in der KI!“. Ein Tripo-Job rechnet seine Erkennung als Test (`_test/<kennung>/`, `ergebnis_figur.test`
im Lauf); dort liegen die Kleider der KI (`Meshgenesistestkikleider`: k geschnitten, s Schnitt, h Frisur) in der Ruhelage der vorhergesagten Figur. Die Jobseite zeigt die Stücke, die die Testseite
wirksam gewählt hat (eine Wahl für beide Seiten), gehäutet mit derselben Haltung der KI (`ergebnis_Form_<g>.npz`: Gelenke, Drehungen, Ruhezentren der Figur) — und richtet sie wie die Figur
auf das Rig der Probe aus. Nur Zeilen aus der KI: die Stücke des Mesh-3D-Laufs (a/b) gehören nicht ins Ergebnis.

    Meshgenesisergebniskleider.fuer(lauf_ergebnis, geschlecht) -> {test, geschlecht, liste, rig, dreh, ruhezentren} oder None
"""
import json
import logging

import numpy as np

from .meshgenesisdaten import Meshgenesisdaten
from .meshgenesistest import Meshgenesistest

logger = logging.getLogger('core')

__all__ = ['Meshgenesisergebniskleider']


class Meshgenesisergebniskleider:
    @classmethod
    def fuer(cls, ergebnis, geschlecht):
        e = (ergebnis or {}).get('ergebnis_figur') or {}
        kennung = e.get('test')
        p = Meshgenesistest.pfad(kennung) if kennung else None
        if p is None or geschlecht not in Meshgenesistest.GESCHLECHTER:
            return None
        if not (p / ('kleider_%s' % geschlecht) / 'ki.json').is_file():
            return None
        datei, kin = p / ('ergebnis_Form_%s.npz' % geschlecht), p / ('form_%s' % geschlecht) / 'kinematik.json'
        if not datei.is_file() or not kin.is_file():
            return None
        try:
            with np.load(datei) as z:
                rig, dreh = z['rig'].astype(float), z['dreh'].astype(float)
            knochen = json.loads(kin.read_text(encoding='utf-8'))['knochen']
            zentren = [k['zentrum'] for k in knochen]
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Meshgenesisergebniskleider: %s/%s nicht lesbar (%s)', kennung, geschlecht, fehler)
            return None
        # `knochen` (22.10.2026): die Namen in der Reihenfolge der Hautgewichte der Stücke — die Animation der Ergebnisfigur bindet die Stücke damit an das Genesis-Skelett (`Meshgenesisbewegungskleid`).
        return {'test': kennung, 'geschlecht': geschlecht, 'liste': '/api/meshgenesis/test/%s/kleider/%s/' % (kennung, geschlecht),
                'rig': np.round(rig, 4).tolist(), 'dreh': np.round(Meshgenesisdaten._quaternionen(dreh), 5).tolist(), 'ruhezentren': np.round(np.array(zentren), 6).tolist(),
                'knochen': [k.get('name') for k in knochen]}
