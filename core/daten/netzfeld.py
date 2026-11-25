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
import struct

import torch
from KoerperKI_alle.kartenwerte import Kartenwerte
from KoerperKI_alle.torchfeld import Torchfeld

from .netzkurz import Netzkurz

__all__ = ['Netzfeld']


class Netzfeld:
    u"""Rohe Bytes eines Zahlenfeldes plus der Typ, mit dem sie zu lesen sind."""

    __slots__ = ('_roh', '_karte', '_kurz', 'typ', 'anzahl', 'genau')

    #: Typen, die der Browser lesen kann (`gemeinsam/netzpaket.js`). Was hier
    #: nicht steht, hat drüben kein `TypedArray` — dann lieber jetzt ein Fehler
    #: als später ein zerrissenes Netz.
    ERLAUBT = ('float32', 'uint32', 'uint16', 'uint8', 'int32')

    def __init__(self, rohdaten, typ, anzahl, genau=False):
        self._roh = rohdaten
        #: Bis zum Abholen der Tensor auf der Karte (`aus`, `abholen`; 18.11.2026).
        self._karte = None
        #: `(bytes uint16, {'ab', 'schritt'})`, wenn das Feld schon gekürzt abgeholt ist (`Netzkurz.auf_karte`, 25.11.2026); die vollen Bytes holt `rohdaten` dann nur auf Verlangen.
        self._kurz = None
        self.typ = typ
        self.anzahl = anzahl
        #: Das Feld trägt NUMMERN (Punkt- oder Knochennummern als float32), keine Messwerte: `Netzpaket` kürzt es nie auf 16 Bit
        #: (`netzkurz.py`, 12.11.2026 — eine halbe Rasterstufe daneben ist ein anderer Punkt).
        self.genau = bool(genau)

    @property
    def rohdaten(self):
        u"""Die Bytes — ein Feld auf der Karte wird spätestens hier abgeholt (sonst gesammelt in `abholen`)."""
        if self._roh is None:
            self._roh, self._karte = Torchfeld.als_bytes(self._karte), None
        return self._roh

    @classmethod
    def aus(cls, werte, typ, genau=False):
        u"""Ein numpy-Feld (oder eine Liste) als Netzfeld.

        `ravel()` und `ascontiguousarray` gehören zusammen: Ein (N, 3)-Feld und
        ein flaches 3N-Feld liefern dieselben Bytes — aber nur, wenn das Feld
        C-zusammenhängend ist. Nach einem `[:, [0, 2, 1]]` ist es das nicht.

        Ein Feld auf der Karte bleibt dort, als eigene Kopie (eine spätere Änderung des Aufrufers erreicht die Antwort nicht), bis `abholen` alle Felder einer Antwort
        in EINER Kopie zur CPU holt (18.11.2026; bis dahin je Feld eine, mit Wartepunkt — 82 je Reglerzug, GPU-Wächter `_wegwerf/zug_kartenwaechter.py`).
        """
        ziel = Torchfeld.dtype(typ)
        if Torchfeld.typname(ziel) not in cls.ERLAUBT:
            raise ValueError('Netzfeld: Typ %s kann der Browser nicht lesen' % Torchfeld.typname(ziel))
        flach = Torchfeld.feld(Torchfeld.feld(werte).ravel(), dtype=ziel)
        if isinstance(flach, torch.Tensor) and flach.device.type != 'cpu':
            feld = cls(None, Torchfeld.typname(ziel), int(flach.numel()), genau=genau)
            feld._karte = flach.detach().contiguous().clone()
            return feld
        return cls(Torchfeld.als_bytes(flach), Torchfeld.typname(ziel), int(Torchfeld.groesse(flach)), genau=genau)

    @classmethod
    def abholen(cls, daten, mit=(), kurz=False):
        u"""Alle Netzfelder in `daten` (verschachtelt in dict, list, tuple), die noch auf der Karte liegen, in EINER Kopie zur CPU — je Gerät; dieselben Bytes wie einzeln.
        In derselben Kopie die `Kartenwerte` der Antwort (Skelett, Höhe, Boden; 18.11.2026): ihr gebauter Wert ersetzt den Platzhalter. `mit`: weitere
        [(uint8-Feld auf der Karte, Empfänger(bytes))] in derselben Kopie (die Prüfbits der Vermutungen, `G9pruefbau`). `kurz`: große Messwertfelder gleich als 16 Bit."""
        netzfelder = []
        gefunden = Kartenwerte.finden(daten, auch=(Netzfeld, netzfelder))
        weitere = list(mit)
        for f in netzfelder:
            if f._roh is not None or f._karte is None or f._kurz is not None:
                continue
            if kurz and f.typ == 'float32' and not f.genau and f.anzahl >= Netzkurz.AB_ANZAHL:
                q, kopf = Netzkurz.auf_karte(f._karte)
                weitere += [(q.view(torch.uint8), f._kurz_bytes), (kopf.view(torch.uint8), f._kurz_kopf)]
            else:
                weitere.append((f._karte.reshape(-1).view(torch.uint8), f._setzen))
        if gefunden or weitere:
            Kartenwerte.einsetzen(gefunden, weitere)

    def _kurz_bytes(self, roh):
        self._kurz = (roh, None)

    def _kurz_kopf(self, roh):
        u"""Nach `_kurz_bytes`, in derselben Kopie: ab, schritt, gültig — ein Feld mit einem einzigen Wert oder NaN bleibt ungekürzt (wie `Netzkurz.packen`)."""
        ab, schritt, gut = struct.unpack('<3d', roh)
        self._kurz = (self._kurz[0], {'ab': ab, 'schritt': schritt}) if gut else None

    @property
    def kurz(self):
        return self._kurz

    def _setzen(self, roh):
        self._roh, self._karte = roh, None

    def base64(self):
        u"""Für den JSON-Rückfall — dieselben Bytes, ein Drittel größer."""
        return base64.b64encode(self.rohdaten).decode('ascii')

    def __len__(self):
        u"""Die Zahl der WERTE, nicht der Bytes."""
        return self.anzahl

    def __repr__(self):
        return '<Netzfeld %s×%s, %d B>' % (self.anzahl, self.typ, len(self.rohdaten))
