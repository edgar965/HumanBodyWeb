# -*- coding: utf-8 -*-
"""Netzqualität — wie fein die HumanBody-Figur gerechnet wird.

Die drei Spalten aus `core/models/netz_einstellungen.py` (Unterteilung im
Browser, im Film, Hautverschiebung; Vorgaben wie MB-Lab: 2, 3, an), je
Prozess EINMAL gelesen: Der WebSocket-Kanal darf die Datenbank nicht aus
dem Ereigniskreis heraus fragen (`SynchronousOnlyOperation`) und wärmt den
Speicher deshalb beim Verbinden über `database_sync_to_async`; der Film-
Unterprozess liest seine eigene Kopie. Die Einstellungsseite leert den
Speicher nach dem Speichern (`uebernehmen` → `vergessen`).
"""

import logging
from types import SimpleNamespace

logger = logging.getLogger('core')

__all__ = ['Netzqualitaet']


class Netzqualitaet:
    #: (Feld, Vorgabe, Minimum, Maximum) — Vorgaben wie MB-Lab.
    STUFEN_BROWSER = ('unterteilung_browser', 2, 1, 3)
    STUFEN_FILM = ('unterteilung_film', 3, 1, 3)
    VERSCHIEBUNG = 'haut_verschiebung'
    FELDER = ('unterteilung_browser', 'unterteilung_film', 'haut_verschiebung')

    _werte = None

    # ---------------------------------------------------------------- lesen

    @classmethod
    def werte(cls):
        """`{unterteilung_browser, unterteilung_film, haut_verschiebung}`.

        Ist die Datenbank nicht erreichbar (Pruefung ohne Datenbank, Aufbau),
        gelten die Vorgaben von MB-Lab — mit Warnung im Log und OHNE sie zu
        merken, damit der naechste Aufruf es wieder versucht."""
        if cls._werte is None:
            werte = cls._lesen()
            if werte is None:
                return cls.aus_einstellungen(SimpleNamespace())
            cls._werte = werte
        return cls._werte

    @classmethod
    def _lesen(cls):
        from django.core.exceptions import SynchronousOnlyOperation

        try:
            return cls._aus_db()
        except SynchronousOnlyOperation:
            # Aus dem Ereigniskreis gerufen, ohne vorheriges `merken()`:
            # in einem eigenen Faden lesen, statt Vorgaben zu raten.
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor(max_workers=1) as faden:
                return faden.submit(cls._aus_db, True).result()
        except Exception as fehler:  # noqa: BLE001
            # stumm gewollt: gemeldet wird es, nur nicht als Fehlerseite —
            # eine Figur mit MB-Lab-Vorgaben ist besser als keine.
            logger.warning('Netzqualitaet nicht lesbar (%s) — Vorgaben von MB-Lab', fehler)
            return None

    @classmethod
    def _aus_db(cls, eigener_faden=False):
        """Nur der Hilfsfaden schliesst seine Verbindung — im Hauptfaden
        laege sie womoeglich in einer Transaktion (Pruefungen)."""
        from ..models import AppSettings

        try:
            return cls.aus_einstellungen(AppSettings.load())
        finally:
            if eigener_faden:
                from django.db import connection

                connection.close()

    @classmethod
    def aus_einstellungen(cls, s):
        """Die drei Werte aus einem `AppSettings`-Objekt, begrenzt."""
        aus = {}
        for name, vorgabe, mini, maxi in (cls.STUFEN_BROWSER, cls.STUFEN_FILM):
            try:
                wert = int(getattr(s, name, vorgabe))
            except TypeError, ValueError:
                wert = vorgabe
            aus[name] = min(max(wert, mini), maxi)
        aus[cls.VERSCHIEBUNG] = bool(getattr(s, cls.VERSCHIEBUNG, True))
        return aus

    @classmethod
    def merken(cls):
        """Den Speicher füllen — im WebSocket über `database_sync_to_async`."""
        return cls.werte()

    @classmethod
    def vergessen(cls):
        cls._werte = None

    # ------------------------------------------------------------- Zugriffe

    @classmethod
    def stufen_browser(cls):
        """Die Stufe im Browser — was der Browser mit dem Keks `netzstufen`
        selbst gewählt hat (Strg+Alt+H, `Netzstufenwahl`), sonst die
        Einstellung."""
        from .netzstufenwahl import Netzstufenwahl

        gewaehlt = Netzstufenwahl.gewaehlt()
        if gewaehlt is not None:
            return gewaehlt
        return cls.werte()[cls.STUFEN_BROWSER[0]]

    @classmethod
    def stufen_film(cls):
        return cls.werte()[cls.STUFEN_FILM[0]]

    @classmethod
    def verschiebung(cls):
        return cls.werte()[cls.VERSCHIEBUNG]

    # ------------------------------------------------------------ schreiben

    @classmethod
    def uebernehmen(cls, s, post):
        """Formularwerte auf das Einstellungsobjekt (Seite Modell)."""
        from ..api.einstellungen.formularwert import Formularwert as F

        for name, vorgabe, mini, maxi in (cls.STUFEN_BROWSER, cls.STUFEN_FILM):
            setattr(s, name, F.zahl(post, name, vorgabe, mini=mini, maxi=maxi, ganz=True))
        setattr(s, cls.VERSCHIEBUNG, F.schalter(post, cls.VERSCHIEBUNG))
        cls.vergessen()
        return s
