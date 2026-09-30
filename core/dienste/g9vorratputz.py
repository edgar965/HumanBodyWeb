# -*- coding: utf-8 -*-
u"""G9vorratputz — den Antwortvorrat klein halten: fremde Fassungen, Leichen, dann Alter.

WARUM GETRENNT VON DER ABLAGE (30.09.2026)
==========================================
`G9antwortvorrat` legt ab und holt. Das Aufräumen ist eine andere Aufgabe mit eigenen
Regeln, und es war der Grund, warum der Ordner auf 1.569 MB wuchs, in denen nur 53
verschiedene Antworten steckten (761 MB Kopien).

DIE REIHENFOLGE IST DER GANZE PUNKT
===================================
1. **Fremde Fassungen, ganz.** Der Schlüssel einer Antwort trägt die Änderungszeit der
   Genesis-9-Quellen und das Ablageschema. Er dreht sich nie zurück — was unter einer
   alten Fassung liegt, wird **nie wieder gelesen**. Das ist kein alter Eintrag, das ist
   Abfall, und er geht unabhängig von jeder Größengrenze.
2. **Leichen.** `.tmp`-Dateien, deren Schreibfaden bei einem Serverneustart starb —
   gemessen am 30.09.2026: 21 Stück, 327 MB, die älteste 11,7 Tage. Die erste Fassung
   dieses Putzes ließ jede `.tmp` liegen („sie gehört einem laufenden Faden"); ein Faden
   braucht aber Sekunden, nicht Tage. Dazu Inhalte, auf die kein Verweis mehr zeigt,
   und Verweise, deren Inhalt fehlt.
3. **Das Alter**, innerhalb der eigenen Fassung: Hier stehen echte Antworten gegeneinander,
   und die zuletzt gebrauchte gewinnt (`holen` setzt `utime`). Gezählt wird der INHALT —
   zehn Verweise auf dasselbe Netz belegen es einmal.

DIE SCHONFRIST
==============
Ein Autoreload lässt alten und neuen Serverprozess kurz nebeneinander laufen
(`projekt.md`, „Vier Prozesse sind normal"), und ein Schreibfaden legt erst den Inhalt,
dann den Verweis ab — dazwischen ist der Inhalt kurz „verwaist". Alles, was jünger ist als
`frist_s`, fasst der Putz deshalb nicht an.
"""
import logging
import shutil
import time

__all__ = ['G9vorratputz']

logger = logging.getLogger('core')


