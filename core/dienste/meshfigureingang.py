# -*- coding: utf-8 -*-
"""Meshfigureingang — Körpernetz und Kopfnetz eines Auftrags „Mesh to 3D": hochgeladen oder als Pfad.

Edgar (27.09.2026): „mach mir zwei Textboxen für die Eingabepfade der Ursprungs-Meshes, auch beim
Job, falls ich neu berechnen will" — „ein Netz für den Körper, ein Netz für den Kopf".

Ein Pfad wird KOPIERT (samt dem, was das Netz nachlädt: MTL und Texturen einer OBJ, Puffer und
Bilder einer GLTF) — der Auftrag bleibt so nachrechenbar, auch wenn die Quelle später überschrieben
wird. Woher die Kopie stammt, steht im Eingang (`ursprung`, `stand` = Änderungszeit und Größe);
daran erkennt `aendern()` beim Neuberechnen, ob die Datei neu eingelesen werden muss.

    eingang = {datei, original, bytes, beilagen, ursprung?, stand?, kopf?: {…dasselbe…}}
"""

import json
import re
import shutil
from pathlib import Path

from ..daten.meshfigurablage import Meshfigurablage

__all__ = ['Meshfigureingang']


class Meshfigureingang:
    #: OBJ → MTL (`mtllib`), MTL → Bilder (`map_Kd`, `bump`, `norm`, …): der Dateiname ist das
    #: letzte Wort der Zeile (Optionen wie `-bm 1.0` davor).
    _MTLLIB = re.compile(r'^\s*mtllib\s+(.+?)\s*$', re.MULTILINE)
    _KARTE = re.compile(
        r'^\s*(?:map_\w+|bump|norm|disp|decal|refl)\s+(.+?)\s*$', re.MULTILINE | re.IGNORECASE
    )

    def __init__(self, ablage):
        self.ablage = ablage

    # ----------------------------------------------------------------- Pfad

    @staticmethod
    def pfad(text):
        """Geprüfter Pfad eines Netzes — oder None bei leerem Feld. Anführungszeichen (aus „Als Pfad
        kopieren" im Explorer) fallen weg."""
        text = str(text or '').strip().strip('"').strip("'").strip()
        if not text:
            return None
        pfad = Path(text).expanduser()
        if not pfad.is_file():
            raise ValueError('Datei nicht gefunden: %s' % text)
        if not Meshfigurablage.ist_netz(pfad.name):
            raise ValueError('Kein Netz (GLB, GLTF, OBJ, PLY, STL, OFF): %s' % pfad.name)
        return pfad

    @classmethod
    def beilagen(cls, pfad):
        """Was das Netz nachlädt und neben ihm liegt: MTL + Texturen (OBJ), Puffer + Bilder (GLTF)."""
        pfad = Path(pfad)
        endung = pfad.suffix.lower()
        namen = []
        if endung == '.obj':
            for mtl in cls._MTLLIB.findall(pfad.read_text(encoding='utf-8', errors='replace')):
                namen.append(mtl)
                datei = pfad.parent / mtl
                if datei.is_file():
                    text = datei.read_text(encoding='utf-8', errors='replace')
                    namen += [zeile.split()[-1] for zeile in cls._KARTE.findall(text)]
        elif endung == '.gltf':
            daten = json.loads(pfad.read_text(encoding='utf-8'))
            namen = [e['uri'] for e in daten.get('buffers', []) + daten.get('images', []) if 'uri' in e]
        dateien = []
        for name in namen:
            datei = (pfad.parent / name).resolve()
            if not name.startswith('data:') and datei.is_file() and Meshfigurablage.ist_beilage(datei.name):
                if datei not in dateien:
                    dateien.append(datei)
        return dateien

    @staticmethod
    def stand(pfad):
        s = Path(pfad).stat()
        return [int(s.st_mtime_ns), int(s.st_size)]

    def uebernehmen(self, pfad, teil):
        """Netz und Beilagen in den Eingang (`teil` = 'koerper' oder 'kopf') kopieren → Eintrag."""
        ordner = self.ablage.eingang(teil)
        self.ablage.leeren(ordner)
        ziel = ordner / Meshfigurablage.sauber(pfad.name)
        shutil.copy2(pfad, ziel)
        beilagen = []
        for datei in self.beilagen(pfad):
            name = Meshfigurablage.sauber(datei.name)
            shutil.copy2(datei, ordner / name)
            beilagen.append(name)
        return {
            'datei': ziel.name,
            'original': pfad.name,
            'bytes': int(pfad.stat().st_size),
            'beilagen': beilagen,
            'ursprung': str(pfad),
            'stand': self.stand(pfad),
        }

    # --------------------------------------------------------------- Anlegen

    def anlegen(self, dateien, pfad_koerper, pfad_kopf):
        """Eingang eines neuen Auftrags aus Hochgeladenem und/oder Pfaden — ValueError mit Klartext."""
        netze = [f for f in dateien if Meshfigurablage.ist_netz(f.name)]
        koerper = self.pfad(pfad_koerper)
        kopf = self.pfad(pfad_kopf)
        if koerper is not None and netze:
            raise ValueError('Körpernetz entweder hochladen oder als Pfad angeben, nicht beides')
        if koerper is None and len(netze) != 1:
            raise ValueError(
                'Genau ein Körpernetz (GLB, GLTF, OBJ, PLY, STL, OFF) hochladen oder als Pfad angeben'
                ' — hochgeladen: %d' % len(netze)
            )
        if koerper is not None:
            eingang = self.uebernehmen(koerper, 'koerper')
        else:
            eingang = {
                'datei': self.ablage.ablegen(netze[0]),
                'original': netze[0].name,
                'bytes': int(netze[0].size),
                'beilagen': [self.ablage.ablegen(f) for f in dateien if Meshfigurablage.ist_beilage(f.name)],
            }
        if kopf is not None:
            eingang['kopf'] = self.uebernehmen(kopf, 'kopf')
        return eingang

    # ------------------------------------------------------------ Neu rechnen

    def _neu(self, eintrag, pfad):
        return not eintrag or eintrag.get('ursprung') != str(pfad) or eintrag.get('stand') != self.stand(pfad)

    def aendern(self, eingang, pfade):
        """`(eingang, geaendert)` — Pfade von der Auftragsseite übernehmen. Ein leeres Körperfeld lässt
        das bisherige (auch hochgeladene) Netz stehen, ein leeres Kopffeld nimmt das Kopfnetz heraus.
        Neu eingelesen wird, wenn sich Pfad, Änderungszeit oder Größe der Quelle geändert haben."""
        eingang = dict(eingang or {})
        geaendert = False
        koerper = self.pfad((pfade or {}).get('koerper'))
        if koerper is not None and self._neu(eingang, koerper):
            kopf = eingang.pop('kopf', None)
            eingang = self.uebernehmen(koerper, 'koerper')
            if kopf:
                eingang['kopf'] = kopf
            geaendert = True
        kopf = self.pfad((pfade or {}).get('kopf'))
        if kopf is not None and self._neu(eingang.get('kopf'), kopf):
            eingang['kopf'] = self.uebernehmen(kopf, 'kopf')
            geaendert = True
        elif kopf is None and eingang.get('kopf'):
            eingang.pop('kopf')
            self.ablage.leeren(self.ablage.eingang('kopf'))
            geaendert = True
        return eingang, geaendert
