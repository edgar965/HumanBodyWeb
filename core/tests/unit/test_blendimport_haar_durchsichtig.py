# -*- coding: utf-8 -*-
"""Haar ohne Alpha-Bild (10.10.2026, „hinako"): das Haar hat nur die Überblendung `HASHED` und eine Farbe ohne Bild,
dazu fast alle Gewichte am Kopf (`DEF-spine.006`, Rigify). Früher wurde es als „Shirt hair" eingeordnet.

1. Hohes Haar mit durchsichtiger Überblendung und Kopfgewicht → Rolle haar.
2. Ein kleines durchsichtiges Netz am Kopf (Augen) bleibt draußen — es ist nicht hoch genug für Haar.
3. Wimpern bleiben Wimpern (kein Haar, auch mit Alpha-Bild am Kopf).
4. Ein Kleidungsstück mit Kopfgewicht, aber ohne durchsichtige Überblendung und ohne Alpha, bleibt Kleidung.

Sabotage-Gegenprobe: `DURCHSICHTIG` leeren → Fall 1 rot; `HAAR_MIN` auf 0 → Fall 2 rot; `spine.006` aus `KOPFKNOCHEN` nehmen → Fall 1 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from core.dienste.blendimportrollen import Blendimportrollen


def _netz(name, z0, z1, gewichte, materialien, breite=0.3):
    return {'name': name, 'datei': name + '.npz', 'punkte': 100, 'min': [0.0, 0.0, z0], 'max': [breite, breite, z1],
            'gewichte': gewichte, 'materialien': materialien}


KOERPER = _netz('BODY', 0.705, 3.012, {'DEF-spine.006': 3000.0, 'DEF-spine': 9000.0, 'DEF-thigh.L': 2000.0},
                [{'name': 'skin'}], breite=0.5)
HASHED = [{'name': 'hair', 'ueberblendung': 'HASHED'}]


class HaarDurchsichtigTest(SimpleTestCase):
    databases = set()

    def _rollen(self, *netze):
        inventar = {'netze': [KOERPER, *netze]}
        return {r['name']: r['rolle'] for r in Blendimportrollen(inventar).zuordnen()}

    def test_1_hohes_haar_ohne_alpha_bild_ist_haar(self):
        haar = _netz('hair', 2.47, 3.07, {'DEF-spine.006': 18168.0, 'DEF-spine.005': 390.0, 'DEF-spine.004': 258.0}, HASHED, breite=0.32)
        self.assertEqual(self._rollen(haar)['hair'], 'haar')

    def test_2_kleines_durchsichtiges_netz_am_kopf_ist_kein_haar(self):
        augen = _netz('eyes', 2.84, 2.87, {'DEF-spine.006': 1604.0}, HASHED, breite=0.05)
        self.assertNotEqual(self._rollen(augen)['eyes'], 'haar')

    def test_3_wimpern_bleiben_wimpern(self):
        lashes = _netz('eyelashes', 2.80, 2.90, {'DEF-spine.006': 7180.0}, [{'name': 'lash', 'alpha': True, 'ueberblendung': 'HASHED'}],
                       breite=0.06)
        self.assertNotEqual(self._rollen(lashes)['eyelashes'], 'haar')

    def test_4_kleidung_mit_kopfgewicht_ohne_durchsichtigkeit_bleibt_kleidung(self):
        mantel = _netz('coat', 2.20, 3.05, {'DEF-spine.006': 4000.0, 'DEF-spine': 6000.0}, [{'name': 'stoff', 'ueberblendung': 'OPAQUE'}],
                       breite=0.4)
        self.assertEqual(self._rollen(mantel)['coat'], 'kleid')
