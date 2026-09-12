# -*- coding: utf-8 -*-
u"""UMA gegen UMA Python — vier Gegenproben gegen Unitys eigenen Bau.

WARUM (Edgar, 08.09.2026: „erstelle doch genau das gleiche UMA Modell über
unity, und überprüfe mit UMA Python", dann: „mach einen testcase der UMA und
UMA Python erstellt und vergleicht. zweiter Testcases mit Skeleton beide,
dritter mit Animation, vierter mit 3 Kleidungsstücke")
=====================================================================
Der Port hatte an diesem Tag Fehler, die alle wie Darstellungsprobleme
aussahen und keiner durch Nachdenken zu finden war. Gefunden hat sie erst
der Vergleich mit dem Ergebnis, das Unity selbst liefert:

    Dreiecke   58.538 statt 29.430   — alle fünf LOD-Stufen übereinander
                                       (`Slot._dreiecke`, `lodRanges`)
    Punkte     16.277 = 16.277       — stimmte
    Hülle      identisch             — stimmte

Ein Unity-Bau kostet im Auftragsmodus 8 Sekunden. Das ist billiger als
jede Überlegung darüber, welche Zahl richtig sein könnte.

DIE REFERENZDATEIEN WERDEN NICHT IM TEST GEBAUT
===============================================
Sie brauchen den Unity-Editor; ein Testlauf darf davon nicht abhängen.
Fehlt eine, sagt der Test, mit welchem Aufruf sie entsteht — statt still
grün zu sein (`~/.claude/rules/analysewerkzeuge.md`: ein Prüfer, der
nichts findet und Entwarnung meldet, ist der teuerste).
"""
import sys
import unittest
from pathlib import Path

from django.conf import settings

sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

import numpy as np                                          # noqa: E402

RASSE = 'Human Male 3.0'
#: Drei Stücke aus drei verschiedenen Plätzen — Oberkörper, Beine, Füße.
KLEIDUNG = ['male_hoodie_blue_Recipe', 'male_shorts_black_cotton_Recipe',
            'M_ChallengerBoots_Recipe']


def _katalog():
    return Path(settings.FIGUREN_KATALOG) / 'uma'


def _referenz(name, kleidung=None):
    u"""Die Unity-GLB — oder eine Anleitung, wie sie entsteht."""
    datei = _katalog() / ('%s.glb' % name)
    if datei.is_file():
        return datei
    stuecke = '","'.join(kleidung) if kleidung else '-'
    raise unittest.SkipTest(
        'Referenz %s fehlt. Erzeugen mit:\n'
        '  curl -X POST http://127.0.0.1:8081/api/character/uma-figur/bauen/ '
        '-H "Content-Type: application/json" -d \'{"rasse":"%s",'
        '"name":"%s","zeiger":0,"kleidung":["%s"]}\''
        % (datei, RASSE, name, stuecke))


def _bauen(kleidung=None):
    from UMA_Python.figur import Figur
    return Figur(str(settings.UMA_PROJEKT)).bauen(RASSE, kleidung=kleidung)


