# -*- coding: utf-8 -*-
u"""Jsquellen — die Fassung eines ES-Moduls als Inhalts-Hash über alles, was es importiert (19.10.2026).

ANLASS (Edgar, 19.10.2026: „hautmaske ablegen, so dass alles schnell beim laden ist"): Im Browser gerechnete Ergebnisse (die Haut-Maske,
`gemeinsam/hautmaskenvorrat.js`) liegen dauerhaft auf dem Server. Sie gelten nur für den Code, der sie gerechnet hat — die Ablage muss seinen Namen
tragen (`~/.claude/rules/artefakte-benennen.md`). Die Fassung der Statik (`Fassungsstatik`, djangoBase) taugt dafür nicht: sie ist die jüngste
Änderungszeit ALLER statischen Dateien, jede Änderung an irgendeinem Skript (am Tag dutzendfach, auch aus anderen Sitzungen) machte jede Ablage
ungültig. Hier zählt nur der Baum des Moduls: das Modul und jede Datei, die es über einen relativen `import` erreicht (statisch, `export … from`,
`import('./x.js')`), bis nichts Neues dazukommt — Pfad und Inhalt, sortiert, SHA-1.

Gemerkt je Modul: Die Dateien des Baums werden höchstens alle `FRISCHE_S` Sekunden neu angesehen (Größe und Änderungszeit); hat sich keine
geändert, gilt der alte Hash. Ein Import, der nur über einen berechneten Namen läuft, wird nicht gesehen — Module mit gerechneten Ergebnissen
importieren statisch.
"""
import hashlib
import re
import threading
import time
from pathlib import Path

from django.conf import settings

__all__ = ['Jsquellen']


class Jsquellen:

    #: Relative Importe: `import … from './x.js'`, `export … from '../y.js'`, `import './z.js'`, `import('./w.js')`.
    MUSTER = re.compile(r'''(?:\bfrom\s*|\bimport\s*\(?\s*)['"](\.{1,2}/[^'"]+\.js)['"]''')
    FRISCHE_S = 2.0
    LAENGE = 16

    _gemerkt = {}
    _schloss = threading.Lock()

    @classmethod
    def statik(cls):
        return Path(settings.BASE_DIR) / 'static'

    @classmethod
    def huelle(cls, relativ):
        u"""Die Dateien des Baums von `relativ` (relativ zu `static/`), das Modul selbst eingeschlossen — sortiert."""
        wurzel = cls.statik().resolve()
        start = (wurzel / relativ).resolve()
        offen, gesehen = [start], set()
        while offen:
            datei = offen.pop()
            if datei in gesehen or not datei.is_file():
                continue
            gesehen.add(datei)
            try:
                text = datei.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue
            for ziel in cls.MUSTER.findall(text):
                pfad = (datei.parent / ziel).resolve()
                if wurzel in pfad.parents and pfad not in gesehen:
                    offen.append(pfad)
        return sorted(gesehen)

    @classmethod
    def fassung(cls, relativ):
        u"""Der Hash des Baums (`LAENGE` Hex-Zeichen) — leer, wenn das Modul fehlt."""
        jetzt = time.monotonic()
        with cls._schloss:
            alt = cls._gemerkt.get(relativ)
            if alt and jetzt - alt['zeit'] < cls.FRISCHE_S:
                return alt['fassung']
        if alt and cls._stempel(alt['dateien']) == alt['stempel']:
            neu = dict(alt, zeit=jetzt)
        else:
            dateien = cls.huelle(relativ)
            neu = {'zeit': jetzt, 'dateien': dateien, 'stempel': cls._stempel(dateien), 'fassung': cls._hash(dateien)}
        with cls._schloss:
            cls._gemerkt[relativ] = neu
        return neu['fassung']

    @classmethod
    def _stempel(cls, dateien):
        teile = []
        for datei in dateien:
            try:
                info = datei.stat()
                teile.append((info.st_size, info.st_mtime_ns))
            except OSError:
                teile.append(None)
        return tuple(teile)

    @classmethod
    def _hash(cls, dateien):
        if not dateien:
            return ''
        wurzel = cls.statik().resolve()
        summe = hashlib.sha1()
        for datei in dateien:
            summe.update(datei.relative_to(wurzel).as_posix().encode('utf-8') + b'\0')
            try:
                summe.update(datei.read_bytes())
            except OSError:
                summe.update(b'?')
            summe.update(b'\0')
        return summe.hexdigest()[:cls.LAENGE]

    @classmethod
    def vergessen(cls):
        with cls._schloss:
            cls._gemerkt.clear()
