# -*- coding: utf-8 -*-
u"""G9texturbasisreihe — die UASTC-Fassungen (`G9texturbasis`) im Hintergrund kodieren, eine nach der anderen (19.10.2026).

`basisu` braucht für ein 4096er-Bild rund 45 s auf sechs Kernen (gemessen 19.10.2026 an Damiras Bildern, `ktx2_kodieren.py`) — das kann keine Anfrage abwarten.
Die Anfrage stellt das Bild hier an und bekommt solange den S3TC-Block. EIN Faden arbeitet die Reihe ab, EIN `basisu` zugleich, mit niedriger Priorität auf
höchstens `KERNE` Kernen (basisu kennt keine Fadenzahl; die Kerne begrenzt die Affinität). Jedes fertige Bild bleibt liegen — die nächste Anfrage findet es.

Ablauf je Bild: Original lesen (`G9texturablage.lesbar`, Zweierpotenz wie beim Block) → PNG neben das Ziel → `basisu -ktx2 -uastc -mipmap -y_flip …` → Container
(`G9texturbasis.packen`) über `AtomarSchreiber` ans Ziel; die beiden Zwischendateien gehen danach weg. Nicht `PipelineProzess`: der kennt weder Priorität noch
Affinität; die Ausgabe von basisu liest `communicate` (kein voller Puffer).
**Stirbt der Server** (Autoreload, Neustart), läuft ein gestartetes basisu sein Bild zu Ende und endet von selbst; seine Zwischendateien tragen die Prozessnummer und
werden beim nächsten Start der Reihe weggeräumt, wenn sie älter als `ALT_S` sind. Die Reihe selbst ist dann leer — die nächste Seite stellt neu an.
"""
import logging
import os
import queue
import subprocess
import threading
import time
from pathlib import Path

from django.conf import settings
from PIL import Image

from ..atomic_write import AtomarSchreiber
from .g9texturbasis import G9texturbasis
from .g9texturblock import G9texturblock

logger = logging.getLogger('core')

__all__ = ['G9texturbasisreihe']


