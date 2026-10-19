# -*- coding: utf-8 -*-
"""Mesh3daiflaechennetz — das gemeinsame Anzeigenetz eines Mesh3D-AI-Jobs: Dreiecke, Teile, Hautgewichte, UV, Material je Dreieck und die Bilder (15.10.2026).

Edgar: „Warum ist beim Ziel bei Ursula so eine schlechte Ansicht zb bei Textur? die Haare sind nicht sichtbar, die Textur der Haut nicht usw." — die Flächen je Probe trugen nur
flache Teilfarben (keine UV, keine Bilder) und vom Haar nur die sichtbaren Bänder des ausgedünnten Datensatzes. Seit `flaeche.npz` Fassung 4 steht das Netz EINMAL je Job in
`<Job>/anzeige/` (`ProjektTemp/_wegwerf/mesh3dai_ursula_anzeigenetz.py`): das volle Netz mit allem Haar; je Probe nur noch Punkte und Außenfläche (`Mesh3daiflaeche`).

    Mesh3daiflaechennetz.laden(modell) -> dict | None      im Speicher, solange sich `netz.npz` und `materialien.json` nicht ändern
    Mesh3daiflaechennetz.paket(modell) -> bytes | None
    Mesh3daiflaechennetz.bild(modell, name) -> Path | None  nur `m<Zahl>.jpg` aus `anzeige/bilder/`

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, auf ein Vielfaches von 4 aufgefüllt: {fassung, punkte, dreiecke, haut, teile, teilfarben, materialien, ruhe}) · uint32 dreiecke (F·3)
· uint8 knochen (V·haut) · uint8 gewicht (V·haut) · uint8 etikett (F) · (auf 4 aufgefüllt) · float32 uv (V·2) · int16 material (F, −1 = ohne Bild) · mit `ruhe` im Kopf: (auf 4
aufgefüllt) float32 ruhe (V·3). Jeder Block beginnt auf einem Vielfachen von 4 (Sichten im Browser ohne Kopie).
`ruhe` (16.10.2026, `ProjektTemp/_wegwerf/mesh3dai_kinematik.py --netz`): die Punkte in der Ruhelage (Meter, Raum der Retarget-Rechnung, NICHT ausgerichtet) — damit häutet die Seite das Ergebnis eines
Laufs mit Daz-Winkeln genau so wie das Datenskript das Ziel (Hautmischung aus der Ruhelage), statt der Näherung aus den Rig-Punkten.
`verborgen` (19.10.2026, Trainingspaare: die Haut unter dem Anatomie-Stück, `ProjektTemp/_wegwerf/mesh3dai_paar_geograft.py`): Nummern der Dreiecke, die die Seite NICHT zeichnet — sie bleiben im Netz,
weil `Mesh3daianatomie` aus ihnen das Stück backt. Im Kopf die Zahl, am Ende (nach `ruhe`) uint32 verborgen (Zahl).
`normalen` (19.10.2026, Trainingspaare: die Normalen des Genesis-Exports, sonst knickt die Naht Haut ↔ Anatomie-Stück): im Kopf `normalen: true`, danach int8 (V·3, × 127, auf 4 aufgefüllt);
`anatomie_fertig` im Kopf: das Stück trägt schon die Karte der Charakter-Seite, die Seite backt nicht neu.
"""

import json
import logging
import re
import struct
import zipfile

import numpy as np

from .mesh3daidatensatz import Mesh3daidatensatz

logger = logging.getLogger('core')

__all__ = ['Mesh3daiflaechennetz']


