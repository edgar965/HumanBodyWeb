"""`Kettenablage.leeren`: Ende der Foto-Kette im Skriptdienst, dort kommt `atexit` erst mit dem Ende des Dienstes. Ohne Datenbank, ohne Karte."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from django.conf import settings

_quelle = importlib.util.spec_from_file_location('nurfotos_ablage_probe', Path(settings.TOOLS_ROOT) / 'fotogenesis' / 'nurfotos_ablage.py')
_modul = importlib.util.module_from_spec(_quelle)
_quelle.loader.exec_module(_modul)
Kettenablage = _modul.Kettenablage


class KettenablageLeerenTest(unittest.TestCase):
    databases = []

    def test_schreibt_und_gibt_den_speicher_frei(self):
        datei = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf')) / 'nurfotos_einpassen.json'
        Kettenablage.json_schreiben(datei, {'gueltig': True})
        self.assertFalse(datei.is_file())
        Kettenablage.leeren(log=lambda _text: None)
        self.assertEqual(json.loads(datei.read_text(encoding='utf-8')), {'gueltig': True})
        self.assertNotIn(datei, Kettenablage._ram)
        self.assertEqual(Kettenablage.json(datei), {'gueltig': True})        # danach von der Platte
