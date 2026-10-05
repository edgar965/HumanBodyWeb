# -*- coding: utf-8 -*-
"""Netztiefe — die Tiefe (vorn–hinten) des Netzes an die Silhouette des Seitenfotos angleichen, bevor der Körper darauf gerechnet wird (05.10.2026).

Edgar (05.10.2026): „bauch ist viel zu dick beim Modell im vergleich zur vorlage". Gemessen am Auftrag 2026.10.04.11.11.44 (`Seitentiefe`, Ruhelage, Tiefe als Anteil der Körpergröße ≙ mm bei 1,693 m):
das TRELLIS-Netz ist bei 0,50 und 0,55 der Größe 33 und 29 mm tiefer als die Silhouette im Seitenfoto, der Körper folgt ihm (302 mm bei 0,55, 22 mm über dem ganzen Foto samt Hemd), und die
Hemd-Hülle (Körperhaut + höchstens 30 mm) erbt es: +42 mm. Die Iterationen gleichen den Rumpf nur über die BREITE aus (`IterationKoerper`, nur wo das Foto Haut zeigt) — unter dem Hemd nie.

Diese Klasse ist die Stelle, an der es ein für alle Mal stimmt: aus dem Roh-Netz wird ein abgeleitetes (`arbeit/netz_tiefe.glb`, Original und Segmentierung bleiben unberührt), dessen Tiefe je Höhe in
`BAND` höchstens so groß ist wie die des Seitenfotos (nur verkleinern, nie vergrößern; höchstens um `tiefe_min`). Die Körper-Kette, die Fotostücke und die Frisur lesen es über
`Engine2d3dKleiderablage.netzdatei()`; Sapiens bleibt beim Original (`original=True`) — Flächen und UV sind dieselben, nur die Punkte liegen anders.

VERFAHREN (je Höhenanteil h des Rumpfs, `BAND`):
  1. Tiefe des Netzes (Mittelstreifen, Perzentil 1…99 entlang z) und des Seitenfotos (Breite der Maske, Mittel aus „rechts" und „links", wenn beide da sind) — beide als Anteil der Größe
  2. Faktor s(h) = Foto ÷ Netz, nur wenn das Netz mehr als `tiefe_toleranz` tiefer ist; sonst 1; nicht kleiner als `tiefe_min`; über die Höhe geglättet (`GLAETTUNG`)
  3. Jeder Punkt im Rumpf (Quer ≤ `QUER_VOLL` der Größe von der Mitte, bis `QUER_NULL` auslaufend — die Arme bleiben) wird um die RÜCKSEITE des Netzes in dieser Höhe auf s gestaucht:
     z' = hinten + s·(z − hinten). Der Bauch ragt vorn heraus, der Rücken nicht — so wandert die Vorderseite, nicht die Wirbelsäule.
Das Band läuft oben und unten weich aus (`SAUM`). Ohne Seitenfoto (Rolle „rechts" oder „links") bleibt das Netz, wie es ist; der Grund steht in `arbeit/netz_tiefe.json`.

Gemessen/nicht gemessen: Dass das Foto die richtige Tiefe liefert, ist eine Annahme (Perspektive macht es höchstens zu tief; ein Seitenfoto mit weit nach vorn gestrecktem Arm würde die Tiefe überschätzen — dann
wird weniger gestaucht, nicht mehr). Wie die Figur danach aussieht, zeigt nur der Lauf.
"""

import json
import logging
import os
import time
from datetime import datetime

import numpy as np

from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .seitentiefe import Seitentiefe

logger = logging.getLogger('core')

__all__ = ['Netztiefe']


