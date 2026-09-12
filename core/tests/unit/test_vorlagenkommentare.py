# -*- coding: utf-8 -*-
u"""Kein Kommentar steht sichtbar im UI.

DER BEFUND (Edgar, 09.09.2026: „fixe den Kommentar im UI", mit dem Text
gleich mitgeschickt)
====================================================================
In `scene_config.html` stand ein Kommentar in der Kurzform mit Doppelkreuz
ueber DREI Zeilen. Die Kurzform ist einzeilig — Djangos Lexer erkennt sie
nur, wenn Anfang und Ende in derselben Zeile stehen
(`django/template/base.py`, `tag_re`). Ueber mehrere Zeilen bleibt der Text
gewoehnlicher Inhalt, und er stand im Datei-Menue zwischen „Laden..." und
„Modell speichern".

WARUM DAS KEIN TEST BISHER SAH
==============================
Die Seite antwortet mit 200, die Vorlage rendert ohne Fehler, und im
Quelltext sieht die Zeile wie ein Kommentar aus. Genau die Sorte stiller
Fehler, gegen die es `djangobase.tests.konform` gibt — nur dass dort die
Vorlagenpruefung auf Bausteine und Tabellen zielt, nicht auf Kommentare.

Der Fall unten braucht keinen Server und keine Datenbank: Er liest die
Vorlagen als Text. Die Gegenprobe (`test_die_pruefung_findet_den_fall`)
haelt die kaputte Schreibweise als Zeichenkette gegen dieselbe Logik — ohne
sie waere eine Pruefung, die nichts findet, nicht von einer kaputten zu
unterscheiden (`~/.claude/rules/analysewerkzeuge.md`).
"""
import io

from django.conf import settings
from django.test import SimpleTestCase


def _offene_kurzkommentare(text):
    u"""Zeilennummern, in denen `{#` steht, ohne dass `#}` folgt."""
    offen = []
    for nummer, zeile in enumerate(text.splitlines(), start=1):
        stelle = zeile.find('{#')
        if stelle >= 0 and '#}' not in zeile[stelle:]:
            offen.append(nummer)
    return offen


def _vorlagen():
    return sorted((settings.BASE_DIR / 'templates').rglob('*.html'))


class VorlagenkommentareTest(SimpleTestCase):

    databases = set()

    def test_keine_vorlage_hat_einen_mehrzeiligen_kurzkommentar(self):
        befunde = []
        for pfad in _vorlagen():
            text = io.open(pfad, encoding='utf-8').read()
            for nummer in _offene_kurzkommentare(text):
                befunde.append('%s:%d' % (pfad.name, nummer))
        self.assertEqual(befunde, [],
                         u'Mehrzeilig geht nur ein comment-Block; die '
                         u'Kurzform steht sonst sichtbar auf der Seite.')

    def test_es_gibt_ueberhaupt_vorlagen_zu_pruefen(self):
        u"""Ein Pruefer, der nichts liest, meldet immer gruen."""
        self.assertGreater(len(_vorlagen()), 20)

    def test_die_pruefung_findet_den_fall(self):
        u"""Gegenprobe mit genau der Schreibweise, die im Menue stand."""
        kaputt = ('<div>a</div>\n'
                  '{# Speichern hiess immer die SZENE. Modell\n'
                  '   und Szene sind zwei Dinge. #}\n'
                  '<div>b</div>\n')
        self.assertEqual(_offene_kurzkommentare(kaputt), [2])

    def test_einzeilige_kommentare_sind_in_ordnung(self):
        self.assertEqual(_offene_kurzkommentare('{# alles gut #}\n{# auch #}'),
                         [])
