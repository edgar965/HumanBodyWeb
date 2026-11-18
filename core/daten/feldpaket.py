# -*- coding: utf-8 -*-
u"""Feldpaket — das Format von `gemeinsam/feldpaket.js` auf der Serverseite (18.11.2026, Haut-Maske auf der Karte, `Hautkarterechnung`).

Aufbau: `HBF1` · Länge des Kopfes (uint32, little endian) · Kopf (JSON: `geruest` mit `{"$f": i}` an der Stelle eines Feldes, `felder` mit Typ, Versatz,
Länge) · die Felder, jedes auf 8 Bytes ausgerichtet. Felder sind hier torch-Tensoren: `entpacken` legt sie auf `geraet`, `packen` holt sie EINMAL zur
CPU (die Bytes der Antwort).
"""
import ctypes
import gzip
import json
import struct

import torch

__all__ = ['Feldpaket']


class Feldpaket:
    MARKE = b'HBF1'
    TYPEN = {'Uint8Array': torch.uint8, 'Int8Array': torch.int8, 'Int16Array': torch.int16, 'Uint16Array': torch.uint16, 'Int32Array': torch.int32,
             'Uint32Array': torch.uint32, 'Float32Array': torch.float32, 'Float64Array': torch.float64}
    BREITE = {'Uint8Array': 1, 'Int8Array': 1, 'Int16Array': 2, 'Uint16Array': 2, 'Int32Array': 4, 'Uint32Array': 4, 'Float32Array': 4, 'Float64Array': 8}
    NAMEN = {v: k for k, v in TYPEN.items()}

    @staticmethod
    def _rund(n):
        return (n + 7) // 8 * 8

    @classmethod
    def entpacken(cls, roh, geraet='cuda'):
        u"""Bytes (auch gzip) → das Objekt mit Tensoren auf `geraet`."""
        if roh[:2] == b'\x1f\x8b':
            roh = gzip.decompress(roh)
        if roh[:4] != cls.MARKE:
            raise ValueError('kein Feldpaket')
        laenge = struct.unpack('<I', roh[4:8])[0]
        kopf = json.loads(roh[8:8 + laenge].decode('utf-8'))
        start = cls._rund(8 + laenge)
        puffer = bytearray(roh)
        felder = []
        for f in kopf['felder']:
            typ, breite, von = cls.TYPEN[f['typ']], cls.BREITE[f['typ']], start + f['versatz']
            if von + f['laenge'] * breite > len(puffer):
                raise ValueError('Feld %s passt nicht' % f['typ'])
            if not f['laenge']:
                felder.append(torch.zeros(0, dtype=typ, device=geraet))
                continue
            feld = torch.frombuffer(puffer, dtype=typ, count=f['laenge'], offset=von)  # cpu gewollt: Bytes der Anfrage, gleich danach zur Karte
            felder.append(feld.to(geraet))
        return cls._fuellen(kopf['geruest'], felder)

    @classmethod
    def packen(cls, objekt, mit_gzip=True):
        u"""Das Objekt (Tensoren, Listen, Dicts, Zahlen) → Bytes (mit gzip, wie `Feldpaket.gzip`)."""
        felder = []
        geruest = cls._geruest(objekt, felder)
        roh = [f.contiguous().cpu() for f in felder]                 # cpu gewollt: die Bytes der Antwort
        liste, versatz = [], 0
        for f in roh:
            liste.append({'typ': cls.NAMEN[f.dtype], 'versatz': versatz, 'laenge': int(f.numel())})
            versatz += cls._rund(f.numel() * f.element_size())
        kopf = json.dumps({'geruest': geruest, 'felder': liste}, separators=(',', ':')).encode('utf-8')
        start = cls._rund(8 + len(kopf))
        aus = bytearray(start + versatz)
        aus[:4] = cls.MARKE
        aus[4:8] = struct.pack('<I', len(kopf))
        aus[8:8 + len(kopf)] = kopf
        for f, e in zip(roh, liste, strict=True):
            if f.numel():
                daten = ctypes.string_at(f.data_ptr(), f.numel() * f.element_size())
                aus[start + e['versatz']:start + e['versatz'] + len(daten)] = daten
        return gzip.compress(bytes(aus), compresslevel=1) if mit_gzip else bytes(aus)

    @classmethod
    def _geruest(cls, wert, felder):
        if isinstance(wert, torch.Tensor):
            felder.append(wert.reshape(-1))
            return {'$f': len(felder) - 1}
        if isinstance(wert, (list, tuple)):
            return [cls._geruest(w, felder) for w in wert]
        if isinstance(wert, dict):
            return {k: cls._geruest(w, felder) for k, w in wert.items()}
        return wert

    @classmethod
    def _fuellen(cls, wert, felder):
        if isinstance(wert, list):
            return [cls._fuellen(w, felder) for w in wert]
        if isinstance(wert, dict):
            if isinstance(wert.get('$f'), int) and len(wert) == 1:
                return felder[wert['$f']]
            return {k: cls._fuellen(w, felder) for k, w in wert.items()}
        return wert
