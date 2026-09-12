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

SEIT 12.09.2026 (Befund `doppelcode`) fuehren die vier Arten neben HumanBody
`toJSON`/`fromJSON` nicht mehr selbst: Sie erben von `scene/figurbasis.js`,
und dort steht der Weg EINMAL. Gemessen wird deshalb an der Datei, die den
Weg TRAEGT — die Art selbst, oder ihre Basis, wenn sie `extends Figurbasis`
sagt. Eine Art, die die Basis verlaesst, faellt damit wieder auf die
eigene Datei zurueck und muss den Weg selbst fuehren.
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


BASIS = 'scene/figurbasis.js'


class GcAblageTest(SimpleTestCase):

    databases = set()

    def test_jede_figurart_schreibt_die_liste(self):
        u"""Ohne den Eintrag in `toJSON` ist das Stueck nach dem Laden weg."""
        for name, pfad in ARTEN.items():
            quelle = GcAblageTest._traeger(pfad)
            self.assertIn('[GarmentcodeAblage.FELD]: GarmentcodeAblage.toJSON(',
                          quelle, '%s speichert keine GarmentCode-Stuecke' % name)

    def test_beide_zweige_der_humanbody_figur_schreiben_die_liste(self):
        u"""`CharacterInstance.toJSON` hat ZWEI Rueckgaben.

        Eine erzeugte Figur (`generatedConfig`) kehrt frueher zurueck. Der
        Zweig fuehrte das Feld bis zum 09.09.2026 nicht — wer eine
        generierte Figur in eine Szene speicherte, fand sie beim Laden
        nackt wieder. Aufgefallen ist es nur beim Nachlesen: Der Fall
        `test_jede_figurart_schreibt_die_liste` oben genuegt sich mit EINEM
        Vorkommen je Datei, und das zweite stand ja da.
        """
        quelle = GcAblageTest._dateitext('scene/character.js')
        rumpf = quelle.split('    toJSON() {')[1]
        rumpf = rumpf.split('    static ')[0]
        self.assertEqual(rumpf.count('[GarmentcodeAblage.FELD]'), 2,
                         u'Ein Rueckgabezweig von toJSON fuehrt die Liste '
                         u'nicht.')

    def test_jede_figurart_laedt_die_liste(self):
        u"""Speichern ohne Laden ist der haeufigere halbe Umbau."""
        for name, pfad in ARTEN.items():
            quelle = GcAblageTest._traeger(pfad)
            self.assertIn('GarmentcodeAblage.laden(', quelle,
                          '%s stellt die Stuecke nicht wieder her' % name)

    def test_jede_figurart_importiert_die_ablage(self):
        u"""Ein fehlender Import ist ein Laufzeitfehler beim Speichern."""
        for name, pfad in ARTEN.items():
            quelle = GcAblageTest._traeger(pfad)
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
            quelle = GcAblageTest._traeger(pfad)
            laden = quelle.index('GarmentcodeAblage.laden(')
            # `\.load\(` statt `\.load\(\)`: Seit dem 10.09.2026 nimmt
            # `load` einen Rueckruf entgegen, mit dem die Figur auf die
            # Buehne kommt, sobald ihr KOERPER steht — Haare und Kleidung
            # laden danach weiter (`character.js`). Die Aussage dieses
            # Tests aendert sich dadurch nicht: Angezogen wird immer noch
            # erst, wenn `load` durch ist.
            aufbau = max((m.end() for m in re.finditer(r'\.load\(', quelle)),
                         default=-1)
            self.assertGreater(aufbau, 0, '%s ruft kein load()' % name)
            self.assertGreater(laden, aufbau,
                               '%s zieht an, bevor die Figur steht' % name)

    def test_jeder_ladeweg_geht_ueber_die_gemeinsame_kette(self):
        u"""Drei Wege bauen eine Figur aus Modelldaten — einer zog an.

        BEFUND (Edgar, 09.09.2026): „Ueber Datei - Modell Importieren
        funktioniert das Modell ‘Female GarmentCode’ nicht, keine Kleider.
        ueber den + Button im UI funktioniert das."

        `addCharacterFromPreset` (der „+"-Knopf) hatte
        `GarmentcodeAblage.laden`; „Datei -> Laden..." mit einer
        Modelldatei und „Datei -> Modell importieren..." bauten die Figur
        selbst zusammen — ohne die Stuecke und noch mit dem festen
        Abstand von 0,8 m, den `Figurplatzierung` am 06.09.2026 ersetzt
        hat. Seither gibt es `charakterAusModelldaten` als einzigen Weg.
        """
        dialoge = GcAblageTest._dateitext('scene/szene_dialoge.js')
        self.assertEqual(dialoge.count('charakterAusModelldaten'), 2,
                         u'Beide Dateiwege muessen die gemeinsame Kette '
                         u'rufen.')
        # Und keiner darf sich seine Figur weiter selbst zusammenbauen.
        self.assertNotIn('new fn.CharacterInstance(', dialoge,
                         u'Ein eigener Aufbau umgeht die Kette — genau so '
                         u'sind die Kleider verloren gegangen.')

    def test_die_gemeinsame_kette_zieht_die_stuecke_an(self):
        quelle = GcAblageTest._dateitext('scene/charakterliste.js')
        rumpf = quelle.split('export async function charakterAusModelldaten')[1]
        rumpf = rumpf.split('export async function')[0]
        for erwartet in ('await inst.load(', 'Figurplatzierung.anwenden(',
                         'GarmentcodeAblage.laden('):
            self.assertIn(erwartet, rumpf, erwartet)
        # Die Reihenfolge ist der Grund, warum es eine Kette ist.
        self.assertLess(rumpf.index('await inst.load('),
                        rumpf.index('GarmentcodeAblage.laden('))

    def test_geloeschtes_stueck_kommt_nicht_zurueck(self):
        u"""Der Loeschzweig muss die Ablage mitnehmen.

        Ohne ihn steht ein geloeschtes Stueck weiter in `gcStuecke` und
        haengt beim naechsten Laden der Szene wieder an der Figur — ein
        Loeschen, das nur bis zum Speichern haelt.
        """
        quelle = GcAblageTest._dateitext('scene/teilnetz_auswahl.js')
        self.assertIn("target.key.startsWith('gc_')", quelle)
        self.assertIn('GarmentcodeAblage.vergessen(', quelle)

    def test_gebaute_stuecke_landen_in_der_ablage(self):
        u"""Gemerkt wird beim Anziehen — sonst ist die Liste immer leer."""
        quelle = GcAblageTest._dateitext('scene/garmentcode_drapieren.js')
        self.assertIn('GarmentcodeAblage.merken(', quelle)

    def test_gegenprobe_der_suchbegriff_trifft_wirklich(self):
        u"""Sabotage: ein Begriff, der nirgends steht, MUSS fehlschlagen.

        Ohne diesen Fall koennte ein Tippfehler im Suchtext alle Pruefungen
        oben gruen halten (`~/.claude/rules/analysewerkzeuge.md`).
        """
        for pfad in ARTEN.values():
            self.assertNotIn('GarmentcodeAblage.gibtsNicht(', GcAblageTest._traeger(pfad))
        # Und der echte Begriff steht in ALLEN, nicht nur in einer:
        treffer = sum('GarmentcodeAblage.laden(' in GcAblageTest._traeger(p)
                      for p in ARTEN.values())
        self.assertEqual(treffer, len(ARTEN), treffer)

    def test_die_vier_arten_erben_wirklich_von_der_basis(self):
        u"""`GcAblageTest._traeger` darf nicht ins Leere greifen: Wer `extends Figurbasis`
        sagt, ruft auch deren `ausJSON` und `grunddaten` — sonst haette
        die Art ein eigenes `toJSON` ohne die Liste, und die Basis wuerde
        fuer sie buergen."""
        for name, pfad in ARTEN.items():
            quelle = GcAblageTest._dateitext(pfad)
            if ' extends Figurbasis {' not in quelle:
                self.assertEqual(name, 'HumanBody')
                continue
            self.assertIn('...this.grunddaten(),', quelle, name)
            self.assertIn('return Figurbasis.ausJSON(', quelle, name)
            self.assertNotIn('transform:', quelle, name)

    @staticmethod
    def _dateitext(pfad):
        voll = settings.BASE_DIR / 'static' / 'viewer' / pfad
        return io.open(voll, encoding='utf-8').read()

    @staticmethod
    def _traeger(pfad):
        u"""Die Quelle, die Speichern und Laden fuer diese Art fuehrt."""
        quelle = GcAblageTest._dateitext(pfad)
        if ' extends Figurbasis {' in quelle:
            return GcAblageTest._dateitext(BASIS)
        return quelle
