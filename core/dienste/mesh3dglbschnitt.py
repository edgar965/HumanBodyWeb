# -*- coding: utf-8 -*-
"""Mesh3dglbschnitt — eine GLB ohne bestimmte Flächen schreiben, alles andere BYTEGLEICH (13.10.2026, „Netz bearbeiten“).

Warum nicht trimesh (`Trimesh.export`): geprüft an der Spiralballerina (`ProjektTemp/_wegwerf/mesh3d/netzschnitt_pruefen.py`, `textur_vergleich.py`) — trimesh kodiert die JPEG-Textur neu (2,66 → 0,95 MB, bei 77 % der
Pixel ein Unterschied, größter 58 von 255) und lässt die Erweiterung `KHR_materials_specular` und die Knotenstruktur fallen. Das Ausschneiden darf an Farbe und Material nichts ändern. Darum wird der Behälter selbst
umgeschrieben: das JSON-Stück bleibt, wie es ist (Knoten, Material, Erweiterungen, Bilder), und im BIN-Stück ändern sich nur die Puffer des einen Netzes — Indizes und Attribute (Punkt, Normale, UV, Farbe …) werden auf die
behaltenen Flächen verkleinert, Punkte, die keine Fläche mehr braucht, entfallen. Die Bildpuffer und alle anderen Puffer werden unverändert übernommen (nach dem Schreiben Byte für Byte verglichen).

Unterstützt: eine GLB mit EINEM Netz und EINEM Dreiecks-Primitiv (`mode` 4), eingebettetem Puffer, Attribute der Typen SCALAR/VEC2/VEC3/VEC4, keine Morphziele, keine „sparse“-Zugriffe. Alles andere ist ein `ValueError` mit dem
Grund — es wird nie etwas Halbes geschrieben. Die Reihenfolge der behaltenen Flächen und Punkte bleibt die der Quelle.
"""

import json
import os
import struct
from pathlib import Path

import numpy as np

__all__ = ['Mesh3dglbschnitt']


