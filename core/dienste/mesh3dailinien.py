# -*- coding: utf-8 -*-
"""Mesh3dailinien — die Messlinien der Regler-KI je Probe einer Prüfform als Binärpaket für die Seite „Formvariante“ (27.10.2026, Edgar: „Zeig mir den Input, den Output und die ganzen
Linien, die du errechnet hast“).

Gerechnet wird nicht hier, sondern auf der Karte (`A:/3DTools/mesh3dai/mesh3dai_reglerki_linien.py`): je Lauf `<Lauf>/linien/<Figur>.npz` (float16) und `linien/linien.json` (Zahlen).
Je Probe nr und Weg (mia, rig, eingang) und Figur (start, ergebnis, ziel): `p<nr>_<weg>_<was>_ort|ende|klasse|abstand`, dazu `p<nr>_wolke`, `p<nr>_etikett`, `p<nr>_rig_wolke`,
`p<nr>_eingang_wolke` (Weg „eingang“, 27.10.2026 nachts: die Wolke in der Pose des Eingangs, `mesh3dai_reglerki_eingang.Reglerkieingang`).

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, auf 4 aufgefüllt) · Blöcke in der Reihenfolge von `kopf['bloecke']` ([Name, Typ, Zahl der Werte]), jeder auf 4 aufgefüllt;
Typ 'f4' (float32: Punkte, Abstand) oder 'u1' (uint8: Klasse, Etikett + 1 bei `etikett`, damit −1 nicht stört).

    Mesh3dailinien.stand(lauf_ordner)                -> dict | None    linien.json
    Mesh3dailinien.paket(lauf_ordner, figur, nr)     -> bytes | None
    Mesh3dailinien.test(test_ordner, kennung)        -> bytes | None    Testjob: `reglerki_linien.npz` des Formschritts
"""

import json
import logging
import re
import struct

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mesh3dailinien']


class Mesh3dailinien:
    ORDNER = 'linien'
    NAME = re.compile(r'^[A-Za-z0-9_\-]+$')
    WEGE = ('mia', 'rig', 'eingang')
    WOLKEN = ('wolke', 'rig_wolke', 'eingang_wolke')
    WAS = ('start', 'ergebnis', 'ziel')
    TEILE = (('ort', 'f4'), ('ende', 'f4'), ('klasse', 'u1'), ('abstand', 'f4'))

    @classmethod
    def stand(cls, lauf):
        datei = lauf / cls.ORDNER / 'linien.json'
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @staticmethod
    def _block(werte, typ):
        roh = np.ascontiguousarray(werte, dtype='<f4' if typ == 'f4' else np.uint8).tobytes()
        return roh + b'\0' * (-len(roh) % 4)

    @classmethod
    def paket(cls, lauf, figur, nr):
        if not cls.NAME.match(str(figur)):
            return None
        return cls._paket(lauf / cls.ORDNER / ('%s.npz' % figur), cls.stand(lauf), figur, nr)

    @classmethod
    def test(cls, ordner, kennung):
        """Ein Testjob (27.10.2026): `reglerki_linien.npz` + `.json` im Testordner, geschrieben vom Formschritt der Kette (`mesh3dai_reglerki_test.py`), Probe 0, nur der Weg der Kette."""
        try:
            stand = json.loads((ordner / 'reglerki_linien.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return cls._paket(ordner / 'reglerki_linien.npz', stand, kennung, 0)

    @classmethod
    def _paket(cls, datei, stand, figur, nr):
        if not datei.is_file() or stand is None:
            return None
        vor = 'p%d_' % int(nr)
        bloecke, teile = [], []
        try:
            with np.load(datei) as z:
                if not any(vor + w in z.files for w in cls.WOLKEN):
                    return None
                for name, typ in [(vor + w, 'f4') for w in cls.WOLKEN] + [(vor + 'etikett', 'u1')]:
                    if name not in z.files:
                        continue
                    werte = z[name].astype(np.int16) + 1 if typ == 'u1' else z[name]
                    bloecke.append([name[len(vor):], typ, int(werte.size)])
                    teile.append(cls._block(werte.reshape(-1), typ))
                for weg in cls.WEGE:
                    for was in cls.WAS:
                        for teil, typ in cls.TEILE:
                            schluessel = '%s%s_%s_%s' % (vor, weg, was, teil)
                            if schluessel in z.files:
                                bloecke.append([schluessel[len(vor):], typ, int(z[schluessel].size)])
                                teile.append(cls._block(z[schluessel].reshape(-1), typ))
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Messlinien %s Probe %s nicht lesbar: %s', datei, nr, fehler)
            return None
        zahlen = (stand.get('formen') or {}).get(figur, {}).get(str(int(nr)), {})
        kopf = {'figur': figur, 'nr': int(nr), 'lauf': stand.get('lauf'), 'erzeugt': stand.get('erzeugt'), 'wege': stand.get('wege'), 'rig_gelernt': stand.get('rig_gelernt'),
                'rig': stand.get('rig'), 'zahlen': zahlen, 'bloecke': bloecke, 'test': stand.get('test'), 'weg': stand.get('weg'), 'wahrheit': stand.get('wahrheit', True)}
        roh = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        roh += b' ' * (-len(roh) % 4)
        return struct.pack('<I', len(roh)) + roh + b''.join(teile)
