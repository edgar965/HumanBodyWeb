# -*- coding: utf-8 -*-
u"""Ein Klick ins Leere wählt die Figur nicht ab — geprüft am Quelltext.

WARUM (Edgar, 10.09.2026): „wenn ich aufs leere klicke soll mir nicht diese
komische auswahl angezeigt werden". Der Leerklick auf der Leinwand rief
`fn.deselectCharacter()`; damit fielen die sechs Figur-Reiter weg
(`Reiterfreigabe`, 08.09.2026) und die Seite sprang auf „Szene" — wer neben
das Kleid klickte, sah Beleuchtung und Kamera statt seiner Regler.

DAS ABWÄHLEN BLEIBT ERREICHBAR: Escape und das Menü „Bearbeiten" rufen es
weiter. Ein Test, der nur das Fehlen der Zeile prüft, wäre auch grün, wenn
jemand das Abwählen ganz ausbaute — deshalb die zweite Klasse.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul


def _lies(*teile):
    return Jsmodul(*teile).pfad.read_text(encoding='utf-8')


def _code(quelle):
    u"""Nur Codezeilen: Der Kommentar an der Stelle nennt die alte Zeile mit
    Absicht — er erklärt, warum sie fehlt."""
    return '\n'.join(z for z in quelle.splitlines()
                     if not z.strip().startswith('//'))


class DerLeerklickBehaeltDieFigurTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.quelle = _lies('scene', 'interaction.js')

    def test_die_leinwand_waehlt_nicht_ab(self):
        self.assertNotIn('fn.deselectCharacter()', _code(self.quelle))

    def test_der_leerklick_loest_nur_die_markierung(self):
        u"""Teilnetz- und Knochenmarkierung gehen weg, die Figur bleibt."""
        stelle = self.quelle.rindex('_clearBoneSelection();')
        schluss = self.quelle[stelle:]
        self.assertIn('clearSubMeshSelection();', schluss)
        self.assertIn('_setBodyEmissive(gewaehlt, state._SELECT_EMISSIVE)', schluss)
        self.assertNotIn('switchTab', schluss)


class DasAbwaehlenBleibtErreichbarTest(SimpleTestCase):

    databases = []

    def test_escape_und_menue_waehlen_weiter_ab(self):
        menue = _lies('scene', 'menubar.js')
        self.assertIn("case 'deselect': fn.deselectCharacter();", menue)
        self.assertIn("case 'escape': fn.deselectCharacter();", menue)
