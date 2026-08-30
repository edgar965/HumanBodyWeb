# -*- coding: utf-8 -*-
"""Ein Gelenk mit ungewöhnlicher Kanalzahl darf die Zeile nicht verschieben.

ANLASS: Review-Befund zu `BvhDatei._frame_schreiben` (Nemotron, Bereich
`api_bvh`). Der dort behauptete Fehler — „schreibt Positionen auch bei drei
Kanälen" — trifft NICHT zu; die Wache `if kanaele >= 6` steht da. Beim
Nachsehen lag daneben ein echter:

    stelle += kanaele if kanaele >= 6 else 3

Für die beiden üblichen Fälle (3 und 6) ist das dasselbe. Für alles dazwischen
nicht: Ein Gelenk mit `CHANNELS 4` rückte um 3 weiter, und ab da landete jedes
weitere Gelenk der Zeile EINE SPALTE ZU FRÜH. Die Datei bleibt dabei formal
gültig — sie beschreibt nur eine andere Bewegung. Kein Fehler, keine Warnung,
nur eine Figur, die sich falsch bewegt.

Die Kanalzahl kommt ungeprüft aus dem Dateikopf (`int(teile[1])`); 4 und 5
sind nach der BVH-Spezifikation erlaubt.

GEPRÜFT WIRD DIE RECHNUNG, NICHT DIE DATEI
==========================================
`_frame_schreiben` braucht nur `ordnungen`, `self.gelenke` und `self.bvh` —
kein Dateisystem, kein Parser. Der Test baut die Werte direkt und schaut, an
welchen Spalten sie landen.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.bvh_datei import BvhDatei


class Bewegungsattrappe:
    """Was `_frame_schreiben` von `parse_bvh` liest."""

    def __init__(self, gelenke):
        self.names = ['G%d' % i for i in range(gelenke)]
        self.frame_count = 1
        # Einheitsquaternionen: Die Drehung ist überall 0 Grad, damit man
        # die POSITIONEN im Ergebnis wiedererkennt.
        self.quats = np.tile(np.array([0.0, 0.0, 0.0, 1.0]), (1, gelenke, 1))
        self.positions = np.zeros((1, gelenke, 3))
        for ji in range(gelenke):
            self.positions[0, ji] = [ji * 10 + 1, ji * 10 + 2, ji * 10 + 3]


class Schreibprobe(BvhDatei):
    """Ein `BvhDatei` ohne Datei — nur die Rechnung."""

    def __init__(self, gelenke):
        self.pfad = None
        self.bvh = Bewegungsattrappe(gelenke)
        self.angewandt = []

    @classmethod
    def zeile(cls, ordnungen):
        """Eine Zeile schreiben und die belegten Spalten zurückgeben."""
        from scipy.spatial.transform import Rotation
        probe = cls(len(ordnungen))
        werte = ['LEER'] * sum(k for k, _o in ordnungen)
        probe._frame_schreiben(Rotation, werte, 0, ordnungen)
        return werte


class KanalversatzTest(SimpleTestCase):

    #: Die übliche Wurzel: drei Positionen, drei Drehungen.
    WURZEL = (6, 'ZXY')
    #: Ein übliches Gelenk: nur Drehung.
    GELENK = (3, 'ZXY')

    def test_der_uebliche_fall_bleibt_wie_er_war(self):
        """6 + 3 + 3 — die Gegenprobe, dass der Fix nichts verschiebt."""
        werte = Schreibprobe.zeile([self.WURZEL, self.GELENK, self.GELENK])
        self.assertEqual(len(werte), 12)
        self.assertNotIn('LEER', werte, 'jede Spalte muss belegt sein')
        # Die Wurzelposition steht vorn und ist die des ERSTEN Gelenks.
        self.assertEqual(werte[:3], ['1.000000', '2.000000', '3.000000'])

    def test_vier_kanaele_verschieben_die_folgenden_gelenke_nicht(self):
        """DER FEHLER, festgenagelt.

        Nicht jede Spalte MUSS beschrieben werden: Bei vier erklaerten
        Kanaelen kennt die Rechnung nur drei Drehwinkel, die vierte Spalte
        behaelt ihren Originalwert aus der Zeile. Entscheidend ist, wo das
        FOLGENDE Gelenk anfaengt — mit `+= 3` waere es Spalte 9 statt 10
        gewesen, und ab da stuende die ganze Zeile verschoben.
        """
        werte = Schreibprobe.zeile([self.WURZEL, (4, 'ZXY'), self.GELENK])
        self.assertEqual(len(werte), 13)
        # 6 (Wurzel) + 4 (Gelenk mit vier Kanaelen) = Spalte 10.
        self.assertEqual(werte[9], 'LEER',
                         'die vierte Spalte des Gelenks bleibt unangetastet')
        self.assertTrue(all(w != 'LEER' for w in werte[10:13]),
                        'das dritte Gelenk gehoert auf 10..12, steht aber '
                        'auf: %s' % werte)

    def test_fuenf_kanaele_ebenso(self):
        werte = Schreibprobe.zeile([self.WURZEL, (5, 'ZXY'), self.GELENK])
        self.assertEqual(len(werte), 14)
        self.assertEqual(werte[9:11], ['LEER', 'LEER'])
        self.assertTrue(all(w != 'LEER' for w in werte[11:14]),
                        'das dritte Gelenk gehoert auf 11..13: %s' % werte)

    def test_die_alte_formel_haette_verschoben(self):
        """DIE GEGENPROBE: Ohne sie prueft der Test nichts.

        So stand es bis zum 28.08.2026 — nachgerechnet, nicht behauptet.
        """
        ordnungen = [self.WURZEL, (4, 'ZXY'), self.GELENK]
        stelle, stellen = 0, []
        for kanaele, _ordnung in ordnungen:
            stellen.append(stelle)
            stelle += kanaele if kanaele >= 6 else 3      # die alte Formel
        self.assertEqual(stellen, [0, 6, 9],
                         'die alte Formel setzt das dritte Gelenk auf 9')
        stelle, neue = 0, []
        for kanaele, _ordnung in ordnungen:
            neue.append(stelle)
            stelle += kanaele                             # die neue
        self.assertEqual(neue, [0, 6, 10])

    def test_positionen_nur_ab_sechs_kanaelen(self):
        """Die Wache, die der Review-Befund für kaputt hielt — sie hält.

        Bei drei Kanälen darf KEINE Position geschrieben werden; die drei
        Werte des Gelenks sind Drehwinkel (hier 0).
        """
        werte = Schreibprobe.zeile([self.GELENK, self.GELENK])
        self.assertEqual(len(werte), 6)
        self.assertTrue(all(float(w) == 0.0 for w in werte),
                        'bei 3 Kanaelen stehen dort Drehwinkel, keine '
                        'Positionen: %s' % werte)
