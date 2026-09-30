# -*- coding: utf-8 -*-
"""Kostuemabschluss — was am Ende eines Kostüm-Laufs abgelegt wird (aus `Kostuemkreislauf` herausgelöst, 30.09.2026).

1. Die NEUESTE Runde bekommt ein Modell, wenn sie keines hat (`Kostuemmodellablage.nachtragen`): Sie ist meist ein verworfener
   Vorschlag der Prüf-KI, und die Tabelle „Iterationen" stellt sie neben die beste Runde — nur mit Modell sind beide Bilder
   dieselbe Darstellung wie in der 3D-Ansicht.
2. Das beste Kostüm einmal bauen, ans Rig binden und nach `ergebnis/` legen: GLB (Figur + Kostüm + Rig in der RUHELAGE —
   dieselbe wie `figur.glb`, darauf laufen Blender-Film und Bühne), .blend und die Begleitdatei mit den flachen Farben.
3. Das Sichtmodell des besten Kostüms (`kostuem_sicht.glb`).
"""

import logging
import shutil

from .kostuemmodellablage import Kostuemmodellablage

logger = logging.getLogger('core')

__all__ = ['Kostuemabschluss']


class Kostuemabschluss:
    GLB, BLEND, FARBEN = 'kostuem.glb', 'kostuem.blend', 'kostuem.farben.json'
    SICHT_GLB = 'kostuem_sicht.glb'

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    def ausfuehren(self, runde_, bester, z):
        self.neueste_bebildern(runde_)
        self.lauf.melden(0.97, 'Bestes Kostüm als GLB und .blend ablegen')
        self._bestes(runde_, bester, z)
        self._sicht_ablegen(runde_, bester, z)
        self._sichern(z)
        self.lauf.melden(
            1.0, 'Kostüm: Abweichung %.4f (Runde %d)' % (z['note']['abweichung'], z['runde_bester'])
        )

    def _sichern(self, z):
        self.job.ergebnis['kostuem'] = z
        self.lauf.sichern('ergebnis')

    def neueste_bebildern(self, runde_):
        """Der Eintrag mit der höchsten Rundennummer bekommt ein Modell, wenn er keines hat. Ein Fehler des Baus hält den
        Abschluss nicht auf (`Kostuemrunde.modell` meldet ihn im Log, der Eintrag bleibt ohne Modell)."""
        eintraege = self.job.ergebnis.get('iterationen') or []
        if not runde_.textur or not eintraege:
            return
        neueste = max(eintraege, key=lambda e: int(e['runde']))
        if (neueste.get('dateien') or {}).get('modell'):
            return
        self.lauf.melden(0.95, 'Modell der neuesten Runde %d bauen' % neueste['runde'])
        if Kostuemmodellablage.nachtragen(runde_, neueste):
            self.lauf.sichern('ergebnis')

    def _bestes(self, runde_, bester, z):
        aus = runde_.ordner(999999)
        befehl = {'glb': True, 'blend': True, 'haltung': False, **runde_.huellenwahl(bester)}
        winkel = [0]
        if runde_.textur:
            texturen = runde_.texturen()
            winkel = sorted(texturen)
            befehl.update(texturen=texturen, textur_winkel=runde_.TEXTUR_WINKEL)
        bericht = runde_.blender.rendern(runde_.koerper, aus, [('bester', bester)], winkel, **befehl)
        eintrag = bericht['kandidaten']['bester']
        farben = (eintrag.get('glb') or '').rsplit('.', 1)[0] + '.farben.json'
        for quelle, ziel in (
            (eintrag.get('glb'), self.GLB),
            (eintrag.get('blend'), self.BLEND),
            (farben, self.FARBEN),
        ):
            if quelle and (aus / 'bester' / quelle).is_file():
                shutil.copyfile(aus / 'bester' / quelle, self.ablage.ergebnis(ziel))
        z.update(glb=self.GLB, blend=self.BLEND, teile=eintrag.get('teile') or {})
        shutil.rmtree(aus, ignore_errors=True)

    def _sicht_ablegen(self, runde_, bester, z):
        """Das Sichtmodell des besten Kostüms nach `ergebnis/` — in der gestellten Haltung (in der Ruhelage der Figur, Arme
        seitlich ausgestreckt, wären die Übergänge zwischen Rumpf und Armen auseinandergezogen). Ein Fehler hier hält den
        Abschluss nicht auf: Er steht im Log, das Modell aus Teilen ist schon abgelegt."""
        if not (runde_.sicht and runde_.huelle and runde_.textur):
            return
        aus = runde_.ordner(999998)
        texturen = runde_.texturen()
        try:
            bericht = runde_.blender.rendern(
                runde_.koerper,
                aus,
                [('sicht', bester)],
                sorted(texturen),
                glb=True,
                sicht=True,
                texturen=texturen,
                textur_winkel=runde_.TEXTUR_WINKEL,
                **runde_.huellenwahl(bester),
            )
        except RuntimeError as fehler:
            logger.warning('BlenderModel %s: Sichtmodell des besten Kostüms: %s', self.job.kennung, fehler)
            return
        datei = aus / 'sicht' / (bericht['kandidaten']['sicht'].get('sicht_glb') or 'sicht.glb')
        if datei.is_file():
            shutil.copyfile(datei, self.ablage.ergebnis(self.SICHT_GLB))
            z.update(sicht_glb=self.SICHT_GLB)
        shutil.rmtree(aus, ignore_errors=True)
