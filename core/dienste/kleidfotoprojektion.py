# -*- coding: utf-8 -*-
"""Kleidfotoprojektion — die Fotoprojektion auf Kleid und Haar innerhalb einer Runde (30.09.2026, Konzept 4.5).

`kleid_fototextur`/`haar_fototextur` im Rezept merken nur den Wunsch (`modell.fotowuensche`); die Runde ruft nach dem Bau
der Teile `bauen`: je Vorlage ein Kennfarbenrender in Texturgröße (`GROESSE`, feiner als die Note — die Farbe je Texel
braucht mehr als 128 × 192), daraus der Kasten der Normierung (`Iterationsbild.abbildung`) und die Teilmasken, das Foto
in derselben Größe; dann je gewünschtem Stück: seine Teile in den UV-Raum gerastert (`G9uvraster`), `Fotoprojektion`
(`iterationen2d3d`) holt die Farbe, `G9kleidfototextur` legt die Schicht `foto` ab. Ergebnis je Stück ein Steckbrief
(getroffene Texel je Gruppe, Ansichten, Sekunden) — oder der Fehler als Text; ein Stück, das die Fotos nicht sehen, hält
die Runde nicht auf.
"""

import logging
import time

import numpy as np
from Genesis9.kleidfototextur import G9kleidfototextur
from Genesis9.uvraster import G9uvraster
from iterationen2d3d.fotoprojektion import Fotoprojektion
from iterationen2d3d.teilmasken import Teilmasken
from PIL import Image

from .iterationsbild import Iterationsbild
from .iterationsreferenz import Iterationsreferenz
from .kleidhautfilter import Kleidhautfilter

logger = logging.getLogger('core')

__all__ = ['Kleidfotoprojektion']


class Kleidfotoprojektion:
    #: Fläche der Projektion (Breite, Höhe) — 512 × 768 wie der Render der Engine, 4-fach feiner als die Note.
    GROESSE = (512, 768)
    #: Bildpunkte vom Rand der freigestellten Figur, die nicht zählen (`Fotoprojektion(figurrand=)`).
    FIGURRAND = 2

    def __init__(self, ablage, render, ordner):
        self.ablage = ablage
        self.render = render
        self.ordner = ordner

    def _ansichten(self, teile, referenzen):
        """`[(referenz, abbildung, foto, masken)]` je Vorlage mit Blickwinkel."""
        aus = []
        for r in referenzen:
            pfad = self.ordner / ('textur_kennung_%+04d.png' % int(round(r.winkel)))

            def kennbild(farben, block, r=r, pfad=pfad):     # je Block ein Bild (`Teilmasken.messen`)
                ziel = pfad if not block else pfad.with_name('%s_b%d%s' % (pfad.stem, block, pfad.suffix))
                self.render.bild_teile([(t['punkte'], t['dreiecke'], farben[i]) for i, t in enumerate(teile)],
                                       r.winkel, ziel, groesse=self.GROESSE, kennung=True)
                bild = Iterationsbild.aus_render(ziel, self.GROESSE)
                return bild.farbe, bild.maske

            masken = Teilmasken.messen(len(teile), kennbild)
            with Image.open(pfad) as bild:
                abbildung = Iterationsbild.abbildung(np.asarray(bild.convert('RGBA'))[..., 3] > 127)
            if abbildung is None:
                continue
            foto = Iterationsreferenz.bild(self.ablage, r.datei, self.GROESSE)
            aus.append((r, abbildung, foto, masken))
        return aus

    @staticmethod
    def _hautausschluesse(ansichten, teilmasken, haut):
        """Je Ansicht die Foto-Pixel, die Haut zeigen und für das Stück nicht zählen (`Kleidhautfilter`): die erweiterte Teilmaske ließ Haut neben dem Saum als hautfarbene Zellen in die Textur der Hose, und im Seitenfoto
        kam die Hand vor der Hose dazu. Den Farbton des Stücks gibt die reinste Ansicht (`Kleidhautfilter.reinster`) — ohne Körper oder ohne Unterschied zur Haut gibt es keinen Ausschluss (None je Ansicht)."""
        if not haut:
            return [None] * len(ansichten)
        hautmasken = [np.any([masken[i] for i in haut], axis=0) for _r, _a, _f, masken in ansichten]
        bezug = Kleidhautfilter.reinster([Kleidhautfilter.bezug(foto.farbe, foto.maske, tm, hm) for (_r, _a, foto, _m), tm, hm in zip(ansichten, teilmasken, hautmasken)])
        if bezug is None:
            return [None] * len(ansichten)
        return [Kleidhautfilter.haut(foto.farbe, foto.maske, tm, hm, stoff_ab=bezug[0]) for (_r, _a, foto, _m), tm, hm in zip(ansichten, teilmasken, hautmasken)]

    def bauen(self, modell, teile, referenzen):
        """→ `{kennung: steckbrief | {'fehler': text}}` für jeden Wunsch des Modells; die Wünsche werden geleert."""
        wuensche = dict(getattr(modell, 'fotowuensche', None) or {})
        if not wuensche or not referenzen:
            return {}
        t0 = time.perf_counter()
        alle = np.vstack([np.asarray(t['punkte']) for t in teile])
        kamera = Fotoprojektion.aus_render(alle, self.render.RAND, self.GROESSE)
        ansichten = self._ansichten(teile, referenzen)
        aus = {}
        for kennung, art in wuensche.items():
            indizes = [i for i, t in enumerate(teile) if t.get('sorte') == kennung and t.get('uv') is not None
                       and t.get('gruppen')]
            if not indizes:
                aus[kennung] = {'fehler': 'Stück nicht gebaut oder ohne UV (%s)' % art}
                continue
            projektion = Fotoprojektion(kamera.mitte, kamera.halb, self.GROESSE, hoehenprofil=True, figurrand=self.FIGURRAND)
            haut = [i for i, t in enumerate(teile) if t.get('art') == 'koerper' and t.get('sorte') == 'koerper']
            teilmasken = [np.any([masken[i] for i in indizes], axis=0) for _r, _a, _f, masken in ansichten]
            ausschluesse = self._hautausschluesse(ansichten, teilmasken, haut)
            for (r, abbildung, foto, _masken), teilmaske, ausschluss in zip(ansichten, teilmasken, ausschluesse):
                projektion.ansicht(r.winkel, abbildung, foto.farbe, foto.maske, teilmaske, ausschluss=ausschluss)
            raster = [G9uvraster(teile[i]['punkte'], teile[i]['dreiecke'], teile[i]['uv'], teile[i]['gruppen'],
                                 normalen=teile[i].get('normalen')) for i in indizes]
            try:
                aus[kennung] = G9kleidfototextur.bauen(kennung, raster, projektion, schicht=modell.fotoschicht())
            except (ValueError, OSError) as fehler:
                aus[kennung] = {'fehler': str(fehler)}
                logger.warning('Fotoprojektion %s: %s', kennung, fehler)
        modell.fotowuensche.clear()
        logger.info('Fotoprojektion: %s in %.1f s', sorted(aus), time.perf_counter() - t0)
        return aus
