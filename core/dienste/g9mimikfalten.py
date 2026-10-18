# -*- coding: utf-8 -*-
"""G9mimikfalten — die 27 FACS-Detail-HD-Morphs als Normalenatlas der Kopfkachel (17.10.2026).

Edgar, 17.10.2026: „mach alles was offen ist" — dazu die Mimikfalten (Tabelle 11 in `genesis9-alter.md`). Die Bibliothek hat 27 FACS-Details (`FACSDetails_facs_bs_<Ausdruck>_HD2`: Brauen, Lidfalten, Nasenrümpfen,
Lippen, Kinn), die `facs_ctrl_FACSDetailStrength` an die Mimik koppelt. Sie sind HD-Morphs (`G9hdmorphe`): ein Kanal verschiebt Punkte der Stufe 1 und 2. Gemessen am 17.10.2026
(`ProjektTemp/_wegwerf/hautebenen/facs_hd_probe.py`, Vektoren in Daz-Zentimetern → Millimeter gerechnet): größte Verschiebung je Kanal auf Stufe 1 Median 0,10 mm, auf Stufe 2 Median 0,16 mm (BrowInnerUp bis 0,77 mm) —
bei 3,3 mm Kantenlänge der Ansichtsstufe ist das KEINE Geometrie, nur Licht. Darum wie bei den Altersfalten (`G9hautfalten`) und der Zeichnung (`G9hautzeichnung`) eine Normalenkarte:

    Kanal (Wert 1) → `G9hdmorphe.beitrag` auf Stufe 2 → Höhe je Punkt = Verschiebung · Normale → Raster auf die Kopfkachel (1001) → Steigung je Meter Kante → Normale (x, y)

Alle 27 Kanäle in EINEM Bild (Atlas, 6 Spalten × 5 Zeilen, je 512²; R/G = Normale x/y, flach = 128): ein Sampler. Welche Zelle welcher Kanal ist, steht in der Liste (`kanaele`). Der Browser summiert im Shader
`Σ Gewicht · Normale` über die Kanäle mit Gewicht > 0 (`Genesis9mimikfalten`); die Gewichte kommen als `hdwerte` vom Server (Wert je HD-Kanal der Stellung).

ABLAGE: `Genesis9/ablage/mimikfalten_v<FASSUNG>_1001.png` und `….json` (Liste ohne Geschlecht: die Kanäle liegen auf der Grundfigur, der Atlas gilt für beide). Bau und Stand: `G9mimikfaltenablage`.
"""
import json
import logging
import time

import numpy as np

from .g9hautfalten import G9hautfalten

logger = logging.getLogger('core')

__all__ = ['G9mimikfalten']


