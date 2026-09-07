# -*- coding: utf-8 -*-
u"""MakeHuman-Figur: Basisnetz, Garderobe und der Sitz der Kleidung.

WARUM (Edgar, 06.09.2026: „unter anderem gibt es garments fuer MakeHuman, die
sollten dann perfekt funktionieren"): „Perfekt" ist hier keine Meinung,
sondern messbar. Diese Faelle nageln fest, was gemessen wurde:

    1. Das Basisnetz kommt in Metern mit Y oben, Fuesse bei 0, 13.380 Punkte
       und 166,6 cm hoch. Ein Achsentausch, den Three.js nicht erwartet,
       faellt hier auf.
    2. Der Umlaufsinn stimmt: Das eingeschlossene Volumen des geschlossenen
       Koerpers ist POSITIV (rund 55 Liter). Negativ hiesse Normalen nach
       innen — die Figur waere von aussen unsichtbar.
    3. Ein Kleidungsstueck sitzt an: Kein Punkt weiter als 4 cm von der
       naechsten Hautstelle. Der Anzug misst 8,2 mm im Median.
    4. Die `delete_verts` wirken: Mit angezogenem Anzug hat das Koerpernetz
       WENIGER Flaechen. Ohne das steht die Haut durch den Stoff (gemessen:
       23,5 % der Anzugpunkte liegen innerhalb der Haut).
    5. Ein LFS-Zeiger ist keine Textur. `female_casualsuit01_diffuse.png` ist
       135 Bytes Text; die Antwort darf `has_texture` NICHT melden, sonst
       bleibt das Stueck weiss und die Farbe aus der `.mhmat` wird nie
       versucht.
    6. Unbekannte Namen sind 404, nicht 500.
"""
import base64
import json

import numpy as np
from django.test import SimpleTestCase

from MakeHuman.basisnetz import Mhbasisnetz


def _feld(b64, typ, breite):
    return np.frombuffer(base64.b64decode(b64), dtype=typ).reshape(-1, breite)


