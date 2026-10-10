# -*- coding: utf-8 -*-
"""Fotohautbrauen — die aufgemalten Augenbrauen aus der Kopfkachel (1001) einer Fotohaut nehmen.

Edgar, 10.10.2026, Asian: „die Augenbrauen sind noch nicht gefixt, ändern funktioniert nicht." Die gebackene Kopfkachel
eines Blender-Imports (und die Fotohaut von „Mesh to 3D") trägt die Brauen des Originals AUFGEMALT. Die Figur zeichnet ihre
Brauen zusätzlich als Netz (Brauenstil im Bedienfeld: Karte, Faser, Charakterbraue) — das Netz liegt genau auf der
aufgemalten Braue (gemessen: Brauenpunkte im UV-Raum auf dem Bogen der Kachel, `asian_brauen_uv.py`). Welchen Stil man auch
wählt, die gemalte Braue bleibt darunter stehen, und das Ändern sieht aus, als täte es nichts.

Wer einen Brauenstil gewählt hat (`Genesis9fototextur.gruppen`), bekommt die Kachel mit dieser Retusche
(`?brauen=ohne`, `G9fototextur`): die Brauen werden gefunden und mit der Haut der Umgebung gefüllt, die Datei des Modells
bleibt unberührt. Modell-unabhängig: es gibt nur die Zone der Genesis-UV (`ZONE`) und Verhältnisse zur Umgebung, keine Werte je Modell.

SUCHE (in der Zone, alle Maße relativ zu deren Breite, damit 2048 und 8192 px gleich rechnen):
  1. Hintergrund `B` = die Haut ohne Dunkles: Gauß mit Gültigkeitsmaske, dreimal verfeinert (Dunkles fällt aus der Maske).
  2. Dünne dunkle Striche = schwarzer Top-Hat (Schließen minus Bild, Element etwas dicker als eine Braue) über `KONTRAST` × `B`.
     Große dunkle Flächen (Haar, Augen, Schatten) füllt das Schließen nicht und bleiben stehen — anders als bei einer Suche nach
     zusammenhängenden dunklen Flecken, wo eine Braue, die am Haar oder am Lidschatten hängt, mit ihm zu einer „dicken" Fläche wird
     (die erste Fassung fand so bei drei von acht Kacheln nichts). Brauenstück = lang genug (`LAENGE`) oder groß genug (`MINDEST`).
  3. Die Maske wird erweitert und mit der Haut der Umgebung gefüllt (Gauß mit Gültigkeitsmaske, in zwei Maßstäben; Rand weich).
Das Ergebnis liegt unter `media/hauttexturen/ohne_brauen/` (Projekt, nicht System-Temp) und wird neu gerechnet, wenn die
Quelle jünger ist oder `FASSUNG` steigt.
"""

import logging
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

logger = logging.getLogger('core')

__all__ = ['Fotohautbrauen']


