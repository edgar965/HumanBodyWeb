"""`Blendimportnetz`: die Streckung des Wegs „netz“ muss beim Leser ankommen (25.10.2026, zauberer_fantasy).

trimesh nennt seinen Basisrahmen „world“ und schreibt seine Wurzel so; ein Knoten dieses Namens fällt beim Lesen mit dem Basisrahmen zusammen, seine Matrix geht verloren. Die gedrehte Kopie der
Vorstufe (`eingabe_aufrecht.glb`, von trimesh geschrieben) trug die Streckung 2,04 an „world“ — „Mesh to 3D“ las 0,98 m statt 2,00 m, die Figur passte sich hockend an. Geprüft wird mit trimesh selbst,
dem Leser von Pose, Segmentierung und „Mesh to 3D“ — eine Rechnung über das JSON sähe den Fehler nicht.
"""
import tempfile
from pathlib import Path

import numpy as np
import trimesh
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.blendimportnetz import Blendimportnetz
from core.dienste.blendimportweg import Blendimportweg


class BasisrahmenTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _ordner():
        return tempfile.TemporaryDirectory(dir=str(Path(settings.TOOLS_ROOT) / 'ProjektTemp'))

    @staticmethod
    def _kiste(pfad):
        """1 m hohe Kiste, von trimesh geschrieben: Wurzel „world“ → Netzknoten."""
        kiste = trimesh.creation.box(extents=(0.4, 1.0, 0.3))
        kiste.apply_translation((0.0, 0.5, 0.0))
        kiste.export(str(pfad))

    @staticmethod
    def _hoehe(pfad):
        tief, hoch = trimesh.load(str(pfad), force='scene', process=False).bounds
        return float(hoch[1] - tief[1])

    def test_1_trimesh_glb_hat_den_knoten_world(self):
        """Voraussetzung des Falls: trimesh schreibt den Basisrahmen als Knoten in die Datei."""
        with self._ordner() as o:
            glb = Path(o) / 'kiste.glb'
            self._kiste(glb)
            self.assertTrue(Blendimportnetz._basisknoten(Blendimportweg.glb_json(glb)))

    def test_2_streckung_kommt_beim_leser_an(self):
        with self._ordner() as o:
            glb, ziel = Path(o) / 'kiste.glb', Path(o) / 'kiste_x2.glb'
            self._kiste(glb)
            Blendimportnetz._skaliert_schreiben(glb, ziel, Blendimportweg.glb_json(glb), 2.0)
            self.assertAlmostEqual(self._hoehe(ziel), 2.0, places=4)
            self.assertFalse(Blendimportnetz._basisknoten(Blendimportweg.glb_json(ziel)))
            self.assertAlmostEqual(Blendimportnetz._pruefen(ziel, 2.0), 2.0, places=4)

    def test_3_pruefung_wird_rot_wenn_die_streckung_verloren_geht(self):
        """Der Stand vor dem Fix: Streckung am Knoten „world“ — die Prüfung muss abbrechen."""
        with self._ordner() as o:
            glb, ziel = Path(o) / 'kiste.glb', Path(o) / 'kiste_alt.glb'
            self._kiste(glb)
            daten = Blendimportweg.glb_json(glb)
            alt = Blendimportnetz._basisknoten
            Blendimportnetz._basisknoten = classmethod(lambda cls, d: [])          # ohne Umbenennen, wie bis 24.10.2026
            try:
                Blendimportnetz._skaliert_schreiben(glb, ziel, daten, 2.0)
            finally:
                Blendimportnetz._basisknoten = alt
            self.assertAlmostEqual(self._hoehe(ziel), 1.0, places=4)
            with self.assertRaises(RuntimeError):
                Blendimportnetz._pruefen(ziel, 2.0)

    def test_4_glb_mit_einem_netzknoten_bleibt_wie_sie_war(self):
        """Tripo-Dateien (ein Knoten, der das Netz trägt): Name bleibt, Streckung am Knoten, gelesen 2 m."""
        with self._ordner() as o:
            glb, ziel = Path(o) / 'kiste.glb', Path(o) / 'kiste_x2.glb'
            kiste = trimesh.creation.box(extents=(0.4, 1.0, 0.3))
            kiste.apply_translation((0.0, 0.5, 0.0))
            szene = trimesh.Scene(base_frame='szene')
            szene.add_geometry(kiste, node_name='tripo_node', geom_name='kiste')
            szene.export(str(glb))
            daten = Blendimportweg.glb_json(glb)
            self.assertFalse(Blendimportnetz._basisknoten(daten))
            Blendimportnetz._skaliert_schreiben(glb, ziel, daten, 2.0)
            namen = [k.get('name') for k in Blendimportweg.glb_json(ziel)['nodes']]
            self.assertIn('tripo_node', namen)
            self.assertAlmostEqual(self._hoehe(ziel), 2.0, places=4)
            self.assertTrue(np.isfinite(Blendimportnetz._pruefen(ziel, 2.0)))
