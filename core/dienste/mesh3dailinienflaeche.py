# -*- coding: utf-8 -*-
"""Mesh3dailinienflaeche — das Mesh eines Testjobs in der A-Pose, im Raum der Messlinien der Regler-KI (27.10.2026, Edgar zur Reihe „Messlinien“: „Was sollen diese Punkte? Wo sind die
Einstellungen, dass ich auch die Textur sehe und so weiter, sowie bei der Anzeige oben?“).

Gerechnet wird nichts Neues. Die Kette legt das Mesh in der A-Pose schon ab (`vorstufe/<nnnn>/apose_flaeche.npz`: Punkte, Dreiecke, Farbe je Punkt); die Wolke der KI
(`reglerki_linien.npz` → `p0_wolke`) sind die Punkte von `apose.npz`, ausgerichtet und auf die Figurhöhe des Rahmens gebracht (`Reglerkitest.eingang`). Die Abbildung dazwischen wird
hier aus diesen beiden Punktmengen bestimmt (Umeyama: Maßstab, Drehung, Verschiebung) und aufs Netz gelegt; ihr Rest steht im Kopf (edgar: median 0,14 mm, größter 0,53 mm —
`ProjektTemp/_wegwerf/regler_ki/linienflaeche_probe.py`). Das Netz wird auf einem Gitter von 3 mm zusammengefasst (edgar: 985.091 → 271.124 Punkte, 0,25 s).

Paket wie `Mesh3dailinien`: uint32 Länge des Kopfes · Kopf (JSON) · Blöcke `punkte` (f4), `dreiecke` (u4), `farbe` (u1, RGB je Punkt), jeder auf 4 aufgefüllt.

    Mesh3dailinienflaeche.paket(test_ordner) -> bytes | None
"""

import json
import logging
import struct
from pathlib import Path

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mesh3dailinienflaeche']


