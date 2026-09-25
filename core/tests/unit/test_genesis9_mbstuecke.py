# -*- coding: utf-8 -*-
u"""MakeHuman-Kleidung als Genesis-9-Stueck (`G9mbstuecke`, 25.09.2026; Edgar:
„Probiere erstmal mit T-Shirt, markiere das als MB-T-Shirt oder so", dann
„mach das für alle Kleider von MakeHuman / Garment Code" — „Material, Stärke,
Glanz und viele andere. Portiere die auch alle").

Kunstdaten, keine Bibliothek:

1. `G9mhstueck.punkte`: Neunerzeile = Σ Gewicht · Grundpunkt + Versatz (dm) ×
   Achsenmassstab, Einerzeile = der Grundpunkt selbst; der Massstab kommt aus
   `x_scale` (Abstand der Referenzpunkte / Referenzwert).
2. `G9dsonschreiber._uvsatz`: die ersten UVs gehoeren den Punkten, eine
   abweichende Flaechenecke bekommt einen weiteren UV und steht in
   `polygon_vertex_indices` — und `G9basisnetz.uvsatz` liest es zurueck.
3. `G9pfade.finden`: eine Datei nur in der eigenen Wurzel wird dort gefunden,
   eine in beiden in der Daz-Bibliothek; `wurzel_von` nennt die richtige.
4. `G9mhstueck._mhclo_lesen`: `delete_verts` traegt seine Bereiche auf
   FOLGEZEILEN (kein Kopfschluessel) — sie duerfen nicht in die Vertexliste
   rutschen, auch wenn `material`/`vertexboneweights_file` dazwischenstehen.
5. `G9materialkanaele`: Bild-Kanaele (Normal Map, Cutout Opacity) landen in
   `scene.materials[].extra`, Skalarwerte (Glanz aus `1 − shininess`) in
   `scene.animations` — nur dort liest sie `Genesis9/material.py`.
6. `G9dforcemodifier.freiheit`: `1 − stiffness`, nach unten auf 0,15 begrenzt.

Sabotage: Versatz ohne Massstab -> Fall 1 rot; Nahtkopie weglassen -> Fall 2 rot;
`delete_verts` in die Vertexliste lassen -> Fall 4 rot.
"""
import gzip
import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.dforcemodifier import G9dforcemodifier
from Genesis9.dsonschreiber import G9dsonschreiber
from Genesis9.materialkanaele import G9materialkanaele
from Genesis9.mbkategorien import G9mbkategorien
from Genesis9.mhstueck import G9mhstueck
from Genesis9.pfade import G9pfade

WEGWERF = Path(__file__).resolve().parent / '_wegwerf'


class Mhstueck(SimpleTestCase):

    def test_1_regel_und_massstab(self):
        stueck = G9mhstueck.__new__(G9mhstueck)
        stueck.kopf = {'x_scale': (0, 1, 2.0)}           # Referenz 2 dm = 0,2 m
        stueck.zeilen = [['0', '1', '2', '0.5', '0.25', '0.25', '1', '0', '0'], ['2']]
        stueck.punktzahl = 2
        grund = np.array([[0.0, 0.0, 0.0], [0.4, 0.0, 0.0], [0.0, 1.0, 0.0]])
        p = stueck.punkte(grund)
        # x-Massstab 0,4 / 0,2 = 2; Versatz 1 dm = 0,1 m -> 0,2 m
        np.testing.assert_allclose(p[0], [0.5 * 0 + 0.25 * 0.4 + 0.2, 0.25, 0.0])
        np.testing.assert_allclose(p[1], grund[2])


class Uvsatz(SimpleTestCase):

    def test_2_nahtkopie_rundlauf(self):
        from Genesis9.basisnetz import G9basisnetz
        WEGWERF.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=WEGWERF) as ordner:
            s = G9dsonschreiber(ordner, 'MB', 'Probe', 'Probe')
            uvs = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]])
            # Punkt 0 hat in Flaeche 1 einen anderen UV (4) als in Flaeche 0 (0)
            satz = s._uvsatz(3, [[0, 1, 2], [2, 1, 0]], uvs, [[0, 1, 2], [2, 1, 4]])
            werte = satz['uv_set_library'][0]
            self.assertEqual(werte['uvs']['count'], 4)
            self.assertEqual(werte['polygon_vertex_indices'], [[1, 0, 3]])
            s._json(s.uvdatei, satz)
            with gzip.open(s.uvdatei, 'rb') as datei:
                self.assertIn('uv_set_library', json.loads(datei.read().decode('utf-8')))
            with mock.patch('Genesis9.dson.G9dson.aus_url') as aus_url:
                from Genesis9.dson import G9dson
                aus_url.return_value = (G9dson(str(s.uvdatei), satz), 'default')
                gelesen, ueber = G9basisnetz.uvsatz('egal')
            self.assertEqual(ueber, {(1, 0): 3})
            np.testing.assert_allclose(gelesen[3], [0.5, 0.5])


