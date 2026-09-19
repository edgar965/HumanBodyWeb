# -*- coding: utf-8 -*-
"""Bildmodellhaende — die Nebenbild-Regler: Fingerlänge aus Handaufnahmen.

Edgar (19.09.2026, „baue alles"): Daz-Shopbilder zeigen die Hände als
Nahaufnahme. Ein solches Bild hat keinen Maßstab, aber ein Verhältnis:
Mittelfinger zu Handfläche (`G9handmasse`, MediaPipe-Weltpunkte aus der
Sichtung, `haende_punkte`). Über ALLE Hände des Auftrags (Haupt- und
Nebenbilder, Güte ≥ 0,8) der Median, daraus `ProportionFingersLength`
— und der wird in der Ausgleichung FESTGEHALTEN (`fest`), damit die
Hauptbilder (Hände zu 42–46 % zugeordnet, 9 mm Rest) ihn nicht verwässern.
Nur ein Regler: `breite` ändert kein Proportionsregler, und PalmSize wirkt
auf dasselbe Verhältnis gegenläufig (singulär) — steht in `G9handmasse`.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Bildmodellhaende']


class Bildmodellhaende:
    def __init__(self, job, grund):
        self.job = job
        self.grund = grund

    def regler(self):
        """`({variable: wert}, beleg)` — leer, wenn keine sichere Hand da ist."""
        from Genesis9.formung import G9formung
        from Genesis9.handmasse import G9handmasse
        from Genesis9.reglerableitung import G9reglerableitung

        gemessen = G9handmasse.aus_bildern(self.job.bilder)
        if not gemessen:
            return {}, {'haende': 0}
        grenzen = {r['name']: (r['min'], r['max']) for r in G9reglerableitung.regler('proportionen')}
        werte, erreicht = G9handmasse.regler(
            gemessen, self.grund, G9formung, grenzen.get(G9handmasse.REGLER, (-2.0, 2.0))
        )
        beleg = {
            'haende': gemessen['haende'],
            'finger': round(gemessen['finger'], 4),
            'finger_streuung': round(gemessen.get('finger_streuung', 0.0), 4),
            'breite': round(gemessen['breite'], 4),
            'erreicht': round(erreicht['finger'], 4),
            'regler': werte,
        }
        logger.info(
            'Bildmodell %s: %d Hände, Finger/Handfläche %.3f → %s',
            self.job.kennung,
            gemessen['haende'],
            gemessen['finger'],
            werte,
        )
        return werte, beleg
