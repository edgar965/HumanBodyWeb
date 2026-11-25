# -*- coding: utf-8 -*-
"""Meshgenesistesthaar — die Bewegung von Haar und Bart eines Teststücks für die Animation der Seite ausliefern (20.11.2026, Edgar: „Weg 2“ — Physik überall mit demselben Code).

Gerechnet wird beim MP4-Export (`Exportleistekettenlauf`, Schritt „haar“: `meshgenesis/meshgenesis_kleiderhaar_lauf.py`, bis 25.11.2026 im Job — die Leitsträhnen mit der Stoffsolver-`Straehnenbahn` auf den Kernen); abgelegt je
Stück und Bewegung unter `kleider_<g>/<weg>/<stück>/haar/<Kategorie>__<Name>.npz` mit Kopf `.json` (Fassung 2 wie der Stoff, `Meshgenesisteststoff`): `index` int32 (P,) und
`paket` (deflate der int16-Versätze an den P simulierten Punkten, NACH dem Häuten, mal `skala` Meter), dazu je Leitpunkt `ab` int32 (simulierter Punkt davor, −1 = gehäutet)
und `anteil` uint8 (·255).

Paket: uint32 Länge des Kopfs (JSON: `fassung, bvh, fps, jedes, skala, bilder, punkte, leitpunkte, netz, bewegt`), Kopf auf 4 Bytes aufgefüllt, `ab` int32 (leitpunkte), `anteil`
uint8 (leitpunkte) auf 4 Bytes aufgefüllt, `index` int32 (punkte), dann `paket`. Die Seite (`Meshgenesishaarfilm`) nimmt es nur, wenn `netz` (Leitsträhnen, Schritte) zu ihrem
Netz passt; sonst rechnet sie weiter ihre eigenen Pendel (`Lockenpendel`).
"""

import json
import logging
import struct

import torch

from .meshgenesisteststoff import Meshgenesisteststoff
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402
from KoerperKI_alle.torchfeld import Torchfeld  # noqa: E402

logger = logging.getLogger('core')

__all__ = ['Meshgenesistesthaar']


class Meshgenesistesthaar(Meshgenesisteststoff):
    ORDNER = 'haar'
    KOPF = ('fassung', 'bvh', 'fps', 'jedes', 'skala', 'bilder', 'punkte', 'leitpunkte', 'netz', 'bewegt')

    @staticmethod
    def _auf4(b):
        return b + b'\0' * ((-len(b)) % 4)

    @classmethod
    def paket(cls, kennung, geschlecht, weg, stueck, bvh):
        d = cls.dateien(kennung, geschlecht, weg, stueck, bvh)
        if d is None:
            return None
        kopf = json.loads(d[1].read_text(encoding='utf-8'))
        if kopf.get('fassung') != cls.FASSUNG or 'leitpunkte' not in kopf:
            logger.warning('Haar %s/%s (%s, Test %s): Ablage Fassung %s ohne Zuordnung je Leitpunkt — Schritt „haar“ neu rechnen', weg, stueck, bvh, kennung, kopf.get('fassung'))
            return None
        f = Npztorch.laden(d[0], felder=['index', 'paket', 'ab', 'anteil'])
        kopf = {k: kopf[k] for k in cls.KOPF if k in kopf}
        text = json.dumps(kopf).encode('utf-8')
        text += b' ' * ((-(4 + len(text))) % 4)
        return b''.join([struct.pack('<I', len(text)), text, Torchfeld.als_bytes(Torchfeld.astype(f['ab'], torch.int32)),
                         cls._auf4(Torchfeld.als_bytes(Torchfeld.astype(f['anteil'], torch.uint8))), Torchfeld.als_bytes(Torchfeld.astype(f['index'], torch.int32)),
                         Torchfeld.als_bytes(f['paket'])])
