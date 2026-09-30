# -*- coding: utf-8 -*-
u"""G9antwortvorrat — fertige Netzantworten als Bytes: im Prozess und auf der
Platte (`Genesis9/ablage/antworten/<fassung>/`). Der Grund steht in
`g9antworten.py` (`G9antworten` erbt von hier); getrennt, weil die Datei 313
Zeilen hatte. Aufgeräumt wird in `g9vorratputz.py`.

DUBLETTEN, ZWEI URSACHEN (30.09.2026, Edgar: „warum löschst du keine Dubletten")
================================================================================
Gemessen im gewachsenen Vorrat: **105 Dateien, 1.569 MB — aber nur 53 verschiedene
Inhalte**, 761 MB Kopien. Zwei Ursachen, gemessen nacheinander:

1. **Alte Code-Fassungen.** Der Schlüssel trägt die Änderungszeit der Genesis-9-Quellen
   (`G9antworten.fassung`); jede Änderung baut alles unter neuem Schlüssel neu, die alten
   Dateien blieben liegen. Jetzt hat jede Fassung ihren Ordner, und fremde Fassungen
   räumt der Putz zuerst — sie werden nie wieder gelesen.
2. **Verschiedene Anfragen, dasselbe Netz.** Nach dem ersten Umbau lagen in EINER Fassung
   64 Dateien, davon 42 Dubletten: `haar_generisch` mit `sorte.kin_hair = 1` und direkt
   `kin_hair`, zwei Rümpfe, die sich nur in `sorte_zuletzt` unterscheiden, dasselbe Stück
   mit anderen getragenen Stücken ohne Überlappung. Der Schlüssel hängt an der EINGABE,
   und viele Eingaben ergeben dieselbe Ausgabe. Das kann kein Schlüssel verhindern —
   deshalb liegt jetzt der INHALT unter seinem Hash, einmal, und jeder Schlüssel ist nur
   ein Verweis darauf:

       antworten/<fassung>/inhalt/<sha1>.hbm     der Inhalt, genau einmal
       antworten/<fassung>/<schluessel>.ref      40 Zeichen: sein sha1

Gehasht wird im Schreibfaden, nicht in der Anfrage (bei 90 MB etwa 0,1 s). Der Speicher
im Prozess bleibt nach Schlüssel — acht Einträge, dort lohnt kein Hash im Anfragefaden.

`SCHEMA` steht in der Fassungsmarke: Wer das Ablageformat ändert, zählt es hoch, und der
alte Ordner wird zur fremden Fassung (`~/.claude/rules/artefakte-benennen.md`).
"""
import hashlib
import logging
import os
import shutil
import threading
from collections import OrderedDict

from Genesis9.pfade import G9pfade

__all__ = ['G9antwortvorrat']

logger = logging.getLogger('core')


