# -*- coding: utf-8 -*-
u"""Hilfe -> Kleidung: die beiden Seiten und ihre Datenquelle.

WARUM ALS TEST (07.09.2026): Die Seiten liegen unter `/hilfe/`, einem
Praefix, der djangoBase gehoert. Beide Richtungen muessen gelten — die
eigenen Seiten antworten, UND die mitgelieferten bleiben erreichbar. Genau
dort ist das Projekt am 27.08.2026 schon einmal hineingelaufen: Vier
mitgelieferte JS-Module riefen `/hilfe/tests/aufzeichnung/` fest an und
landeten bei jedem Seitenaufruf dreimal in einer 404 — ohne Fehlerseite,
ohne Logeintrag.

(Die urspruengliche Begruendung hier war falsch: „ein include beendet die
Suche". Das tut es nicht — Django probiert die folgenden Muster weiter.
Aufgefallen ist es, weil die Gegenprobe mit vertauschter Reihenfolge NICHT
rot wurde.)

Dazu die Datenquelle: Die Messmatrix kommt aus YAML-Dateien, die ein
Messlauf schreibt. Fehlt eine, muss die Seite das SAGEN — eine leere
Tabelle saehe aus wie „alles gut" (dieselbe Lehre wie bei der Fehlerseite,
die alte Fehler zeigte).
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from django.test import Client, SimpleTestCase

from GarmentCode.messreihen import Garmentcodemessung
from kleidung.verfahren import Kleidungsverfahren
from kleidung.tempo import Kleidungstempo


class SeitenTest(SimpleTestCase):
    u"""Beide Seiten antworten und tragen ihren Inhalt."""

    databases = []

    def setUp(self):
        self.client = Client()

    def test_uebersicht_antwortet(self):
        antwort = self.client.get('/hilfe/kleidung/')
        self.assertEqual(antwort.status_code, 200)

    def test_garmentcode_antwortet(self):
        antwort = self.client.get('/hilfe/kleidung/garmentcode/')
        self.assertEqual(antwort.status_code, 200)

    def test_uebersicht_nennt_alle_verfahren(self):
        u"""Alle sechs Verfahren stehen auf der Seite — nicht nur die,
        an die man beim Schreiben gerade gedacht hat."""
        text = self.client.get('/hilfe/kleidung/').content.decode('utf-8')
        for verfahren in Kleidungsverfahren.alle():
            self.assertIn(verfahren['name'], text, verfahren['schluessel'])

    def test_ungemessenes_steht_ausgeschrieben_da(self):
        u"""Wo keine Messreihe vorliegt, darf die Zelle nicht leer sein."""
        text = self.client.get('/hilfe/kleidung/').content.decode('utf-8')
        self.assertIn('nicht gemessen', text)

    def test_beide_seiten_verweisen_aufeinander(self):
        uebersicht = self.client.get('/hilfe/kleidung/').content.decode('utf-8')
        einzeln = self.client.get(
            '/hilfe/kleidung/garmentcode/').content.decode('utf-8')
        self.assertIn('/hilfe/kleidung/garmentcode/', uebersicht)
        self.assertIn('/hilfe/kleidung/', einzeln)


class MenueTest(SimpleTestCase):
    u"""Die Punkte haengen in djangoBases Hilfe-Gruppe."""

    databases = []

    def test_hilfe_extra_ist_gesetzt(self):
        from django.conf import settings
        eintraege = settings.DJANGOBASE.get('hilfe_extra') or []
        self.assertTrue(eintraege, 'hilfe_extra fehlt')
        adressen = [unterpunkt['url']
                    for eintrag in eintraege
                    for unterpunkt in eintrag.get('untermenu', [])]
        self.assertIn('/hilfe/kleidung/', adressen)
        self.assertIn('/hilfe/kleidung/garmentcode/', adressen)

    def test_djangobase_hilfe_bleibt_erhalten(self):
        u"""Die mitgelieferten Hilfeseiten duerfen durch die eigenen nicht
        verdeckt werden — waere der eigene Praefix zu weit gefasst
        (`hilfe/` statt `hilfe/kleidung/`), schluckte er sie."""
        for pfad in ('/hilfe/versionen/', '/hilfe/logs/', '/hilfe/tests/'):
            antwort = Client().get(pfad)
            self.assertEqual(antwort.status_code, 200, pfad)


class MessungTest(SimpleTestCase):
    u"""`Garmentcodemessung` liest die Messreihen — oder sagt, dass sie fehlen."""

    databases = []

    def test_fehlende_datei_gibt_none(self):
        u"""Nicht `{}`: Eine leere Tabelle sieht aus wie „nichts gefunden",
        nicht wie „nie gemessen".

        ZUM ZWEITEN MAL UMGELEITET, ZUM ZWEITEN MAL DIESELBE FALLE
        ==========================================================
        07.09.2026: Die Umleitung stand auf `HUMANBODY_ROOT`, die Reihen
        zogen nach `Assets/` — der Test las die echten Messreihen.
        08.09.2026: Die Umleitung stand auf `ASSETS_ROOT`, und
        `Garmentcodemessung` rechnet seinen Ordner seither aus der eigenen
        Lage (`Gcpfade`), nicht mehr aus den Settings — wieder ins Leere.

        Beide Male wurde der Test rot, weil er auf `None` prüft. Prüfte er
        auf „leer", wäre er still falsch geblieben. Die Gegenprobe steht
        deshalb jetzt VOR der eigentlichen Behauptung: erst zeigen, dass
        die Umleitung greift, dann messen
        (`~/.claude/rules/test-isolation.md`).
        """
        from GarmentCode.pfade import Gcpfade
        with tempfile.TemporaryDirectory() as ordner:
            with mock.patch.object(Gcpfade, 'PAKET', Path(ordner)):
                # Gegenprobe zuerst — sonst schlägt die Behauptung an, und
                # niemand sieht, dass gar nicht umgeleitet wurde.
                self.assertTrue(Garmentcodemessung.wurzel().startswith(ordner),
                                'Umleitung greift ins Leere')
                self.assertIsNone(Garmentcodemessung.matrix('humanbody'))
                self.assertEqual(Garmentcodemessung.koerper(), [])

    def test_matrix_wenn_vorhanden(self):
        if not os.path.isfile(Garmentcodemessung.pfad('humanbody')):
            self.skipTest('noch keine Messreihe abgelegt')
        matrix = Garmentcodemessung.matrix('humanbody')
        self.assertIsNotNone(matrix)
        self.assertTrue(matrix['koerper'], 'keine Körper in der Matrix')
        self.assertTrue(matrix['zeilen'], 'keine Stücke in der Matrix')
        self.assertEqual(
            matrix['anzahl'],
            matrix['gelungen'] + matrix['fehlgeschlagen'])
        # Jede Zeile hat so viele Zellen wie es Körper gibt — sonst
        # verrutscht die Tabelle, ohne dass es auffällt.
        for zeile in matrix['zeilen']:
            self.assertEqual(len(zeile['zellen']), len(matrix['koerper']),
                             zeile['stueck'])

    def test_zellenzustand_folgt_dem_wert(self):
        u"""Die Farbe der Zelle muss am Wert hängen, nicht am Zufall."""
        gut = Garmentcodemessung._zelle({'durchstich_prozent': 0.05})
        warnung = Garmentcodemessung._zelle({'durchstich_prozent': 1.2})
        schlecht = Garmentcodemessung._zelle({'durchstich_prozent': 4.0})
        fehler = Garmentcodemessung._zelle({'fehler': 'StitchingError'})
        self.assertEqual(gut['zustand'], 'gut')
        self.assertEqual(warnung['zustand'], 'warnung')
        self.assertEqual(schlecht['zustand'], 'fehler')
        self.assertEqual(fehler['zustand'], 'fehler')
        self.assertIn('StitchingError', fehler['titel'])


if __name__ == '__main__':
    unittest.main()


class KleidungTempoTest(SimpleTestCase):
    u"""Die Tempo-Erklaerung steht auf der Seite — mit ihren Zahlen.

    WARUM (Edgar, 08.09.2026: „schreibe das ueber makeHuman hier hinein"):
    Die Frage „warum ist MakeHuman so viel schneller" beantwortet man sonst
    nur durch Lesen von vier Modulen. Die Antwort ist nicht Optimierung,
    sondern ein anderes Verfahren — und drei naheliegende Beschleunigungen
    sind gemessen und verworfen. Genau das soll die Seite festhalten.
    """

    databases = []

    def test_seite_zeigt_den_vergleich(self):
        antwort = self.client.get('/hilfe/kleidung/')
        self.assertEqual(antwort.status_code, 200)
        text = antwort.content.decode('utf-8')
        for frage, _, _ in Kleidungstempo.vergleich():
            self.assertIn(frage, text)

    def test_seite_zeigt_die_gemessenen_phasen(self):
        u"""Jede Phase MIT ihrer Dauer — eine Tabelle ohne Zahlen erklaert nichts."""
        text = self.client.get('/hilfe/kleidung/').content.decode('utf-8')
        for name, dauer, _, _ in Kleidungstempo.phasen():
            self.assertIn(name, text)
            self.assertIn(str(dauer), text)

    def test_seite_nennt_was_verworfen_wurde(self):
        u"""Der teuerste Teil des Wissens: was NICHT hilft."""
        text = self.client.get('/hilfe/kleidung/').content.decode('utf-8')
        for idee, _ in Kleidungstempo.verworfen():
            self.assertIn(idee, text)

    def test_summe_kommt_aus_den_phasen(self):
        u"""Nicht danebengeschrieben: sonst laufen Tabelle und Summe
        auseinander, sobald jemand eine Zahl nachmisst."""
        self.assertAlmostEqual(
            Kleidungstempo.summe_s(),
            sum(d for _, d, _, _ in Kleidungstempo.PHASEN), places=2)

    def test_die_simulation_ist_der_groesste_posten(self):
        u"""Die Kernaussage der Seite, gegen die Daten geprueft.

        Faende jemand eine Beschleunigung von `run_sim`, muesste diese
        Tabelle mitwachsen — und dieser Test faellt auf, wenn sie es nicht
        tut.
        """
        groesster = max(Kleidungstempo.PHASEN, key=lambda z: z[1])
        self.assertIn('run_sim', groesster[0])
        self.assertGreater(groesster[2], 50)
