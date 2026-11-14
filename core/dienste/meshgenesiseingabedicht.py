# -*- coding: utf-8 -*-
"""Meshgenesiseingabedicht — die dichte Start-Wolke eines Tripo-Jobs als Binärpaket (21.10.2026, Edgar: „mach endlich die Tripo ansicht links besser! 2 Mio punkte!“).

Quelle `<Datensatz>/proben/<nr>/eingabe_dicht.npz` (`ProjektTemp/_wegwerf/meshgenesis_tripo_wolke_dicht.py`: 2 Mio. Punkte des Tripo-Netzes nach Fläche, so dicht wie der Eingang der Stufe 2).
Paket ohne Polster: uint32 Anzahl · float32 Einheit (m) · int16 Lage (n × 3) · uint8 Farbe sRGB (n × 3) · int8 Teil (n); die Seite liest es in `Meshgenesisseite._wolkeHolen`.
Fehlt die Datei: None — die Seite nimmt dann die 16.384 Punkte aus `eingabe.npz` (`Meshgenesisdaten.eingabe`).
"""

import struct

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

from .meshgenesisdatensatz import Meshgenesisdatensatz

__all__ = ['Meshgenesiseingabedicht']


class Meshgenesiseingabedicht:
    DATEI = 'eingabe_dicht.npz'

    @classmethod
    def paket(cls, job, nr):
        datei = Meshgenesisdatensatz.ordner(job['ordner']) / 'proben' / ('%04d' % int(nr)) / cls.DATEI
        if not Npztorch.da(datei):
            return None
        with Npztorch.lesen(datei) as z:
            lage = Torchfeld.feld(z['punkte_q'], dtype='<i2')
            farbe = Torchfeld.feld(z['farbe'], dtype=torch.uint8)
            teil = Torchfeld.feld(z['etikett'], dtype=torch.int8)
            einheit = float(z['einheit_m'])
        return struct.pack('<If', len(lage), einheit) + Torchfeld.als_bytes(lage) + Torchfeld.als_bytes(farbe) + Torchfeld.als_bytes(teil)
