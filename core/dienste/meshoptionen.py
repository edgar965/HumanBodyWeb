# -*- coding: utf-8 -*-
"""Meshoptionen — was der Reiter „Mesh" einstellen lässt, mit Vorgaben und Verfügbarkeit.

Edgar (26.09.2026): „Optionen auswählen (mach Vorschlag)" — „Mache die Auswahl Hunyuan3D
und Trellis auswählbar", später „bei Hunyuan3D auch Textur Malerei" und (26.09.2026,
abends) alle drei besprochenen Mehrbild-Wege zugleich als Option: Fotogewicht je Bild
(live in der Textur-Vorschau), Hunyuan3D-2mv (echtes Multiview-Formmodell) und Fusion
(mehrere Einzelnetze gewichtet gemittelt). Der Vorschlag steht als Tabelle `KATALOG`
(Seite und Lauf lesen dieselbe); `pruefen` lässt nur bekannte Schlüssel und Werte durch,
alles andere fällt auf die Vorgabe (ein altes Formular oder ein Tippfehler startet sonst
einen Lauf mit `None`-Werten).

Formmodelle (Gewichte unter `settings.HF_HOME_DIR`, Umgebung `settings.MESH_PYTHON`):
    trellis2       TRELLIS.2-4B (Microsoft, MIT) — ein Bild, bis 1536³, EIGENE PBR-Textur
                   (gelernt, `o_voxel.postprocess.to_glb`) — voll verdrahtet.
    hunyuan3d_2    Hunyuan3D-2.0 (Tencent, Forschungslizenz — NICHT in EU/UK/Südkorea, Edgar
                   26.09.2026: „downloade auch Hunyuan3D, das ist für Forschung") —
                   `hy3dgen.shapegen` für die Form, bei „ki"/„fotos_ki" zusätzlich Hunyuan3Ds
                   EIGENE Multiview-Diffusions-Texturmalerei (`hy3dgen.texgen`, Edgar
                   26.09.2026: „bei Hunyuan3D auch Textur Malerei"). Braucht die von Hand
                   kompilierte `custom_rasterizer`-Erweiterung; fehlt sie, fällt der Runner
                   automatisch auf die Fotos zurück (`_run_mesh.py::fototextur_vertexfarben`).
    hunyuan3d_2mv  Hunyuan3D-2mv — ECHTES Multiview-Formmodell: bis zu vier Fotos
                   (vorne/hinten/links/rechts) gehen GEMEINSAM in einen Formlauf
                   (`hy3dgen.shapegen.preprocessors.MVImageProcessorV2`, Schlüssel
                   front/back/left/right). Dieselbe Texturmalerei wie hunyuan3d_2.
    hunyuan3d_21   Gewichte werden heruntergeladen, aber NOCH NICHT verdrahtet (eigenes
                   `hy3dgen`) — `NICHT_VERDRAHTET`, im Katalog als „in Vorbereitung" markiert.

`mehrbildmodus` (unabhängig vom Formmodell): „einzelbild" (Vorgabe, nur das „vorne"-Bild
bestimmt die Form) oder „fusion" (je Bild ein eigener Formlauf mit dem gewählten
Formmodell, per Fotogewicht zu einem Netz gemittelt — `_run_mesh.py::form_fusion`,
SDF-Averaging + Marching Cubes; keine geerbte PBR/Texturmalerei danach, nur Fotos).
Jedes Bild trägt zusätzlich ein `gewicht` (0–100, Vorgabe 100) und optional einen
`bereich` (Rechteck-Ausschnitt) — beide wirken auf die Textur-Projektion IMMER, auf die
Form nur bei `mehrbildmodus=fusion`.
"""

import os
from pathlib import Path

from django.conf import settings

__all__ = ['Meshoptionen']


