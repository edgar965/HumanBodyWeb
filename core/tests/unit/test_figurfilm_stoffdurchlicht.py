"""`Material.woerterbuch` mit `stoff_durchlicht` und die Regel des Profils (06.11.2026, schwarze Innenseite der Hose im Film).
    1  mit dem Feld: `principledthin` mit `diff_trans`, kein `twosided` nötig
    2  ohne das Feld: unverändert `twosided`
    3  Haut bleibt unberührt, auch mit dem Feld
    4  das Profil gibt das Feld den KI-Stücken, nicht dem Haar, nicht den übrigen Stücken
Sabotage (von Hand): Regel ohne `(?!haar)` → Fall 4 rot.
"""
import json
import re
import sys
import unittest

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))


class Fall(unittest.TestCase):
    def woerterbuch(self, **felder):
        from Figurfilm.material import Material
        return Material.woerterbuch(dict({'art': 'farbe', 'rgb': [0.4, 0.4, 0.5]}, **felder))

    def test_stoff_duenn(self):
        w = self.woerterbuch(stoff_durchlicht=0.6)
        self.assertEqual(w['type'], 'principledthin')
        self.assertEqual(w['diff_trans'], 0.6)

    def test_ohne_feld_unveraendert(self):
        self.assertEqual(self.woerterbuch()['type'], 'twosided')

    def test_haut_bleibt(self):
        self.assertNotEqual(self.woerterbuch(art='haut', stoff_durchlicht=0.6)['type'], 'principledthin')

    def test_profil(self):
        pfad = settings.TOOLS_ROOT / 'Figurfilm' / 'standfilm' / 'profil_generisch.json'
        regeln = json.loads(pfad.read_text(encoding='utf-8'))['werkstoffe']

        def feld(name):
            return next(r['werkstoff'] for r in regeln if re.search(r['muster'], name)).get('stoff_durchlicht')

        self.assertTrue(feld('kleidung__eigen_foto_ki_ki_hose__7_g0'))
        self.assertIsNone(feld('kleidung__eigen_foto_ki_ki_haar__6_g0'))
        self.assertIsNone(feld('kleidung__gc_hemd__2_g0'))
        self.assertIsNone(feld('kleidung__eigen_foto_jacke__1_g0'))
