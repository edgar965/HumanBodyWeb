# -*- coding: utf-8 -*-
"""Wächter für die Brücke Browser -> Kollisions-Pipeline (collision/bridge.py).

WARUM (Review 15.08.2026, alles nachgemessen)
---------------------------------------------
Der Browser schickt eine ganze Szene als JSON mit base64-kodierten Binärfeldern.
Vier Dinge kamen dabei ungeprüft durch, und nur zwei davon endeten laut:

1. **Bereiche der Kleidungsstücke** — `bone_vertex_ranges` geht als
   `garment_mask[start:start+count] = True` und `positions[start:end]` weiter.
   NumPy-Slices werfen nicht, sie schneiden zurecht. Gemessen bei 10 Vertices:

       start=-5 count=3   ->  markiert Vertex 5..7 (nicht die gemeinten)
       start=20 count=3   ->  leeres Segment, keine Meldung

   Ergebnis: ein Video mit falsch aufgeteiltem Netz, kein Eintrag im Protokoll.

2. **Knochenindex** — `skin_indices.astype(np.uint16)` wickelt still um
   (gemessen: 70000 -> 4464). Im NumPy-Weg endet der Index daneben als
   IndexError, im Warp-Kernel auf der GPU ist er undefiniert.

3. **base64** — `b64decode` ohne `validate=True` wirft ungültige Zeichen weg
   (gemessen: `b64decode('QUJD!!!') == b'ABC'`). Aus verstümmelten Daten wird
   ein kürzeres, plausibles Array.

4. **Feldnamen in Meldungen** — acht Felder liefen in dasselbe nackte
   `ValueError: cannot reshape array of size ...`. Welches Feld gemeint war,
   stand nirgends.

WIDERLEGT wurde dagegen die Behauptung, `np.frombuffer` lese bei einer Länge,
die kein Vielfaches von 4 ist, „abgeschnitten weiter": Es wirft ValueError
(NumPy 2.4.4). Der stille Fall war allein das base64.
"""
import base64
import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase


def _b64(arr):
    return base64.b64encode(np.asarray(arr).tobytes()).decode('ascii')


