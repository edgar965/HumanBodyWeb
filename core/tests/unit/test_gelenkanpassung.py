# -*- coding: utf-8 -*-
u"""Das Skelett folgt dem Netz — und steht still, wenn das Netz stillsteht.

DER BEFUND (05.09.2026)
=======================
``def_skeleton.json`` ist eine Momentaufnahme aus Blender. Am Größenregler
wuchs der Körper von 110 cm auf 228 cm, das Skelett blieb bei 168 cm — die
Figur wuchs aus ihrem Rig heraus. `Gelenkanpassung` zieht die Knochenköpfe
nach.

WAS HIER GEPRÜFT WIRD — UND WARUM GERADE DAS
============================================
Der gefährliche Fall ist nicht „bewegt sich zu wenig", sondern **„bewegt
sich, obwohl niemand etwas verstellt hat"**. Ein Skelett, das bei Morph 0
auch nur um einen Millimeter von der exportierten Datei abweicht, verschiebt
jede Hautbindung und jede Retarget-Kalibrierung — lautlos, denn das Ergebnis
sieht ja aus wie ein Körper. Deshalb steht die Identität an erster Stelle
und wird auf **Gleichheit**, nicht auf Nähe geprüft.

Diese Fälle laufen ohne Datenbank und ohne die echten Morphdaten: Ein
Würfelnetz mit drei Knochen zeigt dieselbe Rechnung wie 18.210 Punkte mit
176 Knochen, nur nachrechenbar. Was an den echten Daten hängt (Zuordnung zu
`def_skeleton.json`, Vergleich mit der MB-Lab-Gelenkregel), steht in
`ProjektTemp/gelenkanpassung_probe.py` — dort liegen auch die Messwerte,
auf die sich der Modulkopf von `gelenkanpassung.py` beruft.
"""
import numpy as np
from django.test import SimpleTestCase

from humanbody_core import Gelenkanpassung


class Wuerfelnetz:
    u"""Das Testnetz — ein Gitter von Punkten auf und in einem Würfel.

    Nicht zufällig und nicht flach: Die Ähnlichkeitstransformation braucht
    eine Umgebung, die den Raum aufspannt, sonst ist ihre Drehung beliebig.

    Als Klasse und nicht als freie Funktion, weil das Werkzeug
    `freie-funktionen` genau danach sucht — eine Funktion auf Modulebene ist
    „eine Klasse, die noch niemand geschrieben hat".
    """

    @staticmethod
    def bauen(kante=1.0, punkte=6):
        achse = np.linspace(0.0, kante, punkte)
        gitter = np.stack(np.meshgrid(achse, achse, achse, indexing='ij'),
                          axis=-1)
        return gitter.reshape(-1, 3).astype(np.float64)


#: Drei Knochen in einer Kette, alle ohne Eigendrehung — dann ist die
#: lokale Lage eines Knochens genau sein Abstand zum Elternknochen.
KETTE = [
    {'name': 'wurzel', 'parent': None,
     'local_position': [0.5, 0.5, 0.0], 'local_quaternion': [1.0, 0.0, 0.0, 0.0]},
    {'name': 'mitte', 'parent': 'wurzel',
     'local_position': [0.0, 0.0, 0.5], 'local_quaternion': [1.0, 0.0, 0.0, 0.0]},
    {'name': 'spitze', 'parent': 'mitte',
     'local_position': [0.0, 0.0, 0.5], 'local_quaternion': [1.0, 0.0, 0.0, 0.0]},
]


