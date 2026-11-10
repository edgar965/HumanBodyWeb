"""`Netzvorrat.ort` nach dem Umzug von `3DObjects/models/Tripo` (06.11.2026; ältere `apose.npz` tragen den alten Pfad).
    1  am alten Ort fehlt die Datei, am neuen liegt sie: der neue
    2  am alten Ort liegt sie noch: der alte
    3  sie liegt nirgends: der gespeicherte, damit der Fehler ihn nennt
Sabotage (von Hand): `UMZUG` auf zwei gleiche Texte setzen → Fall 1 rot.
"""
import sys
import tempfile
import unittest
from pathlib import Path

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))
from meshgenesis_netzvorrat import Netzvorrat  # noqa: E402


class TestOrt(unittest.TestCase):
    databases = []

    def setUp(self):
        self.ablage = tempfile.TemporaryDirectory(dir=settings.TOOLS_ROOT / 'ProjektTemp')
        self.addCleanup(self.ablage.cleanup)
        self.wurzel = Path(self.ablage.name)
        self.alt = self.wurzel / 'models' / 'Tripo' / 'a.glb'
        self.neu = self.wurzel / 'Tripo3D' / 'a.glb'

    @staticmethod
    def _anlegen(pfad):
        pfad.parent.mkdir(parents=True)
        pfad.write_bytes(b'x')

    def test_neuer_ort(self):
        self._anlegen(self.neu)
        self.assertEqual(Netzvorrat.ort(self.alt), self.neu)

    def test_alter_ort_bleibt(self):
        self._anlegen(self.alt)
        self._anlegen(self.neu)
        self.assertEqual(Netzvorrat.ort(self.alt), self.alt)

    def test_nirgends(self):
        self.assertEqual(Netzvorrat.ort(self.alt), self.alt)
