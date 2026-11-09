"""`Ai2d3dgenesisstart.eingang`: Netz, Foto und Maske, die ein Job an die Kette gibt. Ohne Datenbank."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from core.dienste.ai2d3dgenesisstart import Ai2d3dgenesisstart
from core.dienste.mesh3daitest import Mesh3daitest


class Ai2d3dgenesisstartTest(unittest.TestCase):
    databases = []

    def _job(self, netz=True, befund=None, maske=True):
        ordner = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        (ordner / 'pshuman' / 'aufgerichtet').mkdir(parents=True)
        (ordner / 'foto.jpg').write_bytes(b'x')
        if netz:
            (ordner / 'pshuman' / 'result_clr_scale4_1.glb').write_bytes(b'x')
        if maske:
            (ordner / 'pshuman' / 'eingang_maske.png').write_bytes(b'x')
        if befund is not None:
            text = json.dumps(befund(ordner))
            (ordner / 'pshuman' / 'befund.json').write_text(text, encoding='utf-8')
        return ordner

    def test_groesse_vor_dem_einreihen(self):
        # Direkt nach `anlegen` gibt es noch keine test.json, `Mesh3daitest.pfad` kennt den Test nicht (Jobprobe_durant, 06.11.2026)
        wurzel = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        (wurzel / 'k').mkdir()
        (wurzel / 'k' / 'einstellung.json').write_text('{"geschlecht": "maennlich"}', encoding='utf-8')
        with mock.patch.object(Mesh3daitest, 'ordner', return_value=wurzel):
            Ai2d3dgenesisstart._groesse_setzen('k', 1.9)
        self.assertEqual(json.loads((wurzel / 'k' / 'einstellung.json').read_text(encoding='utf-8')), {'geschlecht': 'maennlich', 'koerpergroesse_m': 1.9})

    def test_ohne_netz_nichts(self):
        self.assertEqual(Ai2d3dgenesisstart.eingang(self._job(netz=False)), (None, None, None))

    def test_stehendes_foto_geht_mit(self):
        gerade = {'aufrichtung': [{'gedreht': False}]}
        ordner = self._job(befund=lambda o: dict(gerade, foto=str(o / 'foto.jpg')))
        netz, foto, maske = Ai2d3dgenesisstart.eingang(ordner)
        self.assertEqual(netz.name, 'result_clr_scale4_1.glb')
        self.assertEqual(foto, ordner / 'foto.jpg')
        self.assertEqual(maske, ordner / 'pshuman' / 'eingang_maske.png')

    def test_aufgerichtetes_foto_geht_vor(self):
        def befund(o):
            bild = o / 'pshuman' / 'aufgerichtet' / 'foto_0.png'
            bild.write_bytes(b'x')
            bild.with_name('maske_0.png').write_bytes(b'x')
            gedreht = {'gedreht': True, 'aufgerichtet': str(bild)}
            return {'foto': str(o / 'foto.jpg'), 'aufrichtung': [gedreht]}
        _, foto, maske = Ai2d3dgenesisstart.eingang(self._job(befund=befund))
        self.assertEqual(foto.name, 'foto_0.png')
        self.assertEqual(maske.name, 'maske_0.png')

    def test_ohne_maske_kein_foto(self):
        ordner = self._job(befund=lambda o: {'foto': str(o / 'foto.jpg')}, maske=False)
        netz, foto, maske = Ai2d3dgenesisstart.eingang(ordner)
        self.assertIsNotNone(netz)
        self.assertIsNone(foto)
        self.assertIsNone(maske)