class DieRuhelageBleibtDieRuhelage(SimpleTestCase):
    u"""Unverändertes Netz, unverändertes Skelett — auf die letzte Stelle."""

    def setUp(self):
        self.netz = Wuerfelnetz.bauen()
        self.anpassung = Gelenkanpassung(KETTE, self.netz, nachbarn=20)

    def test_die_lokalen_lagen_sind_zahl_fuer_zahl_die_datei(self):
        u"""Keine Toleranz — und zwar auf dem Weg, der wirklich hinausgeht.

        Bei ``Y = X`` ist die Transformation rechnerisch die Identität
        (siehe Modulkopf); übrig bleibt Fließkommastaub in der Größe von
        1e-17. Weil sowohl die Datei als auch die Nachricht sechs
        Nachkommastellen führen und `lokales_feld` genauso rundet, ist das
        Ergebnis hier nicht „fast", sondern gleich.
        """
        lagen = self.anpassung.lokale_positionen(self.netz)
        for knochen in KETTE:
            self.assertEqual(lagen[knochen['name']], knochen['local_position'])

    def test_kein_knochen_gilt_als_bewegt(self):
        u"""Das ist der Schalter, an dem die leere Nachricht hängt: Solange
        nichts bewegt ist, schickt der Server nichts."""
        self.assertEqual(self.anpassung.bewegte(self.netz), {})

    def test_auch_die_weltkoepfe_stimmen(self):
        u"""`weltkoepfe` rundet nicht — hier bleibt der Staub aus der SVD
        stehen (gemessen 2,8e-17 m, also 28 Attometer). Die Toleranz ist so
        gewählt, dass eine echte Verschiebung sie nie unterschreitet."""
        erwartet = np.array([[0.5, 0.5, 0.0], [0.5, 0.5, 0.5], [0.5, 0.5, 1.0]])
        np.testing.assert_allclose(self.anpassung.weltkoepfe(self.netz), erwartet,
                                   atol=1e-12)


class EineVerschiebungWandertMit(SimpleTestCase):
    u"""Das Netz als Ganzes versetzt: Die Knochen versetzen sich genauso,
    und ihre LOKALEN Lagen ändern sich dabei nicht — nur die der Wurzel."""

    def setUp(self):
        self.netz = Wuerfelnetz.bauen()
        self.anpassung = Gelenkanpassung(KETTE, self.netz, nachbarn=20)
        self.versetzt = self.netz + np.array([0.0, 0.0, 2.0])

    def test_die_koepfe_folgen_dem_netz(self):
        np.testing.assert_allclose(
            self.anpassung.weltkoepfe(self.versetzt),
            self.anpassung.koepfe + np.array([0.0, 0.0, 2.0]), atol=1e-9)

    def test_nur_die_wurzel_meldet_eine_neue_lage(self):
        u"""Kinder messen relativ zum Elternknochen — der ist mitgewandert."""
        self.assertEqual(list(self.anpassung.bewegte(self.versetzt)), ['wurzel'])


class EinGroesseresNetzErgibtEinGroesseresSkelett(SimpleTestCase):
    u"""Der gemeldete Fall: Der Körper wächst, das Skelett soll mitwachsen."""

    def setUp(self):
        self.netz = Wuerfelnetz.bauen()
        self.anpassung = Gelenkanpassung(KETTE, self.netz, nachbarn=20)
        # Um den Mittelpunkt des Würfels auf das Doppelte.
        mitte = np.array([0.5, 0.5, 0.5])
        self.doppelt = (self.netz - mitte) * 2.0 + mitte

    def test_die_knochenkette_wird_doppelt_so_lang(self):
        koepfe = self.anpassung.weltkoepfe(self.doppelt)
        vorher = np.linalg.norm(self.anpassung.koepfe[2] - self.anpassung.koepfe[0])
        nachher = np.linalg.norm(koepfe[2] - koepfe[0])
        # `float(...)`: `assertAlmostEqual` rechnet sonst auf `np.float64`,
        # was zur Laufzeit gutgeht und beim Typpruefer als `reportCallIssue`
        # steht — ein Befund, der einen echten verdeckt.
        self.assertAlmostEqual(float(nachher / vorher), 2.0, places=6)

    def test_alle_drei_knochen_melden_sich(self):
        self.assertEqual(sorted(self.anpassung.bewegte(self.doppelt)),
                         ['mitte', 'spitze', 'wurzel'])

    def test_die_lokale_lage_eines_kindes_verdoppelt_sich(self):
        u"""0,5 zwischen Wurzel und Mitte werden 1,0 — genau das ist die
        Länge, die dem Netz vorher gefehlt hat."""
        lagen = self.anpassung.lokale_positionen(self.doppelt)
        np.testing.assert_allclose(lagen['mitte'], [0.0, 0.0, 1.0], atol=1e-5)


