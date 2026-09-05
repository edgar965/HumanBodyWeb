# -*- coding: utf-8 -*-
"""Die Skripte neben dem Projekt müssen noch importieren können.

DER BEFUND (02.09.2026, Code Review)
====================================
Zwei Prüfskripte waren seit dem Klassen-Umbau tot, ohne dass es jemand
bemerkte:

* `Docu/golden_master_retarget.py` — der Golden Master des Retargets.
  `SkeletonRigify` ist von `skeleton.py` nach `rigify.py` gewandert;
  das Skript starb in der Importzeile.
* `Docu/gegenprobe_pushout.py` — die Gegenprobe zum Push-Out. Sie holte
  zwei private Funktionen, die in `Netzmathematik` aufgegangen sind.
  Der Docstring von `Netzmathematik.herausschieben` verweist auf sie
  als Beleg.

Beides sind Sicherheitsnetze. Ein totes Sicherheitsnetz meldet nicht
rot, es meldet gar nichts — man merkt es erst, wenn man es braucht.

WARUM KEIN VORHANDENES WERKZEUG DAS SAH
=======================================
`proben` sucht unter `Docu/umbau/`; beide liegen eine Ebene höher.
`tote-importe` prüft benutzte Namen, nicht auflösbare Ziele.
`esmodulimporte` ist für JavaScript. Und ein Skript wird nirgends
importiert — also fasst es kein Test an.

WAS GEPRÜFT WIRD
================
Für jede `.py` unter `Docu/`, `scripts/` und `werkzeug/`: Lässt sich
jeder Import auf Modulebene, der auf ein EIGENES Paket zeigt, wirklich
auflösen — Modul und Name? Ausgeführt wird dabei nichts (siehe
`_skriptbaum`).
"""
from django.test import SimpleTestCase

from ._skriptbaum import Skriptbaum


class JederSkriptimportFindetSeinZiel(SimpleTestCase):
    """Kein Skript zeigt auf ein Modul oder einen Namen, den es nicht gibt."""

    def test_kein_import_zeigt_ins_leere(self):
        tot = Skriptbaum.unaufloesbar()
        self.assertEqual(tot, [], 'tote Importe in Skripten:\n' + '\n'.join(
            '  %s  %s  ->  %s' % z for z in tot))

    def test_es_werden_ueberhaupt_importe_geprueft(self):
        """Sonst bestünde die Prüfung oben mit einer leeren Menge."""
        self.assertGreater(Skriptbaum.geprueft(), 20)

    def test_es_werden_ueberhaupt_dateien_gefunden(self):
        self.assertGreater(len(list(Skriptbaum.dateien())), 50)


class DiePruefungSiehtIhrenEigenenFall(SimpleTestCase):
    """Gegenprobe: Ein erfundener Name muss auffallen.

    Ohne sie wäre nicht gesagt, dass `unaufloesbar` überhaupt etwas
    findet — sie könnte auch deshalb leer sein, weil die Auflösung
    stillschweigend alles durchwinkt.
    """

    def test_ein_erfundener_name_wird_gemeldet(self):
        self.assertIsNotNone(Skriptbaum._gibt_es(
            'humanbody_core.skeleton', 'SkelettDasEsNichtGibt'))

    def test_ein_erfundenes_modul_wird_gemeldet(self):
        self.assertIsNotNone(Skriptbaum._gibt_es(
            'humanbody_core.skeleton.gibtesnicht', None))

    def test_der_echte_fall_von_damals(self):
        """`SkeletonRigify` liegt in `rigify`, nicht in `skeleton`."""
        self.assertIsNotNone(Skriptbaum._gibt_es(
            'humanbody_core.skeleton.skeleton', 'SkeletonRigify'))
        self.assertIsNone(Skriptbaum._gibt_es(
            'humanbody_core.skeleton', 'SkeletonRigify'))

    def test_ein_gueltiger_name_wird_nicht_gemeldet(self):
        self.assertIsNone(Skriptbaum._gibt_es(
            'humanbody_core.skeleton.bewegungsspuren', 'Bewegungsspuren'))
