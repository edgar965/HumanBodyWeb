# -*- coding: utf-8 -*-
u"""Der Auftrag an Unity: was aus `kleidung` wird.

WARUM (Edgar, 08.09.2026: „wenn ich einer UMA figur ALLE kleider wegtue,
dann erscheinen plötzlich wieder alle"): Die leere Liste und „nicht
angegeben" waren dasselbe. Der Browser schickt bei „alles abgewählt" eine
leere Liste (`umakleider.js`: `.filter(Boolean)`), `if kleidung:` verwarf
sie, und drüben schaltet `loadDefaultRecipes = IsNullOrEmpty(...)` auf
UMAs Vorgabe je Platz. Das genaue Gegenteil der Eingabe — ohne Fehler,
ohne Meldung.

Geprüft wird der AUFTRAG, nicht der Unity-Lauf: Der braucht den Editor
und acht Sekunden. Was im Auftrag steht, entscheidet die Sache.
"""
import unittest
from unittest import mock

from core.dienste.umabauer import Umabauer


class Kleidungsauftrag(unittest.TestCase):

    databases = set()

    def _auftrag(self, kleidung):
        with mock.patch.object(Umabauer, '_auftrag',
                               side_effect=lambda name, auftrag, **k: auftrag):
            return Umabauer.bauen('Human Male 3.0', name='Probe',
                                  kleidung=kleidung)

    def test_nicht_angegeben_laesst_uma_entscheiden(self):
        self.assertNotIn('kleidung', self._auftrag(None))

    def test_genannte_rezepte_kommen_durch(self):
        auftrag = self._auftrag(['A_Recipe', 'B_Recipe'])
        self.assertEqual(auftrag['kleidung'], 'A_Recipe,B_Recipe')

    def test_leere_liste_heisst_nackt(self):
        u"""Der Fall, um den es geht."""
        self.assertEqual(self._auftrag([])['kleidung'], Umabauer.OHNE_KLEIDUNG)

    def test_nur_leere_eintraege_heissen_auch_nackt(self):
        u"""Ein Auswahlfeld auf „—" liefert einen leeren Text, keine
        fehlende Zeile — auch das ist eine Abwahl."""
        self.assertEqual(self._auftrag(['', '  '])['kleidung'],
                         Umabauer.OHNE_KLEIDUNG)

    def test_das_zeichen_ist_dasselbe_wie_drueben(self):
        u"""`UmaFigurExport.OhneKleidung` — zwei Seiten, ein Wert.

        Der Exporter ist eine Datei der Roomguest-Sitzung. Läuft er
        auseinander, baut Unity wieder angezogen, und niemand sieht,
        warum.
        """
        from pathlib import Path
        from django.conf import settings
        quelle = (Path(settings.UMA_PROJEKT) / 'Assets' / 'Roomguest'
                  / 'Editor' / 'UmaFigurExport.cs')
        if not quelle.is_file():
            self.skipTest('Exporter nicht vorhanden: %s' % quelle)
        text = quelle.read_text(encoding='utf-8', errors='replace')
        self.assertIn('public const string OhneKleidung = "%s";'
                      % Umabauer.OHNE_KLEIDUNG, text)
