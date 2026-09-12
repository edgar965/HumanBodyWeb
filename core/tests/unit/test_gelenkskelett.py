# -*- coding: utf-8 -*-
u"""Gelenkskelett — aus Gelenkpunkten ein Skelett, das man BESPIELEN kann.

WARUM (Edgar, 07.09.2026: „du hast doch retarget fuer das SMPL skeleton,
konfiguriere das"): SMPL und MakeHuman liefern ihr Skelett als Punkte. Zum
Zeichnen reicht das; zum Abspielen nicht — der Retarget-Motor fragt jeden
Zielknochen, wohin er in RUHE zeigt, und bei lauter Einheitsdrehungen
antwortet jeder dasselbe.

DIE PROBE IST DIE UMKEHRUNG
===========================
`weltlagen()` rechnet die gebaute Kette vorwaerts. Sie MUSS die Gelenke und
ihre Richtungen wieder treffen — bei jedem Vorzeichenfehler, jeder
vergessenen Elterndrehung und jeder verwechselten Reihenfolge tut sie es
nicht. Das ist eine Gegenprobe gegen bekannte Wahrheit, keine gegen sich
selbst.
"""
import unittest

import numpy as np

from humanbody_core.quaternion import Quat
from humanbody_core.skeleton.gelenkskelett import Gelenkskelett


def kette(*glieder):
    u"""Eine Knochenliste aus `(name, eltern, kopf, schwanz)`."""
    return [{'name': n, 'eltern': e, 'kopf': list(k), 'schwanz': list(s)}
            for n, e, k, s in glieder]


ARM = kette(
    ('wurzel', None, (0, 1.0, 0), (0, 1.2, 0)),
    ('schulter', 'wurzel', (0, 1.2, 0), (0.2, 1.2, 0)),
    ('oberarm', 'schulter', (0.2, 1.2, 0), (0.5, 1.05, 0)),
    ('hand', 'oberarm', (0.5, 1.05, 0), (0.6, 0.98, 0.05)),
)


class GelenkskelettTest(unittest.TestCase):

    databases = set()

    # ------------------------------------------------------- die Gegenprobe

    def test_die_kette_trifft_die_gelenke_wieder(self):
        u"""Vorwaerts gerechnet muss jeder Knochen an seinem Punkt landen."""
        skelett = Gelenkskelett(ARM)
        lagen = skelett.weltlagen()
        for k in ARM:
            punkt, _ = lagen[k['name']]
            self.assertLess(np.linalg.norm(punkt - np.array(k['kopf'])), 1e-5,
                            k['name'])

    def test_die_kette_trifft_die_richtungen_wieder(self):
        u"""Und in die Richtung zeigen, die `schwanz` vorgibt."""
        skelett = Gelenkskelett(ARM)
        lagen = skelett.weltlagen()
        for k in ARM:
            soll = np.array(k['schwanz']) - np.array(k['kopf'])
            soll = soll / np.linalg.norm(soll)
            _, ist = lagen[k['name']]
            self.assertLess(np.linalg.norm(ist - soll), 1e-5, k['name'])

    def test_ohne_ruhedrehung_zeigt_alles_in_dieselbe_richtung(self):
        u"""Die Sabotage-Gegenprobe: genau das war der Fehler.

        Setzt man alle Ruhedrehungen auf die Einheit, zeigt jeder Knochen
        entlang der Achse — und die Richtungskorrektur des Retargets
        rechnet gegen eine Ruhelage, die die Figur nicht hat. Der Test
        haelt fest, dass die gebauten Drehungen wirklich verschieden sind.
        """
        skelett = Gelenkskelett(ARM)
        richtungen = [r for _, r in skelett.weltlagen().values()]
        paare = [float(np.dot(a, b)) for a in richtungen for b in richtungen]
        self.assertLess(min(paare), 0.99,
                        'alle Knochen zeigen in dieselbe Richtung')

    # ------------------------------------------------------------- Bauplan

    def test_lokale_lage_ist_relativ_zum_elternteil(self):
        u"""Weltpunkte unveraendert einzusetzen addiert jede Ebene doppelt."""
        plan = {k['name']: k for k in Gelenkskelett(ARM).bauplan()}
        self.assertNotEqual(plan['hand']['pos'], plan['hand']['kopf'])
        # Die Wurzel hat keinen Elternteil: dort ist beides dasselbe.
        self.assertEqual(plan['wurzel']['pos'], plan['wurzel']['kopf'])

    def test_jedes_blatt_bekommt_einen_endknochen(self):
        plan = Gelenkskelett(ARM).bauplan()
        enden = [k for k in plan if k['ende']]
        self.assertEqual([k['name'] for k in enden], ['hand_ende'])
        lagen = Gelenkskelett(ARM).weltlagen()
        self.assertLess(np.linalg.norm(lagen['hand_ende'][0]
                                       - np.array(ARM[-1]['schwanz'])), 1e-5)

    def test_endknochen_der_laenge_null_entfaellt(self):
        u"""Eine Linie ohne Laenge wird gezeichnet und ist doch unsichtbar."""
        plan = Gelenkskelett(kette(
            ('a', None, (0, 1, 0), (0, 1, 0)))).bauplan()
        self.assertEqual([k for k in plan if k['ende']], [])

    def test_eltern_stehen_vor_ihren_kindern(self):
        u"""Auch wenn die Quelle sie verkehrt herum liefert."""
        plan = Gelenkskelett(list(reversed(ARM))).bauplan()
        gesehen = set()
        for k in plan:
            if k['eltern']:
                self.assertIn(k['eltern'], gesehen, k['name'])
            gesehen.add(k['name'])

    def test_unbekannter_elternteil_gilt_als_wurzel(self):
        u"""Verworfen wird nichts — ein Knochen im Nichts faellt eher auf."""
        plan = Gelenkskelett(kette(
            ('a', 'gibtsnicht', (0, 1, 0), (0, 1.2, 0)))).bauplan()
        self.assertEqual(plan[0]['eltern'], None)

    def test_knochen_ohne_laenge_erbt_die_lage_des_elternteils(self):
        u"""Eine Richtung zu erfinden waere schlimmer als sie zu erben."""
        plan = {k['name']: k for k in Gelenkskelett(kette(
            ('a', None, (0, 1, 0), (0.3, 1, 0)),
            ('b', 'a', (0.3, 1, 0), (0.3, 1, 0)))).bauplan()}
        self.assertEqual([round(w, 6) for w in plan['b']['quat']],
                         [0.0, 0.0, 0.0, 1.0])

    # ------------------------------------------------------- fuer den Motor

    def test_geometrie_kennt_die_achse_und_alle_knochen(self):
        u"""Ein Knochen ohne Eintrag bekaeme keine Spur und bliebe stehen."""
        geometrie = Gelenkskelett(ARM).geometrie()
        self.assertEqual(len(geometrie.bones), len(ARM) + 1)   # + Endknochen
        self.assertEqual(geometrie.root_name, 'wurzel')
        self.assertTrue(np.allclose(geometrie.richtungsachse,
                                    Gelenkskelett.ACHSE))

    def test_geometrie_kennt_die_ruherichtungen(self):
        u"""Was `Richtungskorrektur._ruherichtung` liest, muss stimmen."""
        geometrie = Gelenkskelett(ARM).geometrie()
        for k in ARM:
            soll = np.array(k['schwanz']) - np.array(k['kopf'])
            soll = soll / np.linalg.norm(soll)
            ist = Quat.rotate(geometrie.bones[k['name']].world_rest_quat,
                              geometrie.richtungsachse)
            self.assertLess(np.linalg.norm(ist - soll), 1e-5, k['name'])
