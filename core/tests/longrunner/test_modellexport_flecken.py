# -*- coding: utf-8 -*-
u"""Steckt woanders eine fremde Farbe im Umriss eines einfarbigen Teils?

DER VORFALL (27.09.2026): Edgar meldete am selben Export sowohl in der
`.obj` als auch der `.glb` Flecken auf den Schuhen — „regression … teste
wieder, passe deine testcases an, die müssen das alles erkennen. Melde nicht
mehr fertig wenn noch solche Bugs da sind." `Exportbildpruefung` (farblose
Stellen) sieht das nicht: die Flecken sind FARBIG, nur die falsche Farbe —
verdeckte Haut, die trotz `Hauteinzug` durch Schuh oder Kleid sticht.

MESSUNG AM ECHTEN EXPORT (Damira1/DanceKurz, 27.09.2026):

    Schuh (`garmentcode_schuh`): 16,8 % der Silhouette waren Hautfarbe statt
    der einzigen Schuhfarbe (`mat_16`, keine Bildkarte — jede Abweichung IST
    ein Fund).

NUR KÖRPER + DAS GEPRÜFTE TEIL, nicht die volle Szene (eigene Falle desselben
Tages): Haare, die legitim vor dem Kleidausschnitt hängen, sahen im Vollbild
wie ein 9,5-%-Fleck aus — nach Beschränkung der Vergleichsszene auf
Körper+Kleid (ohne Haare) fiel der Wert auf 0,45 %, dieselbe Größenordnung
wie das saubere Kleid vom Vortag (0,8 %, von Hand gemessen).

WELCHE TEILE GEPRÜFT WERDEN: nicht fest im Code — `Objwerkstoffe` liest aus
der Exportdatei, welche Objekte einen Werkstoff OHNE eigene Bildkarte tragen
(reine `Kd`-Farbe). Kommt ein weiteres solches Teil dazu, prüft der Fall es
automatisch mit.

DER FALL BRAUCHT EINE ECHTE EXPORTDATEI, siehe `test_modellexport_ansicht.py`
— dieselbe Übersprung-Logik bei fehlender Datei.
"""
import subprocess
import unittest
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.exportfleckenpruefung import Exportfleckenpruefung
from core.dienste.objwerkstoffe import Objwerkstoffe
from core.projekt_temp import ProjektTemp

SKRIPT = Path(settings.BASE_DIR) / 'core' / 'dienste' / 'blender' / 'exportbild.py'

#: Der Schuh maß 16,8 %, ein sauberes Teil 0,45–0,8 % — die Schwelle in
#: `Exportfleckenpruefung` (5 %) liegt schon dazwischen; hier zusätzlich
#: eine Mindestgröße, damit ein winziges Teil (z. B. eine Wimper mit wenigen
#: hundert Bildpunkten) nicht am Kantenrauschen allein durchfällt.
MINDESTPUNKTE = 300


def neueste_ausgabe():
    u"""Die zuletzt geschriebene `.obj` im Ausgabeordner — oder None.
    Dieselbe `rglob`-Begründung wie in `test_modellexport_ansicht.py`."""
    wurzel = Path(settings.HUMANBODY_MODELLEXPORT_VORGABE_DIR)
    if not wurzel.is_dir():
        return None
    dateien = sorted(wurzel.rglob('*.obj'), key=lambda p: p.stat().st_mtime, reverse=True)
    return dateien[0] if dateien else None


def rendern(obj, ziel, nur):
    lauf = subprocess.run(
        [str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python', str(SKRIPT), '--',
         '--obj', obj.as_posix(), '--png', ziel.as_posix(),
         '--breite', '900', '--hoehe', '1400', '--nur', nur],
        capture_output=True, text=True, timeout=900,
    )
    if lauf.returncode != 0 or not ziel.is_file():
        raise RuntimeError(f'Blender-Lauf gescheitert ({nur}):\n{lauf.stdout[-3000:]}\n{lauf.stderr[-2000:]}')
    return ziel


class ModellexportFleckenTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.obj = neueste_ausgabe()
        cls.berichte = None
        if not cls.obj:
            return
        ordner = Path(ProjektTemp.ordner('test_modellexport_flecken'))
        teile = [o for o in Objwerkstoffe(cls.obj).objekte_ohne_karte()
                 if not o.startswith('genesis9_koerper')]
        cls.berichte = {}
        for teil in teile:
            silhouette = rendern(cls.obj, ordner / f'{teil}_silhouette.png', teil)
            vergleich = rendern(cls.obj, ordner / f'{teil}_vergleich.png',
                                'genesis9_koerper,' + teil)
            b = Exportfleckenpruefung(vergleich, silhouette).bericht()
            b['name'] = teil
            cls.berichte[teil] = b

    def setUp(self):
        if not self.obj:
            raise unittest.SkipTest(
                'Keine Exportdatei unter %s — erst im Browser exportieren, dann läuft der Fall.'
                % settings.HUMANBODY_MODELLEXPORT_VORGABE_DIR)
        if not self.berichte:
            raise unittest.SkipTest('Kein Teil ohne eigene Bildkarte in dieser Exportdatei.')

    def test_kein_teil_hat_fremde_farbe_im_umriss(self):
        for teil, b in self.berichte.items():
            with self.subTest(teil=teil):
                if b['punkte'] < MINDESTPUNKTE:
                    continue
                self.assertFalse(
                    b['fleckig'],
                    'Fremde Farbe im Umriss von "%s": %.1f %% der Silhouette (%d Punkte) '
                    'weichen von der Hauptfarbe %s ab — verdeckte Haut, die durchsticht?\n%s'
                    % (teil, 100 * b['fleckenanteil'], b['punkte'], b['hauptfarbe'], self.obj))