class Mesh3dglbschnitt:
    MAGIE = 0x46546C67  # 'glTF'
    JSON, BIN = 0x4E4F534A, 0x004E4942
    DTYPEN = {5120: '<i1', 5121: '<u1', 5122: '<i2', 5123: '<u2', 5125: '<u4', 5126: '<f4'}
    KOMPONENTEN = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}

    # ------------------------------------------------------------------ Behälter

    @classmethod
    def lesen(cls, pfad):
        """→ `(json, bin)` einer GLB; `ValueError`, wenn sie keine mit eingebettetem Puffer ist."""
        daten = Path(pfad).read_bytes()
        if len(daten) < 20 or struct.unpack_from('<I', daten, 0)[0] != cls.MAGIE:
            raise ValueError('Keine GLB-Datei: %s' % Path(pfad).name)
        kopf, binaer, aus = None, b'', 12
        while aus + 8 <= len(daten):
            laenge, art = struct.unpack_from('<II', daten, aus)
            stueck = daten[aus + 8:aus + 8 + laenge]
            if art == cls.JSON and kopf is None:
                kopf = json.loads(stueck.decode('utf-8'))
            elif art == cls.BIN and not binaer:
                binaer = bytes(stueck)
            aus += 8 + laenge
        if kopf is None:
            raise ValueError('Die GLB hat kein JSON-Stück')
        return kopf, binaer

    @classmethod
    def _bytes(cls, kopf, binaer):
        text = json.dumps(kopf, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        binaer += b'\x00' * (-len(binaer) % 4)
        gesamt = 12 + 8 + len(text) + 8 + len(binaer)
        return (struct.pack('<III', cls.MAGIE, 2, gesamt) + struct.pack('<II', len(text), cls.JSON) + text + struct.pack('<II', len(binaer), cls.BIN) + binaer)

    # ------------------------------------------------------------------ Zugriffe

    @classmethod
    def _zugriff(cls, kopf, binaer, nr):
        """Die Werte eines Zugriffs als (Anzahl, Komponenten)-Feld in der Typbreite der Datei."""
        z = kopf['accessors'][nr]
        if 'sparse' in z or 'bufferView' not in z:
            raise ValueError('Zugriff %d ist „sparse“ oder ohne Puffer — nicht unterstützt' % nr)
        if z['type'] not in cls.KOMPONENTEN:
            raise ValueError('Zugriffstyp %s nicht unterstützt' % z['type'])
        ansicht = kopf['bufferViews'][z['bufferView']]
        dtype, n = np.dtype(cls.DTYPEN[z['componentType']]), cls.KOMPONENTEN[z['type']]
        schritt = ansicht.get('byteStride') or dtype.itemsize * n
        anfang = ansicht.get('byteOffset', 0) + z.get('byteOffset', 0)
        return np.ndarray(shape=(z['count'], n), dtype=dtype, buffer=binaer, offset=anfang, strides=(schritt, dtype.itemsize))

    @classmethod
    def _primitiv(cls, kopf):
        netze = kopf.get('meshes') or []
        if len(netze) != 1 or len(netze[0].get('primitives') or []) != 1:
            raise ValueError('Die Datei enthält mehr als ein Netz oder Primitiv — nicht unterstützt')
        p = netze[0]['primitives'][0]
        if p.get('mode', 4) != 4 or 'indices' not in p or p.get('targets'):
            raise ValueError('Nur Dreiecksnetze mit Indizes ohne Morphziele werden unterstützt')
        buffers = kopf.get('buffers') or []
        if len(buffers) != 1 or 'uri' in buffers[0]:
            raise ValueError('Nur eine GLB mit einem eingebetteten Puffer wird unterstützt')
        return p

    @classmethod
    def flaechen(cls, pfad):
        """(F, 3) Indizes der Flächen in der Reihenfolge der Datei."""
        kopf, binaer = cls.lesen(pfad)
        return cls._zugriff(kopf, binaer, cls._primitiv(kopf)['indices']).reshape(-1, 3).astype(np.int64)

    @classmethod
    def punkte(cls, pfad):
        """(N, 3) float64 — die Punkte des einen Netzes in der Reihenfolge der Datei (14.10.2026, Gelenkfelder der Objekte: `Meshfigurobjektfelder`)."""
        kopf, binaer = cls.lesen(pfad)
        return cls._zugriff(kopf, binaer, cls._primitiv(kopf)['attributes']['POSITION']).astype(np.float64)

    # ------------------------------------------------------------------ Schneiden

    @classmethod
    def schreiben(cls, quelle, ziel, behalten):
        """`ziel` = `quelle` ohne die Flächen, für die `behalten` (F,) bool falsch ist → `(Flächen vorher, nachher, Punkte vorher, nachher)`. Schreibt über eine Nebendatei."""
        kopf, binaer = cls.lesen(quelle)
        p = cls._primitiv(kopf)
        faces = cls._zugriff(kopf, binaer, p['indices']).reshape(-1, 3).astype(np.int64)
        behalten = np.asarray(behalten, dtype=bool)
        if len(behalten) != len(faces):
            raise ValueError('Die Datei hat %d Flächen, die Auswahl %d' % (len(faces), len(behalten)))
        if not behalten.any():
            raise ValueError('Es bliebe keine Fläche übrig')
        neue_faces = faces[behalten]
        genutzt = np.unique(neue_faces)
        punkte_vorher = int(kopf['accessors'][p['attributes']['POSITION']]['count'])
        neu_nummer = np.full(punkte_vorher, -1, dtype=np.int64)
        neu_nummer[genutzt] = np.arange(len(genutzt))
        neue_faces = neu_nummer[neue_faces]
        ersetzt = {}
        for name, nr in p['attributes'].items():
            werte = cls._zugriff(kopf, binaer, nr)
            if len(werte) != punkte_vorher:
                raise ValueError('Attribut %s hat %d statt %d Werte' % (name, len(werte), punkte_vorher))
            ersetzt[nr] = np.ascontiguousarray(werte[genutzt])
        breit = len(genutzt) > 65535 or kopf['accessors'][p['indices']]['componentType'] == 5125
        ersetzt[p['indices']] = np.ascontiguousarray(neue_faces.reshape(-1, 1).astype('<u4' if breit else '<u2'))
        kopf, binaer = cls._ersetzen(kopf, binaer, ersetzt, p['attributes']['POSITION'], p['indices'])
        teil = Path(str(ziel) + '.teil')
        teil.write_bytes(cls._bytes(kopf, binaer))
        os.replace(teil, ziel)
        cls._pruefen(quelle, ziel, int(behalten.sum()), len(genutzt))
        return len(faces), int(behalten.sum()), punkte_vorher, int(len(genutzt))

    @classmethod
    def _ersetzen(cls, kopf, binaer, ersetzt, position, indizes):
        """Die Puffer der Zugriffe in `ersetzt` {Zugriff: Feld} durch die neuen Felder tauschen; jede andere Pufferansicht bleibt Byte für Byte. Die Nummern der Pufferansichten ändern sich nicht.
        `min`/`max` stehen nach dem Tausch dort, wo sie vorher standen, und immer bei `position` (glTF verlangt sie für POSITION); `indizes` bekommt die Komponentenbreite des neuen Feldes."""
        kopf = json.loads(json.dumps(kopf))
        ansichten = {}
        for nr, feld in ersetzt.items():
            z = kopf['accessors'][nr]
            if z['bufferView'] in ansichten:
                raise ValueError('Zwei Zugriffe teilen sich eine Pufferansicht — nicht unterstützt')
            teilen = [i for i, a in enumerate(kopf['accessors']) if a.get('bufferView') == z['bufferView'] and i != nr]
            if teilen:
                raise ValueError('Die Pufferansicht von Zugriff %d wird auch von Zugriff %s gebraucht — nicht unterstützt' % (nr, teilen))
            ansichten[z['bufferView']] = nr
            z['count'], z['byteOffset'] = int(len(feld)), 0
            if nr == indizes:
                z['componentType'] = {v: k for k, v in cls.DTYPEN.items()}[feld.dtype.str]
            if 'min' in z or 'max' in z or nr == position:
                z['min'] = [(float(v) if feld.dtype.kind == 'f' else int(v)) for v in feld.min(axis=0)]
                z['max'] = [(float(v) if feld.dtype.kind == 'f' else int(v)) for v in feld.max(axis=0)]
        neu = bytearray()
        for i, a in enumerate(kopf['bufferViews']):
            if i in ansichten:
                inhalt = ersetzt[ansichten[i]].tobytes()
                a.pop('byteStride', None)
            else:
                inhalt = binaer[a.get('byteOffset', 0):a.get('byteOffset', 0) + a['byteLength']]
            neu += b'\x00' * (-len(neu) % 4)
            a['byteOffset'], a['byteLength'] = len(neu), len(inhalt)
            neu += inhalt
        kopf['buffers'][0]['byteLength'] = len(neu)
        return kopf, bytes(neu)

    @classmethod
    def _pruefen(cls, quelle, ziel, flaechen, punkte):
        """Die geschriebene Datei neu lesen: Flächen- und Punktzahl, kein Index außerhalb, und jede NICHT ersetzte Pufferansicht (Bilder …) Byte für Byte wie in der Quelle."""
        try:
            k0, b0 = cls.lesen(quelle)
            k1, b1 = cls.lesen(ziel)
            p = cls._primitiv(k1)
            f = cls._zugriff(k1, b1, p['indices']).reshape(-1, 3)
            ersetzt = {k1['accessors'][nr]['bufferView'] for nr in list(p['attributes'].values()) + [p['indices']]}
            if len(f) != flaechen or int(f.max()) >= punkte or int(k1['accessors'][p['attributes']['POSITION']]['count']) != punkte:
                raise ValueError('Flächen- oder Punktzahl der geschriebenen Datei stimmt nicht')
            if len(k0['bufferViews']) != len(k1['bufferViews']):
                raise ValueError('Die Zahl der Pufferansichten hat sich verändert')
            for i, (a0, a1) in enumerate(zip(k0['bufferViews'], k1['bufferViews'], strict=True)):
                if i in ersetzt:
                    continue
                s0, s1 = a0.get('byteOffset', 0), a1.get('byteOffset', 0)
                if b0[s0:s0 + a0['byteLength']] != b1[s1:s1 + a1['byteLength']]:
                    raise ValueError('Pufferansicht %d (Bild oder Beilage) hat sich verändert' % i)
            if {k: v for k, v in k0.items() if k not in ('accessors', 'bufferViews', 'buffers')} != {k: v for k, v in k1.items() if k not in ('accessors', 'bufferViews', 'buffers')}:
                raise ValueError('Das JSON außerhalb der Puffer hat sich verändert')
        except ValueError:
            Path(ziel).unlink(missing_ok=True)
            raise
