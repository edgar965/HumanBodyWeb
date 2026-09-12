# -*- coding: utf-8 -*-
u"""Welches Stoffnetz die Vorschau bindet — das korrigierte, nicht das rohe.

BEFUND (Edgar, 08.09.2026, mit Bild: „haut geht durch die hose hindurch").
Die Geometrie war in Ordnung: Am gebauten Ergebnis (`*_sim_rig.json`)
steckten 10 von 14.338 Stoffpunkten im Koerper (0,07 %), koerperseitig
stand nirgends Haut heraus, und der kleinste Spalt lag bei 3,1 mm.

Gebunden hat die Vorschau aber `*_sim.obj` — das ROHE Ergebnis der
Simulation, VOR `stoffkorrektur.py`. Sobald sie einmal nachzog (jeder
Reglerzug), ersetzte sie die korrigierten Punkte durch die rohen:

    korrigiert   10 von 14.338 (0,07 %)   davon bei 50-60 % Figurhoehe:  6
    roh         118 von 14.338 (0,82 %)   davon bei 50-60 % Figurhoehe: 69

50 bis 60 % ist Huefte und oberer Oberschenkel — genau die Stelle im Bild.

WAS DIESE FAELLE PRUEFEN
========================
Nicht die Zahlen oben (die stehen in `nachfuehrung.py` mit ihrer Quelle),
sondern die Eigenschaft, an der es still schiefgeht: dass die BEVORZUGTE
Datei die korrigierte ist, dass ihre LAGE richtig gedeutet wird (Meter/
Z oben gegen Zentimeter/Y oben — eine Verwechslung ergibt eine Bindung,
die sitzt und sich nicht bewegt), und dass der Rueckfall auf die OBJ
erhalten bleibt: Der SMPL-Referenzkoerper-Weg hat keine Rig-Datei.
"""
import io
import json
import os
import tempfile

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._kunstkoerper import Kunstkoerper


class NachfuehrungsnetzTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        # Der Ordner muss UNTERHALB des Ausgabeordners liegen — `netzpfad`
        # prueft das gegen den Ausbruch aus dem Ausgabebaum.
        from GarmentCode.entwurf import Entwurf
        self.wurzel = tempfile.mkdtemp(prefix='pruef_', dir=str(Entwurf.AUSGABE))
        self.addCleanup(self._aufraeumen)

    def _aufraeumen(self):
        for name in os.listdir(self.wurzel):
            os.remove(os.path.join(self.wurzel, name))
        os.rmdir(self.wurzel)

    def _obj(self, punkte, name='x_sim.obj'):
        pfad = os.path.join(self.wurzel, name)
        with io.open(pfad, 'w', encoding='utf-8') as datei:
            for p in punkte:
                datei.write(u'v %f %f %f\n' % tuple(p))
        return pfad

    def _rig(self, punkte, name='x_sim_rig.json'):
        pfad = os.path.join(self.wurzel, name)
        with io.open(pfad, 'w', encoding='utf-8') as datei:
            datei.write(json.dumps({'punkte': [list(map(float, p))
                                               for p in punkte],
                                    'dreiecke': [[0, 1, 2]]}))
        return pfad

    # -- Auswahl der Datei ----------------------------------------------------

    def test_rigdatei_wird_bevorzugt(self):
        u"""Liegen beide da, gilt die korrigierte."""
        self._obj([[0, 0, 0]])
        self._rig([[0, 0, 0]])
        pfad = NachfuehrungsnetzTest._nachfuehrung().netzpfad(self.wurzel)
        self.assertTrue(pfad.endswith('_sim_rig.json'), pfad)

    def test_ohne_rigdatei_bleibt_die_obj(self):
        u"""Der Rueckfall MUSS bleiben: Der SMPL-Weg hat kein Rig.

        Ohne diesen Fall waere die Vorschau auf dem Referenzkoerper-Weg
        (06.09.2026) still ohne Bindung — kein Fehler, nur ein Stoff, der
        sich nicht bewegt.
        """
        self._obj([[0, 0, 0]])
        pfad = NachfuehrungsnetzTest._nachfuehrung().netzpfad(self.wurzel)
        self.assertTrue(pfad.endswith('_sim.obj'), pfad)

    def test_ordner_ausserhalb_des_ausgabebaums_wird_verworfen(self):
        u"""Der Pfad kommt aus dem Browser — die Pruefung bleibt scharf."""
        self.assertIsNone(NachfuehrungsnetzTest._nachfuehrung().netzpfad(str(settings.BASE_DIR)))

    # -- Deutung der Lage -----------------------------------------------------

    def test_rigpunkte_werden_als_meter_gelesen(self):
        u"""Meter bleiben Meter — die Rig-Datei rechnet KEINE Zentimeter um.

        Die OBJ steht in Zentimetern und wird durch 100 geteilt. Waere die
        Rig-Datei denselben Weg gegangen, laege der Stoff hundertfach zu
        klein im Ursprung: eine Bindung, die „sitzt" meldet und nichts
        bewegt (der Fehler vom 08.09.2026).
        """
        punkte, korrigiert = NachfuehrungsnetzTest._nachfuehrung().stoffpunkte(
            self._rig([[0.1, 1.2, -0.3]]))
        self.assertTrue(korrigiert)
        self.assertAlmostEqual(float(punkte[0][1]), 1.2, places=6)

    def test_objpunkte_gelten_als_unkorrigiert(self):
        punkte, korrigiert = NachfuehrungsnetzTest._nachfuehrung().stoffpunkte(
            self._obj([[10.0, 120.0, -30.0]]))
        self.assertFalse(korrigiert)
        # Roh gelesen, in Zentimetern — umgerechnet wird erst im Konstruktor.
        self.assertAlmostEqual(float(punkte[0][1]), 120.0, places=6)

    def test_unlesbare_rigdatei_faellt_auf_die_obj_zurueck(self):
        u"""Und sie meldet es — ein stiller Rueckfall waere schlechter.

        `korrigiert=False` steht danach in der Bilanz; ohne diese Angabe
        waere von aussen nicht zu sehen, dass die schlechtere Bindung gilt.
        """
        self._obj([[1.0, 2.0, 3.0]])
        kaputt = os.path.join(self.wurzel, 'x_sim_rig.json')
        with io.open(kaputt, 'w', encoding='utf-8') as datei:
            datei.write(u'{kein json')
        punkte, korrigiert = NachfuehrungsnetzTest._nachfuehrung().stoffpunkte(kaputt)
        self.assertFalse(korrigiert)
        self.assertEqual(len(punkte), 1)

    def test_fehlende_datei_gibt_none(self):
        u"""Und der Testordner ist wirklich der Testordner.

        Die Gegenprobe steht mit im Fall: Zeigte `wurzel` woanders hin,
        lasen die Faelle oben die ECHTEN Ergebnisse und blieben gruen
        (`~/.claude/rules/test-isolation.md`).
        """
        self.assertIn('pruef_', str(self.wurzel))
        punkte, korrigiert = NachfuehrungsnetzTest._nachfuehrung().stoffpunkte(
            os.path.join(self.wurzel, 'gibtsnicht_sim.obj'))
        self.assertIsNone(punkte)
        self.assertFalse(korrigiert)

    # -- Die Bindung selbst ---------------------------------------------------

    def test_bindung_reproduziert_das_korrigierte_netz(self):
        u"""Auf DEMSELBEN Koerper muss die Vorschau die Eingabe zurueckgeben.

        Das ist die scharfe Probe: Sie faellt bei jeder Verwechslung von
        Einheit oder Achse. Gemessen an der echten Hose: 0,0000 mm Median
        und 0,0000 mm Maximum.
        """
        kv_yoben, kf = Kunstkoerper.wuerfel(8)
        # Der Aufrufer liefert Z oben (`CharacterState.compute()`).
        kv = np.column_stack([kv_yoben[:, 0], -kv_yoben[:, 2], kv_yoben[:, 1]])
        stoff = kv[:40] * 1.05          # etwas ausserhalb, in Projektlage
        nach = NachfuehrungsnetzTest._nachfuehrung()()
        bilanz = nach.binden('probe', self._rig(stoff), kv, kf)
        self.assertNotIn('fehler', bilanz)
        self.assertTrue(bilanz['korrigiert'])
        neu = nach.bindungen['probe'].punkte_zoben(kv)
        weg = np.linalg.norm(neu - stoff, axis=1)
        self.assertLess(float(weg.max()), 1e-9, 'Bindung reproduziert nicht')

    def test_gegenprobe_die_obj_wuerde_zentimeter_annehmen(self):
        u"""Sabotage: dieselben Punkte als OBJ ergeben eine andere Bindung.

        Ohne diesen Fall pruefte der Test oben eine Eigenschaft, die
        vielleicht ohnehin gilt (`~/.claude/rules/analysewerkzeuge.md`).
        Dieselben Zahlen als OBJ gelesen sind Zentimeter — der Stoff landet
        hundertfach zu klein im Ursprung, die Bindung sitzt NICHT mehr auf
        dem Wuerfel.
        """
        kv_yoben, kf = Kunstkoerper.wuerfel(8)
        kv = np.column_stack([kv_yoben[:, 0], -kv_yoben[:, 2], kv_yoben[:, 1]])
        stoff = kv[:40] * 1.05
        nach = NachfuehrungsnetzTest._nachfuehrung()()
        bilanz = nach.binden('probe', self._obj(stoff), kv, kf)
        self.assertFalse(bilanz.get('korrigiert'))
        if 'fehler' not in bilanz:
            neu = nach.bindungen['probe'].punkte_zoben(kv)
            weg = np.linalg.norm(neu - stoff, axis=1)
            self.assertGreater(float(weg.max()), 1e-3,
                               'Die OBJ-Deutung muesste hier abweichen')

    @staticmethod
    def _nachfuehrung():
        from GarmentCode.nachfuehrung import Stoffnachfuehrung
        return Stoffnachfuehrung
