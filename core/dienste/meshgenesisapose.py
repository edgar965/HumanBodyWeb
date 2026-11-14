# -*- coding: utf-8 -*-
"""Meshgenesisapose — das Zwischenbild „Rig → A-Pose" einer Probe auf der Jobseite von Mesh-Genesis (17.10.2026).

Edgar: „Wird als erstes das Mesh gerickt und in die A-Position gebracht? … Gegebenenfalls müsste man auf der Trainingsseite ein Zwischenbild machen. Also nicht drei Bilder, sondern vier Bilder, mit dem Rig
und Bringen in die A-Position?" — die Vorstufe (Rig aus „Mesh to 3D", Netz damit in die A-Pose, darauf das Netz der Vorstufe) lief seit dem Morgen, die Seite zeigte aber nur Start · Ziel · Ergebnis.
Gelesen wird, was die Kette der Vorstufe ablegt (`ProjektTemp/_wegwerf/meshgenesis_vorstufe_anzeige.py`): `<ablage>/<Netz der Vorstufe>/anzeige_<Figur>.npz` — die Fläche des Netzes in der Ruhelage der
Rig-Figur, im Rahmen, den das Netz der Vorstufe sieht (Blick +Z, Hüfte in der Mitte, Füße auf dem Boden), dazu die Gelenke der Rig-Figur in Ruhe und die Gelenke, die das Netz dort abstimmt. Welche
Ablage zu einem Lauf gehört, steht in der Fassung von `wege.json`, die die Jobseite zeigt (`Meshgenesiswege.gewaehlt`: jüngster Lauf der Methode aus Einstellungen → Mesh-Genesis — seit 18.10.2026 abends
MeshToRigToPose_MIA oder MeshToRigToPose; `ablage`, `netz_vorstufe`).

    Meshgenesisapose.vorhanden(lauf) -> bool          (die Probe 1 des Jobs hat ein Zwischenbild)
    Meshgenesisapose.paket(lauf, namen) -> bytes|None

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, auf ein Vielfaches von 4 aufgefüllt: {punkte, dreiecke, rig (138 × 3, Reihenfolge `namen`), netz (dito), abstand_mm, ablage, mesh3d,
netz_vorstufe}) · float32 punkte (V·3) · uint32 dreiecke (F·3) · uint8 farbe (V·3, sRGB), aufgefüllt auf 4.
"""

import json
import logging
import struct
import zipfile
from pathlib import Path

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

from .meshgenesisaposewahl import Meshgenesisaposewahl
from .meshgenesiswege import Meshgenesiswege

logger = logging.getLogger('core')

__all__ = ['Meshgenesisapose']