class Meshoptionen:
    #: Die Rollen eines Fotos (Auswahl je Bild auf der Seite).
    ROLLEN = [
        ('auto', 'Automatisch'),
        ('vorne', 'Vorne'),
        ('hinten', 'Hinten'),
        ('links', 'Links'),
        ('rechts', 'Rechts'),
        ('gesicht', 'Nahaufnahme Gesicht'),
        ('detail', 'Nur Textur (Detail)'),
        ('aus', 'Nicht verwenden'),
    ]

    #: Welche HF-Ablage ein Formmodell braucht (`models--<org>--<name>` in hf_home/hub).
    GEWICHTE = {
        'trellis2': ['microsoft/TRELLIS.2-4B', 'microsoft/TRELLIS-image-large', 'timm/vit_large_patch16_dinov3.lvd1689m'],
        'hunyuan3d_2': ['tencent/Hunyuan3D-2'],
        'hunyuan3d_2mv': ['tencent/Hunyuan3D-2mv'],
        'hunyuan3d_21': ['tencent/Hunyuan3D-2.1'],
    }
    #: Noch kein Runner-Code (`_run_mesh.py`) — im Katalog wählbar, aber gesperrt.
    NICHT_VERDRAHTET = ('hunyuan3d_21',)

    KATALOG = [
        {'schluessel': 'formmodell', 'titel': 'Formmodell', 'art': 'wahl', 'vorgabe': 'trellis2', 'werte': [
            ('trellis2', 'TRELLIS.2 (Microsoft, 4B) — ein Bild, sehr fein, eigene PBR-Textur'),
            ('hunyuan3d_2', 'Hunyuan3D-2.0 — ein Bild, eigene Texturmalerei oder Fotos (Forschungslizenz)'),
            ('hunyuan3d_2mv', 'Hunyuan3D-2mv — mehrere Ansichten fließen in die Form ein (Forschungslizenz)'),
            ('hunyuan3d_21', 'Hunyuan3D-2.1 — ein Bild (in Vorbereitung)'),
        ], 'hinweis': 'Hunyuan3D: Tencent-Forschungslizenz, gilt nicht in der EU/UK/Südkorea.'},
        {'schluessel': 'mehrbildmodus', 'titel': 'Mehrere Fotos', 'art': 'wahl',
         'vorgabe': 'einzelbild', 'werte': [
            ('einzelbild', 'Nur „Vorne" bestimmt die Form (Vorgabe)'),
            ('fusion', 'Je Foto ein eigenes Netz, per Fotogewicht gemittelt (langsamer, gröber)'),
        ], 'hinweis': 'Fusion rechnet die Form je gewichtetem Foto neu und mittelt — deutlich '
                      'länger, gröberes Ergebnis, danach nur Foto-Textur (keine KI-Textur).'},
        {'schluessel': 'aufloesung', 'titel': 'Auflösung', 'art': 'wahl', 'vorgabe': 'hoch', 'werte': [
            ('schnell', 'Schnell — TRELLIS 512³ / Hunyuan Octree 256'),
            ('mittel', 'Mittel — TRELLIS 1024³ / Hunyuan Octree 384'),
            ('hoch', 'Hoch — TRELLIS 1536³ / Hunyuan Octree 512'),
        ]},
        {'schluessel': 'freistellen', 'titel': 'Hintergrund', 'art': 'wahl', 'vorgabe': 'auto', 'werte': [
            ('auto', 'Automatisch freistellen (BiRefNet)'),
            ('alpha', 'Alphakanal der Datei verwenden'),
        ]},
        {'schluessel': 'textur', 'titel': 'Textur', 'art': 'wahl', 'vorgabe': 'fotos_ki', 'werte': [
            ('fotos_ki', 'Fotos aufprojiziert, Lücken aus der Modelltextur'),
            ('fotos', 'Nur Fotos (Lücken aufgefüllt)'),
            ('ki', 'Nur die Textur des Formmodells (TRELLIS.2: PBR; Hunyuan3D: eigene Texturmalerei)'),
            ('keine', 'Keine (grau)'),
        ], 'hinweis': 'Hunyuan3D ohne kompilierte Rasterizer-Erweiterung fällt bei „ki"/„fotos_ki" '
                      'automatisch auf die Fotoprojektion zurück.'},
        {'schluessel': 'gesicht', 'titel': 'Gesicht', 'art': 'wahl', 'vorgabe': 'an', 'werte': [
            ('an', 'Nahaufnahme für Form und Textur des Kopfes nutzen'),
            ('textur', 'Nahaufnahme nur für die Textur'),
            ('aus', 'Nahaufnahme nicht nutzen'),
        ]},
        {'schluessel': 'texturgroesse', 'titel': 'Texturgröße', 'art': 'wahl', 'vorgabe': '4096', 'werte': [
            ('2048', '2048 × 2048'), ('4096', '4096 × 4096'),
        ]},
        {'schluessel': 'flaechen', 'titel': 'Flächen', 'art': 'wahl', 'vorgabe': '500000', 'werte': [
            ('100000', '100.000'), ('300000', '300.000'), ('500000', '500.000'), ('1000000', '1 Mio.'),
        ]},
        {'schluessel': 'hoehe_cm', 'titel': 'Höhe (cm)', 'art': 'zahl', 'vorgabe': 170, 'min': 1, 'max': 100000,
         'hinweis': 'Das Netz wird auf diese Höhe skaliert, Füße auf 0, Y oben.'},
        {'schluessel': 'formate', 'titel': 'Ausgabe', 'art': 'mehrfach', 'vorgabe': ['glb', 'obj'], 'werte': [
            ('glb', 'GLB (Textur eingebettet)'), ('obj', 'OBJ + MTL + PNG'), ('ply', 'PLY (Punktfarben)'),
        ]},
        {'schluessel': 'seed', 'titel': 'Seed', 'art': 'zahl', 'vorgabe': 42, 'min': 0, 'max': 2 ** 31 - 1},
    ]

    @classmethod
    def eintrag(cls, schluessel):
        for e in cls.KATALOG:
            if e['schluessel'] == schluessel:
                return e
        raise KeyError(schluessel)

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: (list(e['vorgabe']) if isinstance(e['vorgabe'], list) else e['vorgabe'])
                for e in cls.KATALOG}

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Schlüssel mit gültigen Werten — der Rest wird Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            erlaubt = [w for w, _ in e.get('werte', [])]
            if e['art'] == 'wahl' and str(wert) in erlaubt:
                aus[e['schluessel']] = str(wert)
            elif e['art'] == 'mehrfach' and isinstance(wert, list):
                gewaehlt = [w for w in erlaubt if w in wert]
                aus[e['schluessel']] = gewaehlt or aus[e['schluessel']]
            elif e['art'] == 'zahl':
                try:
                    zahl = float(wert)
                except (TypeError, ValueError):
                    continue
                if e.get('min', zahl) <= zahl <= e.get('max', zahl):
                    aus[e['schluessel']] = int(zahl) if float(zahl).is_integer() else zahl
        if 'glb' not in aus['formate']:
            aus['formate'] = ['glb', *aus['formate']]  # die Vorschau der Seite liest das GLB
        return aus

    @classmethod
    def rolle_pruefen(cls, rolle):
        return rolle if rolle in dict(cls.ROLLEN) else 'auto'

    @staticmethod
    def gewicht_pruefen(wert):
        try:
            zahl = float(wert)
        except (TypeError, ValueError):
            return 100
        return int(max(0, min(100, zahl)))

    @staticmethod
    def bereich_pruefen(wert):
        """`[x0,y0,x1,y1]` normiert 0..1, x0<x1 und y0<y1 — sonst `None` (ganzes Bild)."""
        if not isinstance(wert, (list, tuple)) or len(wert) != 4:
            return None
        try:
            x0, y0, x1, y1 = (float(w) for w in wert)
        except (TypeError, ValueError):
            return None
        x0, x1 = sorted((max(0.0, min(1.0, x0)), max(0.0, min(1.0, x1))))
        y0, y1 = sorted((max(0.0, min(1.0, y0)), max(0.0, min(1.0, y1))))
        if x1 - x0 < 0.01 or y1 - y0 < 0.01:
            return None
        return [x0, y0, x1, y1]

    # --------------------------------------------------------- Verfügbarkeit

    @staticmethod
    def _hf_da(repo):
        ordner = Path(settings.HF_HOME_DIR) / 'hub' / ('models--' + repo.replace('/', '--')) / 'snapshots'
        return ordner.is_dir() and any(ordner.iterdir())

    @classmethod
    def verfuegbar(cls):
        """`{formmodell: grund_oder_leer}` — leer heißt bereit."""
        umgebung = os.path.isfile(settings.MESH_PYTHON)
        aus = {}
        for modell, repos in cls.GEWICHTE.items():
            if modell in cls.NICHT_VERDRAHTET:
                aus[modell] = 'In Vorbereitung — noch kein Runner-Code'
                continue
            fehlt = [r for r in repos if not cls._hf_da(r)]
            if not umgebung:
                aus[modell] = 'Umgebung python10_mesh fehlt'
            elif fehlt:
                aus[modell] = 'Gewichte fehlen: %s' % ', '.join(fehlt)
            else:
                aus[modell] = ''
        return aus

    @classmethod
    def katalog(cls):
        """Der Katalog für die Seite, mit Verfügbarkeit je Formmodell."""
        frei = cls.verfuegbar()
        aus = []
        for e in cls.KATALOG:
            neu = dict(e, werte=[{'wert': w, 'text': t, **({'fehlt': frei[w]} if frei.get(w) else {})}
                                 for w, t in e.get('werte', [])])
            aus.append(neu)
        return {'optionen': aus, 'rollen': [{'wert': w, 'text': t} for w, t in cls.ROLLEN]}
