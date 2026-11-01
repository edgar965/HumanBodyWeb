# -*- coding: utf-8 -*-
u"""Bereich „2D3D Kleider" — jedes Bedienelement der beiden Seiten (30.09.2026).

Edgar: „schreibe Testcases für alle buttons".

WAS HIER GEPRÜFT WIRD: dass jeder Knopf, jede Auswahl und jedes Feld der Vorlagen im
JavaScript ÜBERHAUPT vorkommt — ein Knopf, den niemand anfasst, sieht auf der Seite
vollkommen richtig aus und tut nichts. Das ist statische Prüfung: Sie liest die Vorlagen
und die Module, startet keinen Browser und braucht keine Datenbank (rund 40 Dateien, weit
unter der Sekunde — `projekt.md`, Schwelle 1 s).

WAS SIE NICHT PRÜFT: ob der Knopf das RICHTIGE tut. Das steht hinter den Endpunkten
(`test_engine2d3dkleider_endpunkte.py`) und in der Sichtprüfung im Browser
(`~/.claude/rules/nur-echter-chrome.md`) — eine Kennzahl ist kein Bild.

Die Liste der Elemente steht bewusst AUSGESCHRIEBEN in `ERWARTET`: Verschwindet ein Knopf
aus der Vorlage, fällt das hier auf, statt die Prüfung stillschweigend kleiner zu machen.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

#: Ordner, in denen die Module des Bereichs liegen. `meshfigur` gehört dazu: Bühne, Export
#: und „Modell speichern" teilt sich die Seite mit „Mesh to 3D" (sie ist eine Kopie von
#: BlenderModel, das darauf aufbaut) — `meshfigurspeicher.js`, `meshfigurexport.js`.
JS_ORDNER = ('viewer/engine2d3dkleider', 'viewer/gemeinsam', 'viewer/meshfigur')

#: Jedes Bedienelement der beiden Vorlagen — `id` oder, wo es keine gibt, `data-schalter`
#: bzw. `data-reiter`. Gezählt am 30.09.2026: 5 auf der Übersicht, 33 auf der Auftragsseite (34 seit 02.10.2026: „bis").
ERWARTET = {
    'engine2d3dkleider.html': [
        'engine2d3dkleider-name', 'engine2d3dkleider-dateien', 'engine2d3dkleider-anlegen',
        'engine2d3dkleider-duplizieren', 'engine2d3dkleider-bulk-delete',
        # Kopie samt Runden, Mesh-Figur-Übernahme und Weiterführen eines Auftrags (seit 02.–06.10.2026)
        'engine2d3dkleider-kopie-alles', 'engine2d3dkleider-meshfigur', 'engine2d3dkleider-weiter', 'engine2d3dkleider-weiter-runden',
    ],
    'engine2d3dkleider_auftrag.html': [
        # Kopf und Laufband
        'auftrag-loeschen', 'laufband-anhalten',
        # Reiter
        'reiter:auftrag', 'reiter:iterationen',
        # Der Lauf ('bis-schritt' seit 02.10.2026: jeder Schritt startet getrennt; der Knopf „Mesh erzeugen" entsteht
        # in `engine2d3dkleidermeshkarte.js`, nicht in der Vorlage)
        'ab-schritt', 'bis-schritt', 'starten', 'anhalten',
        # „Modell im System Speichern" (08.10.2026, rechts oben unter „Neu berechnen")
        'modell-im-system-speichern',
        # Die Bühne (seit dem 30.09.2026 dazu: Formen und Malen der Mesh-Bühne, Referenz, Reiter „Bewertung" und „Gesicht", die Begutachtung)
        'buehne-iterationsmodell', 'buehne-film', 'buehne-haarwahl', 'buehne-formen', 'buehne-malen',
        'reiter:bewertung', 'reiter:gesicht', 'referenz-pfad', 'referenz-uebernehmen',
        'begutachtung-ausgang', 'begutachtung-automatisch', 'begutachtung-rezept', 'begutachtung-runde', 'begutachtung-runden',
        'schalter:mesh', 'schalter:haare', 'schalter:kleider',
        'schalter:nebeneinander', 'schalter:modell',
        # Die Bewegung
        'anim-zurueck', 'anim-play', 'anim-vor', 'anim-scrubber', 'anim-anfang', 'anim-ende', 'anim-stopp',
        # Ausgabe: Export, Render und „Modell speichern" stehen seit 31.10.2026 in der Exportleiste (`_exportleiste.html`, eingebunden — `test_6_…`)
        # Der Reiter „Iterationen"
        'iterationen-weiter', 'iterationen-anhalten', 'iterationen-jede',
        'iterationen-alle-auf', 'iterationen-alle-zu', 'iterationen-loeschen',
    ],
}

ELEMENT = re.compile(r'<(?:button|select|input|a)\b[^>]*>', re.I | re.S)
ID = re.compile(r'\bid="([^"]+)"')
SCHALTER = re.compile(r'\bdata-schalter="([^"]+)"')
REITER = re.compile(r'\bdata-reiter="([^"]+)"')


class Engine2d3dKleiderknoepfeTest(SimpleTestCase):

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

    def test_2_die_zahl_der_bedienelemente(self):
        """Gezählt am 08.10.2026: 9 auf der Übersicht, 60 auf der Auftragsseite (sie wächst mit jedem Knopf — dieser Wert ist die Mahnung, die Liste oben mitzupflegen).
        31.10.2026: 41 auf der Auftragsseite — Export (7), Render (9) und „Modell speichern" (3) kommen aus der Exportleiste."""
        self.assertEqual(sum(len(v) for v in ERWARTET.values()), 50)

    # ------------------------------------------------- jedes ist verdrahtet

    def test_3_jedes_bedienelement_kommt_im_javascript_vor(self):
        u"""Ein Knopf, den kein Modul anfasst, ist tot: Er sieht richtig aus und tut nichts."""
        for name, erwartet in ERWARTET.items():
            for kennung in erwartet:
                gesucht = kennung.split(':', 1)[-1]
                with self.subTest(vorlage=name, element=kennung):
                    # Bewusst `assertTrue` statt `assertIn`: `assertIn` hängt bei einem
                    # Fehlschlag den ganzen Quelltext an die Meldung — hier 2,2 MB.
                    self.assertTrue(gesucht in self.js,
                                    '%s wird in keinem Modul unter %s angefasst'
                                    % (kennung, ' / '.join(JS_ORDNER)))

    # ------------------------------------------------- die Knöpfe, die gefährlich sind

    def test_4_jeder_loeschknopf_fragt_vorher(self):
        u"""Auftrag löschen, Gewählte löschen, Runden löschen: Ein Klick darf nicht sofort
        löschen — `auftragsseiten.md`, dieselbe Regel gilt für alle drei Joblisten."""
        for kennung in ('auftrag-loeschen', 'engine2d3dkleider-bulk-delete', 'iterationen-loeschen'):
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
        # Das Modul, das den Knopf verdrahtet — nicht das Aktionslog, dessen Kommentar `#starten` nennt (08.10.2026).
        modul = self._modul_mit("getElementById('starten')")
        self.assertIsNotNone(modul)
        # `assertTrue` statt `assertIn`: ein Fehlschlag hängt sonst den ganzen Quelltext an die Meldung.
        self.assertTrue('anhalten' in modul, 'das Modul des Startknopfes kennt „anhalten" nicht')
        self.assertTrue('disabled' in modul, 'das Modul des Startknopfes sperrt nichts')

    def test_6_die_exportleiste_ist_eingebunden_und_jedes_ihrer_elemente_verdrahtet(self):
        u"""Seit 31.10.2026 trägt die Auftragsseite die Exportleiste (Bereich `engine2d3dkleider`, `Engine2d3dKleiderexportquelle`) statt eigener Blöcke für Export, Render und
        „Modell speichern". Jedes Element der Leiste muss ein Modul der Leiste anfassen; die Felder von „Modell speichern" bindet `Meshfigurspeicher.EXPORTLEISTE`."""
        auftrag = self.vorlagen['engine2d3dkleider_auftrag.html']
        self.assertTrue(re.search(r'{%\s*include\s+"_exportleiste.html"\s+with\s+bereich="engine2d3dkleider"', auftrag), 'die Exportleiste ist nicht eingebunden')
        self.assertTrue('new Engine2d3dKleiderexportquelle(' in auftrag and 'Exportleiste.starten(' in auftrag, 'die Exportleiste wird nicht gestartet')
        wurzel = Path(settings.BASE_DIR)
        leiste = (wurzel / 'templates' / '_exportleiste.html').read_text(encoding='utf-8')
        js = self.js + '\n'.join(p.read_text(encoding='utf-8') for p in sorted((wurzel / 'static' / 'viewer' / 'exportleiste').glob('*.js')))
        elemente = self._elemente(leiste)
        self.assertGreaterEqual(len(elemente), 15)                     # gezählt 31.10.2026: 15 mit Kennung (dazu die Knöpfe mit `data-format`/`data-bilder`)
        for kennung in elemente:
            with self.subTest(element=kennung):
                self.assertTrue(kennung in js, '%s wird in keinem Modul der Leiste angefasst' % kennung)
        self.assertTrue('Meshfigurspeicher.EXPORTLEISTE' in self.js, '„Modell speichern" der Leiste ist nicht an Meshfigurspeicher gebunden')

    def _modul_mit(self, kennung):
        u"""Der Quelltext des ersten Moduls, das diese Kennung als Zeichenkette nennt (`'starten'`, `"starten"`, `#starten`) — nicht irgendeines, in dem das Wort nur vorkommt
        (08.10.2026: `engine2d3dkleideraktionslog.js` enthält „starten" im Kommentar und kommt alphabetisch vor der Seite, die den Knopf verdrahtet)."""
        wurzel = Path(settings.BASE_DIR)
        gesucht = kennung.split(':', 1)[-1]
        genau = re.compile(r'''['"`#]%s['"`\s]''' % re.escape(gesucht))
        module = [p.read_text(encoding='utf-8', errors='replace')
                  for ordner in JS_ORDNER for p in sorted((wurzel / 'static' / ordner).glob('*.js'))]
        return next((t for t in module if genau.search(t)), next((t for t in module if gesucht in t), None))