class Meshgenesisapose:
    #: Die Kette der Vorstufe läuft je Prüfposen-Job auf Probe 1 (`Vorstufenkette.job`).
    PROBE = 1

    @staticmethod
    def _gewaehlt(lauf):
        """(wege, kette) der Fassung, die die Jobseite zeigt (`Meshgenesiswege.gewaehlt`: jüngster Lauf der Methode aus Einstellungen → Mesh-Genesis) — oder (None, {})."""
        g = Meshgenesiswege.gewaehlt(lauf) if lauf else None
        if g is None:
            return None, {}
        try:
            return json.loads(g[0].read_text(encoding='utf-8')), g[1]
        except (OSError, ValueError):
            return None, {}

    @classmethod
    def _wege(cls, lauf):
        return cls._gewaehlt(lauf)[0]

    @classmethod
    def datei(cls, lauf):
        """`anzeige_<Figur>.npz` der Ablage, die `wege.json` des Laufs nennt — oder None (keine Vorstufe, Ablage vor dem Zwischenbild)."""
        wege = cls._wege(lauf)
        if not wege or not wege.get('ablage') or not wege.get('netz_vorstufe'):
            return None
        ordner = Path(wege['ablage']) / wege['netz_vorstufe']
        dateien = sorted(Npztorch.glob(ordner, 'anzeige_*.npz')) if ordner.is_dir() else []
        if len(dateien) > 1:
            logger.warning('Meshgenesisapose: %s hat %d Zwischenbilder — das erste gilt (%s)', ordner, len(dateien), dateien[0].name)
        return dateien[0] if dateien else None

    @classmethod
    def vorhanden(cls, lauf):
        return cls.datei(lauf) is not None

    #: Welche Datei die Kette las (`kette.json` der Ablage, Feld `netz`) — seit 17.10.2026 nachmittags die Außenfläche mit Textur (Edgar: „Die Textur ist eine andere“).
    EINGABEN = {'eingabe_textur.glb': 'Außenfläche mit Textur (eingabe_textur.glb)', 'eingabe.glb': 'Außenfläche mit flachen Teilfarben (eingabe.glb)'}

    @classmethod
    def eingabe(cls, wege):
        try:
            netz = Path(json.loads((Path(wege['ablage']) / 'kette.json').read_text(encoding='utf-8'))['netz']).name
        except (OSError, ValueError, KeyError, TypeError):
            return None
        return cls.EINGABEN.get(netz, netz)

    @classmethod
    def paket(cls, lauf, namen):
        datei = cls.datei(lauf)
        if datei is None:
            return None
        try:
            with Npztorch.lesen(datei) as z:
                punkte, dreiecke, farbe = Torchfeld.astype(z['punkte'], Torchfeld.dtype('<f4')), Torchfeld.astype(z['dreiecke'], Torchfeld.dtype('<u4')), Torchfeld.astype(z['farbe'], torch.uint8)
                ix = {str(n): i for i, n in enumerate(z['knochen'])}
                rig, netz = z['rig'], z['netz']
                # Seit 17.10.2026 abends füllt der Schritt „apose“ die Löcher (`Vorstufenluecken`): Zahl der Fülldreiecke, die hinten an der Fläche hängen; ältere Ablagen ohne das Feld: 0.
                gefuellt = int(z['gefuellt']) if 'gefuellt' in z.files else 0
                if any(n not in ix for n in namen):
                    logger.warning('Meshgenesisapose: %s kennt nicht alle Knochen des Rigs — nicht ausgeliefert', datei)
                    return None
                sel = [ix[n] for n in namen]
                rig, netz = Torchfeld.astype(rig[sel], torch.float64), Torchfeld.astype(netz[sel], torch.float64)
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as fehler:
            logger.warning('Meshgenesisapose: %s nicht lesbar (%s)', datei, fehler)
            return None
        wege, kette = cls._gewaehlt(lauf)
        wege = wege or {}
        # `methode` (18.10.2026 abends): MeshToRigToPose_MIA oder MeshToRigToPose — der Text unter dem Feld beschreibt, was DIESE Methode tat.
        kopf = {'methode': Meshgenesisaposewahl.methode(kette), 'methode_name': Meshgenesisaposewahl.name_des_laufs(kette), 'weg_grund': kette.get('weg_grund', ''),
                'punkte': int(len(punkte)), 'dreiecke': int(len(dreiecke)), 'rig': Torchfeld.round(rig, 5).tolist(), 'netz': Torchfeld.round(netz, 5).tolist(),
                'abstand_mm': round(float(1000 * Torchfeld.linalg_norm(netz - rig, dim=1).mean()), 1), 'ablage': Path(wege.get('ablage', '')).name,
                'mesh3d': wege.get('mesh3d'), 'netz_vorstufe': wege.get('netz_vorstufe'), 'figur': datei.stem.replace('anzeige_', ''),
                'eingabe': cls.eingabe(wege), 'gefuellt': gefuellt}
        text = json.dumps(kopf).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        farbteil = Torchfeld.als_bytes(farbe)
        farbteil += b'\0' * (-len(farbteil) % 4)
        return b''.join([struct.pack('<I', len(text)), text, Torchfeld.als_bytes(punkte), Torchfeld.als_bytes(dreiecke), farbteil])
