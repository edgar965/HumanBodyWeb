"""Die Physik (Stoff, Haar) rechnet der MP4-Export, nicht der Job (25.11.2026, Edgar: „physik muss doch erst beim export in mp4 berechnet werden“).

Geprüft: „stoff“ und „haar“ stehen in keiner Schrittliste; `Exportleistekette.fehlend` nennt Stücke ohne Ablage, auch wenn die Kette sie noch nie gerechnet hat, und nur solche, die der Kettenschritt
rechnet; eine Ablage, die älter ist als das Stück, gilt nicht. Läuft nur auf Ansage; beim Schreiben nicht gelaufen.
Sabotage (von Hand): „stoff“ wieder in `NACH` → „keine Physik im Job“ rot; in `veraltet` `>` zu `<` → „ältere Ablage“ rot.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from django.conf import settings

from core.dienste.exportleistekette import Exportleistekette
from core.dienste.meshgenesisrechengenesiszuerst import Meshgenesisrechengenesiszuerst
from core.dienste.meshgenesisrechenlauf import Meshgenesisrechenlauf
from core.dienste.meshgenesisteststoff import Meshgenesisteststoff

ADR = '/api/meshgenesis/test/zauberer_mesh_genesis_23/kleid/maennlich/%s/%s'


class PhysikBeimExportTest(unittest.TestCase):
    databases = []

    def test_keine_physik_im_job(self):
        schritte = [s[0] for s in Meshgenesisrechengenesiszuerst.einreihen(Meshgenesisrechenlauf.SCHRITTE)]
        self.assertNotIn('stoff', schritte)
        self.assertNotIn('haar', schritte)
        self.assertEqual(schritte[-1], 'pruefung_p')

    def test_fehlend_ohne_frueheren_lauf(self):
        seite = {'kette': [{'name': 'ki_' + s, 'adresse': ADR % (w, s), 'art': a} for w, s, a in (('z', 'ki_oberteil', 'oberteil'), ('z', 'ki_haar', 'haar'), ('z', 'ki_schuh_1', 'schuh'))]}
        rechenbar = {'stoff': {('z', 'ki_oberteil')}, 'haar': {('z', 'ki_haar')}}
        with patch('core.dienste.exportleistekette.Meshgenesistestkleider.stueck_ordner', return_value='x'), \
                patch.object(Exportleistekette, 'dateien', staticmethod(lambda *a: None)), \
                patch.object(Exportleistekette, 'rechenbar', staticmethod(lambda k, g, schritt: rechenbar[schritt])):
            fehlt = Exportleistekette.fehlend(seite, 'A:/b/A_Results/DanceKurz.bvh')
        self.assertEqual(sorted((s, x) for _k, _g, s, x in fehlt), [('haar', 'ki_haar'), ('stoff', 'ki_oberteil')])

    def test_aeltere_ablage_gilt_nicht(self):
        with tempfile.TemporaryDirectory(dir=settings.TOOLS_ROOT / 'ProjektTemp') as t:
            ordner = Path(t) / 'ki_oberteil' / 'stoff'
            netz = Path(t) / 'ki_oberteil' / 'anzeige' / 'netz.npz'
            ordner.mkdir(parents=True)
            netz.parent.mkdir()
            feld = ordner / 'A__B.npz'
            for p in (feld, netz):
                p.write_bytes(b'x')
            os.utime(feld, (1000, 1000))
            os.utime(netz, (2000, 2000))
            self.assertTrue(Meshgenesisteststoff.veraltet(ordner, feld))
            os.utime(feld, (3000, 3000))
            self.assertFalse(Meshgenesisteststoff.veraltet(ordner, feld))


if __name__ == '__main__':
    unittest.main()
