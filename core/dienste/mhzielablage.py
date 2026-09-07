# -*- coding: utf-8 -*-
u"""Mhzielablage — die 1.280 Modellierziele, kompiliert und im Zugriff.

WARUM KOMPILIERT (gemessen 06.09.2026)
======================================
Die `.target`-Dateien sind Text: je Zeile eine Vertexnummer und drei
Verschiebungen. 1.280 Dateien mit 6.147.800 Zeilen EINMAL zu lesen kostet
**17,7 s**. Aus der Ablage ist ein Ziel in **0,02 s** da, und ein Regler holt
selten mehr als zwanzig.

Gespeichert wird wie im Upstream (`core/algos3d.Target._save_binary`):

    <pfad>|i   uint16   Vertexnummern
    <pfad>|v   int16    Verschiebungen in Tausendstel-Dezimetern

Der groesste Betrag im ganzen Bestand ist 10.670 — `int16` reicht bis 32.767.
Die Aufloesung ist damit 0,001 dm = **0,1 mm**; das ist MakeHumans eigene
Genauigkeit, nicht eine hier gewaehlte.

Das npz misst 30,4 MB gegen 133 MB Text.

BAUEN: `manage.py mh_ziele_bauen`. Ohne die Ablage arbeitet diese Klasse
direkt auf den Textdateien weiter — langsamer, aber richtig; eine fehlende
Ablage darf die Seite nicht lahmlegen.
"""

import io
import logging
import os
import threading

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mhzielablage']


class Mhzielablage:
    u"""Ein Ziel als `(Vertexnummern, Verschiebungen in Dezimetern)`."""

    #: Faktor zwischen gespeichertem int16 und Dezimetern.
    TAUSENDSTEL = 1e-3

    _ablage = None
    _gepruef = False
    _zwischen = {}
    _schloss = threading.Lock()

    # ------------------------------------------------------------------ Pfade

    @classmethod
    def pfad(cls):
        from django.conf import settings
        return str(settings.MAKEHUMAN_ZIELABLAGE)

    @classmethod
    def textwurzel(cls):
        from django.conf import settings
        return str(settings.MAKEHUMAN_ZIELE_DIR)

    @classmethod
    def bereit(cls):
        u"""Gibt es ueberhaupt Ziele — als Ablage oder als Text?"""
        return os.path.isfile(cls.pfad()) or os.path.isdir(cls.textwurzel())

    # ------------------------------------------------------------------ lesen

    @classmethod
    def _npz(cls):
        if cls._gepruef:
            return cls._ablage
        with cls._schloss:
            if not cls._gepruef:
                pfad = cls.pfad()
                if os.path.isfile(pfad):
                    cls._ablage = np.load(pfad)
                    logger.info('MakeHuman-Zielablage geöffnet: %d Felder',
                                len(cls._ablage.files))
                else:
                    logger.warning('Keine Zielablage (%s) — die Textdateien '
                                   'werden gelesen, das ist langsam', pfad)
                cls._gepruef = True
        return cls._ablage

    @classmethod
    def ziel(cls, pfad):
        u"""`(nummern, verschiebungen)` — leer, wenn es das Ziel nicht gibt.

        Einmal Gelesenes bleibt im Speicher: Wer einen Regler zieht, holt
        dieselben zwanzig Ziele wieder und wieder.
        """
        if pfad in cls._zwischen:
            return cls._zwischen[pfad]
        werte = cls._holen(pfad)
        cls._zwischen[pfad] = werte
        return werte

    @classmethod
    def _holen(cls, pfad):
        ablage = cls._npz()
        if ablage is not None:
            try:
                nummern = ablage['%s|i' % pfad]
                werte = ablage['%s|v' % pfad]
            except KeyError:
                logger.debug('Ziel nicht in der Ablage: %s', pfad)
                return cls._leer()
            return (nummern.astype(np.int64),
                    werte.astype(np.float64) * cls.TAUSENDSTEL)
        return cls.text_lesen(os.path.join(cls.textwurzel(),
                                           *(pfad + '.target').split('/')))

    @staticmethod
    def _leer():
        return (np.zeros((0,), dtype=np.int64), np.zeros((0, 3)))

    # ------------------------------------------------------------- Textlesen

    @classmethod
    def text_lesen(cls, pfad):
        u"""Eine `.target`-Datei: `vertexnummer dx dy dz` je Zeile.

        Kommentarzeilen tragen im Upstream die Lizenzangabe; hier zaehlen nur
        die Zahlen. Zeilen mit einer anderen Wortzahl als vier werden
        uebergangen — genau wie in `algos3d.Target._load_text`.
        """
        if not os.path.isfile(pfad):
            return cls._leer()
        nummern, werte = [], []
        with io.open(pfad, encoding='utf-8', errors='replace') as quelle:
            for zeile in quelle:
                zeile = zeile.strip()
                if not zeile or zeile.startswith('#'):
                    continue
                teile = zeile.split()
                if len(teile) != 4:
                    continue
                nummern.append(int(teile[0]))
                werte.append((float(teile[1]), float(teile[2]),
                              float(teile[3])))
        if not nummern:
            return cls._leer()
        return (np.asarray(nummern, dtype=np.int64),
                np.asarray(werte, dtype=np.float64))

    # ------------------------------------------------------------------ bauen

    @classmethod
    def bauen(cls, melden=None):
        u"""Alle Textziele in die Ablage schreiben. Gibt die Anzahl zurueck."""
        from .mhzielbaum import Mhzielbaum
        wurzel = cls.textwurzel()
        felder = {}
        ziele = Mhzielbaum.holen().ziele
        for nummer, ziel in enumerate(ziele, 1):
            datei = os.path.join(wurzel, *(ziel.pfad + '.target').split('/'))
            nummern, werte = cls.text_lesen(datei)
            felder['%s|i' % ziel.pfad] = nummern.astype(np.uint16)
            felder['%s|v' % ziel.pfad] = np.round(
                werte / cls.TAUSENDSTEL).astype(np.int16)
            if melden and nummer % 100 == 0:
                melden(nummer, len(ziele))
        ziel_pfad = cls.pfad()
        os.makedirs(os.path.dirname(ziel_pfad), exist_ok=True)
        np.savez_compressed(ziel_pfad, **felder)
        cls.vergessen()
        logger.info('MakeHuman-Zielablage gebaut: %d Ziele, %.1f MB',
                    len(ziele), os.path.getsize(ziel_pfad) / 1048576.0)
        return len(ziele)

    @classmethod
    def vergessen(cls):
        u"""Ablage und Zwischenspeicher fallen lassen — nach einem Neubau."""
        with cls._schloss:
            cls._ablage = None
            cls._gepruef = False
            cls._zwischen = {}
