# -*- coding: utf-8 -*-
"""Bringt der Zwischenschritt A-Pose etwas? (18.10.2026, Edgar: „Könnten wir zwei, drei Tests schreiben, ob sich das Ergebnis verbessert, wenn wir das so machen?“)

Messtests auf den gerechneten Prüfposen-Jobs (UrsulaSpagat, DamiraSitzen, MattLiegen, MannLaufen; Probe 1, nie trainiert) — sie LESEN nur, was die Kette abgelegt hat
(`wege.json` + `wege_vor_*.json`, über `Architekturmesh3daimia`, dieselbe Quelle wie Hilfe → Architektur → Mesh3DAI). Fehlen die Läufe, wird übersprungen. Hier und nicht in `unit`, weil das Ergebnis
an Edgars Daten hängt (es ändert sich mit jedem Lauf der Kette), nicht am Code.
    1  A-Pose gegen Netz direkt: über die A-Pose (alter Weg UND Weg MIA) liegt jede Probe näher am Ziel als das Netz direkt auf der Pose.
    2  Weg MIA gegen den alten Weg (Mesh-3D „Nur Rig“): im Mittel nicht schlechter als `TOLERANZ_MM` — **am 18.10.2026 rot erwartet** (16,9 gegen 13,4 mm, Hilfeseite).
    3  Das Netz der Vorstufe hilft MIA: MIA → A-Pose → Netz liegt je Probe näher am Ziel als MIA allein.
Sabotage-Gegenprobe (von Hand): in `Architekturmesh3daimia._mm` 'vorstufe' und 'direkt' vertauschen → Fall 1 rot.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.architekturmesh3daimia import Architekturmesh3daimia


class Mesh3daiAposeWirkungTest(SimpleTestCase):
    #: Setzung: Läufe derselben Kette mit demselben Netz streuen um rund 2 mm (DamiraSitzen 14,9 / 16,7 / 16,6 mm, 18.10.2026).
    TOLERANZ_MM = 2.0

    @classmethod
    def daten(cls):
        return Architekturmesh3daimia.kontext(Path(settings.OBJECTS_ROOT) / 'mesh3dai')

    def setUp(self):
        self.d = self.daten()
        if not self.d:
            self.skipTest('Kein Prüfposen-Job hat beide Wege gerechnet (mesh3dai_vorstufe.py job <Job>)')

    def test_1_a_pose_naeher_als_netz_direkt(self):
        for j in self.d['jobs']:
            for weg in ('alt', 'mia'):
                with self.subTest(job=j['job'], weg=weg):
                    self.assertLess(j[weg]['vorstufe'], j['direkt'], '%s, Weg %s: über die A-Pose %.1f mm, Netz direkt %.1f mm' % (j['job'], weg, j[weg]['vorstufe'], j['direkt']))

    def test_2_mia_im_mittel_nicht_schlechter_als_der_alte_weg(self):
        m = self.d['mittel']
        je = '; '.join('%s %.1f / %.1f' % (j['job'], j['mia']['vorstufe'], j['alt']['vorstufe']) for j in self.d['jobs'])
        self.assertLessEqual(m['mia'], m['alt'] + self.TOLERANZ_MM, 'Weg MIA Ø %.1f mm gegen alten Weg Ø %.1f mm (MIA / alt je Job: %s)' % (m['mia'], m['alt'], je))

    def test_3_das_netz_der_vorstufe_hilft_mia(self):
        for j in self.d['jobs']:
            with self.subTest(job=j['job']):
                self.assertLess(j['mia']['vorstufe'], j['mia']['rig'], '%s: MIA → A-Pose → Netz %.1f mm, MIA allein %.1f mm' % (j['job'], j['mia']['vorstufe'], j['mia']['rig']))