class Wurzeln(SimpleTestCase):

    def test_3_finden_in_beiden_wurzeln(self):
        WEGWERF.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=WEGWERF) as ordner:
            daz, eigen = Path(ordner) / 'daz', Path(ordner) / 'eigen'
            for wurzel in (daz, eigen):
                (wurzel / 'data').mkdir(parents=True)
                (wurzel / 'data' / 'beide.dsf').write_text('x')
            (eigen / 'data' / 'nur_eigen.dsf').write_text('x')
            with mock.patch.dict(os.environ, {G9pfade.UMGEBUNG_EIGENE: str(eigen)}):
                G9pfade.setzen(daz)
                try:
                    self.assertEqual(G9pfade.finden('/data/nur_eigen.dsf'), eigen / 'data' / 'nur_eigen.dsf')
                    self.assertEqual(G9pfade.finden('data/beide.dsf'), daz / 'data' / 'beide.dsf')
                    pfad, kennung = G9pfade.aufloesen('/data/nur_eigen.dsf#k')
                    self.assertEqual((pfad, kennung), (eigen / 'data' / 'nur_eigen.dsf', 'k'))
                    self.assertEqual(G9pfade.wurzel_von(eigen / 'data'), eigen)
                    self.assertEqual(G9pfade.wurzel_von(daz / 'data'), daz)
                finally:
                    G9pfade.zuruecksetzen()


class Mhclolesen(SimpleTestCase):

    def _schreiben(self, ordner, zeilen):
        pfad = ordner / 'probe.mhclo'
        pfad.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
        return pfad

    def test_4_delete_verts_nach_verts_und_zwischen_kopfzeilen(self):
        u"""Wie `shoes02`: `verts 0` VOR `material`; wie die Handschuhe:
        `delete_verts` traegt seine Bereiche auf eigenen Zeilen."""
        WEGWERF.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=WEGWERF) as ordner:
            ordner = Path(ordner)
            pfad = self._schreiben(ordner, [
                'name probe', 'verts 0', 'material probe.mhmat',
                'vertexboneweights_file probe.jsonw',
                '0 1 2 0.5 0.25 0.25 1.0 0.0 0.0',
                'delete_verts',
                '10 - 20 25 30 - 40',
                '50',
            ])
            kopf, zeilen = G9mhstueck._mhclo_lesen(pfad)
            self.assertEqual(kopf.get('material'), 'probe.mhmat')
            self.assertEqual(len(zeilen), 1)
            self.assertEqual(zeilen[0][:3], ['0', '1', '2'])

    def test_5_sabotage_delete_verts_als_kopfschluessel(self):
        u"""Gegenprobe zu Fall 4: `delete_verts` als GEWOEHNLICHER Kopfschluessel
        (die Fassung vor 25.09.2026) laesst seine Folgezeilen in die Vertexliste
        rutschen — 2 Zeilen zu viel statt 1 echter Punktzuordnung."""
        WEGWERF.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=WEGWERF) as ordner:
            pfad = self._schreiben(Path(ordner), [
                'verts 0',
                '0 1 2 0.5 0.25 0.25 1.0 0.0 0.0',
                'delete_verts',
                '10 - 20 25 30 - 40',
            ])
            with mock.patch.object(G9mhstueck, '_MODUSSCHLUESSEL', frozenset(('verts',))), \
                 mock.patch.object(G9mhstueck, '_KOPFSCHLUESSEL',
                                   G9mhstueck._KOPFSCHLUESSEL | {'delete_verts'}):
                _kopf, zeilen = G9mhstueck._mhclo_lesen(pfad)
            self.assertEqual(len(zeilen), 2)  # richtig waere 1


class Materialkanaele(SimpleTestCase):

    def test_6_bild_und_wertkanaele_getrennt(self):
        extra = G9materialkanaele.extra({'normalen': '/a/norm.png', 'bild': '/a/diff.png'})
        self.assertEqual(extra, [{'type': 'studio_material_channels',
                                  'channels': [{'channel': {'id': 'Normal Map',
                                                            'image_file': '/a/norm.png'}}]}])
        animationen = G9materialkanaele.animationen('Grp', {'shininess': 0.8, 'opacity': 0.5},
                                                     hat_alpha_bild=False)
        namen = {a['url'].rsplit('/', 2)[-2] for a in animationen}
        self.assertEqual(namen, {'Glossy Roughness', 'Cutout Opacity'})
        # Cutout Opacity entfaellt, wenn schon ein Alphabild geht:
        ohne_opacity = G9materialkanaele.animationen('Grp', {'opacity': 0.5}, hat_alpha_bild=True)
        self.assertEqual(ohne_opacity, [])


class Dforce(SimpleTestCase):

    def test_7_freiheit_begrenzt(self):
        self.assertAlmostEqual(G9dforcemodifier.freiheit(0.8), 0.2)
        self.assertEqual(G9dforcemodifier.freiheit(1.0), G9dforcemodifier.MINDESTFREIHEIT)
        self.assertEqual(G9dforcemodifier.freiheit(None), 1.0 - G9dforcemodifier.STANDARD_STIFFNESS)
        mod = G9dforcemodifier.modifikator('Geo', 3, 0.8)
        self.assertEqual(mod['extra'][0]['influence_weights']['values'], [[0, 0.2], [1, 0.2], [2, 0.2]])


class Kategorien(SimpleTestCase):

    def test_8_suit_und_armor_schlagen_den_ordner(self):
        self.assertEqual(G9mbkategorien.fuer('tops', 'female_casualsuit01')[1],
                         '/Default/Wardrobe/Full-Body')
        self.assertEqual(G9mbkategorien.fuer('tops', 'matcreator_mc-scifi-armor_guardian')[1],
                         '/Default/Wardrobe/Armor')
        self.assertEqual(G9mbkategorien.fuer('accessories', 'v0rt3x_stockings_black')[1],
                         '/Default/Wardrobe/Socks')
        self.assertEqual(G9mbkategorien.fuer('accessories', 'toigo_gloves_long')[1],
                         '/Default/Accessories')