class Netztiefe:
    FASSUNG = 1
    DATEI, ZETTEL = 'netz_tiefe.glb', 'netz_tiefe.json'
    #: Höhenanteile, in denen korrigiert wird (Bauch bis Schulter), und die Breite des Auslaufs an beiden Enden.
    BAND = (0.48, 0.80)
    SAUM = 0.03
    #: Sigma der Glättung des Faktors, in Höhenanteilen.
    GLAETTUNG = 0.015
    #: Quer zur Mitte (Anteil der Größe): bis hierher volle Wirkung, ab `QUER_NULL` keine — dazwischen läuft sie aus (die hängenden Arme bleiben unberührt).
    QUER_VOLL, QUER_NULL = 0.10, 0.15
    SEITEN = ('rechts', 'links')

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    # ------------------------------------------------------------------ Eingaben

    def einstellungen(self):
        o = Engine2d3dKleideroptionen.koerper(self.job.optionen)
        return {'tiefe': o.get('tiefe', 'aus'), 'tiefe_min': float(o.get('tiefe_min', 0.8)), 'tiefe_toleranz': float(o.get('tiefe_toleranz', 3)) / 100.0}

    def seitenfotos(self):
        """`[(rolle, Pfad der vorbereiteten PNG)]` der Seitenfotos (Rolle rechts/links)."""
        from .engine2d3dkleidersegmentierung import Engine2d3dKleidersegmentierung
        return [(b['rolle'], b['png']) for b in Engine2d3dKleidersegmentierung.bilder_fuer(self.job, self.ablage) if b['rolle'] in self.SEITEN]

    @staticmethod
    def _alpha(png):
        """Die Maske eines vorbereiteten Fotos, auf höchstens 1.600 px Kantenlänge verkleinert (die Rechnung ist verhältnistreu)."""
        from PIL import Image
        with Image.open(png) as bild:
            kanal = bild.convert('RGBA').getchannel('A')
        f = max(1, max(kanal.size) // 1600)
        return np.asarray(kanal.resize((kanal.width // f, kanal.height // f), Image.NEAREST)) > 8

    @staticmethod
    def _stat(pfad):
        s = os.stat(str(pfad))
        return [s.st_size, s.st_mtime_ns]

    def _runden(self, profil, schluessel=None):
        """`{str(höhenanteil): Wert auf 4 Stellen}` nur im Band — `profil` Werte sind Zahlen oder Wörterbücher (dann `schluessel`)."""
        return {str(h): round(float(v[schluessel] if schluessel else v), 4) for h, v in profil.items() if self.BAND[0] <= h <= self.BAND[1]}

    # ------------------------------------------------------------------ Rechnen

    def faktoren(self, netz, foto, tiefe_min, toleranz):
        """`{höhenanteil: s}` auf dem Raster `Seitentiefe.HOEHEN` — 1 außerhalb von `BAND` und wo das Netz nicht deutlich tiefer ist als das Foto."""
        raster = list(Seitentiefe.HOEHEN)
        roh = np.ones(len(raster))
        for i, h in enumerate(raster):
            if h in netz and h in foto and self.BAND[0] <= h <= self.BAND[1] and netz[h]['tiefe'] > (1.0 + toleranz) * foto[h]:
                roh[i] = max(tiefe_min, min(1.0, foto[h] / netz[h]['tiefe']))
        schritt = raster[1] - raster[0]
        halb = int(np.ceil(3 * self.GLAETTUNG / schritt))
        kern = np.exp(-0.5 * (np.arange(-halb, halb + 1) * schritt / self.GLAETTUNG) ** 2)
        kern /= kern.sum()
        glatt = np.convolve(np.pad(roh, halb, constant_values=1.0), kern, mode='valid')
        return {h: float(min(1.0, g)) for h, g in zip(raster, glatt, strict=True)}

    def anwenden(self, punkte, faktoren, hinten):
        """Neue Punkte (V, 3): die Tiefe je Höhe um die Rückseite stauchen — nur im Rumpf (Quer) und im Band (mit Auslauf)."""
        p = np.asarray(punkte, dtype=np.float64)
        y0, y1 = float(p[:, 1].min()), float(p[:, 1].max())
        hoehe = max(y1 - y0, 1e-9)
        h = (p[:, 1] - y0) / hoehe
        raster = np.array(sorted(faktoren))
        s = np.interp(h, raster, [faktoren[x] for x in raster], left=1.0, right=1.0)
        hinten_z = np.interp(h, np.array(sorted(hinten)), [hinten[x] for x in sorted(hinten)])
        auslauf = np.clip(np.minimum(h - self.BAND[0], self.BAND[1] - h) / self.SAUM, 0.0, 1.0)
        auslauf = auslauf * auslauf * (3.0 - 2.0 * auslauf)                                  # weich
        mitte = float(np.median(p[(h > self.BAND[0]) & (h < self.BAND[1]), 0]))
        quer = np.clip((self.QUER_NULL - np.abs(p[:, 0] - mitte) / hoehe) / (self.QUER_NULL - self.QUER_VOLL), 0.0, 1.0)
        wirkung = 1.0 - (1.0 - s) * auslauf * quer
        neu = p.copy()
        neu[:, 2] = hinten_z + wirkung * (p[:, 2] - hinten_z)
        return neu

    @staticmethod
    def _laden(pfad):
        import trimesh
        roh = trimesh.load(str(pfad), force='scene', process=False)
        netz = roh.to_geometry() if hasattr(roh, 'to_geometry') else roh.dump(concatenate=True)
        if not isinstance(netz, trimesh.Trimesh) or len(netz.faces) == 0:
            raise ValueError('Kein Dreiecksnetz in %s' % pfad)
        return netz

    # ------------------------------------------------------------------ Ablauf

    def sichern(self):
        """Das abgeleitete Netz schreiben (oder den Grund ablegen, warum nicht) → Bericht `{aktiv, grund, …}`; steht auch in `arbeit/netz_tiefe.json`.
        Nach Änderung von Netz, Seitenfotos oder Einstellungen neu, sonst bleibt es."""
        t0 = time.perf_counter()
        o = self.einstellungen()
        original = self.ablage.netzdatei(original=True)
        zettel = self.ablage.arbeit(self.ZETTEL)
        if o['tiefe'] != 'an':
            return self._ablegen(zettel, {'aktiv': False, 'grund': 'Option „Rumpftiefe an das Seitenfoto angleichen“ ist aus'})
        if original is None:
            return self._ablegen(zettel, {'aktiv': False, 'grund': 'kein Netz'})
        fotos = self.seitenfotos()
        if not fotos:
            return self._ablegen(zettel, {'aktiv': False, 'grund': 'kein Seitenfoto (Rolle „rechts“ oder „links“) — das Netz bleibt, wie es ist'})
        stand = {'fassung': self.FASSUNG, 'quelle': self._stat(original), 'fotos': {r: self._stat(p) for r, p in fotos},
                 'einstellungen': {'tiefe_min': o['tiefe_min'], 'tiefe_toleranz': o['tiefe_toleranz']}}
        alt = self._lesen(zettel)
        if alt.get('aktiv') and self.ablage.arbeit(self.DATEI).is_file() and all(alt.get(k) == v for k, v in stand.items()):
            return alt
        foto = Seitentiefe.mittel([Seitentiefe.foto_profil(self._alpha(p)) for _, p in fotos])
        netz = self._laden(original)
        punkte = np.asarray(netz.vertices, dtype=np.float64)
        vorher = Seitentiefe.modell_profil(punkte)
        hinten = self._glatt_hinten(vorher)
        faktoren = self.faktoren(vorher, foto, o['tiefe_min'], o['tiefe_toleranz'])
        wirksam = {h: s for h, s in faktoren.items() if s < 0.999}
        if not wirksam:
            return self._ablegen(zettel, dict(stand, aktiv=False, grund='das Netz ist an keiner Höhe tiefer als das Seitenfoto (Toleranz %.0f %%) — nichts zu tun' % (100 * o['tiefe_toleranz'])))
        neu = self.anwenden(punkte, faktoren, hinten)
        nachher = Seitentiefe.modell_profil(neu)
        netz.vertices = neu
        ziel = self.ablage.arbeit(self.DATEI)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        teil = ziel.with_name(ziel.stem + '.teil' + ziel.suffix)          # trimesh erkennt die Art an der Endung: `.glb` bleibt hinten
        netz.export(str(teil), file_type='glb')
        pruefung = self._pruefen(original, teil, neu)
        if pruefung:
            teil.unlink(missing_ok=True)
            return self._ablegen(zettel, dict(stand, aktiv=False, grund='abgeleitetes Netz verworfen: %s' % pruefung))
        teil.replace(ziel)
        bericht = dict(stand, aktiv=True, stand_zeit=datetime.now().isoformat(timespec='seconds'), sekunden=round(time.perf_counter() - t0, 1), punkte=int(len(neu)),
                       faktoren={str(h): round(s, 4) for h, s in wirksam.items()}, foto=self._runden(foto),
                       vorher=self._runden(vorher, 'tiefe'), nachher=self._runden(nachher, 'tiefe'), staerkster_faktor=round(min(wirksam.values()), 4))
        logger.info('2D3D Kleider %s: Netztiefe — Faktor bis %.3f, %d Höhen, %.1f s', self.job.kennung, bericht['staerkster_faktor'], len(wirksam), bericht['sekunden'])
        return self._ablegen(zettel, bericht)

    @staticmethod
    def _glatt_hinten(profil):
        """`{höhenanteil: z der Rückseite}` — über fünf Höhen gemittelt, damit ein einzelner Ausreißer die Rückseite nicht zackt."""
        hs = sorted(profil)
        z = np.array([profil[h]['hinten'] for h in hs])
        glatt = np.convolve(np.pad(z, 2, mode='edge'), np.ones(5) / 5.0, mode='valid')
        return dict(zip(hs, glatt.tolist(), strict=True))

    def _pruefen(self, original, abgeleitet, erwartet):
        """None, wenn das abgeleitete Netz dieselben Flächen und UV hat und die erwarteten Punkte; sonst der Grund."""
        a, b = self._laden(original), self._laden(abgeleitet)
        if not np.array_equal(np.asarray(a.faces), np.asarray(b.faces)):
            return 'Flächen anders als im Original'
        if len(a.vertices) != len(b.vertices):
            return 'Punktzahl anders (%d gegen %d)' % (len(b.vertices), len(a.vertices))
        hoehe = float(np.ptp(np.asarray(a.vertices)[:, 1]))
        if float(np.abs(np.asarray(b.vertices) - erwartet).max()) > 1e-4 * hoehe:
            return 'Punkte nach dem Schreiben nicht wie berechnet'
        if (getattr(a.visual, 'uv', None) is None) != (getattr(b.visual, 'uv', None) is None):
            return 'UV-Belegung geht verloren'
        return None

    def _lesen(self, zettel):
        try:
            return json.loads(zettel.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}

    def _ablegen(self, zettel, bericht):
        zettel.parent.mkdir(parents=True, exist_ok=True)
        zettel.write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding='utf-8')
        return bericht
