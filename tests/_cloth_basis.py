# -*- coding: utf-8 -*-
"""Beiwerk der Cloth-Export-Tests: Importe, Pfade, Vorlagen.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist — sonst stuende sie als „ungegliedert" in den Befunden.

Aus tests/cloth_export_tests.py herausgeloest (17.08.2026), zusammen mit der
Aufteilung der 34 Tests in drei Kategorien:

    cloth_export_tests.py   die Endpunktpruefung (Methode, Engine-Auswahl)
    cloth_szene_tests.py    SceneInput als .npz, Aufteilen in Rigid und Stoff
    cloth_engine_tests.py   Y-up/Z-up-Kamera, Nutzlast, Geometrie der Backe

Die Tests laufen im Prozess des Servers als Teil der /tests/-Oberflaeche und
muessen daher schnell und ohne Nebenwirkung sein. Geprueft werden

  - collision.scene_input:    Datenklasse + .npz-Rundlauf
  - collision.splitter:       Pin-Gruppen-Mathematik + split_scene
  - collision.bridge:         Y-up-Kameramatrix (R @ M)
  - collision._yup_to_zup:    genau der Fehler, der den einfarbigen
                              Blender-Export verursacht hat
  - /api/cloth/export/:       Methode und Engine-Namen

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `klassenreif` Frage 1,
`globaler-zustand`): vier freie Funktionen und zwei `global`-Zwischenspeicher.
Beides steht jetzt in `Clothbasis`; die Vorlagen haengen als Klassenfeld daran
und lassen sich mit `.leeren()` verwerfen.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import numpy as np

from core.projekt_temp import ProjektTemp


class Clothbasis:
    """Pfad, Kunstanimation und die zwei teuren Vorlagen der Cloth-Tests."""

    # Pfade ABGELEITET, nicht eingetippt (Review 15.08.2026): Hier standen
    # `A:\HumanBodyTest\HumanBody` und `A:\HumanBodyTest` — das alte Projekt,
    # das noch auf der Platte liegt. Mit `sys.path.insert(0, ...)` haette
    # dieser Test das `collision`-Paket VON DORT importiert und fremden Code
    # geprueft, ohne dass es jemandem auffaellt. Denselben Rueckfall hat
    # cloth_export_api.py am 12.08.2026 verloren; hier blieb er stehen.
    HB_WURZEL = str(Path(__file__).resolve().parents[2] / 'HumanBody')
    HB_ELTERN = str(Path(__file__).resolve().parents[2])

    #: {Name: Ergebnis} — je Vorlage einmal gerechnet.
    _vorlagen = {}

    @classmethod
    def leeren(cls):
        cls._vorlagen = {}

    # ------------------------------------------------------------------ Pfad

    @classmethod
    def pfad_sichern(cls):
        """`HumanBody/` in `sys.path`, damit `collision.*` importierbar ist.

        ALS AUFRUF, NICHT ALS NEBENWIRKUNG (17.08.2026): Vorher lief das beim
        Import dieses Moduls. Zwei der drei Testdateien brauchen von hier gar
        keinen Namen — nur diesen Pfad — und mussten das Modul deshalb
        „unbenutzt" importieren. `tote-importe` hat genau das gemeldet, und zu
        Recht: Ein Import, dessen Zweck nirgends im Code steht, wird beim
        naechsten Aufraeumen entfernt und die Tests fallen aus.
        """
        for pfad in (cls.HB_WURZEL, cls.HB_ELTERN):
            if pfad not in sys.path:
                sys.path.insert(0, pfad)

    # `_import_collision()` stand hier bis zum 17.08.2026: eine Fabrik, die
    # vier Module als Tupel zurueckgab, deren vierter Eintrag
    # `… if False else None` lautete — und die NIEMAND aufrief. Die Tests
    # importieren `collision.*` seit langem direkt in der jeweiligen
    # Testmethode. Gefunden von `altlast` („Name kommt nur an der Definition
    # vor") und `rueckgabetupel` gleichzeitig.

    @classmethod
    def kunstanimation(cls, knochen, bilder):
        """Eine Animation aus lauter Einheitsmatrizen — nichts bewegt sich."""
        cls.pfad_sichern()
        from collision.scene_input import AnimationTrack
        matrizen = np.tile(np.eye(4, dtype=np.float32), (bilder, knochen, 1, 1))
        return AnimationTrack(
            bone_names=['B%d' % i for i in range(knochen)],
            fps=30.0, frame_count=bilder, matrices=matrizen)

    # -------------------------------------------------------- .npz-Rundlauf

    @classmethod
    def npz_rundlauf(cls):
        """Eine Szene schreiben, zurueckladen und die Felder nachzaehlen."""
        if 'npz' in cls._vorlagen:
            return cls._vorlagen['npz']
        cls.pfad_sichern()
        try:
            from collision.scene_input import SceneInput, ClothSegment
        except Exception as fehler:                              # noqa: BLE001
            cls._vorlagen['npz'] = {'_err': 'import failed: %s' % fehler}
            return cls._vorlagen['npz']
        szene = cls._kunstszene(SceneInput, ClothSegment)
        cls._vorlagen['npz'] = cls._schreiben_und_lesen(szene)
        return cls._vorlagen['npz']

    @classmethod
    def _kunstszene(cls, SceneInput, ClothSegment):
        segment = ClothSegment(
            bone_name='DEF-spine',
            vertices=np.array([[0, 0, 1], [0.1, 0, 0.9], [-0.1, 0, 0.9]],
                              dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            pin_indices=np.array([0], dtype=np.uint32),
            pin_local_positions=np.zeros((1, 3), dtype=np.float32))
        return SceneInput(
            rigid_vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]],
                                    dtype=np.float32),
            rigid_faces=np.array([[0, 1, 2]], dtype=np.uint32),
            rigid_skin_indices=np.zeros((3, 4), dtype=np.uint16),
            rigid_skin_weights=np.tile(
                np.array([[1, 0, 0, 0]], dtype=np.float32), (3, 1)),
            bone_rest_inverse=np.tile(np.eye(4, dtype=np.float32), (1, 1, 1)),
            animation=cls.kunstanimation(1, 2),
            cloth_segments=[segment],
            scene_name='unit_test_scene')

    @staticmethod
    def _schreiben_und_lesen(szene):
        # ProjektTemp, nicht System-Temp: `tempfile.mkdtemp` ohne `dir=`
        # schreibt auf C:, und das ist in diesem Projekt verboten
        # (Vorgeschichte: ~100 GB Datenmuell).
        ordner = ProjektTemp.ordner(prefix='cloth_npz_')
        try:
            pfad = os.path.join(ordner, 's.npz')
            szene.save_npz(pfad)
            da = os.path.isfile(pfad)
            with np.load(pfad, allow_pickle=True) as daten:
                return {
                    'exists': bool(da),
                    'rigid_V': int(daten['rigid_vertices'].shape[0]),
                    'num_segs': int(daten['num_cloth_segments'][0]),
                    'anim_fps': float(daten['anim_fps'][0]),
                    'scene_name': str(daten['scene_name'][0]),
                    'seg_bone': str(daten['seg0_bone_name'][0]),
                    'seg_V': int(daten['seg0_vertices'].shape[0]),
                }
        finally:
            shutil.rmtree(ordner, ignore_errors=True)

    # ------------------------------------------------------------- Aufteilen

    @classmethod
    def aufteilung(cls):
        """Eine Szene aus Rigid- und Stoffknochen durch `split_scene`."""
        if 'split' in cls._vorlagen:
            return cls._vorlagen['split']
        cls.pfad_sichern()
        try:
            from collision.splitter import split_scene
        except Exception as fehler:                              # noqa: BLE001
            cls._vorlagen['split'] = {'_err': 'import failed: %s' % fehler}
            return cls._vorlagen['split']
        szene = cls._aufgeteilte_szene(split_scene)
        stoff = szene.cloth_segments
        cls._vorlagen['split'] = {
            'rigid_V': int(szene.rigid_vertices.shape[0]),
            'cloth_count': len(stoff),
            'cloth0_bone': stoff[0].bone_name if stoff else '',
            'cloth0_V': int(stoff[0].vertices.shape[0]) if stoff else 0,
            'cloth0_pins': int(stoff[0].pin_indices.shape[0]) if stoff else 0,
        }
        return cls._vorlagen['split']

    @classmethod
    def _aufgeteilte_szene(cls, split_scene):
        # Je drei Punkte pro Knochen: 0..2 = rigid (spine), 3..5 = Stoff (skirt)
        punkte = np.array([
            [0, 0, 0], [0.1, 0, 0], [-0.1, 0, 0],
            [0, 1, 0.2], [0.2, 0.8, 0], [-0.2, 0.8, 0],
        ], dtype=np.float32)
        gewichtsindizes = np.array([
            [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
            [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0],
        ], dtype=np.uint16)
        return split_scene(
            positions=punkte,
            faces=np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32),
            skin_indices=gewichtsindizes,
            skin_weights=np.tile(np.array([1, 0, 0, 0], dtype=np.float32),
                                 (6, 1)),
            bone_vertex_ranges={'DEF-spine': (0, 3), 'DEF-skirt': (3, 3)},
            bone_parts={'DEF-spine': {'shape': 'cylinder'},
                        # `skirt` -> is_garment=true als Vorgabe
                        'DEF-skirt': {'shape': 'skirt'}},
            bone_heads_world={'DEF-spine': np.zeros(3),
                              'DEF-skirt': np.array([0, 0.8, 0])},
            bone_tails_world={'DEF-spine': np.array([0, 0.5, 0]),
                              'DEF-skirt': np.array([0, 0.0, 0])},
            bone_names_ordered=['DEF-spine', 'DEF-skirt'],
            bone_rest_inverse=np.tile(np.eye(4, dtype=np.float32), (2, 1, 1)),
            animation=cls.kunstanimation(2, 2),
            scene_name='split_fx')