class MhfigurTest(SimpleTestCase):

    databases = []

    #: Ein Stueck mit Textur-Zeiger statt Textur und mit `delete_verts`.
    ANZUG = 'tops/female_casualsuit01'

    def setUp(self):
        if not Mhbasisnetz.vorhanden():
            self.skipTest('HumanBody/MakeHuman/base.obj fehlt')

    # --------------------------------------------------------------- Figuren

    def test_liste_nennt_den_basiskoerper(self):
        antwort = self.client.get('/api/character/mh-figur/')
        self.assertEqual(antwort.status_code, 200)
        figuren = json.loads(antwort.content)['figuren']
        self.assertEqual(len(figuren), 1)
        self.assertEqual(figuren[0]['name'], 'basis')
        self.assertEqual(figuren[0]['punkte'], 13380)
        self.assertAlmostEqual(figuren[0]['hoehe'], 1.666, delta=0.01)
        teile = {t['schluessel']: t['flaechen'] for t in figuren[0]['teile']}
        self.assertEqual(teile['koerper'], 13378)
        self.assertGreater(teile['helfer'], 0)
        self.assertGreater(teile['gelenke'], 0)

    def test_netz_in_metern_y_oben(self):
        daten = self._netz()
        punkte = _feld(daten['vertices'], np.float32, 3)
        self.assertEqual(len(punkte), 13380)
        self.assertAlmostEqual(float(punkte[:, 1].min()), 0.0, delta=0.001,
                               msg='Fuesse nicht am Boden')
        self.assertAlmostEqual(daten['hoehe'], 1.666, delta=0.01)

    def test_umlaufsinn_zeigt_nach_aussen(self):
        u"""Positives Volumen = Normalen nach aussen (siehe Mhbasisnetz)."""
        daten = self._netz()
        punkte = _feld(daten['vertices'], np.float32, 3).astype(np.float64)
        dreiecke = _feld(daten['faces'], np.uint32, 3)
        v0, v1, v2 = (punkte[dreiecke[:, i]] for i in range(3))
        volumen = float(np.einsum('ij,ij->i', v0, np.cross(v1, v2)).sum() / 6.0)
        self.assertGreater(volumen, 0.03, 'Umlaufsinn gedreht')
        self.assertLess(volumen, 0.12, 'Volumen unplausibel gross')

    def test_glaetten_vervierfacht_die_flaechen(self):
        grob = self._netz()
        glatt = self._netz('?glaetten=1')
        self.assertTrue(glatt['glatt'])
        self.assertEqual(glatt['face_count'], grob['face_count'] * 4)
        self.assertAlmostEqual(glatt['hoehe'], grob['hoehe'], delta=0.01)

    def test_unbekanntes_modell_ist_404(self):
        antwort = self.client.get('/api/character/mh-figur/quatsch/netz/')
        self.assertEqual(antwort.status_code, 404)

    # ------------------------------------------------------------- Garderobe

    def test_garderobe_nennt_nur_mhclo_stuecke(self):
        antwort = self.client.get('/api/character/mh-figur/garderobe/')
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertGreater(daten['anzahl'], 100)
        kennungen = {s['id'] for s in daten['stuecke']}
        self.assertIn(self.ANZUG, kennungen)
        for stueck in daten['stuecke']:
            self.assertIn('/', stueck['id'])
            self.assertTrue(stueck['kategoriename'])

    def test_kleid_sitzt_am_koerper(self):
        stueck = self._kleid(self.ANZUG)
        stoff = _feld(stueck['vertices'], np.float32, 3).astype(np.float64)
        haut = _feld(self._netz()['vertices'], np.float32, 3).astype(np.float64)
        abstand = self._naechster_abstand(stoff, haut)
        self.assertLess(float(np.median(abstand)), 0.02,
                        'Median-Abstand zur Haut zu gross')
        self.assertLess(float(abstand.max()), 0.04,
                        'Ein Stoffpunkt schwebt weit neben dem Koerper')

    def test_uvs_kommen_je_ecke(self):
        u"""Punkte werden je (Punkt, Texturpunkt) aufgeteilt — sonst Nahtfehler."""
        stueck = self._kleid(self.ANZUG)
        self.assertIn('uvs', stueck)
        uvs = _feld(stueck['uvs'], np.float32, 2)
        self.assertEqual(len(uvs), stueck['vertex_count'])

    def test_lfs_zeiger_ist_keine_textur(self):
        stueck = self._kleid(self.ANZUG)
        self.assertFalse(stueck.get('has_texture'),
                         'Ein 135-Byte-LFS-Zeiger wurde als Textur gemeldet')
        self.assertIn('mat_color', stueck)

    def test_unbekanntes_kleid_ist_404(self):
        antwort = self.client.get(
            '/api/character/mh-figur/garderobe/tops/quatsch/netz/')
        self.assertEqual(antwort.status_code, 404)

    # ----------------------------------------------------------- Loeschmaske

    def test_kleidung_blendet_die_haut_darunter_aus(self):
        ohne = self._netz()
        mit = self._netz('?verdeckt=%s' % self.ANZUG)
        self.assertEqual(mit['verdeckt'], [self.ANZUG])
        self.assertLess(mit['face_count'], ohne['face_count'],
                        'delete_verts wirkt nicht')
        self.assertGreater(mit['face_count'], ohne['face_count'] * 0.5,
                           'Es wurde deutlich zu viel weggenommen')

    def test_hoehe_bleibt_trotz_schuhen(self):
        u"""Schuhe nehmen die Fuesse weg — die Figur darf nicht schrumpfen."""
        schuhe = 'shoes/toigo_mj_cloth_shoes'
        if not self._kennt(schuhe):
            self.skipTest('%s nicht in der Bibliothek' % schuhe)
        self.assertAlmostEqual(self._netz('?verdeckt=%s' % schuhe)['hoehe'],
                               self._netz()['hoehe'], delta=0.001)

    def test_fremde_kennung_wird_verworfen(self):
        daten = self._netz('?verdeckt=../../etc/passwd')
        self.assertEqual(daten['verdeckt'], [])

    # ---------------------------------------------------------------- Helfer

    def _netz(self, abfrage=''):
        antwort = self.client.get(
            '/api/character/mh-figur/basis/netz/%s' % abfrage)
        self.assertEqual(antwort.status_code, 200)
        return json.loads(antwort.content)

    def _kleid(self, kennung):
        antwort = self.client.get(
            '/api/character/mh-figur/garderobe/%s/netz/' % kennung)
        if antwort.status_code == 404:
            self.skipTest('%s nicht in der Bibliothek' % kennung)
        self.assertEqual(antwort.status_code, 200)
        return json.loads(antwort.content)

    def _kennt(self, kennung):
        antwort = self.client.get('/api/character/mh-figur/garderobe/')
        return kennung in {s['id']
                           for s in json.loads(antwort.content)['stuecke']}

    @staticmethod
    def _naechster_abstand(stoff, haut):
        u"""Je Stoffpunkt der Abstand zur naechsten Hautstelle, in Metern."""
        from scipy.spatial import cKDTree
        abstand, _ = cKDTree(haut).query(stoff)
        return abstand