class Mesh3dailinienflaeche:
    GITTER_M = 0.003
    _ablage = {}

    @staticmethod
    def _abbildung(quelle, ziel):
        """Ähnlichkeitsabbildung quelle → ziel (Umeyama) → (Maßstab, Drehung, Verschiebung, Rest je Punkt in m)."""
        mq, mz = quelle.mean(0), ziel.mean(0)
        a, c = quelle - mq, ziel - mz
        u, s, vt = np.linalg.svd(c.T @ a / len(quelle))
        e = np.eye(3)
        e[2, 2] = np.sign(np.linalg.det(u @ vt))
        r = u @ e @ vt
        m = float((s * np.diag(e)).sum() / (a ** 2).sum(1).mean())
        t = mz - m * r @ mq
        return m, r, t, np.linalg.norm((m * (r @ quelle.T)).T + t - ziel, axis=1)

    @classmethod
    def _gitter(cls, punkte, dreiecke, farbe):
        """Punkte in einer Gitterzelle zu ihrem Mittel zusammenfassen; Dreiecke, die dabei zu Kanten oder Punkten werden, fallen weg."""
        k = np.floor(punkte / cls.GITTER_M).astype(np.int64)
        k -= k.min(0)
        n1, n2 = int(k[:, 1].max()) + 1, int(k[:, 2].max()) + 1
        _u, inv = np.unique((k[:, 0] * n1 + k[:, 1]) * n2 + k[:, 2], return_inverse=True)
        n, zahl = len(_u), np.bincount(inv, minlength=len(_u)).astype(np.float64)

        def mittel(werte):
            return np.stack([np.bincount(inv, weights=werte[:, i], minlength=n) for i in range(3)], 1) / zahl[:, None]
        d = inv[dreiecke]
        gut = (d[:, 0] != d[:, 1]) & (d[:, 1] != d[:, 2]) & (d[:, 0] != d[:, 2])
        return mittel(punkte).astype(np.float32), d[gut].astype(np.uint32), np.clip(np.rint(mittel(farbe.astype(np.float64))), 0, 255).astype(np.uint8)

    @staticmethod
    def _block(werte):
        roh = np.ascontiguousarray(werte).tobytes()
        return roh + b'\0' * (-len(roh) % 4)

    @classmethod
    def paket(cls, ordner):
        linien = ordner / 'reglerki_linien.npz'
        form = ordner / 'form_reglerki.npz'
        if not linien.is_file() or not form.is_file():
            return None
        try:
            with np.load(form) as z:
                kette = Path(str(z['kette']))
            dateien = (linien, kette / 'apose.npz', kette / 'apose_flaeche.npz')
            schluessel = tuple((str(d), d.stat().st_mtime_ns) for d in dateien)
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Mesh unter den Messlinien %s: Kette nicht lesbar (%s)', ordner, fehler)
            return None
        if schluessel in cls._ablage:
            return cls._ablage[schluessel]
        try:
            with np.load(linien) as z:
                if 'p0_eingang_wolke' in z.files:
                    return cls._paket_eingang(ordner, kette, linien)
                name = 'p0_wolke' if 'p0_wolke' in z.files else 'p0_rig_wolke'
                wolke = z[name].astype(np.float64)
            with np.load(dateien[1]) as z:
                apose = z['punkte'].astype(np.float64)
            with np.load(dateien[2]) as z:
                punkte, dreiecke, farbe = z['punkte'].astype(np.float64), z['dreiecke'].astype(np.int64), z['farbe']
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Mesh unter den Messlinien %s nicht lesbar: %s', ordner, fehler)
            return None
        if len(apose) != len(wolke):
            logger.warning('Mesh unter den Messlinien %s: A-Pose (%d Punkte) und Wolke der KI (%d) gehören nicht zusammen', ordner, len(apose), len(wolke))
            return None
        m, r, t, rest = cls._abbildung(apose, wolke)
        p, d, f = cls._gitter((m * (r @ punkte.T)).T + t, dreiecke, farbe)
        kopf = {'kette': kette.name, 'gitter_mm': 1000 * cls.GITTER_M, 'punkte_vorher': len(punkte), 'massstab': round(m, 5),
                'rest_median_mm': round(1000 * float(np.median(rest)), 3), 'rest_max_mm': round(1000 * float(rest.max()), 3)}
        paket = cls._packen(kopf, p, d, f)
        cls._ablage.clear()
        cls._ablage[schluessel] = paket
        return paket

    @classmethod
    def _packen(cls, kopf, p, d, f):
        kopf = dict(kopf, bloecke=[['punkte', 'f4', int(p.size)], ['dreiecke', 'u4', int(d.size)], ['farbe', 'u1', int(f.size)]])
        roh = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        roh += b' ' * (-len(roh) % 4)
        return struct.pack('<I', len(roh)) + roh + cls._block(np.asarray(p).astype('<f4')) + cls._block(np.asarray(d).astype('<u4')) + cls._block(np.asarray(f).astype(np.uint8))

    @classmethod
    def _paket_eingang(cls, ordner, kette, linien):
        """Weg „eingang“ (27.10.2026 nachts): das Netz der Datei in der Pose des Eingangs, schon im Rahmen der Wolke und auf dem Gitter (`reglerki_eingang_netz.npz`,
        geschrieben von `mesh3dai_reglerki_test.py`) — keine Abbildung nötig. Gehört es zu einer anderen Kette: kein Mesh, Warnung."""
        datei = ordner / 'reglerki_eingang_netz.npz'
        try:
            schluessel = (str(linien), linien.stat().st_mtime_ns, str(datei), datei.stat().st_mtime_ns)
            if schluessel in cls._ablage:
                return cls._ablage[schluessel]
            with np.load(datei) as z:
                if str(z['kette']) != str(kette):
                    logger.warning('Mesh unter den Messlinien %s: Netz der Pose des Eingangs gehört zur Kette %s, nicht %s', ordner, z['kette'], kette)
                    return None
                p, d, f = z['punkte'], z['dreiecke'], z['farbe']
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Mesh unter den Messlinien %s (Pose des Eingangs) nicht lesbar: %s', ordner, fehler)
            return None
        kopf = {'kette': kette.name, 'gitter_mm': 1000 * cls.GITTER_M, 'punkte_vorher': None, 'massstab': 1.0, 'rest_median_mm': 0.0, 'rest_max_mm': 0.0, 'pose': 'eingang'}
        paket = cls._packen(kopf, p, d, f)
        cls._ablage.clear()
        cls._ablage[schluessel] = paket
        return paket