class Mesh3daiflaechennetz:
    ORDNER = 'anzeige'
    FASSUNGEN = (1,)
    TEILE = ('koerper', 'anatomie', 'haar', 'slip', 'hose', 'hemd')
    _ablage = {}

    @classmethod
    def ordner(cls, modell):
        return Mesh3daidatensatz.ordner(modell) / cls.ORDNER

    @classmethod
    def _stand(cls, ordner):
        try:
            return tuple((p.name, p.stat().st_mtime_ns, p.stat().st_size) for p in (ordner / 'netz.npz', ordner / 'materialien.json'))
        except OSError:
            return None

    @classmethod
    def laden(cls, modell):
        """Die Arrays des Netzes und die Materialien oder `None` (fehlt oder unlesbar — mit Zeile im Log)."""
        ordner = cls.ordner(modell)
        stand = cls._stand(ordner)
        if stand is None:
            return None
        gemerkt = cls._ablage.get(modell)
        if gemerkt and gemerkt['stand'] == stand:
            return gemerkt['daten']
        try:
            with np.load(ordner / 'netz.npz') as z:
                fassung = int(z['fassung'])
                if fassung not in cls.FASSUNGEN:
                    logger.warning('Mesh3daiflaechennetz: %s trägt Fassung %s (bekannt: %s)', ordner, fassung, cls.FASSUNGEN)
                    return None
                daten = {k: z[k] for k in ('dreiecke', 'etikett', 'knochen', 'gewicht', 'uv', 'material', 'teilfarben')}
                if 'ruhe' in z.files and len(z['ruhe']) == len(daten['uv']):
                    daten['ruhe'] = z['ruhe'].astype(np.float32)
                if 'verborgen' in z.files:
                    daten['verborgen'] = z['verborgen'].astype(np.uint32)
                # Trainingspaare (19.10.2026): das Anatomie-Stück trägt schon die Karte der Charakter-Seite — `Mesh3daianatomie` backt dann nicht neu
                daten['anatomie_fertig'] = bool(z['anatomie_fertig']) if 'anatomie_fertig' in z.files else False
                if 'normalen' in z.files and len(z['normalen']) == len(daten['uv']):
                    daten['normalen'] = np.clip(np.round(z['normalen'].astype(np.float32) * 127), -127, 127).astype(np.int8)
            daten['materialien'] = json.loads((ordner / 'materialien.json').read_text(encoding='utf-8'))
            daten['fassung'] = fassung
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as fehler:
            logger.warning('Mesh3daiflaechennetz: %s nicht lesbar (%s)', ordner, fehler)
            return None
        cls._ablage[modell] = {'stand': stand, 'daten': daten}
        return daten

    @staticmethod
    def _auffuellen(daten):
        return daten + b'\0' * (-len(daten) % 4)

    @classmethod
    def paket(cls, modell):
        d = cls.laden(modell)
        if d is None:
            return None
        haut = int(d['knochen'].shape[1])
        kopf = {'fassung': d['fassung'], 'punkte': int(len(d['uv'])), 'dreiecke': int(len(d['dreiecke'])), 'haut': haut, 'teile': list(cls.TEILE),
                'teilfarben': d['teilfarben'].astype(int).tolist(),
                'materialien': [{'name': m.get('name'), 'bild': m.get('bild'), 'farbe': m.get('farbe')} for m in d['materialien']], 'ruhe': 'ruhe' in d,
                'verborgen': int(len(d.get('verborgen', ()))), 'anatomie_fertig': bool(d.get('anatomie_fertig')), 'normalen': 'normalen' in d}
        text = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        a = cls._auffuellen
        teile = [struct.pack('<I', len(text)), text, d['dreiecke'].astype('<u4').tobytes(),
                 a(d['knochen'].astype(np.uint8).tobytes()), a(d['gewicht'].astype(np.uint8).tobytes()), a(d['etikett'].astype(np.uint8).tobytes()),
                 d['uv'].astype('<f4').tobytes(), a(d['material'].astype('<i2').tobytes())]
        if 'ruhe' in d:
            teile.append(d['ruhe'].astype('<f4').tobytes())
        if len(d.get('verborgen', ())):
            teile.append(d['verborgen'].astype('<u4').tobytes())
        if 'normalen' in d:
            teile.append(a(d['normalen'].tobytes()))
        return b''.join(teile)

    @classmethod
    def bild(cls, modell, name):
        if not re.fullmatch(r'm\d{1,4}\.jpg', str(name)):
            return None
        pfad = cls.ordner(modell) / 'bilder' / name
        return pfad if pfad.is_file() else None
