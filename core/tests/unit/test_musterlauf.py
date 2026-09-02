# -*- coding: utf-8 -*-
u"""`Musterlauf` — und die Naht, die am Schwerpunkt zog.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`generate_from_pattern` (209 Zeilen) legt jedes Panel als Fächer an:
zuerst der **Schwerpunkt**, dann die Randpunkte. Die Karte, die je
Kante ihre Vertexnummern merkt, rechnete den Schwerpunkt aber nicht
mit:

    edge_verts.append(vert_offset + len(boundary_pts))    # ohne +1

`vert_offset` ist die Nummer des Schwerpunkts, der Randpunkt Nummer i
liegt also auf `vert_offset + 1 + i`. Jede Naht griff damit einen
Vertex zu früh — und eine Naht auf **Kante 0** zog nicht am Rand,
sondern am Mittelpunkt des Fächers.

Gemessen an einem Muster aus zwei Panels mit einer Naht: Ein Randpunkt
verschob sich nach dem Fix um **17,5 cm**, die Normalensumme des
angelegten Netzes um 2,9 %.

Der Test hält beides fest: dass keine Kantenliste den Schwerpunkt
enthält, und dass die Nummern zu den tatsächlichen Punkten passen.

Aufruf:  python manage.py test core.tests.unit.test_musterlauf
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()


from humanbody_core.cloth.musterlauf import Musterlauf  # noqa: E402


class Musterbau:
    u"""Baut die Punktwolken und Muster fuer diese Faelle.

    Stand bis zum 02.09.2026 als freie Funktionen auf
    Modulebene (Befund `freie-funktionen`).
    """

    @staticmethod
    def punktwolke():
        u"""Eine grobe stehende Röhre — NUR Punkte, keine Flächen.

        Heisst seit dem 01.09.2026 nicht mehr `_koerper`: In
        `test_kleidungsanpassung_lauf.py` steht ein `_koerper`, das
        `(Punkte, Vierecke)` liefert. Zwei Namen für zwei verschiedene
        Dinge — beim Übernehmen eines Falls in die andere Datei fällt das
        erst als Entpack-Fehler auf.
        """
        winkel = np.linspace(0, 2 * np.pi, 12, endpoint=False)
        punkte = [[0.16 * np.cos(w), 0.16 * np.sin(w), z]
                  for z in np.linspace(0, 1.7, 10) for w in winkel]
        return np.array(punkte, dtype=np.float64)

    @staticmethod
    def rechteck(x0, y0, breite, hoehe):
        ecken = [[x0, y0], [x0 + breite, y0],
                 [x0 + breite, y0 + hoehe], [x0, y0 + hoehe]]
        return {'vertices': ecken,
                'edges': [{'endpoints': [i, (i + 1) % 4]} for i in range(4)]}

    @staticmethod
    def muster():
        return {
            'panels': {
                'vorne': dict(Musterbau.rechteck(-18, 90, 36, 45), placement='front'),
                'hinten': dict(Musterbau.rechteck(-18, 90, 36, 45), placement='back'),
            },
            'stitches': [{'panelA': 'vorne', 'edgeA': 0,
                          'panelB': 'hinten', 'edgeB': 2}],
        }


class KantenkarteTest(SimpleTestCase):
    u"""Die Vertexnummern je Kante zeigen auf Randpunkte."""

    def setUp(self):
        self.lauf = Musterlauf(Musterbau.muster(), Musterbau.punktwolke())
        self.vertices, self.dreiecke = self.lauf.bauen()

    def test_kein_schwerpunkt_in_einer_kantenliste(self):
        u"""DER FALL VON FRÜHER: Kante 0 enthielt den Schwerpunkt.

        Die Schwerpunkte sind die jeweils ERSTEN Vertices eines Panels.
        Welche Nummern das sind, steht in den Dreiecken: Jedes Dreieck
        des Fächers beginnt beim Schwerpunkt.
        """
        schwerpunkte = {int(d[0]) for d in self.dreiecke}
        for schluessel, nummern in self.lauf.kantenpunkte.items():
            getroffen = schwerpunkte & set(nummern)
            self.assertEqual(getroffen, set(),
                             'Kante %s nennt den Schwerpunkt %s'
                             % (schluessel, getroffen))

    def test_die_kanten_decken_genau_den_rand(self):
        u"""Zusammen nennen die Kanten eines Panels jeden Randpunkt genau einmal.

        Das ist die eigentliche Zusicherung: Ein Panel belegt einen
        zusammenhängenden Block von Vertices, dessen erster der
        Schwerpunkt ist. Alles danach ist Rand, und jeder Randpunkt
        gehört zu genau einer Kante — auch der letzte, der beim
        Off-by-one durchs Raster fiel.
        """
        for panel in ('vorne', 'hinten'):
            nummern = [n for (p, _), liste
                       in self.lauf.kantenpunkte.items() if p == panel
                       for n in liste]
            self.assertEqual(len(nummern), len(set(nummern)),
                             'ein Randpunkt steht in zwei Kanten')
            schwerpunkt = min(nummern) - 1
            self.assertEqual(sorted(nummern),
                             list(range(schwerpunkt + 1,
                                        schwerpunkt + 1 + len(nummern))),
                             'die Kanten lassen eine Lücke im Rand von %s'
                             % panel)

    def test_jede_nummer_liegt_im_netz(self):
        for nummern in self.lauf.kantenpunkte.values():
            for nummer in nummern:
                self.assertLess(nummer, len(self.vertices))


class NahtTest(SimpleTestCase):
    u"""Vernähte Kanten liegen danach aufeinander."""

    def test_die_vernaehten_punkte_fallen_zusammen(self):
        lauf = Musterlauf(Musterbau.muster(), Musterbau.punktwolke())
        vertices, _ = lauf.bauen()
        a = lauf.kantenpunkte[('vorne', 0)]
        b = lauf.kantenpunkte[('hinten', 2)]
        for ia, ib in zip(a, b):
            self.assertTrue(np.allclose(vertices[ia], vertices[ib]),
                            'Naht %d/%d liegt auseinander: %s vs %s'
                            % (ia, ib, vertices[ia], vertices[ib]))

    def test_eine_naht_ins_leere_stoert_nicht(self):
        u"""Ein Stich auf ein Panel, das es nicht gibt, wird übergangen."""
        muster = Musterbau.muster()
        muster['stitches'].append({'panelA': 'gibtsnicht', 'edgeA': 0,
                                   'panelB': 'hinten', 'edgeB': 0})
        vertices, dreiecke = Musterlauf(muster, Musterbau.punktwolke()).bauen()
        self.assertEqual(len(vertices), 20)
        self.assertEqual(len(dreiecke), 18)


class LeeresMusterTest(SimpleTestCase):
    u"""Was nicht reicht, gibt None statt einer Ausnahme."""

    def test_ohne_panels(self):
        self.assertEqual(Musterlauf({}, Musterbau.punktwolke()).bauen(), (None, None))

    def test_panel_mit_zwei_ecken(self):
        muster = {'panels': {'strich': {
            'vertices': [[0, 0], [1, 0]],
            'edges': [{'endpoints': [0, 1]}]}}, 'stitches': []}
        lauf = Musterlauf(muster, Musterbau.punktwolke())
        self.assertEqual(lauf.bauen(), (None, None))
