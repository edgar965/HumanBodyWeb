# -*- coding: utf-8 -*-
"""Mesh3daieingabedicht — die dichte Start-Wolke eines Tripo-Jobs als Binärpaket (21.10.2026, Edgar: „mach endlich die Tripo ansicht links besser! 2 Mio punkte!“).

Quelle `<Datensatz>/proben/<nr>/eingabe_dicht.npz` (`ProjektTemp/_wegwerf/mesh3dai_tripo_wolke_dicht.py`: 2 Mio. Punkte des Tripo-Netzes nach Fläche, so dicht wie der Eingang der Stufe 2).
Paket ohne Polster: uint32 Anzahl · float32 Einheit (m) · int16 Lage (n × 3) · uint8 Farbe sRGB (n × 3) · int8 Teil (n); die Seite liest es in `Mesh3daiseite._wolkeHolen`.
Fehlt die Datei: None — die Seite nimmt dann die 16.384 Punkte aus `eingabe.npz` (`Mesh3daidaten.eingabe`).
"""

import struct

import numpy as np

from .mesh3daidatensatz import Mesh3daidatensatz

__all__ = ['Mesh3daieingabedicht']


class Mesh3daieingabedicht:
    DATEI = 'eingabe_dicht.npz'

    @classmethod
    def paket(cls, job, nr):
        datei = Mesh3daidatensatz.ordner(job['ordner']) / 'proben' / ('%04d' % int(nr)) / cls.DATEI
        if not datei.is_file():
            return None
        with np.load(datei) as z:
            lage = np.ascontiguousarray(z['punkte_q'], dtype='<i2')
            farbe = np.ascontiguousarray(z['farbe'], dtype=np.uint8)
            teil = np.ascontiguousarray(z['etikett'], dtype=np.int8)
            einheit = float(z['einheit_m'])
        return struct.pack('<If', len(lage), einheit) + lage.tobytes() + farbe.tobytes() + teil.tobytes()
