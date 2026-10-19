# -*- coding: utf-8 -*-
u"""G9texturablage — gemeinsamer Teil der abgeleiteten Bildfassungen (`G9texturkopie`, `G9texturblock`), 19.10.2026.

Eine Fassung wird beim ersten Abruf gerechnet und unter `Genesis9/ablage/texturfassungen/<art>/` abgelegt. Der Schlüssel trägt Pfad, Größe und Zeitstempel des
Originals, die Art samt Kante und die Fassung des Rechenwegs (`~/.claude/rules/artefakte-benennen.md`): ein neues Original oder ein geänderter Rechenweg gibt einen
neuen Namen, nie die Datei eines anderen Laufs. Alte Fassungen bleiben liegen (wie `G9texturverkleinerung`).

Zwei Abrufe desselben Bildes zugleich (Bündel und Einzelabruf) rechnen es einmal: je Schlüssel eine Sperre, geschrieben wird über `AtomarSchreiber`
(Nebendatei, dann umbenannt) — ein Leser sieht nie ein halbes Bild.
"""
import hashlib
import logging
import threading

import numpy as np
from PIL import Image

from Genesis9.pfade import G9pfade

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['G9texturablage']


class G9texturablage:
    u"""Ablage, Schlüssel, Sperre und das Öffnen eines Bildes in einer Form, die jede Fassung schreiben kann."""

    ORDNER = 'texturfassungen'
    _schutz = threading.Lock()
    _sperren = {}

    @classmethod
    def ziel(cls, original, relativ, art, endung, fassung):
        u"""Pfad der Fassung (`<ablage>/<art>/<schluessel><endung>`) — oder None, wenn das Original nicht lesbar ist."""
        try:
            stand = original.stat()
        except OSError:
            return None
        text = '%s|%d|%d|%s|%d' % (relativ, stand.st_size, stand.st_mtime_ns, art, fassung)
        return G9pfade.ablage() / cls.ORDNER / art / (hashlib.sha1(text.encode('utf-8')).hexdigest()[:24] + endung)

    @classmethod
    def sperre(cls, ziel):
        with cls._schutz:
            return cls._sperren.setdefault(str(ziel), threading.Lock())

    @classmethod
    def fertig(cls, ziel, rechnen):
        u"""Die Fassung unter `ziel` — liegt sie nicht, rechnet `rechnen()` ihre Bytes (einmal, auch bei gleichzeitigen Abrufen). None bei einem Lese- oder Bildfehler."""
        if ziel.is_file():
            return ziel
        with cls.sperre(ziel):
            if ziel.is_file():                       # ein anderer Faden war schneller
                return ziel
            try:
                AtomarSchreiber.bytes_schreiben(ziel, rechnen())
            except (OSError, ValueError, SyntaxError) as fehler:     # PIL meldet kaputte Bilder als OSError oder SyntaxError
                logger.warning('Texturfassung %s nicht gerechnet: %s', ziel.parent.name, fehler)
                return None
        return ziel

    @staticmethod
    def lesbar(bild):
        u"""Das Bild als 'RGB', 'RGBA' oder 'L' (8 Bit). 16-Bit-PNG ('I;16', 'I') auf 8 Bit (obere Bits), Palette mit Durchsichtigkeit als RGBA,
        Graustufen mit Alpha als RGBA, alles andere als RGB."""
        modus = bild.mode
        if modus in ('RGB', 'RGBA', 'L'):
            return bild
        if modus.startswith('I'):
            werte = np.asarray(bild, dtype=np.uint32)
            return Image.fromarray(np.clip(werte >> 8 if werte.max() > 255 else werte, 0, 255).astype(np.uint8), 'L')
        if modus in ('LA', 'PA') or (modus == 'P' and 'transparency' in bild.info):
            return bild.convert('RGBA')
        if modus in ('1', 'F'):
            return bild.convert('L')
        return bild.convert('RGB')

    @staticmethod
    def hat_alpha(bild):
        u"""Trägt das Bild eine Durchsichtigkeit, die nicht überall voll ist?"""
        return bild.mode == 'RGBA' and bild.getextrema()[3][0] < 255
