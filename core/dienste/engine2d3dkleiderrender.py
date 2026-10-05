# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrender — der Render-Schritt eines Auftrags „2D3D Kleider": das Modell mit der Bewegung und dem Ton als Video (03.10.2026).

Edgar: „füge rechts auch den render schritt hinzu, mit Option, wie lange der sein soll (in s bis zur ganzen bvh in s)", „mit pfadangabe wo der
Output gerendert ist". Gerechnet wird mit der Film-Bibliothek `Figurfilm` (Figurcache aus Stand-Modell und Bewegung, Stoff und Strähnen,
Mitsuba-Pfadverfolgung mit Entrauscher) in einem eigenen Prozess (`manage.py engine2d3dkleider_render`); die Seite fragt den Stand über den
Zustand des Auftrags ab (`zustand['render']`).

DAS REZEPT: Welche Programme die Stufen ausführen, steht je Auftrag in `arbeit/render/rezept.json` (`programme`: Ordner mit
`video_bauen.py` und `film_video.py`, `name`: Arbeitsname dort). Ohne diese Datei gilt das allgemeine Rezept (`Engine2d3dKleiderrenderallgemein`, 04.10.2026: Standmodell, Figurcache und Mitsuba, ohne
Simulation) — die Stoff- und Strähnenwerte (Hemd, Federn, Ketten) gehören zu den Teilen von Randy und stehen nur in dessen Rezept.

