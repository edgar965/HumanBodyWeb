# -*- coding: utf-8 -*-
"""Rundenglb — die GLB einer Runde von „2D3D Kleider" MIT Rig (01.10.2026): Körper, Kleider und Haar an EINEM Skin mit
den Knochen der Stellung, in der A-Pose.

Bis dahin schrieb `Kleidermodellglb` die Runde als lose Netze ohne Skelett — die Posenkopie der Bühne griff ins Leere,
getanzt wurde nur im Film. Der Schreiber ist der des Standmodells (`Standmodellglb`: Bindematrizen als Inverse der vollen
Weltlage, sRGB → linear, je Materialgruppe ein Knoten `<art>__<sorte>__<n>_g<k>__<slug>` für Pinsel und Schalter); hier
kommt nur der Körper der Runde dazu — der Käfig aus `Kleidermodellbau.koerper` (ohne UV, flach in der Hautfarbe), Knoten
`koerper__koerper__0` wie bisher.
"""

import numpy as np

from .standmodellglb import Standmodellglb

__all__ = ['Rundenglb']


class Rundenglb(Standmodellglb):
    """`Rundenglb(knochen).alle(teile)`, dann `schreiben(pfad)`."""

    UBYTE = 5121

    def _zugriff(self, werte, art, typ, ziel, grenzen=False):
        """Hautgewichte und Knochennummern je ein Byte (glTF erlaubt `WEIGHTS_0` normiert als UNSIGNED_BYTE, `JOINTS_0`
        als UNSIGNED_BYTE): mit float32/uint16 wuchs die GLB von `.51` von 25,5 auf 45,3 MB (576.309 Haarpunkte)."""
        if typ != 'VEC4' or art not in (self.FLOAT, self.USHORT):
            return super()._zugriff(werte, art, typ, ziel, grenzen)
        werte = np.asarray(werte)
        if art == self.USHORT:
            if len(werte) and int(werte.max()) > 255:
                return super()._zugriff(werte, art, typ, ziel, grenzen)
            roh = np.ascontiguousarray(werte, dtype=np.uint8)
            zugriff = {}
        else:                                           # Gewichte: auf 255 runden, Rest auf das größte (Summe 255)
            roh = np.round(np.clip(werte, 0.0, 1.0) * 255.0).astype(np.int64)
            rest = 255 - roh.sum(axis=1)
            groesstes = np.argmax(roh, axis=1)
            roh[np.arange(len(roh)), groesstes] += rest
            roh = np.ascontiguousarray(np.clip(roh, 0, 255), dtype=np.uint8)
            zugriff = {'normalized': True}
        zugriff.update({'bufferView': self._ablegen(roh.tobytes(), ziel), 'componentType': self.UBYTE,
                        'count': int(len(roh)), 'type': typ})
        self.gltf['accessors'].append(zugriff)
        return len(self.gltf['accessors']) - 1

    def alle(self, teile):
        for t in teile:
            if t.get('art') == 'koerper':
                self._netz('koerper__koerper__0', t['punkte'], t['dreiecke'], t.get('normalen'), None,
                           self._haut(t.get('haut'), len(t['punkte'])), faktor=t['farbe'], zweiseitig=False)
        self.teile(teile)
        return self
