# -*- coding: utf-8 -*-
u"""`status_3d`: welche 3D-Pipelines auf diesem Rechner bereitstehen.

WARUM (31.08.2026)
==================
`upload_v4.html` fragte an ZWEI Stellen dasselbe:

    {% if not status_3d.hybrid_gvhmr and not status_3d.hybrid_prompthmr %}

Eine Bedingung, die in die Vorlage gewandert war — und die dort in einer
Zeile keinen Platz mehr hatte (172 Zeichen). Umbrechen geht nicht: Djangos
Lexer kennt kein DOTALL, ein `{% … %}` über zwei Zeilen wird STUMM zu Text,
die Seite antwortet weiter mit 200 und die Bedingung ist fort.

Sie steht jetzt als `hybrid` in `_pipelines_verfuegbar()`. Die Umformung
`(a and v) or (b and v)` → `(a or b) and v` ist algebraisch dieselbe — was
nichts wert ist, solange es niemand nachrechnet. Dieser Test geht deshalb
ALLE ACHT Kombinationen durch.

ES GIBT KEINEN AUGENSCHEIN-BELEG: Auf diesem Rechner sind alle Pipelines
installiert, jede Karte steht aktiv da. Der Fall „ausgegraut" ist im
Browser gar nicht herstellbar.
"""
import itertools
import unittest
from unittest.mock import patch

from core.api.auftrag_upload import Uploadseiten


class EinRechnerMitPipelines(unittest.TestCase):
    u"""Gegeben: bestimmte Verzeichnisse liegen da, andere nicht."""

    databases = []

    #: Reihenfolge, in der `_pipelines_verfuegbar` die Pfade abfragt.
    EINSTELLUNGEN = ('MOCAPNET_V4_SCRIPT', 'GVHMR_ROOT', 'WHAM_ROOT',
                     'PROMPTHMR_ROOT')

    def _status(self, v4, gvhmr, wham, prompthmr):
        u"""`status_3d`, als lägen genau diese Verzeichnisse vor."""
        vorhanden = {'MOCAPNET_V4_SCRIPT': v4, 'GVHMR_ROOT': gvhmr,
                     'WHAM_ROOT': wham, 'PROMPTHMR_ROOT': prompthmr}

        class Pfadattrappe:
            def __init__(self, roh):
                self.roh = roh

            def exists(self):
                return bool(vorhanden.get(self.roh))

            def is_dir(self):
                return bool(vorhanden.get(self.roh))

        with patch('core.api.auftrag_upload.Path', Pfadattrappe), \
                patch('core.api.auftrag_upload.settings') as einst:
            for name in self.EINSTELLUNGEN:
                setattr(einst, name, name)
            return Uploadseiten._pipelines_verfuegbar()

    def test_hybrid_deckt_sich_mit_der_alten_bedingung(self):
        u"""Die Gegenprobe über alle acht Kombinationen."""
        for v4, gvhmr, prompthmr in itertools.product((True, False),
                                                      repeat=3):
            with self.subTest(v4=v4, gvhmr=gvhmr, prompthmr=prompthmr):
                s = self._status(v4, gvhmr, False, prompthmr)
                alt = s['hybrid_gvhmr'] or s['hybrid_prompthmr']
                self.assertEqual(s['hybrid'], alt)

    def test_ohne_v4_kein_hybrid(self):
        u"""Beide Hybridwege brauchen MocapNET v4 für Hände und Gesicht."""
        s = self._status(False, True, True, True)
        self.assertFalse(s['hybrid'])

    def test_v4_allein_reicht_auch_nicht(self):
        u"""Ohne einen Körper-Schätzer gibt es nichts zu ergänzen."""
        s = self._status(True, False, True, False)
        self.assertFalse(s['hybrid'])

    def test_v4_mit_gvhmr_genuegt(self):
        s = self._status(True, True, False, False)
        self.assertTrue(s['hybrid'])

    def test_v4_mit_prompthmr_genuegt(self):
        u"""PromptHMR allein — der zweite Weg zum selben Ziel."""
        s = self._status(True, False, False, True)
        self.assertTrue(s['hybrid'])

    def test_die_einzelnen_bleiben_erhalten(self):
        u"""`hybrid` tritt NEBEN die beiden — das Formular schickt weiter
        `hybrid_gvhmr` oder `hybrid_prompthmr` als Wert."""
        s = self._status(True, True, True, True)
        for schluessel in ('v4', 'gvhmr', 'wham', 'prompthmr',
                           'hybrid_gvhmr', 'hybrid_prompthmr'):
            self.assertIn(schluessel, s)
