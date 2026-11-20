# -*- coding: utf-8 -*-
"""Meshgenesisteststoff — der Stoff eines Teststücks für die Animation der Seite ausliefern (19.11.2026, Kleiderbibliothek als Stoff).

Gerechnet wird in der Kette (Schritt „stoff“, `meshgenesis/meshgenesis_kleiderstoff_lauf.py`, Stoffsolver mit Kernmotor); abgelegt je Stück und Bewegung unter
`kleider_<g>/<weg>/<stück>/stoff/<Kategorie>__<Name>.npz` mit Kopf `.json`. Fassung 2 (19.11.2026 abends, 126 → 26,8 MB am Mieder): `index` int32 (M,) — Spalte des Punkts unter den bewegten
oder −1 (folgt der Häutung) — und `paket` = deflate (zlib) der int16-Versätze (Bilder, bewegte Punkte, 3) in der Ruhelage, mal `skala` Meter, von Bild zu Bild differenziert. Eine Ablage einer
anderen Fassung wird nicht ausgeliefert (Warnung im Log; die Seite zeigt das Stück dann gehäutet) — gegen Daten eines alten Laufs (Regel „Zwischenspeicher tragen den Namen ihrer Fassung“).

Paket: uint32 Länge des Kopfs (JSON, UTF-8: `fassung, bvh, fps, jedes, skala, bilder, punkte, bewegt`), Kopf, auf 4 Bytes aufgefüllt, `index` als int32 little-endian, dann `paket` wie
abgelegt. Die Seite (`Meshgenesisstoffkleid`) entpackt mit `DecompressionStream('deflate')`, summiert die Differenzen einmal auf und setzt je Bild Ruhelage + Versatz als Bindelage des
`SkinnedMesh`; ohne Datei (None) bleibt das Stück gehäutet.
"""

import json
import logging
import re
import struct

import torch

from .meshgenesistestkleider import Meshgenesistestkleider
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402
from KoerperKI_alle.torchfeld import Torchfeld  # noqa: E402

logger = logging.getLogger('core')

__all__ = ['Meshgenesisteststoff']


class Meshgenesisteststoff:
    TEIL = re.compile(r'^[A-Za-z0-9_\-]+$')
    FASSUNG = 2                     # = `Kleiderstofflauf.FASSUNG`
    ORDNER = 'stoff'                # `Meshgenesistesthaar`: 'haar'
    KOPF = ('fassung', 'bvh', 'fps', 'jedes', 'skala', 'bilder', 'punkte', 'bewegt')

    @classmethod
    def name(cls, bvh):
        u"""'Kategorie/Name' (Wahl der Leiste) → 'Kategorie__Name' oder None, wenn ein Teil nicht passt."""
        teile = str(bvh or '').replace('\\', '/').split('/')
        if len(teile) != 2 or not all(cls.TEIL.match(t) for t in teile):
            return None
        return '%s__%s' % tuple(teile)

    @classmethod
    def dateien(cls, kennung, geschlecht, weg, stueck, bvh):
        u"""(Feld-Datei, Kopf-Datei) oder None — alle Teile kommen aus der Adresse und werden geprüft."""
        name = cls.name(bvh)
        if name is None or Meshgenesistestkleider.stueck_ordner(kennung, geschlecht, weg, stueck) is None:
            return None
        ordner = Meshgenesistestkleider.ordner(kennung, geschlecht) / weg / stueck / cls.ORDNER
        feld, kopf = ordner / (name + '.npz'), ordner / (name + '.json')
        if not kopf.is_file() or not Npztorch.da(feld):
            return None
        return feld, kopf

    @classmethod
    def paket(cls, kennung, geschlecht, weg, stueck, bvh):
        d = cls.dateien(kennung, geschlecht, weg, stueck, bvh)
        if d is None:
            return None
        kopf = json.loads(d[1].read_text(encoding='utf-8'))
        if kopf.get('fassung') != cls.FASSUNG:
            logger.warning('Stoff %s/%s (%s, Test %s): Ablage Fassung %s, ausgeliefert wird nur Fassung %d — Schritt „stoff“ neu rechnen', weg, stueck, bvh, kennung, kopf.get('fassung'),
                           cls.FASSUNG)
            return None
        felder = Npztorch.laden(d[0], felder=['index', 'paket'])
        kopf = {k: kopf[k] for k in cls.KOPF if k in kopf}
        text = json.dumps(kopf).encode('utf-8')
        text += b' ' * ((-(4 + len(text))) % 4)                               # `index` (int32) beginnt auf 4 Bytes
        return b''.join([struct.pack('<I', len(text)), text, Torchfeld.als_bytes(Torchfeld.astype(felder['index'], torch.int32)), Torchfeld.als_bytes(felder['paket'])])
