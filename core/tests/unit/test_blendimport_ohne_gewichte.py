# -*- coding: utf-8 -*-
"""Blender-Import: eine .blend OHNE Skelett wird trotzdem eingelesen (09.10.2026).

Edgar: „Fehlermeldung bei dem Import einer Blender Figur … dann fixe das." Die Meldung vom 08.10. („Das Modell hat kein Skelett")
war richtig, der Import hat das Modell aber damit abgewiesen. Gemessen an „Beautiful Asian girl 5.0.blend" (Blender 5.2.2): 15 Netze,
0 Armaturen, 3,26 m hoch (nicht 1,75 m), Character-Creator-Namen. Jetzt exportiert `blendexport.py` solche Netze ohne Hautgewichte
(`ohne_rig`), und `Blendimportrollen` ordnet sie nach Maßen, Material und Namen zu. Die Zahlen unten sind die gemessenen Maße
(Blender-Achsen, Meter, `ProjektTemp/_wegwerf/rigloser_inventar_zeigen.py`).

1. Der Körper ist das höchste Netz, nicht eine Socke (1,49 m hoch ≥ 1 m).
2. Rollen: Augen, Zähne/Zunge, Wimpern, Haar, Kleidung — im Maßstab 3,26 m.
3. Kategorien aus Höhe über der Sohle ÷ Maßstab: Boot = Schuhe, Socken, BH und Slip = Unterwäsche, Shirt = Oberteil, Short = Shorts.
4. Zwei Stücke derselben Art bekommen den Netznamen dazu (sonst schrieben sie dieselbe Kennung).
5. Mit Gewichten ändert sich nichts: ein Netz mit Gewichten auf `head.x` und Alpha bleibt Haar, wie bisher.

Sabotage-Gegenprobe: in `koerper` den Zweig `if self.ohne_gewichte:` streichen → Fall 1 rot; in `kategorie` die Teilung durch `skala`
weglassen → Fall 3 rot (alles landet bei Shirt/Kleid).

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest import mock

import numpy  # noqa: F401 — VORAB laden: `mock.patch.dict(sys.modules)` trüge numpy beim Verlassen wieder aus, ein zweites Laden scheitert
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.blendimportrollen import Blendimportrollen

ALPHA = [{'name': 'm', 'farbe': 'a.png', 'alpha': 'a.png'}]
FARBE = [{'name': 'm', 'farbe': 'a.png'}]


def _netz(name, z0, z1, punkte, materialien=FARBE, gewichte=None, breite=0.3):
    return {'name': name, 'datei': name + '.npz', 'punkte': punkte, 'min': [0.0, 0.0, z0], 'max': [breite, breite, z1],
            'gewichte': gewichte or {}, 'materialien': materialien}


def _asian_girl():
    """Maße von „Beautiful Asian girl 5.0.blend" (z von/bis, Punkte) — Auszug der Breite ist erfunden und spielt keine Rolle,
    nur bei den kleinen Teilen (Augen, Zähne, Zunge) zählt sie: dort stimmt sie mit den gemessenen 0,05–0,12 m."""
    return {'netze': [
        _netz(' bra', 2.295, 2.766, 4675, ALPHA),
        _netz('body', -0.012, 3.248, 44095, breite=1.1),
        _netz('boot', -0.028, 0.550, 16422),
        _netz('eyelashes', 3.037, 3.104, 7180, ALPHA, breite=0.21),
        _netz('hair1', 2.807, 3.290, 127418, ALPHA, breite=0.46),
        _netz('L_eyes', 3.031, 3.079, 770, breite=0.048),
        _netz('L_sock', 0.088, 1.583, 2585, ALPHA),
        _netz('R_eyes', 3.037, 3.084, 770, breite=0.048),
        _netz('R_sock', 0.112, 1.612, 2585, ALPHA),
        _netz('shirt', 1.859, 2.772, 7886),
        _netz('short', 1.737, 2.160, 3180),
        _netz('teeth_lower', 2.904, 2.946, 1682, breite=0.116),
        _netz('teeth_upper', 2.935, 2.976, 1673, breite=0.116),
        _netz('tongue', 2.912, 2.944, 1679, breite=0.098),
        _netz('underwear', 1.473, 2.123, 2532, ALPHA),
    ], 'armaturen': 0, 'ohne_rig': True, 'ohne_armatur': []}


class MassstabTest(SimpleTestCase):
    """6. Der Export bringt ein Modell ohne Rig auf eine Höhe, die „Mesh to 3D" als Meter liest.

    Der erste Lauf (2026.10.09.00.13.42) scheiterte in der Erkennung: 3,26 m gelten dort als Zentimeter (`einheit_anpassen`:
    über 3 → ×0,01), die Figur schrumpfte auf 3,3 cm, die Posenerkennung fand nichts („index 11 is out of bounds … size 0").
    Sabotage-Gegenprobe: in `massstab` immer 1.0 zurückgeben → Fall 6 rot."""

    databases = set()

    @staticmethod
    def _blendexport():
        """`blendexport.py` mit einem Ersatz für `bpy` laden (liegt unter `effekte/`, kein Paket)."""
        pfad = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendimport' / 'blendexport.py'
        with mock.patch.dict(sys.modules, {'bpy': ModuleType('bpy')}):
            spec = importlib.util.spec_from_file_location('blendexport_test', pfad)
            modul = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul)
        return modul.Blendexport

    def test_6_massstab_nur_ausserhalb_des_menschlichen_bereichs(self):
        massstab = self._blendexport().massstab
        self.assertAlmostEqual(massstab(3.2595) * 3.2595, 1.75, places=6, msg='die Asian girl kommt auf 1,75 m')
        for hoehe in (0.5, 1.62, 1.75, 2.5):
            self.assertEqual(massstab(hoehe), 1.0, 'eine mögliche Körperhöhe bleibt, wie sie ist')
        self.assertAlmostEqual(massstab(2.6) * 2.6, 1.75, places=6)
        self.assertAlmostEqual(massstab(0.2) * 0.2, 1.75, places=6, msg='ein Netz im Einheitswürfel')
        self.assertEqual(massstab(0.0), 1.0, 'ohne Netz kein Teilen durch null')

    def test_7_ergebnis_liest_mesh_to_3d_als_meter(self):
        """Gegenprobe gegen die Regel auf der anderen Seite: nach dem Maßstab gilt die Höhe in `einheit_anpassen` als Meter."""
        massstab = self._blendexport().massstab
        hoehe = 3.2595 * massstab(3.2595)
        self.assertTrue(0.3 <= hoehe <= 3.0, 'zwischen 0,3 und 3 m ändert „Mesh to 3D" nichts mehr')


class OhneGewichteTest(SimpleTestCase):
    databases = set()

    def _rollen(self):
        return {r['name']: r for r in Blendimportrollen(_asian_girl()).zuordnen()}

    def test_1_der_koerper_ist_das_hoechste_netz(self):
        rollen = self._rollen()
        self.assertEqual([n for n, r in rollen.items() if r['rolle'] == 'koerper'], ['body'])

    def test_1b_gewaehlt_wird_nach_hoehe_nicht_nach_punkten(self):
        """Beim Asian girl hat der Körper auch die meisten Punkte — dieser Fall trennt Höhe von Punktzahl."""
        inventar = {'netze': [_netz('body', 0.0, 3.2, 3000, breite=1.1), _netz('L_sock', 0.1, 1.6, 5000, ALPHA)], 'ohne_rig': True}
        rollen = {r['name']: r['rolle'] for r in Blendimportrollen(inventar).zuordnen()}
        self.assertEqual(rollen['body'], 'koerper')

    def test_2_rollen_im_massstab_von_3_26_m(self):
        rollen = self._rollen()
        self.assertEqual(rollen['L_eyes']['rolle'], 'auge')
        self.assertEqual(rollen['R_eyes']['rolle'], 'auge')
        self.assertEqual({rollen[n]['rolle'] for n in ('teeth_lower', 'teeth_upper', 'tongue')}, {'mund'})
        self.assertEqual(rollen['eyelashes']['rolle'], 'gesichtshaar', 'Wimpern haben Alpha und sitzen am Kopf, sind aber kein Haar')
        self.assertEqual(rollen['hair1']['rolle'], 'haar')
        self.assertEqual(rollen[' bra']['rolle'], 'kleid', 'der BH hat Alpha, sitzt aber an der Brust — kein Haar')

    def test_3_kategorien_aus_hoehe_ueber_der_sohle_durch_den_massstab(self):
        rollen = self._rollen()
        wunsch = {'boot': ('shoes', 'Schuhe'), 'shirt': ('tops', 'Shirt'), 'short': ('pants', 'Shorts'),
                  'L_sock': ('accessories', 'Socken'), 'R_sock': ('accessories', 'Socken'),
                  ' bra': ('underwear', 'Unterwäsche'), 'underwear': ('underwear', 'Unterwäsche')}
        for name, (ordner, art) in wunsch.items():
            self.assertEqual(rollen[name]['ordner'], ordner, name)
            self.assertTrue(rollen[name]['art'].startswith(art), (name, rollen[name]['art']))

    def test_4_gleiche_art_bekommt_den_netznamen(self):
        rollen = self._rollen()
        arten = [r['art'] for r in rollen.values() if r['rolle'] == 'kleid']
        self.assertEqual(len(arten), len(set(arten)), 'jede Art ist Name UND Kennung — sie muss eindeutig sein')
        self.assertEqual(rollen['L_sock']['art'], 'Socken L_sock')
        self.assertEqual(rollen['shirt']['art'], 'Shirt', 'eine einzelne Art bleibt, wie sie war')

    def test_5_mit_gewichten_gilt_die_bisherige_regel(self):
        inventar = {'netze': [
            _netz('body', 0.0, 1.7, 50000, FARBE, {'spine': 9.0, 'head': 3.0, 'hand.l': 2.0}),
            _netz('hair', 1.5, 1.8, 30000, ALPHA, {'head.x': 7.0}),
            _netz('c_eye', 1.6, 1.64, 700, FARBE, {'c_eye.l': 1.0}, breite=0.03),
        ], 'armaturen': 1, 'ohne_armatur': []}
        rollen = {r['name']: r['rolle'] for r in Blendimportrollen(inventar).zuordnen()}
        self.assertEqual(rollen, {'body': 'koerper', 'hair': 'haar', 'c_eye': 'auge'})
