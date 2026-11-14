# -*- coding: utf-8 -*-
"""Meshgenesisflaechennetz — das gemeinsame Anzeigenetz eines Mesh-Genesis-Jobs: Dreiecke, Teile, Hautgewichte, UV, Material je Dreieck und die Bilder (15.10.2026).

Edgar: „Warum ist beim Ziel bei Ursula so eine schlechte Ansicht zb bei Textur? die Haare sind nicht sichtbar, die Textur der Haut nicht usw." — die Flächen je Probe trugen nur
flache Teilfarben (keine UV, keine Bilder) und vom Haar nur die sichtbaren Bänder des ausgedünnten Datensatzes. Seit `flaeche.npz` Fassung 4 steht das Netz EINMAL je Job in
`<Job>/anzeige/` (`ProjektTemp/_wegwerf/meshgenesis_ursula_anzeigenetz.py`): das volle Netz mit allem Haar; je Probe nur noch Punkte und Außenfläche (`Meshgenesisflaeche`).

    Meshgenesisflaechennetz.laden(modell) -> dict | None      im Speicher, solange sich `netz.npz` und `materialien.json` nicht ändern
    Meshgenesisflaechennetz.paket(modell) -> bytes | None
    Meshgenesisflaechennetz.bild(modell, name) -> Path | None  nur `m<Zahl>.jpg` aus `anzeige/bilder/`

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, auf ein Vielfaches von 4 aufgefüllt: {fassung, punkte, dreiecke, haut, teile, teilfarben, materialien, ruhe}) · uint32 dreiecke (F·3)
· uint8 knochen (V·haut) · uint8 gewicht (V·haut) · uint8 etikett (F) · (auf 4 aufgefüllt) · float32 uv (V·2) · int16 material (F, −1 = ohne Bild) · mit `ruhe` im Kopf: (auf 4
aufgefüllt) float32 ruhe (V·3). Jeder Block beginnt auf einem Vielfachen von 4 (Sichten im Browser ohne Kopie).
`ruhe` (16.10.2026, `ProjektTemp/_wegwerf/meshgenesis_kinematik.py --netz`): die Punkte in der Ruhelage (Meter, Raum der Retarget-Rechnung, NICHT ausgerichtet) — damit häutet die Seite das Ergebnis eines
Laufs mit Daz-Winkeln genau so wie das Datenskript das Ziel (Hautmischung aus der Ruhelage), statt der Näherung aus den Rig-Punkten.
`verborgen` (19.10.2026, Trainingspaare: die Haut unter dem Anatomie-Stück, `ProjektTemp/_wegwerf/meshgenesis_paar_geograft.py`): Nummern der Dreiecke, die die Seite NICHT zeichnet — sie bleiben im Netz,
weil `Meshgenesisanatomie` aus ihnen das Stück backt. Im Kopf die Zahl, am Ende (nach `ruhe`) uint32 verborgen (Zahl).
`normalen` (19.10.2026, Trainingspaare: die Normalen des Genesis-Exports, sonst knickt die Naht Haut ↔ Anatomie-Stück): im Kopf `normalen: true`, danach int8 (V·3, × 127, auf 4 aufgefüllt);
`anatomie_fertig` im Kopf: das Stück trägt schon die Karte der Charakter-Seite, die Seite backt nicht neu.
`punktfarbe` (21.10.2026 abends, Weg g Fassung 3 von Mesh-Genesis: Farbe je Punkt aus dem Eingang): im Kopf `punktfarbe: true`, danach uint8 sRGB (V·3, auf 4 aufgefüllt); die Dreiecke tragen Material −1.
`stufe` 1 (09.11.2026, `paket(…, stufe=1)`, `Meshgenesisflaechennetzfein`): der Körper auf Netzstufe 1; im Kopf `stufe`, `kaefig_dreiecke` (Dreiecke des Netzes auf dem Käfig) und `eltern: true`, danach
uint32 eltern (F, Käfigdreieck je Dreieck — Masken des Käfigs gelten so für die Kinder); mit `matrix` = [Zeilen, nnz] im Kopf die Unterteilungsmatrix der Körperpunkte: uint32 Zeilenanfänge
(Zeilen + 1), uint16 Käfigpunkte (nnz, auf 4 aufgefüllt), float32 Gewichte (nnz).
"""

import json
import logging
import re
import struct
import zipfile

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

from .meshgenesisdatensatz import Meshgenesisdatensatz

logger = logging.getLogger('core')

__all__ = ['Meshgenesisflaechennetz']


