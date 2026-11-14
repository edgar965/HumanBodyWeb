# -*- coding: utf-8 -*-
"""Meshgenesislinienflaeche — das Mesh eines Testjobs in der A-Pose, im Raum der Messlinien der Regler-KI (27.10.2026, Edgar zur Reihe „Messlinien“: „Was sollen diese Punkte? Wo sind die
Einstellungen, dass ich auch die Textur sehe und so weiter, sowie bei der Anzeige oben?“).

Gerechnet wird nichts Neues. Die Kette legt das Mesh in der A-Pose schon ab (`vorstufe/<nnnn>/apose_flaeche.npz`: Punkte, Dreiecke, Farbe je Punkt); die Wolke der KI
(`reglerki_linien.npz` → `p0_wolke`) sind die Punkte von `apose.npz`, ausgerichtet und auf die Figurhöhe des Rahmens gebracht (`Reglerkitest.eingang`). Die Abbildung dazwischen wird
hier aus diesen beiden Punktmengen bestimmt (Umeyama: Maßstab, Drehung, Verschiebung) und aufs Netz gelegt; ihr Rest steht im Kopf (edgar: median 0,14 mm, größter 0,53 mm —
`ProjektTemp/_wegwerf/regler_ki/linienflaeche_probe.py`). Das Netz wird auf einem Gitter von 3 mm zusammengefasst (edgar: 985.091 → 271.124 Punkte, 0,25 s).

Paket wie `Meshgenesislinien`: uint32 Länge des Kopfes · Kopf (JSON) · Blöcke `punkte` (f4), `dreiecke` (u4), `farbe` (u1, RGB je Punkt), jeder auf 4 aufgefüllt.

    Meshgenesislinienflaeche.paket(test_ordner) -> bytes | None
"""

import json
import logging
import struct
from pathlib import Path

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

logger = logging.getLogger('core')

__all__ = ['Meshgenesislinienflaeche']


