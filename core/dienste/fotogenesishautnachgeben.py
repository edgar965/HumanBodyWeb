# -*- coding: utf-8 -*-
"""Fotogenesishautnachgeben — „Haut gibt nach“ eines Foto-Genesis-Jobs an die Eigen-Stücke seines Mesh-Genesis-Tests (15.11.2026 nachts, Edgar: „mach oben bei den Jobs … auch einen
Button ‚Haut gibt nach‘ mit dem dieses Feature eingeschaltet wird, mach auch eine mm angabe“ — „Macht das ein Feature für die Jobs und für die Anpassung der Kleider“).

Die Tiefe wirkt im Browser je Stück (`Bauart.nachgebenM` → `Hauteinzug`, verdeckte Haut zieht bis dahin unter den Stoff) und steht als `nachgeben_mm` in der Bauart der Garderobe
(`Genesis9.bauart.G9bauart`) — dort liest sie jede Seite und jede Animation, die das Stück trägt. Gesetzt wird sie nur an den Eigen-Stücken des Tests (Hersteller EIGEN, je Test
eigene Kennung, `Garderobeeigen`): ein Bibliotheksstück teilen sich viele Figuren. Die gesetzte Bauart (starr für Requisiten) bleibt.

    Fotogenesishautnachgeben.anwenden(test_ordner, mm)          # → [(kennung, mm)]
    Fotogenesishautnachgeben.fuer_job(job)                      # Wahl des Jobs (`Fotogenesispshuman.nachgeben_mm`) an seinen Test
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger('core')

__all__ = ['Fotogenesishautnachgeben']


class Fotogenesishautnachgeben:

    @staticmethod
    def eigen_kennungen(test):
        """Kennungen der Eigen-Stücke, die der Test in Weg z trägt (`kleider_<g>/z/garderobe.json`, Zeilen mit `eigen.genommen`)."""
        aus = []
        for datei in sorted(Path(test).glob('kleider_*/z/garderobe.json')):
            try:
                zeilen = json.loads(datei.read_text(encoding='utf-8')).get('zeilen') or []
            except (OSError, ValueError):
                continue
            aus += [z['kennung'] for z in zeilen if z.get('kennung') and (z.get('eigen') or {}).get('genommen')]
        return sorted(set(aus))

    @staticmethod
    def setzen(kennungen, mm):
        """Tiefe `mm` an die Stücke `kennungen`, ihre gesetzte Bauart bleibt (`G9bauart.setzen` nimmt sonst mit None die Bauart zurück)."""
        from Genesis9.bauart import G9bauart
        for k in kennungen:
            art, _tiefe = G9bauart.gesetzt(k)
            G9bauart.setzen(k, art, float(mm))
        return [(k, mm) for k in kennungen]

    @classmethod
    def anwenden(cls, test, mm):
        gesetzt = cls.setzen(cls.eigen_kennungen(test), mm)
        logger.info('Fotogenesishautnachgeben: %s → %s mm an %d Eigen-Stücken', Path(test).name, mm, len(gesetzt))
        return gesetzt

    @staticmethod
    def test_mm(test):
        """Wirksame Tiefe des Foto-Genesis-Jobs, der den Test nennt (`Hautohneki.jobs`), oder None ohne Job."""
        from meshgenesis_haut_ohneki import Hautohneki

        from .fotogenesispshuman import Fotogenesispshuman
        for _ordner, info in Hautohneki.jobs(Path(test)):
            return Fotogenesispshuman.nachgeben_mm(info)
        return None

    @classmethod
    def fuer_job(cls, job):
        from .fotogenesispshuman import Fotogenesispshuman
        from .meshgenesistest import Meshgenesistest
        if not job.get('test') or not job.get('ordner'):
            return []
        info = json.loads((Path(job['ordner']) / 'job.json').read_text(encoding='utf-8'))
        return cls.anwenden(Meshgenesistest.ordner() / job['test'], Fotogenesispshuman.nachgeben_mm(info))
