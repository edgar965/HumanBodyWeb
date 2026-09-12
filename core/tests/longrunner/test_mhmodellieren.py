# -*- coding: utf-8 -*-
u"""MakeHumans Modellierregler: Zielbaum, Gewichte, Netz.

DER WICHTIGSTE FALL IST DER ERSTE: `test_zielbaum_gegen_upstream` laesst
MakeHumans EIGENEN Crawler (`makehuman/lib/targets.py`) laufen und vergleicht
fuer alle 1.280 Ziele den Gruppenschluessel und die Kategoriewerte. Daraus
entstehen die Gewichte; stimmt das nicht, stimmt nichts. Am 06.09.2026 waren
1.280 von 1.280 gleich.

Der Crawler laeuft als UNTERPROZESS — MakeHumans Paket heisst `core` wie das
dieses Projekts (`_mh_upstream_zerlegung.py`).

Die uebrigen Faelle halten fest, was gemessen wurde:

    Vorgabe (alle Regler mittig)   165,9 cm   Gewichtssumme je Makrogruppe 1,0
    Geschlecht ganz rechts (Mann)  173,0 cm
    Alter 0,15 (kleines Kind)      116,7 cm
    Groesse ganz links / rechts    129,2 / 238,2 cm

und die Falle, die beim Bauen zugeschnappt waere: In der Gruppe
`macrodetails` haengen FUENF Makroregler an denselben Zielen. Wer ihre
Gewichte addiert statt sie zu setzen, verformt die Figur um das Fuenffache.
"""
import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase

from MakeHuman.makrowerte import Mhmakrowerte
from MakeHuman.modifikatoren import Mhmodifikatoren
from MakeHuman.zielablage import Mhzielablage
from MakeHuman.zielbaum import Mhzielbaum


class MhmodellierenTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        if not Mhzielbaum.vorhanden() or not Mhmodifikatoren.vorhanden():
            self.skipTest(u'MakeHuman-Upstream fehlt (MakeHuman/HERKUNFT.md)')

    # ------------------------------------------------------------ Gegenprobe

    def test_zielbaum_gegen_upstream(self):
        u"""Alle 1.280 Ziele: Gruppenschluessel und Werte wie bei MakeHuman."""
        helfer = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              '_mh_upstream_zerlegung.py')
        makehuman = os.path.join(str(settings.MAKEHUMAN_ROOT), 'makehuman')
        lauf = subprocess.run([sys.executable, helfer, makehuman],
                              capture_output=True, timeout=300)
        if lauf.returncode != 0:
            self.skipTest(u'MakeHuman-Crawler nicht lauffähig: %s'
                          % lauf.stderr.decode('utf-8', 'replace')[-300:])
        echt = json.loads(lauf.stdout.decode('utf-8'))
        meine = {z.pfad: z for z in Mhzielbaum.holen().ziele}
        self.assertEqual(len(echt), len(meine))
        abweichungen = []
        for pfad, angabe in echt.items():
            meins = meine.get(pfad)
            if meins is None:
                abweichungen.append((pfad, 'fehlt'))
            elif angabe['schluessel'] != meins.schluessel:
                abweichungen.append((pfad, angabe['schluessel'],
                                     meins.schluessel))
            elif angabe['werte'] != sorted(meins.werte):
                abweichungen.append((pfad, angabe['werte'],
                                     sorted(meins.werte)))
        self.assertEqual(abweichungen[:5], [],
                         u'%d von %d Zielen weichen ab' % (len(abweichungen),
                                                           len(echt)))

    # --------------------------------------------------------------- Katalog

    def test_jeder_regler_findet_ziele(self):
        u"""Ein Regler ohne Ziele bewegt nichts — und sagt es nicht."""
        baum = Mhzielbaum.holen()
        leer = [(k, g) for k, r in Mhmodifikatoren.holen().regler.items()
                for g in r.gruppen() if not baum.in_gruppe(g)]
        self.assertEqual(leer[:5], [])

    def test_keine_zielwoerter_ohne_faktor(self):
        u"""Sonst faellt ein Ziel still durch die 0-Vorgabe in `_gewicht`."""
        self.assertEqual(Mhmodifikatoren.holen().unbekannte_woerter(), [])

    # -------------------------------------------------------------- Gewichte

    def test_makrogruppen_wiegen_in_der_vorgabe_genau_eins(self):
        gewichte = Mhmodifikatoren.holen().gewichte({}, Mhmakrowerte())
        summen = {}
        for pfad, gewicht in gewichte.items():
            gruppe = Mhzielbaum.zerlegen(pfad).schluessel
            summen[gruppe] = summen.get(gruppe, 0.0) + gewicht
        self.assertIn('macrodetails', summen)
        for gruppe, summe in summen.items():
            self.assertAlmostEqual(summe, 1.0, places=6, msg=gruppe)

    def test_fuenf_regler_auf_einer_gruppe_zaehlen_einfach(self):
        u"""macrodetails: Geschlecht, Alter und drei Rassen, dieselben Ziele."""
        gewichte = Mhmodifikatoren.holen().gewichte({}, Mhmakrowerte())
        gross = [g for p, g in gewichte.items()
                 if Mhzielbaum.zerlegen(p).schluessel == 'macrodetails']
        self.assertTrue(gross)
        self.assertLessEqual(max(gross), 1.0,
                             u'Gewichte wurden addiert statt gesetzt')

    def test_mittiger_muskelregler_laesst_die_extremziele_weg(self):
        gewichte = Mhmodifikatoren.holen().gewichte({}, Mhmakrowerte())
        self.assertFalse([p for p in gewichte if 'maxmuscle' in p])
        gewichte = Mhmodifikatoren.holen().gewichte(
            {}, Mhmakrowerte({'muscle': 1.0}))
        self.assertTrue([p for p in gewichte if 'maxmuscle' in p])

    # ------------------------------------------------------------------ Netz

    def test_netz_folgt_den_makroreglern(self):
        if not Mhzielablage.bereit():
            self.skipTest(u'Keine Zielablage — manage.py mh_ziele_bauen')
        vorgabe = self._hoehe({})
        self.assertAlmostEqual(vorgabe, 1.659, delta=0.02)
        self.assertGreater(self._hoehe({'gender': 1.0}), vorgabe + 0.04)
        self.assertLess(self._hoehe({'age': 0.15}), vorgabe - 0.3)
        self.assertLess(self._hoehe({'height': 0.0}), 1.4)
        self.assertGreater(self._hoehe({'height': 1.0}), 2.2)

    def test_detailregler_aendert_das_netz_ohne_die_hoehe(self):
        if not Mhzielablage.bereit():
            self.skipTest(u'Keine Zielablage — manage.py mh_ziele_bauen')
        antwort = self.client.post(
            '/api/character/mh-figur/basis/netz/',
            json.dumps({'regler': {'head/head-scale-horiz-decr|incr': 1.0}}),
            content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertTrue(daten['geformt'])
        self.assertAlmostEqual(daten['hoehe'], self._hoehe({}), delta=0.001)

    def test_kleidung_wird_auf_den_geformten_koerper_gerechnet(self):
        u"""Sonst steckte die Figur im Anzug ihres frueheren Koerpers."""
        if not Mhzielablage.bereit():
            self.skipTest(u'Keine Zielablage — manage.py mh_ziele_bauen')
        kennung = 'tops/female_casualsuit01'
        schlank = self._kleidhoehe(kennung, {})
        gross = self._kleidhoehe(kennung, {'height': 1.0})
        self.assertGreater(gross, schlank * 1.2,
                           u'Das Kleidungsstück ist nicht mitgewachsen')

    # ---------------------------------------------------------------- Regler

    def test_reglerliste_nennt_makrogruppe_und_seiten(self):
        antwort = self.client.get('/api/character/mh-figur/regler/')
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        namen = [s['name'] for s in daten['seiten']]
        self.assertEqual(namen[0], 'Macro modelling')
        anzahl = sum(len(a['regler'])
                     for s in daten['seiten'] for a in s['abschnitte'])
        self.assertEqual(anzahl, len(Mhmodifikatoren.holen().regler))
        self.assertIn('gender', daten['makro'])

    # ---------------------------------------------------------------- Helfer

    def _hoehe(self, makro):
        antwort = self.client.post(
            '/api/character/mh-figur/basis/netz/',
            json.dumps({'makro': makro}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        return json.loads(antwort.content)['hoehe']

    def _kleidhoehe(self, kennung, makro):
        u"""Die y-Ausdehnung eines angepassten Kleidungsstuecks in Metern."""
        import base64

        import numpy as np
        antwort = self.client.post(
            '/api/character/mh-figur/garderobe/%s/netz/' % kennung,
            json.dumps({'makro': makro}), content_type='application/json')
        if antwort.status_code == 404:
            self.skipTest(u'%s nicht in der Bibliothek' % kennung)
        self.assertEqual(antwort.status_code, 200)
        roh = base64.b64decode(json.loads(antwort.content)['vertices'])
        punkte = np.frombuffer(roh, dtype=np.float32).reshape(-1, 3)
        return float(punkte[:, 1].max() - punkte[:, 1].min())
