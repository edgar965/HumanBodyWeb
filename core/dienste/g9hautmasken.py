# -*- coding: utf-8 -*-
u"""G9hautmasken — die im Browser gerechnete Haut-Maske dauerhaft ablegen (19.10.2026).

Edgar, 19.10.2026: „hautmaske ablegen, so dass alles schnell beim laden ist". Die Maske (welche Körperpunkte unter der Kleidung liegen, wohin die
verdeckten Ecken wandern — `gemeinsam/hautrechnung.js`) rechnet ein Worker bei jedem Laden neu: am feinen Körper 2,8 s im Leerlauf, 7–14 s bei
belasteter CPU, auf der Filmstufe länger (`szene-ladezeit.md`, Punkt 7); bis dahin steht „Haut unter der Kleidung" in der Anzeige rechts unten.
Sie hängt nur an der Eingabe — Punkte und Index des Körpers in Ruhe, Punkte und Dreiecke der Stücke, ihre Einstellungen — und am Code der Rechnung.
Der Schlüssel ist ein Hash über die Eingabe (`gemeinsam/hautmaskenvorrat.js`), der Ordner die Fassung des Codes (`Jsquellen`, Meta
`hautmaskenfassung` der Seite):

    Genesis9/ablage/hautmasken/<fassung>/<schluessel>.bin     das Ergebnis von `Hautrechnung.rechnen`, gepackt (`Feldpaket`) und mit gzip

Bis `PLATTE_MB`; was am längsten nicht gelesen wurde, fällt zuerst — auch die Ordner alter Fassungen (ein Tab, der vor einer Code-Änderung geladen
wurde, liest und schreibt dort weiter, bis er neu geladen wird).
"""
import logging
import os
import re
import threading
import time

from Genesis9.pfade import G9pfade

__all__ = ['G9hautmasken']

logger = logging.getLogger('core')


class G9hautmasken:

    ORDNER = 'hautmasken'
    PLATTE_MB = 3000
    #: Eine Maske ist gepackt rund 0,3 MB (fein) bis 2 MB (ultrafein); mehr nimmt der Vorrat nicht an.
    GROESSTE_MB = 64
    FASSUNG = re.compile(r'^[0-9a-f]{8,40}$')
    SCHLUESSEL = re.compile(r'^[a-z0-9]{8,64}$')
    #: gzip-Kopf: so fängt jede Ablage an.
    KOPF = b'\x1f\x8b'

    _schloss = threading.Lock()
    _zuletzt_geduennt = 0.0

    @classmethod
    def wurzel(cls):
        return G9pfade.ablage() / cls.ORDNER

    @classmethod
    def datei(cls, fassung, schluessel):
        u"""Der Pfad — None, wenn Fassung oder Schlüssel nicht so aussehen (sie kommen aus der Anfrage)."""
        if not cls.FASSUNG.match(str(fassung or '')) or not cls.SCHLUESSEL.match(str(schluessel or '')):
            return None
        return cls.wurzel() / fassung / ('%s.bin' % schluessel)

    @classmethod
    def holen(cls, fassung, schluessel):
        u"""Der Pfad der abgelegten Maske — oder None. Ein Treffer frischt die Zeit auf (für das Ausdünnen)."""
        pfad = cls.datei(fassung, schluessel)
        if pfad is None or not pfad.is_file():
            return None
        try:
            os.utime(pfad)
        except OSError:
            pass
        return pfad

    @classmethod
    def ablegen(cls, fassung, schluessel, inhalt):
        u"""Ablegen, ganz oder gar nicht (Nebendatei, dann umbenennen). False bei unpassendem Schlüssel oder Inhalt."""
        pfad = cls.datei(fassung, schluessel)
        if pfad is None or not inhalt or inhalt[:2] != cls.KOPF or len(inhalt) > cls.GROESSTE_MB * 1024 * 1024:
            return False
        if pfad.is_file():
            return True
        neben = pfad.with_name('%s.%d.tmp' % (pfad.name, threading.get_ident()))
        try:
            pfad.parent.mkdir(parents=True, exist_ok=True)
            neben.write_bytes(inhalt)
            os.replace(neben, pfad)
        except OSError as fehler:
            try:
                neben.unlink()
            except OSError:
                pass
            logger.warning('Hautmasken: nicht abgelegt (%s)', fehler)
            return False
        cls.ausduennen()
        return True

    @classmethod
    def ausduennen(cls, mindestens_s=60.0):
        u"""Über `PLATTE_MB`: die am längsten nicht gelesenen Masken zuerst weg; leere Ordner alter Fassungen mit. Höchstens einmal je Minute."""
        with cls._schloss:
            if time.monotonic() - cls._zuletzt_geduennt < mindestens_s:
                return
            cls._zuletzt_geduennt = time.monotonic()
        eintraege = []
        for ordner in cls.wurzel().iterdir() if cls.wurzel().is_dir() else ():
            if not ordner.is_dir() or not cls.FASSUNG.match(ordner.name):
                continue
            for datei in ordner.glob('*.bin'):
                try:
                    info = datei.stat()
                except OSError:
                    continue
                eintraege.append((info.st_mtime, info.st_size, datei))
            for neben in ordner.glob('*.tmp'):
                try:
                    if time.time() - neben.stat().st_mtime > 300:
                        neben.unlink()
                except OSError:
                    pass
        summe = sum(e[1] for e in eintraege)
        for _zeit, groesse, datei in sorted(eintraege):
            if summe <= cls.PLATTE_MB * 1024 * 1024:
                break
            try:
                datei.unlink()
                summe -= groesse
            except OSError:
                continue
        for ordner in cls.wurzel().iterdir():
            try:
                if ordner.is_dir() and cls.FASSUNG.match(ordner.name) and not any(ordner.iterdir()):
                    ordner.rmdir()
            except OSError:
                pass