class G9mimikfalten(G9hautfalten):
    """`bauen()` rechnet den Atlas und schreibt ihn in die Ablage."""

    FASSUNG = 1
    KACHEL = 1001
    #: Seite einer Zelle (Pixel) und Spalten des Atlas.
    ZELLE = 512
    SPALTEN = 6
    MUSTER = 'FACSDetails_facs_bs_'

    @classmethod
    def stamm(cls, geschlecht=None):
        from Genesis9.pfade import G9pfade
        return G9pfade.ablage() / ('mimikfalten_v%d' % cls.FASSUNG)

    # ------------------------------------------------------------- Rechnen

    def kanaele(self):
        """`{kanal: Pfad der .dhdm}` der FACS-Details, nach Namen sortiert."""
        from Genesis9.hdmorphe import G9hdmorphe
        from Genesis9.morphablage import G9morphablage
        from Genesis9.pfade import G9pfade
        gefunden = {n: rel for n, rel in G9hdmorphe.kanaele(G9morphablage.holen()).items() if self.MUSTER in n}
        return {n: G9pfade.finden(gefunden[n]) for n in sorted(gefunden)}

    def raster(self, stufe, fein):
        """`(drin (S, S) bool, ecken (n, 3) Punkte der Stufe, anteile (n, 3), lage (S, S, 3))` der Kopfkachel auf der Stufe — Texel → Dreieck der Stufe."""
        from Genesis9.texturabtastung import G9texturabtastung
        s = self.ZELLE
        dreieck = np.full((s, s), -1, dtype=np.int32)
        bary = np.zeros((s, s, 2), dtype=np.float16)
        uv = np.asarray(stufe.uv, dtype=np.float64) * s
        for g in stufe.gruppen:
            if int(g['kachel']) != self.KACHEL:
                continue
            for t in range(int(g['index_ab']) // 3, (int(g['index_ab']) + int(g['index_anzahl'])) // 3):
                G9texturabtastung._dreieck(dreieck, bary, t, uv[stufe.dreiecke[t]])
        drin = dreieck >= 0
        ecken = np.asarray(stufe.dreiecke, dtype=np.int64)[dreieck[drin]]
        b = bary[drin].astype(np.float64)
        anteile = np.clip(np.concatenate([b, 1.0 - b.sum(1, keepdims=True)], axis=1), 0.0, 1.0)
        lage = np.zeros((s, s, 3))
        lage[drin] = np.einsum('nk,nkc->nc', anteile, fein[ecken])
        return drin, ecken, anteile, lage

    def bauen(self):
        """Den Atlas in die Ablage → die Liste (`{1001: {kanaele, spalten, zeilen, zelle, …}}`)."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.hdmorphe import G9hdmorphe
        from PIL import Image

        t0 = time.perf_counter()
        formung = G9formung({})
        punkte0 = np.asarray(formung.punkte(), dtype=np.float64) - np.array([0.0, formung.boden(), 0.0])
        basis = G9basisnetz.holen()
        s1, s2 = basis.netzstufe(1), basis.netzstufe(2)
        if s2.stufen < 2:
            raise ValueError('Stufe 2 nicht verfügbar')
        fein = s2.punkte(punkte0)
        normalen = np.asarray(s2.normalen(punkte0, fein), dtype=np.float64)
        drin, ecken, anteile, lage = self.raster(s2, fein)
        kx, ky = self._kante(lage, drin, 1), self._kante(lage, drin, 0)
        kanaele = self.kanaele()
        namen = list(kanaele)
        zeilen = -(-len(namen) // self.SPALTEN)
        z = self.ZELLE
        atlas = np.full((zeilen * z, self.SPALTEN * z, 3), 128, dtype=np.uint8)
        steigung_max = {}
        for nr, name in enumerate(namen):
            hd = G9hdmorphe.beitrag(None, s1, s2, punkte0, aktive={name: (1.0, kanaele[name])})
            hoehe = np.zeros((z, z))
            if hd is not None:
                punkthoehe = (np.asarray(hd, dtype=np.float64) * normalen).sum(axis=1)
                hoehe[drin] = np.einsum('nk,nk->n', anteile, punkthoehe[ecken])
            bild, steigung = self.normalen(hoehe, kx, ky)
            zeile, spalte = divmod(nr, self.SPALTEN)
            zelle = np.full((z, z, 3), 128, dtype=np.uint8)
            zelle[drin, 0], zelle[drin, 1], zelle[drin, 2] = bild[drin, 0], bild[drin, 1], 0
            atlas[zeile * z:(zeile + 1) * z, spalte * z:(spalte + 1) * z] = zelle
            steigung_max[name] = round(float(steigung[drin].max()), 3) if drin.any() else 0.0
            logger.info('Mimikfalten %s: Steigung max %.3f, Höhe max %.2f mm (%.0f s)', name, steigung_max[name], float(np.abs(hoehe).max()) * 1000, time.perf_counter() - t0)
        Image.fromarray(atlas, 'RGB').save(self.bildpfad(None, self.KACHEL), 'PNG')
        liste = {'geschlecht': 'alle', 'fassung': self.FASSUNG, 'seite': z,
                 'kacheln': {str(self.KACHEL): {'kanaele': namen, 'spalten': self.SPALTEN, 'zeilen': zeilen, 'zelle': z, 'steigung_max': steigung_max}},
                 'sekunden': round(time.perf_counter() - t0, 1)}
        ziel = self.listenpfad(None)
        vorlaeufig = ziel.with_suffix('.neu')
        vorlaeufig.write_text(json.dumps(liste), encoding='utf-8')
        vorlaeufig.replace(ziel)                    # die Liste kommt zuletzt: sie sagt „fertig"
        return liste
