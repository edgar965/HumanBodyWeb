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

import numpy as np
from django.test import SimpleTestCase
from ._humanbodypfad import Humanbodypfad


class Probepaket:
    """Ein Cloth-Paket, wie es der Browser schickt."""

    @staticmethod
    def b64(arr):
        return base64.b64encode(np.asarray(arr).tobytes()).decode('ascii')

    @staticmethod
    def bauen(vcount=6, n_bones=3, n_frames=2, **abweichung):
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
            'positions': Probepaket.b64(positions),
            'faces': Probepaket.b64(faces),
            'skin_indices': Probepaket.b64(skin_idx),
            'skin_weights': Probepaket.b64(skin_w),
            'bone_names': ['DEF-spine', 'DEF-thigh.L', 'DEF-thigh.R'][:n_bones],
            'inv_bind': Probepaket.b64(einheit),
            'anim_frames': n_frames,
            'anim_fps': 30.0,
            'anim_matrices': Probepaket.b64(anim),
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
        Humanbodypfad.setzen()
        from collision.bridge import payload_to_scene_input
        cls.bauen = staticmethod(payload_to_scene_input)

    # ------------------------------------------------------------ Gegenprobe

    def test_gueltiges_paket_geht_durch(self):
        """Ohne diesen Test wäre jede Absage unten wertlos."""
        szene = self.bauen(Probepaket.bauen())
        self.assertEqual(szene.rigid_vertices.shape, (6, 3))
        self.assertEqual(szene.num_bones(), 3)
        self.assertEqual(szene.animation.frame_count, 2)

    def test_kleidung_wird_ausgeschnitten(self):
        szene = self.bauen(Probepaket.bauen(
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
                    self.bauen(Probepaket.bauen(bone_vertex_ranges={
                        'DEF-spine': {'start': start, 'count': count}}))
                self.assertIn('bone_vertex_ranges', str(f.exception))

    def test_knochenindex_ueber_der_knochenzahl(self):
        idx = np.zeros((6, 4), dtype=np.uint32)
        idx[0, 0] = 70000                      # wickelt in uint16 auf 4464 um
        with self.assertRaises(ValueError) as f:
            self.bauen(Probepaket.bauen(skin_indices=Probepaket.b64(idx)))
        self.assertIn('skin_indices', str(f.exception))

    def test_ungueltiges_base64_wird_nicht_stillschweigend_gekuerzt(self):
        with self.assertRaises(ValueError) as f:
            self.bauen(Probepaket.bauen(positions='QUJD!!!'))
        self.assertIn('positions', str(f.exception))

    def test_meldung_nennt_das_feld(self):
        """Vorher: acht Felder, eine nackte reshape-Meldung."""
        faelle = {
            'positions': Probepaket.b64(np.zeros((2, 3), np.float32)),
            'skin_weights': Probepaket.b64(np.zeros((2, 4), np.float32)),
            'inv_bind': Probepaket.b64(np.zeros((2, 4, 4), np.float32)),
            'anim_matrices': Probepaket.b64(np.zeros((1, 2, 4, 4), np.float32)),
        }
        for feld, wert in faelle.items():
            with self.subTest(feld=feld):
                with self.assertRaises(ValueError) as f:
                    self.bauen(Probepaket.bauen(**{feld: wert}))
                self.assertIn(feld, str(f.exception))

    # ---------------------------------------------------------- weitere Wege

    def test_dreiecke_zeigen_ins_leere(self):
        ins_leere = np.array([[0, 1, 99]], dtype=np.uint32)
        with self.assertRaises(ValueError) as f:
            self.bauen(Probepaket.bauen(faces=Probepaket.b64(ins_leere)))
        self.assertIn('faces', str(f.exception))

    def test_singulaere_bindematrix_nennt_den_knochen(self):
        kaputt = np.tile(np.eye(4, dtype=np.float32), (3, 1, 1))
        kaputt[1] = 0.0
        with self.assertRaises(ValueError) as f:
            self.bauen(Probepaket.bauen(inv_bind=Probepaket.b64(kaputt)))
        self.assertIn('DEF-thigh.L', str(f.exception))

    def test_leere_oder_falsche_zaehler(self):
        for feld, wert in (('vertex_count', 0), ('anim_frames', 0)):
            with self.subTest(feld=feld):
                with self.assertRaises(ValueError):
                    self.bauen(Probepaket.bauen(**{feld: wert}))
        with self.assertRaises(ValueError):
            self.bauen(Probepaket.bauen(bone_names=[]))

    def test_kameraspur_mit_falscher_framezahl(self):
        with self.assertRaises(ValueError) as f:
            self.bauen(Probepaket.bauen(camera_matrices=Probepaket.b64(
                np.tile(np.eye(4, dtype=np.float32), (5, 1, 1)))))
        self.assertIn('camera_matrices', str(f.exception))