class NetzGegenUnity(unittest.TestCase):
    u"""Fall 1 — dieselbe Rasse, nackt: Netz gegen Netz."""

    databases = set()

    @classmethod
    def setUpClass(cls):
        from UMA_Python.gegenprobe import Unityglb
        cls.unity = Unityglb(_referenz('Gegenprobe_nackt'))
        cls.gebaut = _bauen()

    def test_punktzahl_ist_dieselbe(self):
        self.assertEqual(len(self.gebaut.netz.punkte),
                         len(self.unity.punkte))

    def test_dreieckszahl_ist_dieselbe(self):
        u"""Der Fall, der `lodRanges` ans Licht brachte: 58.538 statt 29.430.

        UMA legt fünf Detailstufen in dieselbe `triangles`-Liste; nur die
        erste ist das volle Netz. Wer alle nimmt, legt vier gröbere Netze
        darüber — im Bild Facetten und flackernde Flächen.
        """
        self.assertEqual(len(self.gebaut.netz.dreiecke), self.unity.dreiecke)

    def test_die_huelle_stimmt_ueberein(self):
        eigen = self.gebaut.punkte()
        unten, oben = self.unity.huelle()
        for achse in range(3):
            self.assertAlmostEqual(float(eigen[:, achse].min()),
                                   float(unten[achse]), places=2)
            self.assertAlmostEqual(float(eigen[:, achse].max()),
                                   float(oben[achse]), places=2)

    def test_die_punktwolken_liegen_aufeinander(self):
        u"""In BEIDE Richtungen gemessen.

        Eine Wolke, die eine Teilmenge der anderen ist, sieht in einer
        Richtung perfekt aus. Der Restabstand ist die Reglerstellung:
        Von den 57 DNA-Reglern wirken sechs schon bei ihrer Vorgabe
        (`EyePosition`, `lipsSize`, `earsYaw`, …), und das bewegt das
        Netz um genau die 0,11 mm, die hier stehen bleiben.
        """
        from UMA_Python.gegenprobe import Unityglb
        eigen = self.gebaut.punkte()
        fremd = self.unity.punkte
        for a, b, richtung in ((eigen, fremd, 'Python->Unity'),
                               (fremd, eigen, 'Unity->Python')):
            abstand = Unityglb.abstaende(a, b)
            self.assertLess(float(np.median(abstand)), 1.0, richtung)
            self.assertLess(float(abstand.max()), 15.0, richtung)


class SkelettGegenUnity(unittest.TestCase):
    u"""Fall 2 — dasselbe Skelett auf beiden Wegen."""

    databases = set()

    @classmethod
    def setUpClass(cls):
        from UMA_Python.gegenprobe import Unityglb
        cls.unity = Unityglb(_referenz('Gegenprobe_nackt'))
        cls.gebaut = _bauen()
        cls.fremd = cls.unity.bindeposen()

    def test_jeder_knochen_heisst_gleich(self):
        eigen = {k.name for k in self.gebaut.netz.knochen}
        self.assertEqual(eigen, set(self.fremd),
                         u'Knochennamen müssen deckungsgleich sein')

    def test_die_knochenlaengen_sind_gleich(self):
        u"""Die achsenunabhängige Probe — und die scharfe.

        Unity exportiert nach glTF und SPIEGELT dabei x (linkshändig ->
        rechtshändig, dieselbe Sache wie `Formregler.spiegeln`). Absolute
        Lagen zu vergleichen misst deshalb die Konvention, nicht das
        Skelett: über den Szenengraphen blieben nach der besten starren
        Passung 115 mm Median stehen, und das sah aus wie ein Befund.

        Der Abstand zweier Knochen ist unter Drehung UND Spiegelung
        gleich. Gemessen am 08.09.2026 über alle 228 Eltern-Kind-Paare:
        exakt 0,000000 mm.
        """
        eigen = self._weltlagen()
        fremd = {n: np.linalg.inv(m)[:3, 3] for n, m in self.fremd.items()}
        skelett = self.gebaut.skelett()
        abweichung = []
        for i, knochen in enumerate(skelett.knochen):
            vater = int(skelett.eltern[i])
            if vater < 0:
                continue
            kind, eltern = knochen.name, skelett.knochen[vater].name
            if kind not in fremd or eltern not in fremd:
                continue
            abweichung.append(abs(
                float(np.linalg.norm(eigen[kind] - eigen[eltern]))
                - float(np.linalg.norm(fremd[kind] - fremd[eltern]))))
        self.assertGreater(len(abweichung), 200, u'zu wenige Paare geprüft')
        self.assertLess(max(abweichung) * 1000, 0.5,
                        u'Knochenlängen weichen ab')

    def test_die_wurzel_ist_dieselbe(self):
        skelett = self.gebaut.skelett()
        wurzeln = [k.name for i, k in enumerate(skelett.knochen)
                   if int(skelett.eltern[i]) < 0]
        self.assertEqual(wurzeln, ['Global'])
        self.assertIn('Global', self.fremd)

    def _weltlagen(self):
        posen = self.gebaut.netz.bindeposen
        return {k.name: np.linalg.inv(posen[i])[:3, 3]
                for i, k in enumerate(self.gebaut.netz.knochen)}
