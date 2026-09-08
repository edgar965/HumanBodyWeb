# -*- coding: utf-8 -*-
u"""Jede Figurart speichert ihre GarmentCode-Stuecke — und laedt sie wieder.

BEFUND (Edgar, 08.09.2026): „habe gerade das Modell mit GarmentCode
gespeichert, beim neu laden sind die Garment Code items weg." GarmentCode
hatte keine Liste in der Szenendatei; die Stuecke hingen nur als Netz in der
Figurgruppe, und dort sieht das Speichern nicht hin.

WARUM DIESE FAELLE AM QUELLTEXT MESSEN
======================================
`garmentcode_ablage.js` haengt ueber `garmentcode_anziehen.js` an Three.js
und laeuft deshalb nicht unter node — ein Rechentest wie
`test_js_greifrechnung` ist hier nicht moeglich.

Geprueft wird stattdessen die Eigenschaft, an der es in diesem Projekt schon
einmal still schiefgegangen ist: FUENF Figurarten fuehren je ein eigenes
`toJSON`/`fromJSON`, und wer nur eines erweitert, bekommt eine Szene, die
sich speichern, aber nicht wiederherstellen laesst. Genau dafuer gibt es
`figurarten.py`/`figurarten.js` — der Kommentar dort nennt denselben Fehler
bei UMA (05.09.2026).

Ein Quelltexttest ist hier scharf genug: Fehlt der Aufruf, ist er nicht da.
Die Gegenprobe unten sabotiert den Suchbegriff und muss rot werden.
"""
import io
import re

from django.conf import settings
from django.test import SimpleTestCase

#: Die Figurarten und ihre Datei. Die Liste steht ABSICHTLICH hier und nicht
#: als Glob: Kommt eine sechste Art dazu, soll dieser Test sie verlangen.
ARTEN = {
    'HumanBody': 'scene/character.js',
    'SMPL': 'scene/smpl/smplfigur.js',
    'MakeHuman': 'scene/makehuman/mhfigur.js',
    'UMA': 'scene/uma/umafigur.js',
    'UMA Python': 'scene/umapython/umapythonfigur.js',
}


def _quelle(pfad):
    voll = settings.BASE_DIR / 'static' / 'viewer' / pfad
    return io.open(voll, encoding='utf-8').read()


class GcAblageTest(SimpleTestCase):

    databases = []

    def test_jede_figurart_schreibt_die_liste(self):
        u"""Ohne den Eintrag in `toJSON` ist das Stueck nach dem Laden weg."""
        for name, pfad in ARTEN.items():
            quelle = _quelle(pfad)
            self.assertIn('[GarmentcodeAblage.FELD]: GarmentcodeAblage.toJSON(',
                          quelle, '%s speichert keine GarmentCode-Stuecke' % name)

    def test_jede_figurart_laedt_die_liste(self):
        u"""Speichern ohne Laden ist der haeufigere halbe Umbau."""
        for name, pfad in ARTEN.items():
            quelle = _quelle(pfad)
            self.assertIn('GarmentcodeAblage.laden(', quelle,
                          '%s stellt die Stuecke nicht wieder her' % name)

    def test_jede_figurart_importiert_die_ablage(self):
        u"""Ein fehlender Import ist ein Laufzeitfehler beim Speichern."""
        for name, pfad in ARTEN.items():
            quelle = _quelle(pfad)
            self.assertRegex(
                quelle,
                r"import \{ GarmentcodeAblage \} from '\.{1,2}/garmentcode_ablage\.js';",
                '%s importiert die Ablage nicht' % name)

    def test_geladen_wird_nach_dem_aufbau(self):
        u"""Die Reihenfolge zaehlt: erst `load()`, dann anziehen.

        `GarmentcodeAnziehen` sucht das Skelett der Figur und bindet in der
        Lage der Figurgruppe. Ein Stueck, das VOR `load()` kommt, findet
        kein Skelett und haengt starr da (dieselbe Falle wie bei MakeHuman,
        07.09.2026: „Kleider von MakeHuman animieren immer noch nicht").
        """
        for name, pfad in ARTEN.items():
            quelle = _quelle(pfad)
            laden = quelle.index('GarmentcodeAblage.laden(')
            aufbau = max((m.end() for m in re.finditer(r'\.load\(\)', quelle)),
                         default=-1)
            self.assertGreater(aufbau, 0, '%s ruft kein load()' % name)
            self.assertGreater(laden, aufbau,
                               '%s zieht an, bevor die Figur steht' % name)

    def test_geloeschtes_stueck_kommt_nicht_zurueck(self):
        u"""Der Loeschzweig muss die Ablage mitnehmen.

        Ohne ihn steht ein geloeschtes Stueck weiter in `gcStuecke` und
        haengt beim naechsten Laden der Szene wieder an der Figur — ein
        Loeschen, das nur bis zum Speichern haelt.
        """
        quelle = _quelle('scene/teilnetz_auswahl.js')
        self.assertIn("target.key.startsWith('gc_')", quelle)
        self.assertIn('GarmentcodeAblage.vergessen(', quelle)

    def test_gebaute_stuecke_landen_in_der_ablage(self):
        u"""Gemerkt wird beim Anziehen — sonst ist die Liste immer leer."""
        quelle = _quelle('scene/garmentcode_drapieren.js')
        self.assertIn('GarmentcodeAblage.merken(', quelle)

    def test_gegenprobe_der_suchbegriff_trifft_wirklich(self):
        u"""Sabotage: ein Begriff, der nirgends steht, MUSS fehlschlagen.

        Ohne diesen Fall koennte ein Tippfehler im Suchtext alle Pruefungen
        oben gruen halten (`~/.claude/rules/analysewerkzeuge.md`).
        """
        for pfad in ARTEN.values():
            self.assertNotIn('GarmentcodeAblage.gibtsNicht(', _quelle(pfad))
        # Und der echte Begriff steht in ALLEN, nicht nur in einer:
        treffer = sum('GarmentcodeAblage.laden(' in _quelle(p)
                      for p in ARTEN.values())
        self.assertEqual(treffer, len(ARTEN), treffer)
