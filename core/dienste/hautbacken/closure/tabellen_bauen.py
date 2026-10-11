# -*- coding: utf-8 -*-
"""Werkzeug: liest `intern/cycles/scene/shader.tables` (Blender v5.2.2) und schreibt die BSDF-Tabellen als `cycles_tabellen.npz` neben dieses Modul.

    python tabellen_bauen.py <pfad zu shader.tables>

Cycles legt diese Tabellen beim Szenenaufbau auf das Gerät (`scene/shader.cpp`: `ensure_bsdf_table`) und liest sie im Kernel (`kernel/util/lookup_table.h`). Sie sind Rechenvorgaben des
Principled BSDF (Albedo der Glanz-Closures, Energieerhaltung, Sheen-LTC) — hier unverändert als float32, in der Reihenfolge der Quelldatei. Neu bauen nur bei einer neuen Blender-Fassung.
Herkunft und Prüfsumme: `HERKUNFT.txt`.
"""

import hashlib
import re
import sys
from pathlib import Path

import numpy as np

NAMEN = {'table_ggx_E': 1024, 'table_ggx_Eavg': 32, 'table_ggx_glass_E': 4096, 'table_ggx_glass_Eavg': 256, 'table_ggx_glass_inv_E': 4096, 'table_ggx_glass_inv_Eavg': 256,
         'table_sheen_ltc': 3072, 'table_ggx_gen_schlick_ior_s': 4096, 'table_ggx_gen_schlick_s': 4096}


def lesen(pfad):
    text = Path(pfad).read_text(encoding='utf-8')
    aus = {}
    for name, anzahl in NAMEN.items():
        m = re.search(r'static const float %s\[(\d+)\] = \{(.*?)\};' % name, text, re.S)
        if not m or int(m.group(1)) != anzahl:
            raise SystemExit('Tabelle %s fehlt oder hat eine andere Größe (%s)' % (name, m.group(1) if m else '—'))
        werte = np.array([float(w.rstrip('f')) for w in re.findall(r'[-+0-9.eE]+f', m.group(2))], dtype=np.float32)
        if len(werte) != anzahl:
            raise SystemExit('Tabelle %s: %d Werte statt %d' % (name, len(werte), anzahl))
        aus[name[len('table_'):]] = werte
    return aus, hashlib.sha256(text.encode('utf-8')).hexdigest()


if __name__ == '__main__':
    tabellen, pruefsumme = lesen(sys.argv[1])
    ziel = Path(__file__).with_name('cycles_tabellen.npz')
    np.savez_compressed(ziel, **tabellen)
    Path(__file__).with_name('HERKUNFT.txt').write_text(
        'Tabellen der Glanz-Closures von Cycles — aus intern/cycles/scene/shader.tables, Blender v5.2.2 (github.com/blender/blender, Tag v5.2.2; Build 5.2.2 LTS, hash d13f752e3b9c).\n'
        'SHA-256 der Quelldatei: %s\nTabellen (float32): %s\nGebaut mit tabellen_bauen.py am 11.10.2026.\n' % (pruefsumme, ', '.join('%s[%d]' % (k, len(v)) for k, v in tabellen.items())),
        encoding='utf-8')
    print('geschrieben:', ziel, {k: len(v) for k, v in tabellen.items()})
