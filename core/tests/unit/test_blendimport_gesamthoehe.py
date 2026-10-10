# -*- coding: utf-8 -*-
"""Blender-Import: der Maßstab richtet sich nach der Höhe der GANZEN Figur (10.10.2026).

Edgar: „rainy modell import total kaputt, fixe" — und kurz darauf „auch seori kaputt". Gemessen (`ProjektTemp/_wegwerf/` im Scratchpad der
Sitzung, Inventare der Läufe `…12.55.19` Rainy und `…11.50.14` seori): Rainy ist 3,32 m, seori 3,21 m hoch, aber KEIN einzelnes Netz ist höher
als 2,5 m — Rainys Körper reicht nur von der Hüfte zum Scheitel (1,55 m), die Beine stecken in Hose (1,96 m) und Stiefeln; seoris Körper hat
keinen Kopf (2,34 m). `Blendexport` maß nur das höchste EINZELNE Netz (und rechnete mit Rig gar nicht um), der Maßstab blieb 1,0, „Mesh to 3D"
las die 3,3 m als Zentimeter, die Figur passte ins Leere (Haut-Abstand RMS 372 mm bzw. 274 mm; Asian Female: 5 mm). Dasselbe traf Rosemary
Winters (3,28 m) und hinako (3,07 m).

1. `Blendexport.faktor_fuer`: erst das höchste Einzelnetz (Asian girl 3,26 m, Fallout ranger 2,68 m bleiben bitgleich), ist das menschlich,
   die Gesamthöhe aller Netze.
2. `Blendimportrollen`: Körper ab 40 % der Figurhöhe (früher fest 1,0 m — Rainys Körper ist nach dem Umrechnen 0,82 m, die Hose 1,04 m wurde
   zum „Körper"), Boden und Höhe der Kategorien aus allen Netzen (die Jacke war zur „Hose" geworden, die Wimpern zum „Shirt").

Sabotage-Gegenproben: in `faktor_fuer` nur `massstab(einzel_m)` zurückgeben → Fall 1 rot; in `Blendimportrollen.koerper` die Mindesthöhe
wieder auf 1,0 m setzen → Fall 3 rot; in `zuordnen` `figur()` durch Höhe und Unterkante des Körper-Netzes ersetzen → Fall 4 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage. Geprüft ist es an den echten Daten: Vorlauf `modellimport_formate/vorlauf.py` für Rainy
(Figur 1,736 m, Körper `body`) und seori (1,734 m), Rollenvergleich an allen gespeicherten Inventaren (cute girl, Asian Female, Fallout: 0 Änderungen).
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


def _blendexport():
    """`blendexport.py` mit einem Ersatz für `bpy` laden (liegt unter `effekte/`, kein Paket)."""
    pfad = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendimport' / 'blendexport.py'
    with mock.patch.dict(sys.modules, {'bpy': ModuleType('bpy')}):
        spec = importlib.util.spec_from_file_location('blendexport_gesamthoehe_test', pfad)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
    return modul.Blendexport


def _netz(name, z0, z1, punkte, materialien=FARBE, gewichte=None, breite=0.3):
    return {'name': name, 'datei': name + '.npz', 'punkte': punkte, 'min': [0.0, 0.0, z0], 'max': [breite, breite, z1],
            'gewichte': gewichte if gewichte is not None else {'spine': 1.0}, 'materialien': materialien}


def _rainy():
    """Rainy nach dem Umrechnen auf 1,75 m (Vorlauf `2026.10.10.14.29.08`, Maßstab 0,5264, Gesamthöhe vorher 3,3246 m)."""
    knochen_koerper = {'spine_%02d' % i: 1.0 for i in range(115)}
    return {'netze': [
        _netz('body', 0.911, 1.726, 33323, gewichte=knochen_koerper, breite=0.956),
        _netz('boot', -0.010, 0.264, 16422, gewichte={'foot.l': 1.0, 'foot.r': 1.0}, breite=0.45),
        _netz('hair', 1.142, 1.740, 18059, ALPHA, {'head.x': 1.0}, breite=0.23),
        _netz('L_eyes', 1.621, 1.645, 770, gewichte={'c_eye.l': 1.0}, breite=0.024),
        _netz('lashes', 1.624, 1.661, 7180, ALPHA, {'c_eye.l': 1.0, 'head.x': 1.0}, breite=0.1),
        _netz('pant', 0.158, 1.188, 5339, gewichte={'thigh.l': 1.0, 'leg.l': 1.0}, breite=0.39),
        _netz('R_eyes', 1.621, 1.645, 770, gewichte={'c_eye.r': 1.0}, breite=0.025),
        _netz('shirt', 0.981, 1.455, 13051, gewichte={'spine_02.x': 1.0, 'arm.l': 1.0}, breite=0.77),
        _netz('teeth_lower', 1.561, 1.578, 1682, gewichte={'c_teeth_lower': 1.0}, breite=0.058),
        _netz('teeth_upper', 1.570, 1.591, 1673, gewichte={'c_teeth_upper': 1.0}, breite=0.056),
        _netz('tongue', 1.558, 1.578, 1671, gewichte={'c_tongue': 1.0}, breite=0.028),
    ], 'armaturen': 1, 'ohne_rig': False, 'ohne_armatur': []}


class FaktorTest(SimpleTestCase):
    databases = set()

    def test_1_gesamthoehe_entscheidet_wenn_kein_einzelnetz_zu_hoch_ist(self):
        faktor_fuer = _blendexport().faktor_fuer
        rainy, seori = faktor_fuer(1.9584, 3.3246), faktor_fuer(2.3425, 3.208)
        self.assertAlmostEqual(rainy * 3.3246, 1.75, places=6, msg='Rainy: 3,32 m → 1,75 m (höchstes Einzelnetz 1,96 m, „menschlich")')
        self.assertAlmostEqual(seori * 3.208, 1.75, places=6, msg='seori: 3,21 m → 1,75 m (höchstes Einzelnetz 2,34 m)')

    def test_2_bisherige_faelle_bleiben_bitgleich(self):
        faktor_fuer, massstab = _blendexport().faktor_fuer, _blendexport().massstab
        self.assertEqual(faktor_fuer(3.2595, 3.318), massstab(3.2595), 'Asian girl: das Einzelnetz entscheidet wie bisher (0,5369)')
        self.assertEqual(faktor_fuer(2.6759, 2.899), massstab(2.6759), 'Fallout ranger: 0,654 bleibt, nicht 1,75 / 2,899')
        self.assertEqual(faktor_fuer(1.7308, 1.792), 1.0, 'cute girl: eine mögliche Figur bleibt, wie sie ist')
        self.assertEqual(faktor_fuer(1.7678, 1.82), 1.0, 'Asian Female (Rig): unverändert')
        self.assertEqual(faktor_fuer(0.0, 0.0), 1.0, 'ohne Netz kein Teilen durch null')

    def test_2b_das_ergebnis_liest_mesh_to_3d_als_meter(self):
        """`einheit_anpassen` hält Längen über 3 für Zentimeter — nach dem Maßstab liegt jede der vier betroffenen Figuren darunter."""
        faktor_fuer = _blendexport().faktor_fuer
        for einzel, gesamt in ((1.9584, 3.3246), (2.3425, 3.208), (1.7308, 3.278), (2.3064, 3.072)):
            self.assertTrue(0.3 <= gesamt * faktor_fuer(einzel, gesamt) <= 3.0, (einzel, gesamt))


class RollenTest(SimpleTestCase):
    databases = set()

    def _rollen(self, inventar=None):
        return {r['name']: r for r in Blendimportrollen(inventar or _rainy()).zuordnen()}

    def test_3_der_koerper_ist_das_netz_mit_den_meisten_knochen_auch_wenn_er_unter_einem_meter_bleibt(self):
        rollen = self._rollen()
        self.assertEqual([n for n, r in rollen.items() if r['rolle'] == 'koerper'], ['body'],
                         'Rainys Körper ist 0,82 m hoch; die Hose (1,04 m) darf es nicht werden')

    def test_4_kategorien_aus_der_ganzen_figur(self):
        rollen = self._rollen()
        self.assertEqual((rollen['shirt']['ordner'], rollen['shirt']['art']), ('tops', 'Shirt'), 'die Jacke war zur „Hose shirt" geworden')
        self.assertEqual((rollen['pant']['ordner'], rollen['pant']['art']), ('pants', 'Hose'))
        self.assertEqual(rollen['boot']['ordner'], 'shoes')

    def test_5_wimpern_sind_kein_kleidungsstueck(self):
        self.assertNotEqual(self._rollen()['lashes']['rolle'], 'kleid', 'die Wimpern waren zum „Shirt" geworden')

    def test_6_figur_nimmt_alle_netze(self):
        rollen = Blendimportrollen(_rainy())
        boden, hoehe = rollen.figur(rollen.koerper())
        self.assertAlmostEqual(boden, -0.010, places=6, msg='der Boden ist die Unterkante des Stiefels, nicht die Hüfte des Körpers')
        self.assertAlmostEqual(hoehe, 1.750, places=6, msg='bis zur Oberkante des Haars')

    def test_7_ein_vollstaendiger_koerper_aendert_nichts(self):
        """cute girl: der Körper reicht von der Sohle zum Scheitel — Boden und Höhe sind die des Körpers (Gegenprobe zu 6)."""
        inventar = {'netze': [
            _netz('body', 0.0, 1.75, 54369, gewichte={'spine': 9.0, 'head': 3.0, 'hand.l': 2.0}, breite=0.9),
            _netz('shirt', 0.9, 1.5, 8045, gewichte={'spine': 4.0}, breite=0.7),
            _netz('jeans', 0.0, 1.0, 5272, gewichte={'thigh.l': 4.0}, breite=0.4),
        ], 'armaturen': 1, 'ohne_rig': False, 'ohne_armatur': []}
        rollen = Blendimportrollen(inventar)
        self.assertEqual(rollen.figur(rollen.koerper()), (0.0, 1.75))