class Fotohautbrauen:
    FASSUNG = 5
    #: (u0, u1, v0, v1) in der Kachel 1001 der Genesis-UV (v von unten): von den Schläfen bis zur Nasenwurzel, vom Haaransatz bis unter
    #: die tiefsten Brauen (gemessen an fünf Kacheln mit Brauen: Brauenmitte v 0,60–0,64, Enden bis 0,575). Eine feste Zone ist
    #: erlaubt, weil jede Fotohaut auf DIESELBE Genesis-UV gebacken ist (Proben `ProjektTemp/_wegwerf/import_serie/brauen_retusche_probe.py`, `brauen_probe_ganz.py`).
    ZONE = (0.32, 0.68, 0.565, 0.668)
    #: Die Augen in der Genesis-UV: darin sind dünne dunkle Striche Wimpern, Lidlinien oder Lidschatten, keine Brauen. Unter `AUGEN_UNTEN`
    #: gilt das überall (Wimpernspitzen, Lidwinkel), zwischen `AUGEN_UNTEN` und `AUGEN_OBEN` über den beiden Augen (`AUGEN`: links, rechts —
    #: u von bis); die Brauenenden außerhalb davon bleiben Brauen. Die Oberkante der Lidlinien liegt in allen Kacheln bei v ≤ 0,592.
    AUGEN = ((0.372, 0.465), (0.535, 0.628))
    AUGEN_UNTEN = 0.585
    AUGEN_OBEN = 0.597
    #: Ein Strich ist Braue, wenn er um diesen Anteil der Haut der Umgebung dunkler ist als sie.
    KONTRAST = 0.07
    #: Dicke des Strukturelements (Anteil der Zonenbreite): Striche bis zu dieser Dicke sind „dünn" (Braue ≈ 0,02–0,035).
    DICKE = 0.05
    #: Kleinste Länge eines Brauenstücks (Breite seines Umrisses, Anteil der Zonenbreite) …
    LAENGE = 0.10
    #: … und kleinste Fläche (Anteil der Zone); kleinere Stücke sind Poren, Haarsträhnen oder Staub. Ein Stück, das die Seite oder den oberen
    #: Rand der Zone berührt, gehört zu Haar oder Schatten, nicht zu einer Braue (am unteren Rand endet die Zone mitten in den Brauen).
    MINDEST = 0.002
    #: Ein dünnes Ende (kürzer als `LAENGE`) zählt zur Braue, wenn es höchstens so weit (Anteil der Zonenbreite) von ihr liegt und größer als `ENDE_MINDEST` (Anteil der Zone) ist.
    ENDEN = 0.06
    ENDE_MINDEST = 0.0003
    #: Umfeld großer tief dunkler Flächen (Haar), in dem nichts Braue ist (Anteil der Zonenbreite).
    HAARRAND = 0.03
    #: Mehr Brauenfläche als dieser Anteil der Zone heißt: das ist keine Gesichtshaut (gemalte Muster, Kunsthaut) — nichts wird retuschiert.
    HOECHSTENS = 0.35
    #: Die Maske wächst um diesen Anteil der Zonenbreite (die weichen Ränder der Braue).
    WACHSEN = 0.014
    #: Breite der Zone, auf der gerechnet wird (px); größere Zonen werden dafür verkleinert (8192 px → 2.950 px breite Zone: über eine Minute).
    ARBEIT_PX = 900
    #: Gauß-Maße (Anteil der Zonenbreite): Hintergrund, Füllung (fein, grob), Rand der Maske.
    SIGMA_HINTERGRUND = 0.05
    SIGMA_FUELLUNG = 0.03
    SIGMA_RAND = 0.006

    # ------------------------------------------------------------- Rechnung

    @staticmethod
    def _licht(feld):
        return feld[..., 0] * 0.299 + feld[..., 1] * 0.587 + feld[..., 2] * 0.114

    @staticmethod
    def _glatt(feld, gueltig, sigma):
        """Gauß über die gültigen Pixel (Normalisierung durch die Gültigkeit) — `(Feld, Gewicht)`; `feld` (H, W) oder (H, W, 3)."""
        gewicht = ndimage.gaussian_filter(gueltig.astype(np.float32), sigma, mode='nearest')
        if feld.ndim == 3:
            zaehler = np.stack([ndimage.gaussian_filter(feld[..., k] * gueltig, sigma, mode='nearest') for k in range(3)], axis=-1)
            return zaehler / np.maximum(gewicht, 1e-4)[..., None], gewicht
        return ndimage.gaussian_filter(feld * gueltig, sigma, mode='nearest') / np.maximum(gewicht, 1e-4), gewicht

    @classmethod
    def hintergrund(cls, licht, breite):
        """Die Leuchtdichte der Haut der Zone ohne Dunkles (Brauen, Augen, Haar)."""
        sigma = cls.SIGMA_HINTERGRUND * breite
        rand = max(1, int(round(cls.WACHSEN * breite)))
        gueltig = licht > 0.8 * np.median(licht)
        grund = np.full_like(licht, np.median(licht))
        for _ in range(3):
            if not gueltig.any():
                break
            grund, _gewicht = cls._glatt(licht, gueltig, sigma)
            gueltig = ~ndimage.binary_dilation(licht < 0.92 * grund, iterations=rand) & (licht > 0.55 * grund)
        return grund

    @classmethod
    def augenmaske(cls, form):
        """Die Pixel der Zone, die zu den Augen der Genesis-UV zählen (`AUGEN`, `AUGEN_UNTEN`, `AUGEN_OBEN`)."""
        u0, u1, v0, v1 = cls.ZONE
        hoehe, breite = form
        u = u0 + (np.arange(breite) + 0.5) / breite * (u1 - u0)
        v = v1 - (np.arange(hoehe) + 0.5) / hoehe * (v1 - v0)
        spalten = np.zeros(breite, dtype=bool)
        for von, bis in cls.AUGEN:
            spalten |= (u >= von) & (u <= bis)
        return (v < cls.AUGEN_UNTEN)[:, None] | ((v < cls.AUGEN_OBEN)[:, None] & spalten[None, :])

    @classmethod
    def braue(cls, licht, grund, breite):
        """Maske der gemalten Brauen (noch nicht erweitert): dünne dunkle Striche, lang genug, nicht an der Seite oder oben am Rand der Zone (unten schneidet die Zone die Brauenenden ab), nicht am Haar."""
        seite = max(3, int(round(2 * cls.DICKE * breite)) // 2 * 2 + 1)
        zu = ndimage.grey_closing(licht, size=(seite, seite))
        strich = (zu - licht) > cls.KONTRAST * grund
        # Große tief dunkle Flächen (Haar an den Schläfen) und ihr Umfeld: ihre Strähnen sind keine Brauen.
        tief = (licht < 0.5 * grund).astype(np.uint8)
        gross = ndimage.maximum_filter(ndimage.minimum_filter(tief, size=seite), size=seite) > 0
        strich &= ~ndimage.binary_dilation(gross, iterations=max(1, int(round(cls.HAARRAND * breite))))
        strich &= ~cls.augenmaske(strich.shape)
        marken, anzahl = ndimage.label(strich)
        orte = ndimage.find_objects(marken)
        braue = np.zeros_like(strich)
        for nummer, ort in enumerate(orte, start=1):
            if ort is None or cls._am_rand(ort, strich.shape):
                continue
            fleck = marken[ort] == nummer
            if ort[1].stop - ort[1].start >= cls.LAENGE * breite and fleck.sum() >= cls.MINDEST * licht.size:
                braue[ort] |= fleck
        # Die dünnen Enden einer Braue (Schwanz, einzelne Haare) sind kürzer als `LAENGE`: sie zählen mit, wenn sie nahe an einer Braue liegen.
        if braue.any():
            nahe = ndimage.binary_dilation(braue, iterations=max(1, int(round(cls.ENDEN * breite))))
            for nummer, ort in enumerate(orte, start=1):
                if ort is None or cls._am_rand(ort, strich.shape) or braue[ort][marken[ort] == nummer].any():
                    continue
                fleck = marken[ort] == nummer
                if fleck.sum() >= cls.ENDE_MINDEST * licht.size and nahe[ort][fleck].any():
                    braue[ort] |= fleck
        return braue

    @staticmethod
    def _am_rand(ort, form):
        """Berührt der Ausschnitt `ort` die Seiten oder den oberen Rand der Zone (Haar, Schatten — keine Braue)?"""
        return ort[1].start == 0 or ort[1].stop == form[1] or ort[0].start == 0

    @classmethod
    def fuellung(cls, zone, gueltig, breite):
        """Die Haut ohne Maske, in zwei Maßstäben: fein, wo genug Haut daneben liegt, sonst grob, sonst das Mittel."""
        fein, gewicht = cls._glatt(zone, gueltig, cls.SIGMA_FUELLUNG * breite)
        grob, gewicht_grob = cls._glatt(zone, gueltig, 3 * cls.SIGMA_FUELLUNG * breite)
        mittel = np.array([np.median(zone[..., k][gueltig]) for k in range(3)], dtype=np.float32)
        grob = np.where((gewicht_grob > 0.02)[..., None], grob, mittel)
        anteil = np.clip(gewicht / 0.25, 0, 1)[..., None]
        return fein * anteil + grob * (1 - anteil)

    @classmethod
    def masken(cls, zone):
        """`(weiche Maske (H, W, 1), Füllung (H, W, 3), Bericht)` für eine Zone (Gleitkomma-RGB); ohne Braue (oder bei Unsinn) `(None, None, Bericht)`."""
        zbreite = zone.shape[1]
        licht = cls._licht(zone)
        grund = cls.hintergrund(licht, zbreite)
        braue = cls.braue(licht, grund, zbreite)
        bericht = {'zone_px': [int(zone.shape[1]), int(zone.shape[0])], 'braue_px': int(braue.sum())}
        if not braue.any():
            return None, None, bericht
        if braue.mean() > cls.HOECHSTENS:
            return None, None, dict(bericht, hinweis='zu viel Dunkles: keine Gesichtshaut')
        wachsen = max(1, int(round(cls.WACHSEN * zbreite)))
        maske = ndimage.binary_dilation(braue, iterations=wachsen)
        gueltig = ~ndimage.binary_dilation(maske, iterations=wachsen) & (licht > 0.6 * grund)
        if gueltig.sum() < 0.05 * gueltig.size:
            return None, None, dict(bericht, hinweis='zu wenig Haut zum Füllen')
        weich = np.clip(ndimage.gaussian_filter(maske.astype(np.float32), cls.SIGMA_RAND * zbreite), 0, 1)[..., None]
        bericht['maske_px'] = int(maske.sum())
        return weich, cls.fuellung(zone, gueltig, zbreite), bericht

    @staticmethod
    def _gross(feld, groesse):
        """Ein Gleitkomma-Feld (H, W) oder (H, W, 3) mit Werten 0–255 auf `groesse` = (Breite, Höhe) bringen (glatt, ohne Treppen)."""
        return np.asarray(Image.fromarray(np.clip(feld + 0.5, 0, 255).astype(np.uint8)).resize(groesse, Image.BICUBIC), dtype=np.float32)

    @classmethod
    def retuschieren(cls, bild):
        """`(Bild, Bericht)` — `bild` ist die ganze Kachel (PIL, RGB); ohne gefundene Braue dasselbe Bild.
        Gesucht und gefüllt wird auf einer Zone von höchstens `ARBEIT_PX` Breite (bei 8192 px sonst über eine Minute), angewandt auf die volle."""
        breite, hoehe = bild.size
        u0, u1, v0, v1 = cls.ZONE
        box = (int(u0 * breite), int((1 - v1) * hoehe), int(u1 * breite), int((1 - v0) * hoehe))
        zone_bild = bild.crop(box)
        if zone_bild.width > cls.ARBEIT_PX:
            klein = zone_bild.resize((cls.ARBEIT_PX, max(1, round(zone_bild.height * cls.ARBEIT_PX / zone_bild.width))), Image.LANCZOS)
        else:
            klein = zone_bild
        weich, fuell, bericht = cls.masken(np.asarray(klein, dtype=np.float32))
        if weich is None:
            return bild, bericht
        zone = np.asarray(zone_bild, dtype=np.float32)
        if klein is not zone_bild:
            weich = cls._gross(weich[..., 0] * 255, zone_bild.size)[..., None] / 255
            fuell = cls._gross(fuell, zone_bild.size)
        neu = zone * (1 - weich) + fuell * weich
        ergebnis = bild.copy()
        ergebnis.paste(Image.fromarray(np.clip(neu + 0.5, 0, 255).astype(np.uint8)), box[:2])
        return ergebnis, dict(bericht, voll_px=list(zone_bild.size))

    # --------------------------------------------------------------- Ablage

    @staticmethod
    def ordner():
        from django.conf import settings
        return Path(settings.MEDIA_ROOT) / 'hauttexturen' / 'ohne_brauen'

    @classmethod
    def datei(cls, pfad):
        """Die Kachel `pfad` ohne aufgemalte Brauen (`Path`) — gerechnet beim ersten Aufruf, danach aus der Ablage.
        Der Name trägt Modell, Datei, Stand der Quelle und `FASSUNG` (`artefakte-benennen.md`); scheitert die Rechnung oder
        ist keine Braue zu finden, kommt die Quelle zurück (mit Warnung im Log)."""
        pfad = Path(pfad)
        stand = pfad.stat()
        name = re.sub(r'[^\w.\-]+', '_', '%s_%s' % (pfad.parent.name, pfad.stem))
        ziel = cls.ordner() / ('%s_%d_%d_f%d%s' % (name, stand.st_mtime_ns, stand.st_size, cls.FASSUNG, pfad.suffix.lower()))
        if ziel.is_file():
            return ziel
        try:
            with Image.open(pfad) as roh:
                bild = roh.convert('RGB')
            neu, bericht = cls.retuschieren(bild)
            if neu is bild:
                logger.warning('Fotohautbrauen: in %s keine Braue gefunden (%s) — die Quelle bleibt.', pfad, bericht)
                return pfad
            ziel.parent.mkdir(parents=True, exist_ok=True)
            zwischen = ziel.with_name(ziel.name + '.tmp')
            neu.save(zwischen, format='PNG' if pfad.suffix.lower() == '.png' else 'JPEG', quality=92, subsampling=0)
            os.replace(zwischen, ziel)
            logger.info('Fotohautbrauen: %s → %s (%s)', pfad.name, ziel.name, bericht)
            return ziel
        except (OSError, ValueError) as fehler:
            logger.warning('Fotohautbrauen: %s nicht retuschiert: %s', pfad, fehler)
            return pfad
