# -*- coding: utf-8 -*-
"""Koerperfotoprojektion — die Haut des Körpers aus den FOTOS, nicht aus dem TRELLIS-Netz (02.10.2026, nachts).

Befund Edgar: „die Textur der Beine von hinten ist auch sehr schlecht … Die ganzen iterativen Anpassungen sollen sich an
den Fotos als Vorlage richten, NICHT mehr an dem Trellis Modell." Bis dahin backte der Schritt „Körper" die
Hautkacheln aus den Farbproben des Netzes (`Meshfigurende.backen`) — dessen Textur ist TRELLIS' eigene Malerei, an den
Beinen hinten verwaschen und fleckig; die Runden übernahmen sie unverändert (`Koerpertextur`).

Hier holt der Körper seine Farbe in der Runde aus den Fotos — mit derselben Abbildung wie die Note und die
Fotoprojektion der Stücke (`Fotoprojektion`, Kennfarbenrender in der Haltung der Fotos, Teilmaske des Körpers: was ein
Kleid im Modell verdeckt, nimmt keine Farbe):

1. je Kachel die Texel des Körpers rastern (`G9uvraster`, `RASTER` px; die Kacheln selbst haben 2048 px)
2. Farbe aus den Fotos (Gewicht Normale · Blick⁴), Deckung = bester Blick (Normale · Blick) × im Foto auf der Figur
3. nur Hautfarbe übernehmen: ist die Fotofarbe nicht warm (Shirt, Shorts, Socke unter einem kürzeren Modellstück),
   bleibt die gebackene — außer dort, wo auch die gebackene nicht warm ist (Haar auf der Kopfhaut)
4. weicher Übergang: Deckung geglättet (`WEICH`), Lücken der Fotofarbe aufgefüllt, auf Kachelgröße gezogen und über die
   gebackene Kachel gelegt

Einmal je Körper (`ergebnis.fototextur.stand`) und Fassung: Die neuen Kacheln stehen in `fototextur.kacheln` — Runde,
Bühne (`Engine2d3dKleiderstandmodell`) und Export lesen sie dort —, die gebackenen bleiben als `fototextur.kacheln_netz`.
Rechnet „Körper" neu, ersetzt er `fototextur` ganz, und die nächste Runde projiziert wieder.
"""

import logging
import time

import numpy as np
from PIL import Image

logger = logging.getLogger('core')

__all__ = ['Koerperfotoprojektion']


