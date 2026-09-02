# -*- coding: utf-8 -*-
u"""Was zusammengelegt wurde, darf nicht zurückwandern.

Beim Aufteilen von `collision/` sind mehrfach abgeschriebene Bloecke in
gemeinsame Module gewandert (`arbeitsordner`, `bakedatei`,
`netzmathematik`). Dieser Fall haelt fest, dass die Skripte sie auch
wirklich benutzen — eine zurueckkopierte Fassung faellt sonst niemandem
auf, bis die beiden auseinanderlaufen.

Stand bis zum 01.09.2026 in `test_kollision_importwege.py`, zusammen
mit der Pruefung der beiden Ladewege — zwei eigenstaendige Klassen in
einer Datei.

Aufruf:  python manage.py test core.tests.unit.test_kollision_gemeinsam
"""
from pathlib import Path

from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad


class GemeinsameModuleTest(SimpleTestCase):
    u"""Was zusammengelegt wurde, darf nicht zurückwandern."""

    #: Namen, die am 31.08.2026 aus `warp_sim` und `skinning_only`
    #: nach `bakedatei`/`netzmathematik` zogen.
    GEZOGEN = ('_skin_rigid_frame', '_compute_vertex_normals',
               '_push_outside_body', '_naechste_nachbarn',
               'load_scene_npz', 'save_bake')

    def test_keine_eigene_fassung_mehr(self):
        wurzel = Path(Humanbodypfad.setzen() or '.') / 'collision'
        treffer = []
        for name in ('warp_sim', 'skinning_only'):
            for zeile in (wurzel / ('%s.py' % name)).read_text(
                    encoding='utf-8').splitlines():
                for gezogen in self.GEZOGEN:
                    if zeile.startswith('def %s(' % gezogen):
                        treffer.append('%s: %s' % (name, zeile.strip()))
        self.assertEqual(treffer, [],
                         'Die Rechnung steht wieder doppelt in collision/')

    def test_haeuten_liest_die_spaltenzahl_aus_den_daten(self):
        u"""Die alte Fassung in `skinning_only` lief über feste `range(4)`.

        Mit drei Einflüssen je Vertex hätte sie eine Spalte zu viel
        gelesen — `skin_idx[:, 3]` gibt es dann nicht, also ein
        IndexError mitten im Bake. Mit fünf hätte sie eine liegen
        lassen: kein Fehler, nur ein falsch gewichteter Vertex.
        """
        import numpy as np

        Humanbodypfad.setzen()
        from collision.netzmathematik import Netzmathematik

        rest = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
        # DREI Einflüsse, nicht vier: alles Gewicht auf Knochen 0.
        skin_idx = np.array([[0, 0, 0]], dtype=np.int64)
        skin_w = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
        inv_bind = np.array([np.eye(4)], dtype=np.float32)
        verschiebung = np.eye(4, dtype=np.float32)
        verschiebung[0, 3] = 5.0

        ergebnis = Netzmathematik.haeuten(rest, skin_idx, skin_w, inv_bind,
                                          np.array([verschiebung]))
        np.testing.assert_allclose(ergebnis, [[6.0, 0.0, 0.0]], atol=1e-6)
