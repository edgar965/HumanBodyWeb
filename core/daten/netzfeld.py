# -*- coding: utf-8 -*-
u"""Netzfeld — ein typisiertes Zahlenfeld auf dem Weg zum Browser.

WARUM EIN TRÄGER STATT EINES base64-STRINGS (30.09.2026)
========================================================
Bis heute machte `Netzantwort.feld()` aus einem numpy-Feld sofort einen
base64-String. Das Antwort-Wörterbuch war damit reines JSON — bequem, aber
teuer: Der weibliche Grundkörper geht als 5,24 MB über die Leitung, Ursula auf
Stufe 2 mit Kleid und Haar als 93 MB, und base64 kostet davon ein Drittel allein
an Umfang (3 Bytes werden 4 Zeichen). Der Server maß für eine solche Antwort
0,55 s in base64 und JSON (`g9antworten.py`), der Browser zahlte sie ein zweites
Mal beim Dekodieren.

Ein Träger lässt beides offen. Wer JSON will, bekommt base64 (`Netzjson`); wer
das Binärpaket nimmt (`Netzpaket`), bekommt die **rohen Bytes ohne einen einzigen
Umweg**.

WARUM DAS ÜBER NAMENSRATEN GEHT
===============================
Die Felder stecken verschachtelt und heißen nicht immer wie ihr Inhalt:
`antwort['bindung']['dreieck']`, `antwort['hautgewichte']['skin_indices']`,
`felder['koerper'][kanal]['n']`. Ein Packer, der Feldnamen gegen eine Tabelle
hält, übersieht das `n` in der dritten Ebene — und schickt es still als base64
weiter, während der Browser Binärdaten erwartet. Ein Träger wird erkannt, wo
immer er liegt.

DER TYP BLEIBT AM FELD
======================
Die Breite ist der gefährliche Teil (`netzantwort.py`): Ein Feld, das als
float64 herausgeht, wird auf der Gegenseite falsch gelesen — jeder zweite Wert
wird zum Exponenten seines Nachbarn, das Modell sieht zerrissen aus, und niemand
verdächtigt einen Datentyp. Deshalb reist der Typ hier MIT den Bytes, statt auf
beiden Seiten getrennt gepflegt zu werden.
"""
import base64

import numpy as np

__all__ = ['Netzfeld']


class Netzfeld:
    u"""Rohe Bytes eines Zahlenfeldes plus der Typ, mit dem sie zu lesen sind."""

    __slots__ = ('rohdaten', 'typ', 'anzahl')

    #: Typen, die der Browser lesen kann (`gemeinsam/netzpaket.js`). Was hier
    #: nicht steht, hat drüben kein `TypedArray` — dann lieber jetzt ein Fehler
    #: als später ein zerrissenes Netz.
    ERLAUBT = ('float32', 'uint32', 'uint16', 'uint8', 'int32')

    def __init__(self, rohdaten, typ, anzahl):
        self.rohdaten = rohdaten
        self.typ = typ
        self.anzahl = anzahl

    @classmethod
    def aus(cls, werte, typ):
        u"""Ein numpy-Feld (oder eine Liste) als Netzfeld.

        `ravel()` und `ascontiguousarray` gehören zusammen: Ein (N, 3)-Feld und
        ein flaches 3N-Feld liefern dieselben Bytes — aber nur, wenn das Feld
        C-zusammenhängend ist. Nach einem `[:, [0, 2, 1]]` ist es das nicht.
        """
        ziel = np.dtype(typ)
        if ziel.name not in cls.ERLAUBT:
            raise ValueError('Netzfeld: Typ %s kann der Browser nicht lesen' % ziel.name)
        flach = np.ascontiguousarray(np.asarray(werte).ravel(), dtype=ziel)
        return cls(flach.tobytes(), ziel.name, int(flach.size))

    def base64(self):
        u"""Für den JSON-Rückfall — dieselben Bytes, ein Drittel größer."""
        return base64.b64encode(self.rohdaten).decode('ascii')

    def __len__(self):
        u"""Die Zahl der WERTE, nicht der Bytes."""
        return self.anzahl

    def __repr__(self):
        return '<Netzfeld %s×%s, %d B>' % (self.anzahl, self.typ, len(self.rohdaten))