class Meshgenesisflaechennetz:
    ORDNER = 'anzeige'
    FASSUNGEN = (1,)
    TEILE = ('koerper', 'anatomie', 'haar', 'slip', 'hose', 'hemd', 'augen')         # `augen` seit 24.10.2026 (Figuren der Tests, `Ursula.TEILE`)
    MATERIALWERTE = ('rauheit', 'glanz', 'metall', 'relief')
    _ablage = {}

    @classmethod
    def ordner(cls, modell):
        return Meshgenesisdatensatz.ordner(modell) / cls.ORDNER

    @classmethod
    def _stand(cls, ordner):
        try:
            return tuple((p.name, Npztorch.stat(p).st_mtime_ns, Npztorch.stat(p).st_size) for p in (ordner / 'netz.npz', ordner / 'materialien.json'))
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
            with Npztorch.lesen(ordner / 'netz.npz') as z:
                fassung = int(z['fassung'])
                if fassung not in cls.FASSUNGEN:
                    logger.warning('Meshgenesisflaechennetz: %s trägt Fassung %s (bekannt: %s)', ordner, fassung, cls.FASSUNGEN)
                    return None
                daten = {k: z[k] for k in ('dreiecke', 'etikett', 'knochen', 'gewicht', 'uv', 'material', 'teilfarben')}
                if 'ruhe' in z.files and len(z['ruhe']) == len(daten['uv']):
                    daten['ruhe'] = Torchfeld.astype(z['ruhe'], torch.float32)
                if 'verborgen' in z.files:
                    daten['verborgen'] = Torchfeld.astype(z['verborgen'], torch.uint32)
                # Trainingspaare (19.10.2026): das Anatomie-Stück trägt schon die Karte der Charakter-Seite — `Meshgenesisanatomie` backt dann nicht neu
                daten['anatomie_fertig'] = bool(z['anatomie_fertig']) if 'anatomie_fertig' in z.files else False
                if 'normalen' in z.files and len(z['normalen']) == len(daten['uv']):
                    daten['normalen'] = Torchfeld.astype(Torchfeld.clip(Torchfeld.round(Torchfeld.astype(z['normalen'], torch.float32) * 127), -127, 127), torch.int8)
                if 'punktfarbe' in z.files and len(z['punktfarbe']) == len(daten['uv']):
                    daten['punktfarbe'] = Torchfeld.astype(z['punktfarbe'], torch.uint8)
            daten['materialien'] = json.loads((ordner / 'materialien.json').read_text(encoding='utf-8'))
            daten['fassung'] = fassung
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as fehler:
            logger.warning('Meshgenesisflaechennetz: %s nicht lesbar (%s)', ordner, fehler)
            return None
        cls._ablage[modell] = {'stand': stand, 'daten': daten}
        return daten

    @staticmethod
    def _auffuellen(daten):
        return daten + b'\0' * (-len(daten) % 4)

    @classmethod
    def paket(cls, modell, stufe=0, matrix=False):
        """`stufe` 1 (09.11.2026, Testseiten, `Meshgenesisflaechennetzfein`): der Körper auf Netzstufe 1, dazu `eltern` (Käfigdreieck je Dreieck, uint32) und mit `matrix` die Unterteilungsmatrix
        der Körperpunkte (CSR: uint32 Zeilenanfänge, uint16 Käfigpunkte, float32 Gewichte). Ist der Körper nicht der Genesis-Käfig, bleibt es Stufe 0 (`stufe` im Kopf sagt, was kam).
        Stufe 1 kommt fertig von der Platte, wenn sie zum Stand passt (`Meshgenesisanzeigeablage`, 13.11.2026), und wird nach jedem Bau dort abgelegt."""
        if int(stufe) == 1:
            from .meshgenesisanzeigeablage import Meshgenesisanzeigeablage
            fertig = Meshgenesisanzeigeablage.lesen(modell, matrix)
            if fertig is not None:
                return fertig
            paket = cls._paket(modell, stufe, matrix)
            # nur ein echtes Stufe-1-Paket ablegen: fiel der Bau auf den Käfig zurück (Fehler im Log), baut der nächste Abruf neu (13.11.2026: drei Figuren mit `G9halsfalte` warfen
            # TypeError, die Ablage hätte den Käfig festgehalten)
            if paket and json.loads(paket[4:4 + struct.unpack('<I', paket[:4])[0]]).get('stufe') == 1:
                Meshgenesisanzeigeablage.schreiben(modell, matrix, paket)
            return paket
        return cls._paket(modell, stufe, matrix)

    @classmethod
    def _paket(cls, modell, stufe, matrix):
        d = cls.laden(modell)
        if d is None:
            return None
        if int(stufe) == 1:
            from .meshgenesisflaechennetzfein import Meshgenesisflaechennetzfein
            fein = Meshgenesisflaechennetzfein.netz(modell, d, Meshgenesisdatensatz.ordner(modell), (cls._ablage.get(modell) or {}).get('stand'))
            d = fein if fein is not None else d
        haut = int(d['knochen'].shape[1])
        kopf = {'fassung': d['fassung'], 'punkte': int(len(d['uv'])), 'dreiecke': int(len(d['dreiecke'])), 'haut': haut, 'teile': list(cls.TEILE),
                'teilfarben': Torchfeld.astype(d['teilfarben'], torch.int64).tolist(),
                # Rauheit, Glanz, Metall nur, wenn das Stück sie trägt (21.10.2026 nachts, Stufe 2 der Kleider-KI) — sonst bleibt die Vorgabe der Seite
                'materialien': [dict({'name': m.get('name'), 'bild': m.get('bild'), 'farbe': m.get('farbe')}, **{k: m[k] for k in cls.MATERIALWERTE if isinstance(m.get(k), (int, float))},
                                     **{k: m[k] for k in ('bild_material', 'bild_normal') if isinstance(m.get(k), str)})
                                for m in d['materialien']], 'ruhe': 'ruhe' in d,
                'verborgen': int(len(d.get('verborgen', ()))), 'anatomie_fertig': bool(d.get('anatomie_fertig')), 'normalen': 'normalen' in d, 'punktfarbe': 'punktfarbe' in d,
                'stufe': 1 if 'eltern' in d else 0, 'kaefig_dreiecke': int(d.get('kaefig_dreiecke', len(d['dreiecke']))), 'eltern': 'eltern' in d,
                'matrix': [int(d['matrix'].shape[0]), int(d['matrix'].nnz)] if matrix and 'matrix' in d else None}
        text = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        a = cls._auffuellen
        teile = [struct.pack('<I', len(text)), text, Torchfeld.als_bytes(Torchfeld.astype(d['dreiecke'], Torchfeld.dtype('<u4'))),
                 a(Torchfeld.als_bytes(Torchfeld.astype(d['knochen'], torch.uint8))), a(Torchfeld.als_bytes(Torchfeld.astype(d['gewicht'], torch.uint8))), a(Torchfeld.als_bytes(Torchfeld.astype(d['etikett'], torch.uint8))),
                 Torchfeld.als_bytes(Torchfeld.astype(d['uv'], Torchfeld.dtype('<f4'))), a(Torchfeld.als_bytes(Torchfeld.astype(d['material'], Torchfeld.dtype('<i2'))))]
        if 'ruhe' in d:
            teile.append(Torchfeld.als_bytes(Torchfeld.astype(d['ruhe'], Torchfeld.dtype('<f4'))))
        if len(d.get('verborgen', ())):
            teile.append(Torchfeld.als_bytes(Torchfeld.astype(d['verborgen'], Torchfeld.dtype('<u4'))))
        if 'normalen' in d:
            teile.append(a(Torchfeld.als_bytes(d['normalen'])))
        if 'punktfarbe' in d:
            teile.append(a(Torchfeld.als_bytes(d['punktfarbe'])))
        if 'eltern' in d:
            teile.append(Torchfeld.als_bytes(Torchfeld.astype(d['eltern'], Torchfeld.dtype('<u4'))))
        if kopf['matrix']:
            w = d['matrix']
            teile += [Torchfeld.als_bytes(Torchfeld.astype(w.indptr, Torchfeld.dtype('<u4'))), a(Torchfeld.als_bytes(Torchfeld.astype(w.indices, Torchfeld.dtype('<u2')))), Torchfeld.als_bytes(Torchfeld.astype(w.data, Torchfeld.dtype('<f4')))]
        return b''.join(teile)

    @classmethod
    def bild(cls, modell, name):
        # `m<n>_material.png` (21.10.2026 nachts): Materialkarte eines KI-Stücks der Stufe 2 — G Rauheit, B Metall, A Glanz (wie three.js die Karten liest)
        if not re.fullmatch(r'm\d{1,4}(\.jpg|_material\.png|_normal\.png)', str(name)):
            return None
        pfad = cls.ordner(modell) / 'bilder' / name
        return pfad if pfad.is_file() else None
