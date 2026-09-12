# -*- coding: utf-8 -*-
u"""Die Vorschau liefert Punkte in SZENENLAGE (Y oben) — nicht Z oben.

DER BEFUND, DEN DIESE DATEI FESTHÄLT (08.09.2026)
=================================================
Edgar schickte ein Bild: ein Jumpsuit, der als flacher Klumpen am Boden
neben der Figur liegt. Im Browser nachgemessen:

    Jumpsuit   y −0,187 … 0,099   z −0,053 … 1,417   <- Höhe auf z
    Körper     y −0,001 … 1,678   z −0,094 … 0,231   <- Höhe auf y

Der Server hatte richtig gerechnet (die Meldung nannte 18 mm zur Haut und
197 herausgeholte Punkte). `garmentcode_anziehen.js` baut das Netz auch
korrekt gedreht auf — und die erste Nachricht der Stoffvorschau überschrieb
es mit UNGEDREHTEN Punkten.

Die Ursache war ein Wort im Docstring: `punkte()` hiess „(m, Z oben, wie die
Szene)". Das verwechselt zwei Räume — `CharacterState.compute()` liefert
Z oben, die Three.js-SZENE ist Y oben. Der Browser setzt die empfangenen
Punkte roh ins `position`-Attribut; wer dort Z-oben hineingibt, legt das
Kleidungsstück hin.

WARUM EIN EIGENER TEST UND NICHT EINER MEHR IN `test_stoffvorschau.py`
=====================================================================
Dort wird die Klasse `Stoffvorschau` geprüft, und die war in Ordnung: Ihr
`punkte_zoben` tut genau, was der Name sagt. Falsch war die STELLE, an der
sie benutzt wird. Diese Datei prüft deshalb `Stoffnachfuehrung` — die
Grenze zum Browser.
"""
import numpy as np
from django.test import SimpleTestCase

from ._kunstkoerper import Kunstkoerper


class StoffvorschauLiefertSzenenlage(SimpleTestCase):

    databases = set()

    def setUp(self):
        import os
        import tempfile
        from pathlib import Path
        # Ins Projektverzeichnis, nicht nach C:\Temp (globale Regel).
        from django.conf import settings
        self.ordner = Path(settings.BASE_DIR) / '_wegwerf' / 'achslage'
        self.ordner.mkdir(parents=True, exist_ok=True)
        # `mkstemp` gibt einen OFFENEN Deskriptor zurueck; unter Windows
        # laesst sich die Datei sonst im tearDown nicht loeschen.
        kennung, pfad = tempfile.mkstemp(suffix='.obj', dir=self.ordner)
        os.close(kennung)
        self.datei = Path(pfad)

    def tearDown(self):
        self.datei.unlink(missing_ok=True)

    def test_die_hoehe_steht_auf_y_nicht_auf_z(self):
        u"""Die scharfe Probe: Der Würfel ist 1 m hoch, der Stoff liegt oben
        darüber. In Szenenlage muss die y-Ausdehnung gross und die
        z-Ausdehnung klein sein — vertauscht war es genau andersherum."""
        fuehrung, koerper_zoben, bilanz = StoffvorschauLiefertSzenenlage._gebundene_nachfuehrung(self.datei)
        self.assertNotIn('fehler', bilanz)

        punkte = fuehrung.punkte(koerper_zoben)['probe']
        # Der Stoff liegt auf der Oberseite: y nahe 1,05, z zwischen -0,5..0,5.
        self.assertGreater(punkte[:, 1].min(), 0.9,
                           'Der Stoff muss OBEN liegen (y ~ 1,05)')
        self.assertLess(abs(punkte[:, 2]).max(), 0.6,
                        'Die z-Ausdehnung ist die Tiefe, nicht die Höhe')

    def test_der_stoff_folgt_dem_koerper_in_szenenlage(self):
        u"""Wird der Körper höher, wandert der Stoff auf der y-Achse mit —
        nicht auf der z-Achse."""
        fuehrung, koerper_zoben, _ = StoffvorschauLiefertSzenenlage._gebundene_nachfuehrung(self.datei)
        vorher = fuehrung.punkte(koerper_zoben)['probe'].copy()

        # In `CharacterState`-Lage (Z oben) ist die Höhe die z-Achse.
        hoeher = koerper_zoben.copy()
        hoeher[:, 2] *= 1.5
        nachher = fuehrung.punkte(hoeher)['probe']

        self.assertGreater(nachher[:, 1].max() - vorher[:, 1].max(), 0.1,
                           'Die Figur wurde höher — der Stoff muss mit')
        self.assertLess(abs(nachher[:, 2] - vorher[:, 2]).max(), 0.05,
                        'Die Tiefe darf sich dabei kaum ändern')

    def test_abstand_wird_gegen_dieselbe_lage_gemessen(self):
        u"""`abstand_mm` bekommt jetzt Y-oben-Punkte. Bei unverändertem
        Körper muss der Abstand ~0 sein; mit der alten Z-oben-Erwartung kam
        dort ein zweistelliger Zentimeterwert heraus — eine Zahl, die
        „Finalize drücken" gesagt hätte, obwohl nichts passiert war."""
        fuehrung, koerper_zoben, _ = StoffvorschauLiefertSzenenlage._gebundene_nachfuehrung(self.datei)
        punkte = fuehrung.punkte(koerper_zoben)['probe']
        self.assertLess(fuehrung.abstand_mm('probe', punkte), 1.0)

    @staticmethod
    def _gebundene_nachfuehrung(tmpdatei):
        u"""Eine Nachführung mit einem Stück, das 5 cm über dem Würfel liegt."""
        from GarmentCode.nachfuehrung import Stoffnachfuehrung
        from GarmentCode.stoffvorschau import Stoffvorschau

        koerper_yoben, dreiecke = Kunstkoerper.wuerfel()
        # Das Grundnetz kommt aus `CharacterState.compute()` — Z oben.
        koerper_zoben = Stoffvorschau.nach_zoben(koerper_yoben)

        # Stoff: die Oberseite des Würfels, 5 cm darüber, in Zentimetern (so legt
        # GarmentCode `*_sim.obj` ab).
        oben = koerper_yoben[np.isclose(koerper_yoben[:, 1], 1.0)]
        stoff_cm = (oben + np.array([0.0, 0.05, 0.0])) * 100.0
        tmpdatei.write_text(
            '\n'.join('v %f %f %f' % tuple(p) for p in stoff_cm), encoding='utf-8')

        fuehrung = Stoffnachfuehrung()
        bilanz = fuehrung.binden('probe', str(tmpdatei), koerper_zoben, dreiecke)
        return fuehrung, koerper_zoben, bilanz
