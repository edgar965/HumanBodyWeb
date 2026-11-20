"""`Exportleistekette`: die Stücke der Seite für den Render auflösen (20.11.2026, Edgar „Weg 2“: Testseite und Render zeigen dasselbe Ergebnis).

Geprüft ohne Ablage auf der Platte (`Meshgenesistestkleider`, `Meshgenesisteststoff`, `Meshgenesistesthaar` über `patch`): Namen der Ablage aus der BVH, nur gültige Adressen,
`kette_seite` bleibt zum Nachrechnen, ein Stück ohne Ablage fällt aus `kette`. Läuft nur auf Ansage; nicht gelaufen beim Schreiben (20.11.2026).
Sabotage (von Hand): in `ADRESSE` das `$` streichen → „fremde Adresse“ rot; in `aufloesen` `kette_seite` weglassen → „bleibt zum Nachrechnen“ rot.
"""
import unittest
from pathlib import Path
from unittest.mock import patch

from core.dienste.exportleistekette import Exportleistekette

K = 'zauberer_mesh_genesis_23'
ADR = '/api/meshgenesis/test/%s/kleid/maennlich/z/%%s' % K


class AufloesenTest(unittest.TestCase):
    databases = []

    def setUp(self):
        self.patches = [patch('core.dienste.exportleistekette.Meshgenesistestkleider.stueck_ordner', return_value='_test/x'),
                        patch('core.dienste.exportleistekette.Meshgenesistestkleider.ordner', return_value=Path('A:/nirgends')),
                        patch('core.dienste.exportleistekette.Meshgenesisteststoff.dateien',
                              side_effect=lambda k, g, w, s, b: (Path('s.npz'), Path('s.json')) if s == 'ki_oberteil' else None),
                        patch('core.dienste.exportleistekette.Meshgenesistesthaar.dateien',
                              side_effect=lambda k, g, w, s, b: (Path('h.npz'), Path('h.json')) if s == 'ki_haar' else None)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def _seite(self, *stuecke):
        return {'figur': 'x', 'kette': [{'name': 'ki_' + s, 'adresse': ADR % s, 'art': a} for s, a in stuecke]}

    def test_name_der_ablage_aus_der_bvh(self):
        self.assertEqual(Exportleistekette.wahl(r'A:\3DTools\3DObjects\animations\bvh\A_Results\DanceKurz.bvh'), 'A_Results/DanceKurz')
        self.assertIsNone(Exportleistekette.wahl(''))

    def test_stuecke_mit_ablage(self):
        st = Exportleistekette.aufloesen(self._seite(('ki_oberteil', 'oberteil'), ('ki_haar', 'haar'), ('ki_schuh_1', 'schuh')), 'A:/b/A_Results/DanceKurz.bvh')
        self.assertEqual([(e['name'], bool(e['stoff']), bool(e['haar'])) for e in st['kette']], [('ki_ki_oberteil', True, False), ('ki_ki_haar', False, True)])
        self.assertEqual(st['figur'], 'x')

    def test_bleibt_zum_nachrechnen(self):
        st = Exportleistekette.aufloesen(self._seite(('ki_oberteil', 'oberteil'), ('ki_schuh_1', 'schuh')), 'A:/b/A_Results/DanceKurz.bvh')
        self.assertEqual([e['name'] for e in st['kette_seite']], ['ki_ki_oberteil', 'ki_ki_schuh_1'])
        nochmal = Exportleistekette.aufloesen(st, 'A:/b/A_Results/DanceKurz.bvh')
        self.assertEqual([e['name'] for e in nochmal['kette']], ['ki_ki_oberteil'])

    def test_fremde_adresse(self):
        st = {'kette': [{'name': 'boese', 'adresse': '/api/meshgenesis/test/../kleid/maennlich/z/x', 'art': 'haar'},
                        {'name': 'ki_x', 'adresse': (ADR % 'ki_haar') + '/../../etwas', 'art': 'haar'},
                        {'name': 'a b', 'adresse': ADR % 'ki_haar', 'art': 'haar'}]}
        self.assertEqual(Exportleistekette.seite(st), [])


if __name__ == '__main__':
    unittest.main()