class G9antwortvorrat:
    u"""Schluessel -> Bytes: die juengsten im Speicher, alle auf der Platte."""

    ORDNER = 'antworten'
    INHALT = 'inhalt'
    IM_SPEICHER = 8
    #: So viel Platte hoechstens (Ursula Stufe 2 mit Kleid und Haar: 93 MB).
    PLATTE_MB = 1500
    #: Endung der Inhalte (seit 30.09.2026 ein Binaerpaket, `core/daten/netzpaket.py`).
    ENDUNG = '.hbm'
    #: Endung der Verweise Schluessel -> Inhalt.
    VERWEIS = '.ref'
    #: Das Ablageformat. 1: `<schluessel>.hbm` flach; 2: inhaltsadressiert.
    SCHEMA = 2
    #: So lange bleibt Fremdes unberuehrt: Beim Autoreload laufen alter und neuer
    #: Prozess kurz nebeneinander, und ein Schreibfaden legt erst den Inhalt, dann
    #: den Verweis ab.
    FREMD_FRIST_S = 300.0

    _speicher = OrderedDict()
    _schloss = threading.Lock()

    # ------------------------------------------------------------- Ordner

    @classmethod
    def wurzel(cls):
        u"""Der Ordner ueber allen Fassungen."""
        return G9pfade.ablage() / cls.ORDNER

    @classmethod
    def ordner(cls):
        u"""Der Ordner DIESER Fassung — hier wird gelesen und geschrieben."""
        return cls.wurzel() / cls.fassungsmarke()

    @classmethod
    def fassungsmarke(cls):
        u"""Fassung und Ablageschema als kurzer, dateisystemsicherer Name."""
        roh = '%s/%s' % (cls.fassung(), cls.SCHEMA)
        return 'f' + hashlib.sha1(roh.encode('ascii')).hexdigest()[:12]

    @classmethod
    def fassung(cls):
        u"""Ueberschrieben in `G9antworten` — hier nur, damit der Vorrat
        allein lauffaehig bleibt (Tests legen ihn ohne die Oberklasse an)."""
        return 0

    # ------------------------------------------------------------- Vorrat

    @classmethod
    def holen(cls, schluessel):
        with cls._schloss:
            daten = cls._speicher.get(schluessel)
            if daten is not None:
                cls._speicher.move_to_end(schluessel)
                return daten
        ordner = cls.ordner()
        verweis = ordner / (schluessel + cls.VERWEIS)
        try:
            kennung = verweis.read_text(encoding='ascii').strip()
            inhalt = ordner / cls.INHALT / (kennung + cls.ENDUNG)
            daten = inhalt.read_bytes()
        except OSError:
            return None
        for datei in (verweis, inhalt):     # juengst gebraucht — fuer das Ausduennen
            try:
                os.utime(datei)
            except OSError:
                pass
        cls._im_speicher(schluessel, daten)
        return daten

    @classmethod
    def merken(cls, schluessel, daten, platte=True):
        cls._im_speicher(schluessel, daten)
        if platte:
            threading.Thread(target=cls._schreiben, args=(schluessel, daten),
                             daemon=True, name='g9-antwort').start()

    @classmethod
    def _schreiben(cls, schluessel, daten):
        u"""Erst den Inhalt (falls neu), dann den Verweis — beides ganz oder gar nicht."""
        try:
            ordner = cls.ordner()
            (ordner / cls.INHALT).mkdir(parents=True, exist_ok=True)
            kennung = hashlib.sha1(daten).hexdigest()
            inhalt = ordner / cls.INHALT / (kennung + cls.ENDUNG)
            if not inhalt.exists():
                cls._ablegen(inhalt, daten)
            cls._ablegen(ordner / (schluessel + cls.VERWEIS), kennung.encode('ascii'))
            cls._ausduennen(ordner)
        except OSError as fehler:
            logger.warning('Genesis 9: Antwort nicht ablegbar: %s', fehler)

    @staticmethod
    def _ablegen(ziel, daten):
        vorlaeufig = ziel.with_name('%s.%d.tmp' % (ziel.name, threading.get_ident()))
        vorlaeufig.write_bytes(daten)
        os.replace(vorlaeufig, ziel)

    @classmethod
    def _im_speicher(cls, schluessel, daten):
        with cls._schloss:
            cls._speicher[schluessel] = daten
            cls._speicher.move_to_end(schluessel)
            while len(cls._speicher) > cls.IM_SPEICHER:
                cls._speicher.popitem(last=False)

    @classmethod
    def _ausduennen(cls, ordner):
        u"""Fremde Fassungen, Leichen, dann das Alter (`G9vorratputz`)."""
        from .g9vorratputz import G9vorratputz
        G9vorratputz.fremde_fassungen(cls.wurzel(), cls.fassungsmarke(), cls.FREMD_FRIST_S)
        G9vorratputz.eigene(ordner, cls.PLATTE_MB * 1024 * 1024, cls.FREMD_FRIST_S,
                            inhalt=cls.INHALT, endung=cls.ENDUNG, verweis=cls.VERWEIS)

    @classmethod
    def vergessen(cls):
        u"""Speicher und Platte leeren — ALLE Fassungen, nicht nur die eigene.

        Wer „vergessen" sagt, meint den Ordner: Die Daz-Bibliothek hat sich
        geändert, und die sieht der Fassungsschlüssel nicht (`g9antworten.py`).
        """
        with cls._schloss:
            cls._speicher.clear()
        wurzel = cls.wurzel()
        if not wurzel.is_dir():
            return
        for eintrag in wurzel.iterdir():
            try:
                if eintrag.is_dir():
                    shutil.rmtree(eintrag)
                else:
                    eintrag.unlink()
            except OSError:
                pass