class G9texturbasisreihe:
    u"""Warteschlange und Arbeitsfaden für `basisu`."""

    #: Wie im Versuch gemessen (45 s je 4096er-Bild); der Rechner hat 12 logische Kerne.
    KERNE = 6
    #: Länger darf ein Bild nicht brauchen (4096²: 45 s gemessen) — sonst wird basisu beendet.
    FRIST_S = 600
    ALT_S = 3600
    _reihe = queue.Queue()
    _angestellt = set()
    _schutz = threading.Lock()
    _faden = None
    _fehlt_gemeldet = False

    @staticmethod
    def basisu():
        return Path(settings.TOOLS_ROOT) / 'tools' / 'basisu_src' / 'bin' / 'basisu.exe'

    @classmethod
    def anstellen(cls, ziel, original, relativ, linear):
        u"""Das Bild in die Reihe stellen (einmal je Ziel). Ohne `basisu` nichts, mit einer Warnung je Prozess."""
        if not cls.basisu().is_file():
            if not cls._fehlt_gemeldet:
                cls._fehlt_gemeldet = True
                logger.warning('UASTC: %s fehlt — die Bilder kommen als S3TC-Block (Weg C)', cls.basisu())
            return False
        with cls._schutz:
            if str(ziel) in cls._angestellt:
                return False
            cls._angestellt.add(str(ziel))
            cls._reihe.put((ziel, original, relativ, linear))
            if cls._faden is None or not cls._faden.is_alive():
                cls._faden = threading.Thread(target=cls._arbeiten, name='uastc-reihe', daemon=True)
                cls._faden.start()
        return True

    @classmethod
    def offen(cls):
        u"""Wie viele Bilder noch warten (für Log und Proben)."""
        return cls._reihe.qsize()

    @classmethod
    def _arbeiten(cls):
        cls._aufraeumen()
        while True:
            ziel, original, relativ, linear = cls._reihe.get()
            try:
                if not ziel.is_file():
                    cls.kodieren(ziel, original, relativ, linear)
            except Exception:  # noqa: BLE001 — ein kaputtes Bild darf die Reihe nicht beenden; es bleibt beim Block
                logger.exception('UASTC %s gescheitert', relativ)
            finally:
                with cls._schutz:
                    cls._angestellt.discard(str(ziel))

    @classmethod
    def kodieren(cls, ziel, original, relativ, linear):
        u"""Ein Bild kodieren und den Container ans Ziel legen. Gibt die Sekunden zurück; wirft bei einem Fehler."""
        start = time.perf_counter()
        with Image.open(original) as bild:
            bild = G9texturbasis.lesbar(bild)
            bild.load()
        alpha = G9texturbasis.hat_alpha(bild)
        bild = bild.convert('RGBA' if alpha else 'RGB')
        groesse = (G9texturblock.zweierpotenz(bild.width), G9texturblock.zweierpotenz(bild.height))
        quelle = ziel.with_name('%s.arbeit-%d.png' % (ziel.stem, os.getpid()))
        ausgabe = ziel.with_name('%s.arbeit-%d.ktx2' % (ziel.stem, os.getpid()))
        ziel.parent.mkdir(parents=True, exist_ok=True)
        try:
            (bild if bild.size == groesse else bild.resize(groesse, Image.LANCZOS)).save(quelle, 'PNG', compress_level=1)
            cls._basisu(quelle, ausgabe, relativ, linear)
            AtomarSchreiber.bytes_schreiben(ziel, G9texturbasis.packen(bild, ausgabe.read_bytes(), linear))
        finally:
            for rest in (quelle, ausgabe):
                rest.unlink(missing_ok=True)
        dauer = time.perf_counter() - start
        logger.info('UASTC %s: %.1f s, %d Bytes (noch %d in der Reihe)', relativ, dauer, ziel.stat().st_size, cls.offen())
        return dauer

    @classmethod
    def _basisu(cls, quelle, ausgabe, relativ, linear):
        import psutil
        befehl = [str(cls.basisu()), '-ktx2', '-uastc', '-mipmap', '-y_flip', '-file', str(quelle), '-output_file', str(ausgabe)]
        if linear and G9texturbasis.normalenkarte(relativ):
            befehl.append('-normal_map')
        befehl.append('-linear' if linear else '-srgb')
        flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS | subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        prozess = psutil.Popen(befehl, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=flags)
        try:
            prozess.cpu_affinity(list(range(min(cls.KERNE, max(1, (psutil.cpu_count() or 2) - 1)))))
        except (psutil.Error, OSError, ValueError) as fehler:
            logger.debug('UASTC: Affinität nicht gesetzt (%s)', fehler)
        try:
            text = prozess.communicate(timeout=cls.FRIST_S)[0].decode('utf-8', 'replace')
        except subprocess.TimeoutExpired:
            prozess.kill()
            prozess.communicate()
            raise RuntimeError('basisu nach %d s beendet' % cls.FRIST_S)
        if prozess.returncode != 0 or not ausgabe.is_file():
            raise RuntimeError('basisu Rückgabe %s: %s' % (prozess.returncode, text[-600:]))

    @classmethod
    def _aufraeumen(cls):
        u"""Zwischendateien eines früheren Prozesses (Server starb mitten im Bild) wegräumen — nur eigene Muster, nur älter als `ALT_S`."""
        from Genesis9.pfade import G9pfade
        grenze = time.time() - cls.ALT_S
        for art in ('uastc', 'uastc-lin'):
            ordner = G9pfade.ablage() / G9texturbasis.ORDNER / art
            for rest in ordner.glob('*.arbeit-*') if ordner.is_dir() else ():
                try:
                    if rest.stat().st_mtime < grenze:
                        rest.unlink()
                except OSError:
                    pass
