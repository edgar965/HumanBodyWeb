# -*- coding: utf-8 -*-
"""Mesh3daitestanpassung — die erste Zeile der Testseite von Mesh3D-AI: die Genesis-Figur, rein an das Netz angepasst, ohne KI (28.10.2026, Edgar: „Mache in deinem Jobview auch eine erste
Zeile mit der reinen Anpassung des Genesis Modells an das Mesh. Also ohne KI.“).

Gerechnet wird hier nichts. `mesh3dai/mesh3dai_meshanpassung.py` (Einpassung `Genesis9.meshgenesis.G9meshgenesis`) legt im Testordner `meshanpassung/meshanpassung.npz` (Figur, Netz zur
Anzeige, Kette) und `meshanpassung.json` (Bericht) ab. Gehört die Anpassung nicht mehr zur jüngsten Kette des Tests (`vorstufe/*/apose.npz`), steht `veraltet` im Kopf — gezeigt wird sie
trotzdem, mit dem Hinweis (`artefakte-benennen`: nie still die Datei eines anderen Laufs).

Paket wie `Mesh3dailinienflaeche`: uint32 Länge des Kopfes · Kopf (JSON) · Blöcke `figur` (f4), `figur_dreiecke` (u4), `netz_punkte` (f4), `netz_dreiecke` (u4), `netz_farbe` (u1, RGB je
Punkt), jeder auf 4 aufgefüllt. Dazu die Genesis-Haut (28.10.2026 abends, Edgar: „kannst du das eingepasste Genesis auch mit Textur zeigen?“): `uv` (f4), `uv_ursprung` (u4, Käfigpunkt je
UV-Punkt), `uv_dreiecke` (u4, nach Material) aus `G9basisnetz`, im Kopf `textur` = je Materialgruppe Indexbereich und Albedo der Startfigur (Pfad der Daz-Bibliothek).

    Mesh3daitestanpassung.paket(test_ordner) -> bytes | None
"""

import json
import logging
import struct
from pathlib import Path

import numpy as np

from .mesh3dailinienflaeche import Mesh3dailinienflaeche

logger = logging.getLogger('core')

__all__ = ['Mesh3daitestanpassung']