class Meshgenesislinienflaeche:
    GITTER_M = 0.003
    _ablage = {}

    @staticmethod
    def _abbildung(quelle, ziel):
        """Ähnlichkeitsabbildung quelle → ziel (Umeyama) → (Maßstab, Drehung, Verschiebung, Rest je Punkt in m)."""
        mq, mz = quelle.mean(0), ziel.mean(0)
        a, c = quelle - mq, ziel - mz
        u, s, vt = Torchfeld.linalg_svd(c.T @ a / len(quelle))
        e = torch.eye(3, dtype=torch.float64, device='cuda')
        e[2, 2] = Torchfeld.sign(Torchfeld.linalg_det(u @ vt))
        r = u @ e @ vt
        m = float((s * Torchfeld.diag(e)).sum() / (a ** 2).sum(1).mean())
        t = mz - m * r @ mq
        return m, r, t, Torchfeld.linalg_norm(Torchfeld.feld((m * (r @ quelle.T)).T + t - ziel), dim=1)

    @classmethod
    def _gitter(cls, punkte, dreiecke, farbe):
        """Punkte in einer Gitterzelle zu ihrem Mittel zusammenfassen; Dreiecke, die dabei zu Kanten oder Punkten werden, fallen weg."""
        k = Torchfeld.astype(Torchfeld.floor(punkte / cls.GITTER_M), torch.int64)
        k -= Torchfeld.amin(k, 0)
        n1, n2 = int(k[:, 1].max()) + 1, int(k[:, 2].max()) + 1
        _u, inv = Torchfeld.unique((k[:, 0] * n1 + k[:, 1]) * n2 + k[:, 2], return_inverse=True)
        n, zahl = len(_u), Torchfeld.astype(Torchfeld.bincount(inv, minlength=len(_u)), torch.float64)

        def mittel(werte):
            return Torchfeld.stack([Torchfeld.bincount(inv, weights=werte[:, i], minlength=n) for i in range(3)], 1) / zahl[:, None]
        d = inv[dreiecke]
        gut = (d[:, 0] != d[:, 1]) & (d[:, 1] != d[:, 2]) & (d[:, 0] != d[:, 2])
        return Torchfeld.astype(mittel(punkte), torch.float32), Torchfeld.astype(d[gut], torch.uint32), Torchfeld.astype(Torchfeld.clip(Torchfeld.round(mittel(Torchfeld.astype(farbe, torch.float64))), 0, 255), torch.uint8)

    @staticmethod
    def _block(werte):
        roh = Torchfeld.als_bytes(Torchfeld.feld(werte))
        return roh + b'\0' * (-len(roh) % 4)

    @classmethod
    def paket(cls, ordner):
        linien = ordner / 'reglerki_linien.npz'
        form = ordner / 'form_reglerki.npz'
        if not Npztorch.da(linien) or not Npztorch.da(form):
            return None
        try:
            with Npztorch.lesen(form) as z:
                kette = Path(str(z['kette']))
            dateien = (linien, kette / 'apose.npz', kette / 'apose_flaeche.npz')
            schluessel = tuple((str(d), Npztorch.stat(d).st_mtime_ns) for d in dateien)
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Mesh unter den Messlinien %s: Kette nicht lesbar (%s)', ordner, fehler)
            return None
        if schluessel in cls._ablage:
            return cls._ablage[schluessel]
        try:
            with Npztorch.lesen(linien) as z:
                if 'p0_eingang_wolke' in z.files:
                    return cls._paket_eingang(ordner, kette, linien)
                name = 'p0_wolke' if 'p0_wolke' in z.files else 'p0_rig_wolke'
                wolke = Torchfeld.astype(z[name], torch.float64)
            with Npztorch.lesen(dateien[1]) as z:
                apose = Torchfeld.astype(z['punkte'], torch.float64)
            with Npztorch.lesen(dateien[2]) as z:
                punkte, dreiecke, farbe = Torchfeld.astype(z['punkte'], torch.float64), Torchfeld.astype(z['dreiecke'], torch.int64), z['farbe']
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Mesh unter den Messlinien %s nicht lesbar: %s', ordner, fehler)
            return None
        if len(apose) != len(wolke):
            logger.warning('Mesh unter den Messlinien %s: A-Pose (%d Punkte) und Wolke der KI (%d) gehören nicht zusammen', ordner, len(apose), len(wolke))
            return None
        m, r, t, rest = cls._abbildung(apose, wolke)
        p, d, f = cls._gitter((m * (r @ punkte.T)).T + t, dreiecke, farbe)
        kopf = {'kette': kette.name, 'gitter_mm': 1000 * cls.GITTER_M, 'punkte_vorher': len(punkte), 'massstab': round(m, 5),
                'rest_median_mm': round(1000 * float(Torchfeld.median(rest)), 3), 'rest_max_mm': round(1000 * float(rest.max()), 3)}
        paket = cls._packen(kopf, p, d, f)
        cls._ablage.clear()
        cls._ablage[schluessel] = paket
        return paket

    @classmethod
    def _packen(cls, kopf, p, d, f):
        kopf = dict(kopf, bloecke=[['punkte', 'f4', int(Torchfeld.groesse(p))], ['dreiecke', 'u4', int(Torchfeld.groesse(d))], ['farbe', 'u1', int(Torchfeld.groesse(f))]])
        roh = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        roh += b' ' * (-len(roh) % 4)
        return struct.pack('<I', len(roh)) + roh + cls._block(Torchfeld.astype(Torchfeld.feld(p), Torchfeld.dtype('<f4'))) + cls._block(Torchfeld.astype(Torchfeld.feld(d), Torchfeld.dtype('<u4'))) + cls._block(Torchfeld.astype(Torchfeld.feld(f), torch.uint8))

    @classmethod
    def _paket_eingang(cls, ordner, kette, linien):
        """Weg „eingang“ (27.10.2026 nachts): das Netz der Datei in der Pose des Eingangs, schon im Rahmen der Wolke und auf dem Gitter (`reglerki_eingang_netz.npz`,
        geschrieben von `meshgenesis_reglerki_test.py`) — keine Abbildung nötig. Gehört es zu einer anderen Kette: kein Mesh, Warnung."""
        datei = ordner / 'reglerki_eingang_netz.npz'
        try:
            schluessel = (str(linien), Npztorch.stat(linien).st_mtime_ns, str(datei), Npztorch.stat(datei).st_mtime_ns)
            if schluessel in cls._ablage:
                return cls._ablage[schluessel]
            with Npztorch.lesen(datei) as z:
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
