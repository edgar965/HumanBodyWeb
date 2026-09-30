# -*- coding: utf-8 -*-
u"""Bereich „Haar Engine" — jedes Bedienelement der beiden Seiten (30.09.2026).

Edgar: „schreibe Testcases für alle buttons".

WAS HIER GEPRÜFT WIRD: dass jeder Knopf, jede Auswahl und jedes Feld der Vorlagen im
JavaScript ÜBERHAUPT vorkommt — ein Knopf, den niemand anfasst, sieht auf der Seite
vollkommen richtig aus und tut nichts. Das ist statische Prüfung: Sie liest die Vorlagen
und die Module, startet keinen Browser und braucht keine Datenbank (rund 40 Dateien, weit
unter der Sekunde — `projekt.md`, Schwelle 1 s).

WAS SIE NICHT PRÜFT: ob der Knopf das RICHTIGE tut. Das steht hinter den Endpunkten
(`test_haarengine_endpunkte.py`) und in der Sichtprüfung im Browser
(`~/.claude/rules/nur-echter-chrome.md`) — eine Kennzahl ist kein Bild.

Die Liste der Elemente steht bewusst AUSGESCHRIEBEN in `ERWARTET`: Verschwindet ein Knopf
aus der Vorlage, fällt das hier auf, statt die Prüfung stillschweigend kleiner zu machen.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

#: Ordner, in denen die Module des Bereichs liegen (Bühne und Bildauswahl sind gemeinsam).
JS_ORDNER = ('viewer/haarengine', 'viewer/gemeinsam')

#: Jedes Bedienelement der beiden Vorlagen — `id` oder, wo es keine gibt, `data-schalter`
#: bzw. `data-reiter`. Gezählt am 30.09.2026: 5 auf der Übersicht, 33 auf der Auftragsseite.
ERWARTET = {
    'haarengine.html': [
        'haarengine-name', 'haarengine-dateien', 'haarengine-anlegen',
        'haarengine-duplizieren', 'haarengine-bulk-delete',
    ],
    'haarengine_auftrag.html': [
        # Kopf und Laufband
        'auftrag-loeschen', 'laufband-anhalten',
        # Reiter
        'reiter:auftrag', 'reiter:iterationen',
        # Der Lauf
        'ab-schritt', 'starten', 'anhalten',
        # Die Bühne
        'buehne-iterationsmodell', 'buehne-film', 'buehne-haarwahl',
        'schalter:mesh', 'schalter:haare', 'schalter:kleider',
        'schalter:nebeneinander', 'schalter:modell',
        # Die Bewegung
        'anim-zurueck', 'anim-play', 'anim-vor', 'anim-scrubber',
        # Ausgabe
        'export-aufloesung', 'export-textur', 'export-rig', 'export-name', 'exportieren',
        'modell-format', 'modell-name', 'modell-speichern',
        # Der Reiter „Iterationen"
        'iterationen-weiter', 'iterationen-anhalten', 'iterationen-jede',
        'iterationen-alle-auf', 'iterationen-alle-zu', 'iterationen-loeschen',
    ],
}

ELEMENT = re.compile(r'<(?:button|select|input|a)\b[^>]*>', re.I | re.S)
ID = re.compile(r'\bid="([^"]+)"')
SCHALTER = re.compile(r'\bdata-schalter="([^"]+)"')
REITER = re.compile(r'\bdata-reiter="([^"]+)"')


class HaarengineknoepfeTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wurzel = Path(settings.BASE_DIR)
        cls.vorlagen = {name: (wurzel / 'templates' / name).read_text(encoding='utf-8')
                        for name in ERWARTET}
        cls.js = '\n'.join(
            p.read_text(encoding='utf-8', errors='replace')
            for ordner in JS_ORDNER
            for p in sorted((wurzel / 'static' / ordner).glob('*.js'))
        )

    @staticmethod
    def _elemente(text):
        u"""Die Kennungen aller Bedienelemente einer Vorlage, in der Reihenfolge der Datei."""
        aus = []
        for treffer in ELEMENT.finditer(text):
            roh = treffer.group(0)
            if (kennung := ID.search(roh)):
                aus.append(kennung.group(1))
            elif (schalter := SCHALTER.search(roh)):
                aus.append('schalter:' + schalter.group(1))
            elif (reiter := REITER.search(roh)):
                aus.append('reiter:' + reiter.group(1))
        return aus

    # ------------------------------------------------- die Liste ist vollständig

    def test_1_die_vorlagen_tragen_genau_die_erwarteten_bedienelemente(self):
        u"""Neuer Knopf ohne Test, oder verschwundener Knopf — beides fällt hier auf."""
        for name, erwartet in ERWARTET.items():
            with self.subTest(vorlage=name):
                self.assertEqual(sorted(set(self._elemente(self.vorlagen[name]))),
                                 sorted(set(erwartet)))

    def test_2_es_sind_achtunddreissig_bedienelemente(self):
        self.assertEqual(sum(len(v) for v in ERWARTET.values()), 38)

    # ------------------------------------------------- jedes ist verdrahtet

    def test_3_jedes_bedienelement_kommt_im_javascript_vor(self):
        u"""Ein Knopf, den kein Modul anfasst, ist tot: Er sieht richtig aus und tut nichts."""
        for name, erwartet in ERWARTET.items():
            for kennung in erwartet:
                gesucht = kennung.split(':', 1)[-1]
                with self.subTest(vorlage=name, element=kennung):
                    self.assertIn(gesucht, self.js,
                                  '%s wird in keinem Modul unter %s angefasst'
                                  % (kennung, ' / '.join(JS_ORDNER)))

    # ------------------------------------------------- die Knöpfe, die gefährlich sind

    def test_4_jeder_loeschknopf_fragt_vorher(self):
        u"""Auftrag löschen, Gewählte löschen, Runden löschen: Ein Klick darf nicht sofort
        löschen — `auftragsseiten.md`, dieselbe Regel gilt für alle drei Joblisten."""
        for kennung in ('auftrag-loeschen', 'haarengine-bulk-delete', 'iterationen-loeschen'):
            with self.subTest(element=kennung):
                # Das Modul, das den Knopf anfasst, muss auch eine Rückfrage kennen.
                modul = self._modul_mit(kennung)
                self.assertIsNotNone(modul, '%s wird von keinem Modul angefasst' % kennung)
                self.assertTrue(
                    re.search(r'confirm\s*\(|bestaetigen|Bestaetigung|dialogBestaetigen', modul),
                    '%s löscht ohne Rückfrage' % kennung)

    def test_5_start_und_anhalten_gehoeren_zusammen(self):
        u"""„Neu berechnen" sperrt sich selbst und macht „Anhalten" frei — sonst startet ein
        Doppelklick zwei Läufe (`auftragsseiten.md`, Knopfsperre gegen Doppelstart)."""
        modul = self._modul_mit('starten')
        self.assertIsNotNone(modul)
        self.assertIn('anhalten', modul)
        self.assertIn('disabled', modul)

    def _modul_mit(self, kennung):
        u"""Der Quelltext des ersten Moduls, das diese Kennung nennt."""
        wurzel = Path(settings.BASE_DIR)
        gesucht = kennung.split(':', 1)[-1]
        for ordner in JS_ORDNER:
            for pfad in sorted((wurzel / 'static' / ordner).glob('*.js')):
                text = pfad.read_text(encoding='utf-8', errors='replace')
                if gesucht in text:
                    return text
        return None