class Mesh3daitestanpassung:
    ORDNER = 'meshanpassung'
    BLOECKE = (('figur', 'f4'), ('figur_dreiecke', 'u4'), ('netz_punkte', 'f4'), ('netz_dreiecke', 'u4'), ('netz_farbe', 'u1'))
    #: aus dem Bericht in den Kopf (ohne `verlauf` und die Regler selbst)
    KOPF = ('verfahren', 'start', 'kette', 'erzeugt', 'sekunden', 'sekunden_einpassung', 'masse', 'einpassung', 'innen_stufe', 'lage', 'versatz_mm', 'ziel', 'abgleich', 'ruhelage_mm', 'abnahme', 'versatz_art', 'innen', 'pruefung',
            'mindest_mm', 'kopf_frei', 'anatomie')
    TEXTUR_BLOECKE = (('uv', 'f4'), ('uv_ursprung', 'u4'), ('uv_dreiecke', 'u4'))
    #: das Anatomie-Stück der Startfigur am eingepassten Becken (`Mesh3daimeshanatomie`, seit 28.10.2026 abends; ältere Ergebnisse haben es nicht)
    #: `anatomie_loch` (seit 28.10.2026 nachts): die Dreiecke der Figur unter dem Stück, Daz versteckt sie (`Mesh3daimeshanatomie.figurloch`)
    ANATOMIE_BLOECKE = (('anatomie_punkte', 'f4'), ('anatomie_dreiecke', 'u4'), ('anatomie_loch', 'u4'))
    _ablage = {}

    @staticmethod
    def textur(start):
        """Die UV-Teilung des Käfigs (`G9basisnetz`: je UV-Punkt sein Käfigpunkt `ursprung`, UV, Dreiecke nach Material) und je Materialgruppe die Albedo der Startfigur
        (`G9charaktere.hautbilder`, wie `G9koerpernetz.gruppen_mit_bildern`) → (Blöcke, Gruppen); ohne Daz-Bibliothek (None, None)."""
        try:
            from Genesis9.basisnetz import G9basisnetz
            from Genesis9.charaktere import G9charaktere
            from Genesis9.koerpernetz import G9koerpernetz
            basis = G9basisnetz.holen()
            gruppen = G9koerpernetz.gruppen_mit_bildern(basis.gruppen, G9charaktere.hautbilder(G9charaktere.eintrag(start or 'basis') or {}))
        except (OSError, ValueError, KeyError, ImportError) as fehler:
            logger.warning('Genesis-Anpassung: Haut der Startfigur %s nicht lesbar: %s', start, fehler)
            return None, None
        bloecke = {'uv': basis.uv, 'uv_ursprung': basis.ursprung, 'uv_dreiecke': basis.dreiecke}
        return bloecke, [{'name': g['name'], 'index_ab': int(g['index_ab']), 'index_anzahl': int(g['index_anzahl']), 'albedo': (g.get('bilder') or {}).get('albedo')}
                         for g in gruppen]

    @staticmethod
    def anatomie_farbe(kaefig, haut, gruppen):
        """Farbe je Punkt des Anatomie-Stücks (28.10.2026 nachts; vorher eine Farbe, im Bild heller als die Haut daneben): die Albedo der Startfigur an der UV seines nächsten Käfigpunkts
        (`anatomie_kaefig`, `Mesh3daimeshanatomie`; ein UV-Punkt je Käfigpunkt — über die UV selbst verschmierte die Naht Rumpf/Beine), linear wie Threes Punktfarben → (M, 3) f4 oder None."""
        from PIL import Image
        from Genesis9.pfade import G9pfade
        uv, urs, dr = np.asarray(haut['uv']), np.asarray(haut['uv_ursprung']), np.asarray(haut['uv_dreiecke']).reshape(-1)
        gruppe = np.full(len(uv), -1)
        for i, g in enumerate(gruppen):
            gruppe[dr[g['index_ab']:g['index_ab'] + g['index_anzahl']]] = i
        erster = np.full(int(urs.max()) + 1, -1)
        erster[urs[::-1]] = np.arange(len(urs))[::-1]
        u = erster[np.asarray(kaefig, dtype=np.int64)]
        farbe = np.full((len(u), 3), 0.5, dtype=np.float32)
        for i in np.unique(gruppe[u]):
            pfad = G9pfade.finden(gruppen[i]['albedo']) if i >= 0 and gruppen[i].get('albedo') else None
            if pfad is None:
                continue
            bild = np.asarray(Image.open(pfad).convert('RGB'))
            h, w = bild.shape[:2]
            wahl = gruppe[u] == i
            t = uv[u[wahl]] % 1.0
            px = bild[((1.0 - t[:, 1]) * (h - 1)).round().astype(np.int64), (t[:, 0] * (w - 1)).round().astype(np.int64)] / 255.0
            farbe[wahl] = np.where(px <= 0.04045, px / 12.92, ((px + 0.055) / 1.055) ** 2.4)
        return farbe

    @classmethod
    def paket(cls, test):
        ordner = Path(test) / cls.ORDNER
        npz, bericht = ordner / 'meshanpassung.npz', ordner / 'meshanpassung.json'
        try:
            schluessel = (str(npz), npz.stat().st_mtime_ns, bericht.stat().st_mtime_ns)
        except OSError:
            return None
        if schluessel in cls._ablage:
            return cls._ablage[schluessel]
        try:
            b = json.loads(bericht.read_text(encoding='utf-8'))
            with np.load(npz) as z:
                felder = {name: z[name] for name, _typ in cls.BLOECKE + cls.ANATOMIE_BLOECKE if name in z.files or name not in dict(cls.ANATOMIE_BLOECKE)}
                kette = Path(str(z['kette']))
                anatomie_kaefig = z['anatomie_kaefig'] if 'anatomie_kaefig' in z.files else None
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Genesis-Anpassung des Tests %s nicht lesbar: %s', test, fehler)
            return None
        ketten = sorted(p.parent for p in (Path(test) / 'vorstufe').glob('*/apose.npz'))
        kopf = {k: b.get(k) for k in cls.KOPF}
        kopf.update(stufe1=(b.get('stufe1') or {}).get('masse'), regler=len(b.get('regler') or {}), mesh_regler=len(b.get('mesh_regler') or {}), test=Path(test).name,
                    veraltet=bool(ketten) and ketten[-1] != kette, juengste_kette=ketten[-1].name if ketten else None)
        bloecke = list(cls.BLOECKE) + [blk for blk in cls.ANATOMIE_BLOECKE if blk[0] in felder]
        haut, kopf['textur'] = cls.textur(b.get('start'))
        if haut is not None:
            felder.update(haut)
            bloecke += cls.TEXTUR_BLOECKE
            if anatomie_kaefig is not None and 'anatomie_punkte' in felder:
                try:
                    felder['anatomie_farbe'] = cls.anatomie_farbe(anatomie_kaefig, haut, kopf['textur'])
                    bloecke.append(('anatomie_farbe', 'f4'))
                except (OSError, ValueError, IndexError) as fehler:
                    logger.warning('Genesis-Anpassung: Farbe der Anatomie nicht lesbar: %s', fehler)
        kopf['bloecke'] = [[name, typ, int(felder[name].size)] for name, typ in bloecke]
        roh = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        roh += b' ' * (-len(roh) % 4)
        paket = struct.pack('<I', len(roh)) + roh + b''.join(Mesh3dailinienflaeche._block(np.asarray(felder[name]).astype('<' + typ if typ != 'u1' else np.uint8))
                                                            for name, typ in bloecke)
        cls._ablage.clear()
        cls._ablage[schluessel] = paket
        return paket