class EineDrehungIstKeineVerzerrung(SimpleTestCase):
    u"""Ein gedrehtes Netz darf das Skelett drehen, aber nicht strecken.

    Die Ähnlichkeitstransformation kann das; eine freie affine Anpassung
    würde hier je nach Umgebung scheren.
    """

    def test_die_kettenlaenge_bleibt(self):
        netz = Wuerfelnetz.bauen()
        anpassung = Gelenkanpassung(KETTE, netz, nachbarn=20)
        winkel = np.pi / 3
        drehung = np.array([[np.cos(winkel), -np.sin(winkel), 0.0],
                            [np.sin(winkel), np.cos(winkel), 0.0],
                            [0.0, 0.0, 1.0]])
        koepfe = anpassung.weltkoepfe(netz @ drehung.T)
        vorher = np.linalg.norm(anpassung.koepfe[2] - anpassung.koepfe[0])
        nachher = np.linalg.norm(koepfe[2] - koepfe[0])
        self.assertAlmostEqual(float(nachher), float(vorher), places=6)


class EinFremdesNetzWirdAbgewiesen(SimpleTestCase):
    u"""Der Testcharakter hat 17.996 Punkte statt 18.210.

    Ohne diese Prüfung griffen die gemerkten Nachbarindizes ins Leere —
    entweder mit `IndexError` oder, schlimmer, auf die falschen Punkte.
    """

    def setUp(self):
        self.anpassung = Gelenkanpassung(KETTE, Wuerfelnetz.bauen(), nachbarn=20)

    def test_das_eigene_netz_passt(self):
        self.assertTrue(self.anpassung.passt_zu(Wuerfelnetz.bauen()))

    def test_ein_kuerzeres_nicht(self):
        self.assertFalse(self.anpassung.passt_zu(Wuerfelnetz.bauen(punkte=4)))

    def test_und_gar_keines_auch_nicht(self):
        self.assertFalse(self.anpassung.passt_zu(None))


class DieKnochenlisteBehaeltIhreForm(SimpleTestCase):
    u"""`knochenliste` liefert dieselbe Struktur wie `def_skeleton.json`.

    Sie ist der Weg für alles, was ein ganzes Skelett braucht statt nur der
    Änderung — die Reihenfolge und die Drehungen müssen dabei stehen bleiben.
    """

    def test_reihenfolge_eltern_und_drehungen_bleiben(self):
        netz = Wuerfelnetz.bauen()
        anpassung = Gelenkanpassung(KETTE, netz, nachbarn=20)
        liste = anpassung.knochenliste(netz * 1.5)
        self.assertEqual([k['name'] for k in liste],
                         [k['name'] for k in KETTE])
        self.assertEqual([k['parent'] for k in liste],
                         [k['parent'] for k in KETTE])
        self.assertEqual([k['local_quaternion'] for k in liste],
                         [k['local_quaternion'] for k in KETTE])

    def test_die_vorlage_bleibt_unberuehrt(self):
        u"""`dict(eintrag, ...)` kopiert — sonst wäre die Ruhelage nach dem
        ersten Regler weg, und der zweite rechnete gegen sich selbst."""
        netz = Wuerfelnetz.bauen()
        anpassung = Gelenkanpassung(KETTE, netz, nachbarn=20)
        anpassung.knochenliste(netz * 1.5)
        self.assertEqual(KETTE[1]['local_position'], [0.0, 0.0, 0.5])


class EinZyklusInDerElternkette(SimpleTestCase):
    u"""Die Datei kommt von außen — eine Endlosrekursion wäre ein Hänger
    ohne Fehlermeldung, und ein hängender Daphne-Faden fällt niemandem auf."""

    def test_er_wird_gemeldet_statt_zu_haengen(self):
        ring = [
            {'name': 'a', 'parent': 'b', 'local_position': [0.0, 0.0, 0.1],
             'local_quaternion': [1.0, 0.0, 0.0, 0.0]},
            {'name': 'b', 'parent': 'a', 'local_position': [0.0, 0.0, 0.1],
             'local_quaternion': [1.0, 0.0, 0.0, 0.0]},
        ]
        with self.assertRaises(ValueError):
            Gelenkanpassung(ring, Wuerfelnetz.bauen(), nachbarn=20)