class Koerperfotoprojektion:
    FASSUNG = 1
    GROESSE = (1024, 1536)
    RASTER = 1024
    #: Deckung: ab `DECKUNG[0]` (Kosinus Normale · Blick) beginnt das Foto, ab `DECKUNG[1]` gilt es ganz.
    DECKUNG = (0.25, 0.6)
    WEICH = 3
    #: Warm = Haut: R > G > B mit R − B über dieser Schwelle (0…1); wie `Fotostuecke.HAUT_ABSTAND` sinngemäß.
    WARM = 0.04

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def noetig(self):
        f = (self.job.ergebnis or {}).get('fototextur') or {}
        return bool(f.get('kacheln')) and (f.get('hautfoto') or {}).get('fassung') != self.FASSUNG

    @classmethod
    def warm(cls, rgb):
        rgb = np.asarray(rgb, dtype=np.float64)
        return (rgb[..., 0] > rgb[..., 1]) & (rgb[..., 1] > rgb[..., 2]) & (rgb[..., 0] - rgb[..., 2] > cls.WARM)

    # ------------------------------------------------------------ Rechnung

    def _projektion(self, teile, referenzen, render, aus, index):
        from iterationen2d3d.fotoprojektion import Fotoprojektion

        from .kleidfotoprojektion import Kleidfotoprojektion
        kfp = Kleidfotoprojektion(self.ablage, render, aus)
        kfp.GROESSE = self.GROESSE
        alle = np.vstack([np.asarray(t['punkte']) for t in teile])
        kamera = Fotoprojektion.aus_render(alle, render.RAND, self.GROESSE)
        projektion = Fotoprojektion(kamera.mitte, kamera.halb, self.GROESSE)
        for r, abbildung, foto, masken in kfp._ansichten(teile, referenzen):
            projektion.ansicht(r.winkel, abbildung, foto.farbe, foto.maske, masken[index])
        return projektion

    #: Am Kopf gilt jede Fotofarbe (Befund Edgar 02.10.2026: „die Haare umfassen nicht den ganzen Kopf" — an Schläfen
    #: und Nacken zeigt das Foto kurzes graues Haar, die gebackene Haut dort Hautton): Hautgewicht von `head` und seinen
    #: Kindern ab `KOPF_AB`. Die Maske dafür rendert ohne Haarkarten — sonst deckten die (ohne Alpha) die Kopfhaut ab.
    KOPF_AB = 0.5

    def _kopf(self, koerper, ruhe):
        """(N,) Kopfgewicht je Punkt des Körperteils — aus `genesis_ende.npz` (nächster Punkt), 0 ohne Datei."""
        from scipy.spatial import cKDTree

        from .huellenschnitt import Huellenschnitt
        pfad = self.ablage.arbeit('genesis_ende.npz')
        if not pfad.is_file():
            return np.zeros(len(koerper['punkte']))
        with np.load(pfad) as d:
            gewicht = Huellenschnitt.halsgewichte(d, wurzel='head')
            punkte = np.asarray(d['punkte'], dtype=np.float64)
        if gewicht is None:
            return np.zeros(len(koerper['punkte']))
        _, nah = cKDTree(punkte).query(np.asarray(ruhe['punkte'], dtype=np.float64), workers=-1)
        return gewicht[nah]

    def _deckung(self, projektion, lage, normale):
        beste = np.zeros(len(lage))
        for a in projektion.ansichten:
            _farbe, drin = projektion._farbe_in(lage, a)
            beste = np.maximum(beste, np.clip(normale @ projektion.blick(a['winkel']), 0.0, None) * drin)
        von, bis = self.DECKUNG
        return np.clip((beste - von) / (bis - von), 0.0, 1.0)

    def _kachel(self, projektion, karten, grund_pfad, ziel, kopf=None):
        """Eine Kachel: Fotofarbe und Deckung im Raster, über die gebackene Kachel gelegt → Anteil gedeckter Texel."""
        from Genesis9.kleidfototextur import G9kleidfototextur
        from scipy.ndimage import gaussian_filter
        s = self.RASTER
        farbe = np.zeros((s, s, 3), np.float32)
        deckung = np.zeros((s, s), np.float32)
        maske = np.zeros((s, s), bool)
        with Image.open(grund_pfad) as bild:
            grund = np.asarray(bild.convert('RGB'), dtype=np.float32) / 255.0
        klein = np.asarray(Image.fromarray((grund * 255).astype(np.uint8)).resize((s, s), Image.BILINEAR),
                           dtype=np.float32) / 255.0
        for karte in karten:
            m = karte['maske']
            if not m.any():
                continue
            f, getroffen = projektion.farben(karte['lage'][m], karte['normale'][m])
            d = self._deckung(projektion, karte['lage'][m], karte['normale'][m]) * getroffen
            erlaubt = self.warm(f) | ~self.warm(klein[m])    # Fotofarbe ohne Hautton nur, wo auch die Haut keinen hat
            if kopf is not None:                            # … oder am Kopf (kurzes Haar, Stoppeln)
                erlaubt |= kopf(karte['lage'][m])
            d *= erlaubt
            farbe[m], deckung[m] = f, d
            maske |= m
        if not (deckung > 0).any():
            return 0.0
        voll = G9kleidfototextur._fuellen(farbe, deckung > 0, maske)
        deckung = gaussian_filter(deckung, self.WEICH)
        gross = grund.shape[1], grund.shape[0]
        voll = np.asarray(Image.fromarray(np.clip(voll * 255, 0, 255).astype(np.uint8)).resize(gross, Image.BILINEAR),
                          dtype=np.float32) / 255.0
        alpha = np.asarray(Image.fromarray(deckung.astype(np.float32)).resize(gross, Image.BILINEAR))[..., None]
        ergebnis = grund * (1.0 - alpha) + voll * alpha
        Image.fromarray(np.clip(ergebnis * 255 + 0.5, 0, 255).astype(np.uint8)).save(ziel, quality=92)
        return float((deckung[maske] > 0.5).mean())

    def bauen(self, teile, referenzen, render, aus):
        """Fotohaut je Kachel, Textur der Körperteile umgehängt → Steckbrief (oder None, wenn nichts zu tun war)."""
        from Genesis9.uvraster import G9uvraster
        if not self.noetig() or not referenzen:
            return None
        t0 = time.perf_counter()
        index = next((i for i, t in enumerate(teile) if t.get('art') == 'koerper'), None)
        if index is None:
            return None
        koerper, ruhe = teile[index], teile[index].get('ruhe', teile[index])
        if ruhe.get('uv') is None or not ruhe.get('textur'):
            return None
        f = dict(self.job.ergebnis['fototextur'])
        netz = dict(f.get('kacheln_netz') or f['kacheln'])
        pfade = {str(self.ablage.ergebnis(n)): int(k) for k, n in netz.items()}
        from scipy.spatial import cKDTree
        ohne_haar = [t for t in teile if t.get('art') != 'haar']
        projektion = self._projektion(ohne_haar, referenzen, render, aus,
                                      next(i for i, t in enumerate(ohne_haar) if t is koerper))
        kopfgewicht, baum = self._kopf(koerper, ruhe), cKDTree(np.asarray(koerper['punkte'], dtype=np.float64))

        def kopf(lage):
            return kopfgewicht[baum.query(lage, workers=-1)[1]] >= self.KOPF_AB
        gruppen = {}
        for i, eintrag in enumerate(ruhe['textur']):
            k = pfade.get(str(eintrag.get('albedo')))
            if k is not None:
                gruppen.setdefault(k, []).append({'name': 'k%d_%d' % (k, i), 'index_ab': 3 * int(eintrag['ab']),
                                                  'index_anzahl': 3 * int(eintrag['anzahl'])})
        neu, deckung = {}, {}
        for k, liste in sorted(gruppen.items()):
            raster = G9uvraster(koerper['punkte'], koerper['dreiecke'], ruhe['uv'], liste, groesse=self.RASTER)
            name = 'hautfoto_%d.jpg' % k
            deckung[k] = round(self._kachel(projektion, list(raster.alle().values()),
                                            self.ablage.ergebnis(netz[str(k)]), self.ablage.ergebnis(name), kopf), 3)
            if deckung[k] > 0:
                neu[str(k)] = name
        kacheln = dict(netz, **neu)
        f.update(kacheln=kacheln, kacheln_netz=netz, hautfoto={
            'fassung': self.FASSUNG, 'deckung': deckung, 'sekunden': round(time.perf_counter() - t0, 1)})
        self.job.ergebnis = dict(self.job.ergebnis, fototextur=f)
        self.job.save(update_fields=['ergebnis', 'updated_at'])
        umbenannt = {str(self.ablage.ergebnis(netz[k])): str(self.ablage.ergebnis(n)) for k, n in neu.items()}
        for t in {id(koerper): koerper, id(ruhe): ruhe}.values():
            for eintrag in t.get('textur') or []:
                eintrag['albedo'] = umbenannt.get(str(eintrag.get('albedo')), eintrag.get('albedo'))
        logger.info('2D3D Kleider %s: Haut aus den Fotos — Deckung je Kachel %s, %.1f s', self.job.kennung, deckung,
                    time.perf_counter() - t0)
        return f['hautfoto']
