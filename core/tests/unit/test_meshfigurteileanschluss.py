# -*- coding: utf-8 -*-
"""Mesh to 3D: ein langer, starrer Bestandteil nimmt anliegende, zusammenhängende Flächen auf (14.10.2026, Stab mit Ast in der Robe).

Kunstnetz: ein Streifen (der „Stab") aus Dreiecken entlang x; daneben Streifen anderer Etiketten.
1. Ein Streifen, der ihm anliegt (alle Ecken ≤ 12 mm) und Punkte mit ihm teilt, kommt dazu.
2. Ein Streifen im selben Abstand ohne gemeinsame Punkte bleibt draußen (zufällig vorbeiziehender Stoff).
3. Ein Streifen weiter als 12 mm bleibt draußen; Flächen eines anderen Bestandteils (`andere`) werden nie genommen.
4. Ein Streifen, der nur über einen schon aufgenommenen Streifen mit dem Stab zusammenhängt, kommt mit (Wachsen über mehrere Runden).
5. `Meshfigurteile._anschliessen` fasst nur stabförmige Bestandteile an (ein Würfel bleibt, wie er ist) und lässt Flächen, die Sapiens als Hand sieht, draußen.

Sabotage-Gegenprobe: in `erweitern` die Bedingung `bekannt[ecken_nummern].any(axis=1)` weglassen → `test_2` rot; `<= cls.ANSCHLUSS_M` durch `<= 1.0` ersetzen → `test_3` rot; die Schleife über `RUNDEN` auf eine Runde
kürzen → `test_4` rot; `nie` in `_anschliessen` ohne `haende` → `test_5` rot.

Nicht gelaufen — läuft nur auf Ansage.
"""

from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.meshfigurteile import Meshfigurteile
from core.dienste.meshfigurteileanschluss import Meshfigurteileanschluss


def streifen(y0, y1, teilen_mit=None, start=0, laenge=1.0, schritte=20):
    """Zwei Punktreihen (y0 und y1) entlang x; Dreiecke dazwischen. `teilen_mit`: Nummern der vorhandenen Punktreihe y0 (Punkte werden geteilt, statt neu angelegt)."""
    xs = np.linspace(0.0, laenge, schritte + 1)
    unten = np.array([[x, y0, 0.0] for x in xs])
    oben = np.array([[x, y1, 0.0] for x in xs])
    if teilen_mit is None:
        punkte = np.concatenate([unten, oben])
        u = np.arange(schritte + 1) + start
        o = np.arange(schritte + 1) + start + schritte + 1
    else:
        punkte = oben
        u = np.asarray(teilen_mit)
        o = np.arange(schritte + 1) + start
    f = []
    for i in range(schritte):
        f.append([u[i], u[i + 1], o[i]])
        f.append([u[i + 1], o[i + 1], o[i]])
    return punkte, np.array(f)