Dateien in `arbeit/render/`: `rezept.json`, `auftrag.json` (die Wahl der Seite), `zustand.json` (Stufe, Fortschritt, Ergebnis), `render.pid`.
Das Video: `ergebnis/render_video.mp4` und als Kopie im Exportordner des Auftrags (`<Name>_render.mp4`).
"""

import json
import logging
import time

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .engine2d3dkleiderrenderallgemein import Engine2d3dKleiderrenderallgemein
from .engine2d3dkleiderrenderlaeufe import Engine2d3dKleiderrenderlaeufe

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderrender']


class Engine2d3dKleiderrender:
    ORDNER = 'render'
    VIDEO = 'render_video.mp4'
    FPS = 30
    #: Die Auswahl der Seite: Kamerafahrten (`film_video.KAMERA`) und Bildgrößen.
    KAMERAS = ('zoom_ein', 'zoom_aus', 'zoom_ein_langsam', 'gesicht', 'brust')
    GROESSEN = {'960x1200': (960, 1200), '480x600': (480, 600)}
    #: Kürzester Lauf: 10 Bilder (Edgar, 04.10.2026: „rendere erstmal nur 10 Frames … wenn die gut sind, nimm 30, und dann das ganze BVH").
    MIN_SEKUNDEN = 10 / 30
    #: Proben je Pixel (vor dem Entrauschen): Vorgabe und Grenzen der Seite.
    SPP, SPP_MIN, SPP_MAX = 96, 8, 256

    def __init__(self, job):
        self.job = job
        self.ablage = Engine2d3dKleiderablage(job.kennung)

    # ----------------------------------------------------------------- Dateien

    def _datei(self, name):
        ordner = self.ablage.arbeit(self.ORDNER)
        ordner.mkdir(parents=True, exist_ok=True)
        return ordner / name

    def rezept(self):
        """Das Rezept des Auftrags (`arbeit/render/rezept.json`) — ohne eigenes das allgemeine (`Engine2d3dKleiderrenderallgemein`, 04.10.2026), None nur, wenn auch dessen Vorlage fehlt."""
        pfad = self._datei('rezept.json')
        try:
            if pfad.is_file():
                return json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('2D3D Kleider %s: render/rezept.json nicht lesbar (%s)', self.job.kennung, fehler)
            return None
        return Engine2d3dKleiderrenderallgemein(pfad.parent).rezept()

    def bewegung_sekunden(self):
        """Länge der Bewegung in Sekunden (die ganze BVH) — 0, solange es keine gibt."""
        film = (self.job.ergebnis or {}).get('film') or {}
        pfad = self.ablage.ergebnis(film.get('bewegung') or 'film_bewegung.json')
        if not pfad.is_file():
            return 0.0
        try:
            return float(json.loads(pfad.read_text(encoding='utf-8')).get('duration') or 0.0)
        except (OSError, ValueError):
            return 0.0

    # ------------------------------------------------------------------ Prüfen

    def pruefen(self, sekunden, kamera, groesse):
        """→ `(sekunden, kamera, (breite, hoehe))` oder `ValueError` mit der Meldung für die Seite."""
        if self.rezept() is None:
            raise ValueError('Für diesen Auftrag gibt es noch kein Render-Rezept (arbeit/render/rezept.json)')
        ganz = self.bewegung_sekunden()
        if ganz <= 0:
            raise ValueError('Es gibt noch keine Bewegung — in den Optionen unter „Film" eine BVH wählen oder einmal exportieren')
        try:
            sekunden = float(sekunden)
        except (TypeError, ValueError):
            raise ValueError('Länge in Sekunden fehlt') from None
        bilder = round(sekunden * self.FPS)               # 0,33 s zählen als 10 Bilder, 16,3 s als die 489 der ganzen BVH (ihre Dauer ist 16,2999…)
        if bilder < round(self.MIN_SEKUNDEN * self.FPS) or bilder > round(ganz * self.FPS):
            raise ValueError('Länge: %.2f bis %.1f Sekunden (10 Bilder bis zur ganzen BVH)' % (self.MIN_SEKUNDEN, ganz))
        if kamera not in self.KAMERAS:
            raise ValueError('Kamera: %s' % ', '.join(self.KAMERAS))
        if groesse not in self.GROESSEN:
            raise ValueError('Größe: %s' % ', '.join(self.GROESSEN))
        return sekunden, kamera, self.GROESSEN[groesse]

    # ------------------------------------------------------------------- Stand

    def bericht(self):
        """Für den Zustand der Seite: `{moeglich, dauer, status, schritt, fortschritt, ausgabe, fehler}`."""
        aus = {'moeglich': self.rezept() is not None, 'dauer': round(self.bewegung_sekunden(), 2), 'status': 'leer'}
        pfad = self._datei('zustand.json')
        try:
            if pfad.is_file():
                aus.update(json.loads(pfad.read_text(encoding='utf-8')))
        except (OSError, ValueError) as fehler:
            logger.info('2D3D Kleider %s: render/zustand.json nicht lesbar (%s)', self.job.kennung, fehler)
        aus['laeufe'] = Engine2d3dKleiderrenderlaeufe(self).neueste()
        if aus.get('status') == 'laeuft' and not self.laeuft():
            aus.update(status='fehler', fehler=aus.get('fehler') or 'Der Render-Prozess ist abgebrochen (siehe Protokoll des Auftrags)')
        return aus

    def laeuft(self):
        from ..pipelines.prozesspruefung import Prozesspruefung
        pfad = self._datei('render.pid')
        try:
            return pfad.is_file() and Prozesspruefung.lebt(int(pfad.read_text().strip() or 0))
        except (OSError, ValueError):
            return False

    def melden(self, **felder):
        """Den Stand ablegen (der Arbeitsprozess ruft das je Stufe) — `zustand.json` wird als Ganzes ersetzt."""
        pfad = self._datei('zustand.json')
        alt = {}
        try:
            alt = json.loads(pfad.read_text(encoding='utf-8')) if pfad.is_file() else {}
        except (OSError, ValueError):
            alt = {}
        alt.update(felder, aktualisiert=time.strftime('%H:%M:%S'))
        zwischen = pfad.with_name('zustand.json.teil')
        zwischen.write_text(json.dumps(alt, ensure_ascii=False, indent=1), encoding='utf-8')
        zwischen.replace(pfad)