class G9vorratputz:
    u"""Räumt den Vorratsordner — fremde Fassungen, Leichen, dann nach Alter."""

    @classmethod
    def fremde_fassungen(cls, wurzel, eigene, frist_s):
        u"""Ordner anderer Fassungen und lose Dateien der Wurzel löschen. `(stücke, bytes)`.

        Ein Ordner gilt als unberührt, wenn seine jüngste Datei älter ist als `frist_s` —
        der Ordner-`mtime` selbst reicht nicht: Unter Windows ändert ihn nur das Anlegen
        und Löschen von Einträgen, nicht das Lesen.
        """
        if not wurzel.is_dir():
            return (0, 0)
        jetzt = time.time()
        stuecke = befreit = 0
        for kandidat in wurzel.iterdir():
            if kandidat.name == eigene:
                continue
            if not kandidat.is_dir():
                # Der flache Bestand von vor der Fassungsordnung (bis 30.09.2026 lagen alle
                # Antworten als `<schluessel>.json` nebeneinander) und seine `.tmp`-Leichen.
                groesse = cls._weg_wenn_alt(kandidat, jetzt, frist_s)
                stuecke += 1 if groesse else 0
                befreit += groesse
                continue
            groesse, juengste = cls._bestand(kandidat)
            if juengste and jetzt - juengste < frist_s:
                continue
            try:
                shutil.rmtree(kandidat)
            except OSError as fehler:
                logger.warning('Genesis 9: Fassung %s bleibt liegen: %s', kandidat.name, fehler)
                continue
            stuecke += 1
            befreit += groesse
        if stuecke:
            logger.info('Genesis 9: %d alte Antwort-Stück(e) geräumt, %.0f MB frei',
                        stuecke, befreit / 1e6)
        return (stuecke, befreit)

    @classmethod
    def eigene(cls, ordner, grenze_bytes, frist_s, inhalt, endung, verweis):
        u"""Die eigene Fassung: Leichen weg, dann die ältesten Verweise bis unter die Grenze.

        Liefert die Bytes, die danach belegt sind (nur Inhalte, jeder einmal).
        """
        jetzt = time.time()
        inhaltsordner = ordner / inhalt
        for datei in list(ordner.glob('*.tmp')) + list(inhaltsordner.glob('*.tmp')):
            cls._weg_wenn_alt(datei, jetzt, frist_s)
        inhalte = {}                       # kennung -> (bytes, mtime)
        for datei in inhaltsordner.glob('*' + endung):
            st = cls._stat(datei)
            if st:
                inhalte[datei.stem] = (st.st_size, st.st_mtime)
        verweise = []                      # (mtime, datei, kennung)
        zaehler = {}
        for datei in ordner.glob('*' + verweis):
            st = cls._stat(datei)
            try:
                kennung = datei.read_text(encoding='ascii').strip()
            except OSError:
                continue
            if not st:
                continue
            if kennung not in inhalte:
                # Verweis ins Leere — nur, wenn er alt ist (sonst schreibt gerade jemand).
                cls._weg_wenn_alt(datei, jetzt, frist_s)
                continue
            verweise.append((st.st_mtime, datei, kennung))
            zaehler[kennung] = zaehler.get(kennung, 0) + 1
        # Verwaiste Inhalte: kein Verweis zeigt darauf.
        for kennung, (_groesse, mtime) in list(inhalte.items()):
            if kennung not in zaehler and jetzt - mtime >= frist_s:
                if cls._loeschen(inhaltsordner / (kennung + endung)):
                    del inhalte[kennung]
        belegt = sum(groesse for groesse, _ in inhalte.values())
        verweise.sort()
        for _, datei, kennung in verweise:
            if belegt <= grenze_bytes:
                break
            if not cls._loeschen(datei):
                continue
            zaehler[kennung] -= 1
            if zaehler[kennung] == 0 and kennung in inhalte:
                if cls._loeschen(inhaltsordner / (kennung + endung)):
                    belegt -= inhalte.pop(kennung)[0]
        return belegt

    # ------------------------------------------------------------- Helfer

    @classmethod
    def _weg_wenn_alt(cls, datei, jetzt, frist_s):
        u"""Datei löschen, wenn sie älter als die Frist ist — liefert die Bytes (sonst 0)."""
        st = cls._stat(datei)
        if not st or jetzt - st.st_mtime < frist_s:
            return 0
        return st.st_size if cls._loeschen(datei) else 0

    @staticmethod
    def _stat(datei):
        try:
            return datei.stat()
        except OSError:
            return None

    @staticmethod
    def _loeschen(datei):
        try:
            datei.unlink()
            return True
        except OSError:
            return False

    @staticmethod
    def _bestand(ordner):
        u"""`(Bytes, jüngste Änderungszeit)` der DATEIEN eines Ordners — nicht seiner
        Unterordner: Deren Zeit ändert das Anlegen, und ein frisch angelegtes `inhalt/`
        hielt sonst eine Fassung mit stundenalten Dateien für jung (Test, 30.09.2026)."""
        groesse = juengste = 0
        for datei in ordner.rglob('*'):
            try:
                if not datei.is_file():
                    continue
                st = datei.stat()
            except OSError:
                continue
            groesse += st.st_size
            juengste = max(juengste, st.st_mtime)
        return (groesse, juengste)