def _payload(vcount=6, n_bones=3, n_frames=2, **abweichung):
    """Ein Paket, das durchgehen MUSS — Abweichungen einzeln überschreibbar."""
    positions = np.arange(vcount * 3, dtype=np.float32).reshape(vcount, 3)
    faces = np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32)[:max(1, vcount // 3)]
    skin_idx = np.zeros((vcount, 4), dtype=np.uint32)
    skin_w = np.zeros((vcount, 4), dtype=np.float32)
    skin_w[:, 0] = 1.0
    einheit = np.tile(np.eye(4, dtype=np.float32), (n_bones, 1, 1))
    anim = np.tile(np.eye(4, dtype=np.float32), (n_frames, n_bones, 1, 1))
    daten = {
        'vertex_count': vcount,
        'positions': _b64(positions),
        'faces': _b64(faces),
        'skin_indices': _b64(skin_idx),
        'skin_weights': _b64(skin_w),
        'bone_names': ['DEF-spine', 'DEF-thigh.L', 'DEF-thigh.R'][:n_bones],
        'inv_bind': _b64(einheit),
        'anim_frames': n_frames,
        'anim_fps': 30.0,
        'anim_matrices': _b64(anim),
        'bone_vertex_ranges': {'DEF-spine': {'start': 0, 'count': 3}},
        'bone_parts': {'DEF-spine': {'is_garment': False}},
        'scene_name': 'test',
    }
    daten.update(abweichung)
    return daten


class ClothBrueckeTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wurzel = str(getattr(settings, 'HUMANBODY_ROOT', ''))
        if wurzel and wurzel not in sys.path:
            sys.path.insert(0, wurzel)
        from collision.bridge import payload_to_scene_input
        cls.bauen = staticmethod(payload_to_scene_input)

    # ------------------------------------------------------------ Gegenprobe

    def test_gueltiges_paket_geht_durch(self):
        """Ohne diesen Test wäre jede Absage unten wertlos."""
        szene = self.bauen(_payload())
        self.assertEqual(szene.rigid_vertices.shape, (6, 3))
        self.assertEqual(szene.num_bones(), 3)
        self.assertEqual(szene.animation.frame_count, 2)

    def test_kleidung_wird_ausgeschnitten(self):
        szene = self.bauen(_payload(
            bone_vertex_ranges={'DEF-spine': {'start': 0, 'count': 3}},
            bone_parts={'DEF-spine': {'is_garment': True}}))
        self.assertEqual(len(szene.cloth_segments), 1)
        self.assertEqual(szene.cloth_segments[0].vertices.shape, (3, 3))
        self.assertEqual(szene.rigid_vertices.shape, (3, 3))

    # --------------------------------------------------------- die vier Fälle

    def test_bereich_ausserhalb_wird_abgelehnt(self):
        for start, count in ((-5, 3), (20, 3), (4, 10), (0, -2)):
            with self.subTest(start=start, count=count):
                with self.assertRaises(ValueError) as f:
                    self.bauen(_payload(bone_vertex_ranges={
                        'DEF-spine': {'start': start, 'count': count}}))
                self.assertIn('bone_vertex_ranges', str(f.exception))

    def test_knochenindex_ueber_der_knochenzahl(self):
        idx = np.zeros((6, 4), dtype=np.uint32)
        idx[0, 0] = 70000                      # wickelt in uint16 auf 4464 um
        with self.assertRaises(ValueError) as f:
            self.bauen(_payload(skin_indices=_b64(idx)))
        self.assertIn('skin_indices', str(f.exception))

    def test_ungueltiges_base64_wird_nicht_stillschweigend_gekuerzt(self):
        with self.assertRaises(ValueError) as f:
            self.bauen(_payload(positions='QUJD!!!'))
        self.assertIn('positions', str(f.exception))

    def test_meldung_nennt_das_feld(self):
        """Vorher: acht Felder, eine nackte reshape-Meldung."""
        faelle = {
            'positions': _b64(np.zeros((2, 3), np.float32)),
            'skin_weights': _b64(np.zeros((2, 4), np.float32)),
            'inv_bind': _b64(np.zeros((2, 4, 4), np.float32)),
            'anim_matrices': _b64(np.zeros((1, 2, 4, 4), np.float32)),
        }
        for feld, wert in faelle.items():
            with self.subTest(feld=feld):
                with self.assertRaises(ValueError) as f:
                    self.bauen(_payload(**{feld: wert}))
                self.assertIn(feld, str(f.exception))

    # ---------------------------------------------------------- weitere Wege

    def test_dreiecke_zeigen_ins_leere(self):
        with self.assertRaises(ValueError) as f:
            self.bauen(_payload(faces=_b64(np.array([[0, 1, 99]], dtype=np.uint32))))
        self.assertIn('faces', str(f.exception))

    def test_singulaere_bindematrix_nennt_den_knochen(self):
        kaputt = np.tile(np.eye(4, dtype=np.float32), (3, 1, 1))
        kaputt[1] = 0.0
        with self.assertRaises(ValueError) as f:
            self.bauen(_payload(inv_bind=_b64(kaputt)))
        self.assertIn('DEF-thigh.L', str(f.exception))

    def test_leere_oder_falsche_zaehler(self):
        for feld, wert in (('vertex_count', 0), ('anim_frames', 0)):
            with self.subTest(feld=feld):
                with self.assertRaises(ValueError):
                    self.bauen(_payload(**{feld: wert}))
        with self.assertRaises(ValueError):
            self.bauen(_payload(bone_names=[]))

    def test_kameraspur_mit_falscher_framezahl(self):
        with self.assertRaises(ValueError) as f:
            self.bauen(_payload(camera_matrices=_b64(
                np.tile(np.eye(4, dtype=np.float32), (5, 1, 1)))))
        self.assertIn('camera_matrices', str(f.exception))
