# -*- coding: utf-8 -*-
"""Escape löst jede Auswahl der Szene (`Auswahlaufhebung`, 05.10.2026).

WARUM (Edgar: „implementiere ESC, mit dem ich aus allen aktuellen Selektionen weg bin — auch das
Verschieben"): Escape wählte nur die Figur ab. Die Knochenwahl und die markierten Zeilen im linken Reiter
blieben, mit dem Fokus in einem Schieber tat die Taste nichts (der Hörer kehrte bei jedem `INPUT` zurück),
und während des Verschiebens (G) stellte sie nur den alten Stand her.

Prüft den Quelltext — die Klasse hängt an `Stueckmarkierung` und dem DOM der Szene. Im Browser gesehen
(MCP-Tab): Fokus auf einem Schieber + Escape → Figur abgewählt, Fokus beim `body`; Escape in einem
Textfeld lässt die Wahl stehen.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

CHARAKTER = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'charakter'


def quelle(name):
    return (CHARAKTER / name).read_text(encoding='utf-8')


class EscapeLoestAuswahl(SimpleTestCase):
    databases = set()

    def test_escape_vor_der_eingabefeld_pruefung(self):
        text = quelle('menubar.js')
        escape = text.index("e.key === 'Escape'")
        eingabe = text.index("e.target.tagName === 'INPUT'")
        self.assertLess(escape, eingabe, 'Escape muss vor dem Eingabefeld-Rückkehr stehen')
        self.assertIn('Auswahlaufhebung.alles()', text)
        self.assertNotIn("case 'escape'", text, 'keine zweite, alte Behandlung')

    def test_textfelder_behalten_escape(self):
        text = quelle('auswahl_aufheben.js')
        self.assertIn("'TEXTAREA'", text)
        self.assertIn("'SELECT'", text)
        for art in ('text', 'number', 'search'):
            self.assertRegex(text, r"TEXTFELDER = new Set\(\[[^\]]*'%s'" % art)
        # Schieber und Häkchen gehören NICHT zu den Textfeldern.
        liste = re.search(r'TEXTFELDER = new Set\(\[([^\]]*)\]', text)
        self.assertIsNotNone(liste)
        for art in ('range', 'checkbox', 'radio'):
            self.assertNotIn("'%s'" % art, liste.group(1) if liste else '')

    def test_alles_loest_knochen_figur_zeile_und_fokus(self):
        text = quelle('auswahl_aufheben.js')
        for aufruf in ('fn._clearBoneSelection', 'fn.deselectCharacter',
                       'Stueckmarkierung.loeschen()', 'fokus.blur'):
            self.assertIn(aufruf, text)

    def test_escape_beim_verschieben_loest_auch_die_auswahl(self):
        text = quelle('greifen.js')
        escape = re.search(r"e\.key === 'Escape'\) \{([^}]*)\}", text)
        self.assertIsNotNone(escape)
        zeile = escape.group(1) if escape else ''
        self.assertIn('this.abbrechen()', zeile)
        self.assertIn('fn.auswahlAufheben', zeile)
