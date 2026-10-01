# -*- coding: utf-8 -*-
"""Begutachtungswerkzeug — was eine Begutachtungsrunde um den Bau herum braucht: Sichtkörper der Fotos, Stofflöser,
Fotoprojektion und die gebackene Haut des Körpers (aus `Begutachtungsrunde` herausgelöst, 01.10.2026 — die Datei stand
bei 299 Zeilen).

Eine Instanz je Lauf: Sichtkörper und Körperpunkte werden zwischengespeichert (je Modellhöhe auf den cm).
"""

import numpy as np

__all__ = ['Begutachtungswerkzeug']


class Begutachtungswerkzeug:
    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage
        self._koerper_punkte = None
        self._sicht = None

    def zubehoer(self, referenzen):
        """`{'uhr': ['l'|'r', …]}` — was die Fotos an Zubehör zeigen (`Uhrerkennung`), einmal je Lauf; fehlt das Stück
        dazu in der Garderobe, wird es gebaut (`G9uhrstueck`, ~1 s). Fehler: leer, mit Log — Zubehör ist Beiwerk."""
        if getattr(self, '_zubehoer', None) is None:
            import logging
            try:
                from Genesis9.garderobe import G9garderobe
                from Genesis9.uhrstueck import G9uhrstueck

                from .uhrerkennung import Uhrerkennung
                uhr = [s for s, e in Uhrerkennung(self.ablage).erkennen(referenzen).items() if e['gefunden']]
                for seite in uhr:
                    if not G9garderobe.eintrag('eigen_uhr_%s' % seite):
                        G9uhrstueck.bauen(seite)
                self._zubehoer = {'uhr': uhr}
            except Exception:  # noqa: BLE001 — Beiwerk: die Runde läuft ohne weiter
                logging.getLogger('core').exception('2D3D Kleider %s: Zubehör nicht erkannt', self.job.kennung)
                self._zubehoer = {}
        return self._zubehoer

    def kacheln(self):
        """`{kachel: Pfad}` der gebackenen Haut — der Körper der Runde trägt sie (`Koerpertextur`)."""
        from .koerpertextur import Koerpertextur
        return Koerpertextur.kacheln(self.job, self.ablage)

    def drapierer(self):
        """Die Stofflöser für `kleid_drapieren` — Newton (Vorgabe) und Blender, beide im Arbeitsordner des Auftrags."""
        from .haarengineblender import Haarengineblender
        from .kleiddrapierung import Kleiddrapierung
        return {'newton': Kleiddrapierung(self.ablage.arbeit('stoff')),
                'blender': Haarengineblender(self.ablage.arbeit('blender'))}

    def fototextur(self, modell, teile, referenzen, render, bau, aus):
        """Die Fotoprojektion der gewünschten Stücke (`Kleidfotoprojektion`) und die Texturen der Teile danach neu."""
        from .kleidfotoprojektion import Kleidfotoprojektion
        farbig = [r for r in referenzen if r.farbe]          # Fotos mit anderer Kleidung zählen nur für die Form
        bericht = Kleidfotoprojektion(self.ablage, render, aus).bauen(modell, teile, farbig)
        gebaut = [k for k, b in bericht.items() if not b.get('fehler')]
        if gebaut:
            bau.textur_auffrischen([t.get('ruhe', t) for t in teile], modell, set(gebaut))
            for t in teile:                     # die gehäuteten Kopien tragen dieselben Bilder wie ihre Ruhelage
                t['textur'] = t.get('ruhe', t)['textur']
        return bericht

    def sichtkoerper(self, referenzen, z):
        """`Sichtkoerper` aus den Silhouetten der Vorlagen — je Lauf einmal je Modellhöhe (auf den cm); None ohne
        Fotos."""
        from iterationen2d3d.sichtkoerper import Sichtkoerper

        from .kleidermodellbau import Kleidermodellbau
        if not referenzen:
            return None
        if self._koerper_punkte is None:
            self._koerper_punkte = np.asarray(Kleidermodellbau(self.job.stellung()).koerper()['punkte'])
        hoehe = round(float(z.get('modell_hoehe') or self._koerper_punkte[:, 1].max()), 2)
        if self._sicht is not None and self._sicht[0] == hoehe:
            return self._sicht[1]
        sicht = Sichtkoerper([(r.winkel, r.bild.maske) for r in referenzen], hoehe, self._koerper_punkte)
        self._sicht = (hoehe, sicht)
        return sicht
