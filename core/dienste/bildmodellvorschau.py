# -*- coding: utf-8 -*-
"""Bildmodellvorschau — Schritt „vorschau": Bilder, Maße, Proportionen, Textur, Testfall.

Aus `Bildmodellanpassung.vorschau` herausgelöst (19.09.2026, die Datei
stand bei 291 Zeilen), als der Testfall dazukam. Reihenfolge und Anteile
am Fortschrittsband:

    0,00–0,80  Icon und Ansichten vorn/seite/hinten/Kopf (`G9vorschaubild`)
    0,85       Außenmaße Foto / Zielnetz / Modell (`Bildmodellmasse`) und rund 40 Körpermaße
               SMPL-X (GVHMR) / Ziel / Modell (`Bildmodellmassband`, 20.09.2026)
    0,86–0,96  Proportionen Vorher/Nachher (`Bildmodellproportionen`)
    0,96–1,00  Testfall: Abstand zur Referenzfigur (`Bildmodelltestfall`)

Alles landet in `job.ergebnis` (`vorschau`, `masse`, `proportionen`,
`testfall`); was ein Lauf nicht mehr liefert, wird entfernt. Die Fototextur
ist seit dem 19.09. abends ein eigener Schritt `textur` (`Bildmodelllauf._textur`).
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Bildmodellvorschau']


class Bildmodellvorschau:
    def __init__(self, job, ablage, optionen, stellung, ziel_laden):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen
        self.stellung = stellung
        self._ziel_laden = ziel_laden

    def bilder(self, melder=None):
        """Icon und die vier Ansichten — `{name: dateiname}`."""
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung
        from Genesis9.vorschaubild import G9vorschaubild
        from PIL import Image

        p, _, _ = G9reglerableitung.lage(G9formung(self.stellung))
        bild = G9vorschaubild(p)
        ordner = self.ablage.ergebnis()
        dateien = {'icon': bild.icon(ordner / 'icon.png')}
        for i, ansicht in enumerate(('vorn', 'seite', 'hinten')):
            if melder:
                melder(0.2 + 0.2 * i, 'Ansicht %s' % ansicht)
            dateien[ansicht] = bild.speichern(ordner / ('vorschau_%s.png' % ansicht), ansicht)
        Image.fromarray(bild.kopf('vorn', 500), 'RGBA').save(ordner / 'vorschau_kopf.png')
        dateien['kopf'] = str(ordner / 'vorschau_kopf.png')
        return {k: str(v).replace('\\', '/').split('/')[-1] for k, v in dateien.items()}

    def ausfuehren(self, melder=None):
        from .bildmodellmasse import Bildmodellmasse
        from .bildmodellproportionen import Bildmodellproportionen
        from .bildmodelltestfall import Bildmodelltestfall

        self.job.ergebnis['vorschau'] = self.bilder(melder)
        if melder:
            melder(0.85, 'Außenmaße Foto / Zielnetz / Modell')
        self.job.ergebnis['masse'] = Bildmodellmasse(self.job, self.stellung).alle()
        # Rund 40 Körpermaße SMPL-X (GVHMR) / Ziel / Modell (`G9massband`, 20.09.2026).
        from .bildmodellmassband import Bildmodellmassband

        self.job.ergebnis['massband'] = Bildmodellmassband(self.job, self.stellung, self._ziel_laden).alle()
        self.job.ergebnis['proportionen'] = Bildmodellproportionen(
            self.job, self.ablage, self.stellung, self._ziel_laden
        ).alle(lambda a, t: melder and melder(0.86 + 0.10 * a, t))
        self.job.ergebnis.pop('testfall', None)
        if Bildmodelltestfall.figur(self.optionen):
            self.job.ergebnis['testfall'] = Bildmodelltestfall(self.job, self.optionen).vergleichen(
                self.stellung, lambda a, t: melder and melder(0.96 + 0.04 * a, t)
            )
        return self.job.ergebnis
