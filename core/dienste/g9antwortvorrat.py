# -*- coding: utf-8 -*-
u"""G9antwortvorrat — fertige Netzantworten als Bytes: im Prozess und auf der
Platte (`Genesis9/ablage/antworten/`). Der Grund steht in `g9antworten.py`
(`G9antworten` erbt von hier); getrennt, weil die Datei 313 Zeilen hatte.
"""
import logging
import os
import threading
from collections import OrderedDict

from Genesis9.pfade import G9pfade

__all__ = ['G9antwortvorrat']

logger = logging.getLogger('core')


class G9antwortvorrat:
    u"""Schluessel -> Bytes: die juengsten im Speicher, alle auf der Platte."""

    ORDNER = 'antworten'
    IM_SPEICHER = 8
    #: So viel Platte hoechstens (Ursula Stufe 2 mit Kleid und Haar: 93 MB).
    PLATTE_MB = 1500

    _speicher = OrderedDict()
    _schloss = threading.Lock()

    # ------------------------------------------------------------- Vorrat

    @classmethod
    def ordner(cls):
        return G9pfade.ablage() / cls.ORDNER

    @classmethod
    def holen(cls, schluessel):
        with cls._schloss:
            daten = cls._speicher.get(schluessel)
            if daten is not None:
                cls._speicher.move_to_end(schluessel)
                return daten
        datei = cls.ordner() / (schluessel + '.json')
        try:
            daten = datei.read_bytes()
        except OSError:
            return None
        try:
            os.utime(datei)          # juengst gebraucht — fuer das Ausduennen
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
        try:
            ordner = cls.ordner()
            ordner.mkdir(parents=True, exist_ok=True)
            ziel = ordner / (schluessel + '.json')
            vorlaeufig = ordner / (schluessel + '.%d.tmp' % threading.get_ident())
            vorlaeufig.write_bytes(daten)
            os.replace(vorlaeufig, ziel)
            cls._ausduennen(ordner)
        except OSError as fehler:
            logger.warning('Genesis 9: Antwort nicht ablegbar: %s', fehler)

    @classmethod
    def _im_speicher(cls, schluessel, daten):
        with cls._schloss:
            cls._speicher[schluessel] = daten
            cls._speicher.move_to_end(schluessel)
            while len(cls._speicher) > cls.IM_SPEICHER:
                cls._speicher.popitem(last=False)

    @classmethod
    def _ausduennen(cls, ordner):
        u"""Aelteste Dateien weg, bis der Ordner unter `PLATTE_MB` liegt."""
        dateien = []
        for datei in ordner.glob('*.json'):
            try:
                st = datei.stat()
            except OSError:
                continue
            dateien.append((st.st_mtime, st.st_size, datei))
        dateien.sort()
        summe = sum(groesse for _, groesse, _ in dateien)
        for _, groesse, datei in dateien:
            if summe <= cls.PLATTE_MB * 1024 * 1024:
                break
            try:
                datei.unlink()
                summe -= groesse
            except OSError:
                pass

    @classmethod
    def vergessen(cls):
        with cls._schloss:
            cls._speicher.clear()
        ordner = cls.ordner()
        if ordner.is_dir():
            for datei in ordner.glob('*.json'):
                try:
                    datei.unlink()
                except OSError:
                    pass
