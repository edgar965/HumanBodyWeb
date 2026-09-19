# -*- coding: utf-8 -*-
"""Bildmodellsichtung — Schritt 1: Zuschnitt und Einordnung der Bilder.

Ruft `VideoToBVH/wrappers/_run_bildsichtung.py` (python10: YOLO11-Pose für
den Zuschnitt, MediaPipe für die Sichtung) über alle Originale und legt
das Ergebnis als `job.bilder` ab: je Ausschnitt Datei, Quelle, Kasten,
Kategorie, Gewicht, Ansicht, Haltung, Landmarken (33 × [x, y, sichtbar])
und der Gesichtskasten — die Auftragsseite zeichnet daraus das Rig.

Was der Nutzer auf der Seite umgestellt hat (`manuell: true`), bleibt beim
nächsten Lauf stehen; mit Einordnung „manuell" bleibt alles wie gestellt
und nur neue Ausschnitte werden eingeordnet.
"""

import json
import logging
import os
import subprocess

from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellvideo import Bildmodellvideo

logger = logging.getLogger('core')

__all__ = ['Bildmodellsichtung']


class Bildmodellsichtung:
    RUNNER = '_run_bildsichtung.py'
    WARTEZEIT = 1800
    #: Kategorien, die der Nutzer stellen darf.
    KATEGORIEN = ('koerper', 'kopf', 'video', 'neben', 'gruppe', 'leer')

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    # --------------------------------------------------------------- Lauf

    #: Welche Rigs `--rigs` je Wahl anfordert (MediaPipe läuft immer, es ordnet ein).
    RIGS = {'alle': 'yolo,openpifpaf', 'yolo': 'yolo', 'openpifpaf': 'openpifpaf', 'mediapipe': ''}

    def befehl(self, pfade):
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        befehl = [settings.PIPELINE_PYTHON, runner]
        if self.optionen.get('zuschnitt', 'yolo') == 'yolo':
            befehl += ['--zuschnitt', str(self.ablage.zuschnitt())]
        rigs = self.RIGS.get(self.optionen.get('rig', 'alle'), 'yolo,openpifpaf')
        if rigs:
            befehl += ['--rigs', rigs]
        # Hautton und Texturtauglichkeit je Ausschnitt (`hauttonprobe.py`, 19.09.2026).
        befehl.append('--textur')
        return befehl + [str(p) for p in pfade]

    def ausfuehren(self, melder=None):
        originale = self.ablage.originale()
        videos = Bildmodellvideo(self.ablage).sichten(self.job.bilder)
        if not originale and not videos:
            raise RuntimeError('Keine Bilder oder Videos im Auftrag')
        self.ablage.anlegen()
        befunde = []
        if originale:
            if self.optionen.get('zuschnitt', 'yolo') != 'yolo':
                self._ganz_kopieren(originale)
            if melder:
                melder(0.05, '%d Bilder: Zuschnitt und Sichtung' % len(originale))
            befunde = self._laufen(self.befehl(originale), melder)
        self._uebernehmen(befunde, videos)
        self.job.save(update_fields=['bilder', 'updated_at'])
        return self.job.bilder

    def _ganz_kopieren(self, originale):
        """Ohne Zuschnitt: die Originale als JPG in den Zuschnittordner, damit
        Sichtung und Seite immer denselben Ort lesen (WebP kann der Browser,
        MediaPipe nicht)."""
        from PIL import Image

        for p in originale:
            ziel = self.ablage.zuschnitt() / (p.stem + '.jpg')
            with Image.open(p) as im:
                im.convert('RGB').save(ziel, quality=92)

    def _laufen(self, befehl, melder):
        logger.info('Bildmodell %s: %s', self.job.kennung, ' '.join(befehl[:4]))
        prozess = subprocess.Popen(
            befehl,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Wrapperpfad.pfad(),
        )
        zeilen = []
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('Sichtung: keine Antwort nach %d s' % self.WARTEZEIT) from None
        for zeile in (fehler or '').splitlines():
            if zeile.startswith(('Zuschnitt:', 'Sichtung:')):
                zeilen.append(zeile)
        if melder and zeilen:
            melder(0.9, zeilen[-1])
        antwort = None
        for zeile in (aus or '').splitlines():
            if zeile.startswith('{'):
                antwort = json.loads(zeile)
        if not antwort:
            raise RuntimeError('Sichtung ohne Antwort: %s' % (fehler or '')[-500:])
        if 'error' in antwort:
            raise RuntimeError('Sichtung: %s' % antwort['error'])
        return antwort.get('bilder', [])

    # ------------------------------------------------------ Übernehmen

    def _uebernehmen(self, befunde, videos=()):
        """Ohne Zuschnitt heißen die Dateien wie die Originale (als JPG) —
        die Befunde tragen dann `datei` = Originalname; auf den JPG-Namen
        umschreiben. `videos` kommen fertig von `Bildmodellvideo.sichten`."""
        alt = {b.get('datei'): b for b in self.job.bilder if b.get('datei')}
        manuell = self.optionen.get('einordnung') == 'manuell'
        neu = list(videos)
        for befund in befunde:
            datei = befund.get('datei')
            if not datei:
                continue
            if self.optionen.get('zuschnitt', 'yolo') != 'yolo':
                datei = os.path.splitext(datei)[0] + '.jpg'
                befund['datei'] = datei
            vorher = alt.get(datei)
            eintrag = {k: v for k, v in befund.items() if k != 'fehler' or v}
            eintrag.setdefault('kategorie', 'leer')
            eintrag.setdefault('gewicht', 0.0)
            if eintrag['kategorie'] == 'leer' and self._detailbild(eintrag):
                eintrag['kategorie'] = 'neben'
            if vorher and (manuell or vorher.get('manuell')):
                eintrag['kategorie'] = vorher.get('kategorie', eintrag['kategorie'])
                eintrag['gewicht'] = vorher.get('gewicht', eintrag['gewicht'])
                eintrag['manuell'] = True
            if vorher and 'textur_an' in vorher:
                eintrag['textur_an'] = vorher['textur_an']
            for feld in ('schaetzung', 'gesichtsschaetzung'):
                if vorher and vorher.get(feld):
                    eintrag[feld] = vorher[feld]
            neu.append(eintrag)
        neu.sort(
            key=lambda e: (
                self.KATEGORIEN.index(e['kategorie']) if e['kategorie'] in self.KATEGORIEN else 9,
                -float(e.get('gewicht') or 0),
                e['datei'],
            )
        )
        self.job.bilder = neu

    @staticmethod
    def _detailbild(eintrag):
        """Kein Befund, aber ein großes Bild: ein Detail (Brust, Knie, Füße)
        — Nebenbild, nicht „ohne Befund"."""
        return (eintrag.get('breite') or 0) >= 400 and (eintrag.get('hoehe') or 0) >= 400