class AnschlussTest(SimpleTestCase):
    databases = set()

    def _netz(self, *teile):
        """`teile`: Liste `(Punkte, Flächen)` mit Nummern, die schon auf das Gesamtnetz zeigen. Gibt (Punkte, Flächen, Maske des Stabs = erster Streifen)."""
        punkte = np.concatenate([p for p, _ in teile])
        flaechen = np.concatenate([f for _, f in teile])
        maske = np.zeros(len(flaechen), dtype=bool)
        maske[:len(teile[0][1])] = True
        return punkte, flaechen, maske

    def test_1_ein_anliegender_zusammenhaengender_streifen_kommt_dazu(self):
        stab = streifen(0.0, 0.02)
        daneben = streifen(0.0, 0.03, teilen_mit=np.arange(21) + 21, start=42)         # teilt die Punktreihe y = 0.02 des Stabs
        punkte, flaechen, maske = self._netz(stab, daneben)
        neu, dazu = Meshfigurteileanschluss.erweitern(flaechen, punkte, maske, np.zeros(len(flaechen), dtype=bool))
        self.assertEqual(dazu, len(daneben[1]))
        self.assertTrue(neu.all())

    def test_2_ein_streifen_ohne_gemeinsame_punkte_bleibt_draussen(self):
        stab = streifen(0.0, 0.02)
        vorbei = streifen(0.025, 0.035, start=42)                                       # nah, aber eigene Punkte
        punkte, flaechen, maske = self._netz(stab, vorbei)
        neu, dazu = Meshfigurteileanschluss.erweitern(flaechen, punkte, maske, np.zeros(len(flaechen), dtype=bool))
        self.assertEqual(dazu, 0)
        self.assertEqual(int(neu.sum()), int(maske.sum()))

    def test_3_zu_weit_und_fremde_bestandteile_bleiben_draussen(self):
        stab = streifen(0.0, 0.02)
        weit = streifen(0.0, 0.2, teilen_mit=np.arange(21) + 21, start=42)              # geteilte Punkte, aber Ecken bis 18 cm weg
        fremd = streifen(0.0, 0.03, teilen_mit=np.arange(21) + 21, start=63)            # anliegend, gehört aber einem anderen Bestandteil
        punkte, flaechen, maske = self._netz(stab, weit, fremd)
        andere = np.zeros(len(flaechen), dtype=bool)
        andere[len(stab[1]) + len(weit[1]):] = True
        neu, dazu = Meshfigurteileanschluss.erweitern(flaechen, punkte, maske, andere)
        self.assertEqual(dazu, 0)

    def test_4_wachsen_ueber_einen_aufgenommenen_streifen(self):
        stab = streifen(0.0, 0.004)
        erster = streifen(0.0, 0.008, teilen_mit=np.arange(21) + 21, start=42)          # teilt die Punktreihe y = 0.004 mit dem Stab
        zweiter = streifen(0.0, 0.011, teilen_mit=np.arange(21) + 42, start=63)         # teilt y = 0.008 mit dem ersten, nicht mit dem Stab — alle Ecken liegen trotzdem binnen 12 mm am Stab
        punkte, flaechen, maske = self._netz(stab, erster, zweiter)
        neu, dazu = Meshfigurteileanschluss.erweitern(flaechen, punkte, maske, np.zeros(len(flaechen), dtype=bool))
        self.assertEqual(dazu, len(erster[1]) + len(zweiter[1]))

    def test_5_nur_stabfoermige_bestandteile_und_nie_die_hand(self):
        stab = streifen(0.0, 0.02)
        daneben = streifen(0.0, 0.03, teilen_mit=np.arange(21) + 21, start=42)
        punkte, flaechen, maske = self._netz(stab, daneben)
        scan = SimpleNamespace(punkte=punkte, flaechen=flaechen, flaecheninhalte=lambda: np.full(len(flaechen), 1e-4))
        teile = [{'name': 'stab', 'maske': maske.copy(), 'flaechen': int(maske.sum())}]
        Meshfigurteile._anschliessen(scan, teile)                                        # der Streifen ist 1 m lang und 2 cm breit: stabförmig
        self.assertGreater(teile[0]['flaechen'], int(maske.sum()))
        self.assertEqual(teile[0]['anschluss_flaechen'], len(daneben[1]))
        # eine Hand-Fläche bleibt draußen: Sapiens-Stimmen (F, 28), Klasse 5 (Left_Hand) mit genug Pixeln auf den Flächen des Streifens
        klassen = np.zeros((len(flaechen), 28))
        klassen[len(stab[1]):, 5] = 9.0
        teile = [{'name': 'stab', 'maske': maske.copy(), 'flaechen': int(maske.sum())}]
        Meshfigurteile._anschliessen(scan, teile, klassen)
        self.assertNotIn('anschluss_flaechen', teile[0])
        # ein Würfel ist nicht stabförmig und bleibt unberührt
        w = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], dtype=float) * 0.02
        wf = np.array([[0, 1, 3], [0, 3, 2], [4, 5, 7], [4, 7, 6], [0, 1, 5], [0, 5, 4], [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 3, 7], [1, 7, 5]])
        scan_w = SimpleNamespace(punkte=w, flaechen=wf, flaecheninhalte=lambda: np.full(len(wf), 1e-4))
        teile = [{'name': 'wuerfel', 'maske': np.ones(len(wf), dtype=bool), 'flaechen': len(wf)}]
        Meshfigurteile._anschliessen(scan_w, teile)
        self.assertNotIn('anschluss_flaechen', teile[0])
