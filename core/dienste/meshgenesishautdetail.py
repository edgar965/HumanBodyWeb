# -*- coding: utf-8 -*-
"""Meshgenesishautdetail — Relief und Rauheit der Genesis-Grundhaut für die Hautmaterialien einer Testfigur (15.11.2026 nachts, Edgar: „haut textur an Händen ist noch sehr
künstlich“). Besitzer: Mesh-Genesis.

Die Figur eines Tests (`_test/<kennung>/form_<g>`) trägt je Hautkachel nur ein Farbbild (1024 px), Rauheit überall 0,75 — im Bild glatte Plastikhaut. Mesh-Genesis rechnet die
Normalen- und Materialkarten der Grundhaut je Kachel einmal vor (`meshgenesis/meshgenesis_hautdetail.py`, Ablage `_ablage/hautdetail/f<Fassung>/<g>/<kachel>_normal.png`,
`…_material.png`); diese Klasse hängt sie im Paket an (`bild_normal`, `bild_material`, `Meshgenesisflaechennetz._paket`) und liefert die Bilder (`bild`). Welche Kachel ein Material
trägt, steht in `haut_<g>/anzeige.json` (Überdeckung im UV-Raum, `Testhautbilder`) — die Namen taugen nicht verlässlich (das Kopfbild heißt „Mouth Cavity“); ohne die Zuordnung
der Gruppenname (`KACHEL_NACH_NAME`). Andere Modelle (Datensätze, Jobs) bleiben unverändert.

    Meshgenesishautdetail.werte(modell, materialien)  → [dict | None] je Material
    Meshgenesishautdetail.bild(modell, name)          → Path | None
"""
import json
import re

from .meshgenesisdatensatz import Meshgenesisdatensatz

__all__ = ['Meshgenesishautdetail']


class Meshgenesishautdetail:
    FASSUNG = 1                     # = `Hautdetail.FASSUNG` (meshgenesis)
    MODELL = re.compile(r'^_test/[^/]+/form_(maennlich|weiblich)$')
    NAME = re.compile(r'^hautdetail_(10\d\d)_(normal|material)\.png$')
    KACHEL_NACH_NAME = {'Head': '1001', 'Mouth Cavity': '1001', 'Body': '1002', 'Legs': '1003', 'Arms': '1004', 'Fingernails': '1005', 'Toenails': '1005'}

    @classmethod
    def _geschlecht(cls, modell):
        m = cls.MODELL.match(str(modell).replace('\\', '/'))
        return m.group(1) if m else None

    @classmethod
    def _datei(cls, geschlecht, kachel, art):
        return Meshgenesisdatensatz.ordner('_ablage/hautdetail/f%d/%s/%s_%s.png' % (cls.FASSUNG, geschlecht, kachel, art))

    @classmethod
    def werte(cls, modell, materialien):
        g = cls._geschlecht(modell)
        if g is None:
            return [None] * len(materialien)
        try:
            zuordnung = json.loads((Meshgenesisdatensatz.ordner(modell).parent / ('haut_%s' % g) / 'anzeige.json').read_text(encoding='utf-8')).get('bilder') or {}
        except (OSError, ValueError):
            zuordnung = {}
        aus = []
        for m in materialien:
            kachel = (zuordnung.get(str(m.get('bild'))) or '').split('.')[0] or cls.KACHEL_NACH_NAME.get(str(m.get('name')))
            if not kachel or m.get('bild_normal') or m.get('bild_material'):
                aus.append(None)
                continue
            w = {('bild_%s' % art): 'hautdetail_%s_%s.png' % (kachel, art) for art in ('normal', 'material') if cls._datei(g, kachel, art).is_file()}
            aus.append(w or None)
        return aus

    @classmethod
    def stand(cls, modell):
        """Stand für den Namen des fertigen Pakets (`Meshgenesisanzeigeablage`): Fassung, Zeit der Kachel-Zuordnung, vorhandene Karten — ohne ihn kam nach dem Einbau das alte Paket."""
        g = cls._geschlecht(modell)
        if g is None:
            return None
        zuordnung = Meshgenesisdatensatz.ordner(modell).parent / ('haut_%s' % g) / 'anzeige.json'
        karten = sorted(p.name for p in cls._datei(g, '1001', 'normal').parent.glob('10*_*.png')) if cls._datei(g, '1001', 'normal').parent.is_dir() else []
        return (cls.FASSUNG, zuordnung.stat().st_mtime_ns if zuordnung.is_file() else None, tuple(karten))

    @classmethod
    def bild(cls, modell, name):
        g, m = cls._geschlecht(modell), cls.NAME.match(str(name))
        if g is None or m is None:
            return None
        pfad = cls._datei(g, m.group(1), m.group(2))
        return pfad if pfad.is_file() else None
