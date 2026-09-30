# -*- coding: utf-8 -*-
"""Eine HumanBody-Figur speichert ihre Daz-Stuecke (Kleidung UND Haar) — und laedt sie wieder.

BEFUND (Edgar, 30.09.2026): „habe gerade ein HumanBody mit Genesis Haar und Kleidern
erstellt, gespeichert. beim neu laden von /Charakter/ sind die wieder weg" — dazu: „mache
ein Feld im Modell fuer die Kleidung und das Haar". Der Stand lag nur in `inst.dazKleidung`;
weder `CharacterInstance.toJSON` (Sitzung, Szene) noch `Szenenausgabe.modelldaten`
(„Modell speichern") schrieben ihn. Jetzt Feld `kleidung` (`DazkleidungAblage`), wie bei
einer Genesis-9-Figur.

WARUM AM QUELLTEXT: `dazkleidungablage.js` haengt ueber `dazkleidung.js` an Three.js und
laeuft nicht unter node (dieselbe Begruendung wie `test_gcablage`). Geprueft wird die
Eigenschaft, an der es gescheitert ist: jeder Schreib- und jeder Leseweg fuehrt das Feld.
Im Chrome nachgewiesen (30.09.2026): Neuladen (Sitzung) und „Modell speichern unter" →
„Charakter hinzufuegen" bringen beide Stuecke mit gleichen Werten und Punktzahlen zurueck.

BVH STUDIO (Edgar: „bvh-studio fixe das auch"): `Spurfigurarten.BAUER.modell` zieht die
Stuecke nach dem Bau an (`Spurdazkleidung`); das Studio schluesselt `boneByName` mit
entschaerften Namen (`DEF-breast_L`), `Dazkleidung.mitThreeNamen` sucht beide
Schreibweisen. Im Chrome: Haar an `DEF-spine_006`, Kopf 0,5 rad → Haar 15,8 cm.
"""

import re

from django.conf import settings
from django.test import SimpleTestCase

ORDNER = settings.BASE_DIR / 'static' / 'viewer' / 'charakter'


class DazkleidungAblageTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _text(pfad):
        return (ORDNER / pfad).read_text(encoding='utf-8')

    @staticmethod
    def _rumpf(quelle, anfang, ende):
        """Der Text zwischen `anfang` und dem naechsten `ende` danach."""
        return quelle.split(anfang, 1)[1].split(ende, 1)[0]

    def test_das_feld_heisst_wie_bei_genesis_9(self):
        """Dieselbe Form wie `Genesis9Figur.toJSON` — Kennung → Werte, Haar eingeschlossen."""
        feld = re.search(r"static FELD = '(\w+)';", self._text('genesis9/dazkleidungablage.js'))
        self.assertIsNotNone(feld)
        self.assertEqual(feld.group(1), 'kleidung')
        self.assertIn('kleidung: { ...this.kleidung },', self._text('genesis9/genesis9figur.js'))

    def test_beide_zweige_von_tojson_schreiben_das_feld(self):
        """Die Sitzung, die das Neuladen ueberbrueckt, kommt aus `toJSON` — ZWEI Rueckgaben."""
        rumpf = self._rumpf(self._text('character.js'), '    toJSON() {', '\n    _lage() {')
        self.assertEqual(rumpf.count('[DazkleidungAblage.FELD]: DazkleidungAblage.toJSON(this),'), 2)

    def test_modell_speichern_schreibt_das_feld(self):
        rumpf = self._rumpf(self._text('szenenausgabe.js'), 'static modelldaten(figur) {', '\n    static ')
        self.assertIn('daten[DazkleidungAblage.FELD] = DazkleidungAblage.toJSON(figur);', rumpf)

    def test_beide_ladewege_lesen_das_feld(self):
        """Modelldatei (`charakterAusModelldaten` → Konstruktor) und Sitzung/Szene (`fromJSON`,
        dessen `presetPayload` eine Auswahl ist und das Feld nicht durchreicht)."""
        quelle = self._text('character.js')
        konstruktor = self._rumpf(quelle, 'constructor(id, presetData) {', '\n    }')
        self.assertIn('this._dazVorgabe = presetData[DazkleidungAblage.FELD]', konstruktor)
        laden = self._rumpf(quelle, 'static async fromJSON(', '\n    static ')
        self.assertIn('inst._dazVorgabe = data[DazkleidungAblage.FELD]', laden)

    def test_angezogen_wird_nach_dem_koerper_in_beiden_zweigen(self):
        """Erzeugte und zusammengestellte Figur — jeweils erst, wenn der Koerper steht."""
        rumpf = self._rumpf(self._text('character.js'), 'async bauen({', '\n    async load(')
        treffer = re.findall(r'beiKoerper\?\.\(this\);\s*this\._dazAnziehen\(\);', rumpf)
        self.assertEqual(len(treffer), 2)

    def test_die_ablage_kopiert_tief_und_zieht_ueber_dazkleidung_an(self):
        quelle = self._text('genesis9/dazkleidungablage.js')
        self.assertIn('structuredClone(inst?.dazKleidung', quelle)
        laden = self._rumpf(quelle, 'static laden(inst, stuecke) {', '\n    }\n}')
        self.assertIn('Dazkleidung.anziehen(inst, kennung, werte)', laden)
        # Ein Stueck, das nicht kommt, wird gemeldet — die Szene laedt trotzdem.
        self.assertIn('Protokoll.warnung(', laden)

    def test_gegenprobe_der_suchbegriff_trifft_wirklich(self):
        """Sabotage: ein Begriff, der nirgends steht, MUSS fehlen
        (`~/.claude/rules/analysewerkzeuge.md`)."""
        for pfad in ('character.js', 'szenenausgabe.js', 'genesis9/dazkleidungablage.js'):
            self.assertNotIn('DazkleidungAblage.gibtsNicht(', self._text(pfad))
        rumpf = self._rumpf(self._text('character.js'), 'async bauen({', '\n    async load(')
        self.assertEqual(len(re.findall(r'beiKoerper\?\.\(this\);\s*this\._gibtsNicht\(\);', rumpf)), 0)

    def test_das_studio_zieht_sie_an(self):
        """Der HumanBody-Bauweg des Studios — NACH dem Bau, dann steht das Skelett."""
        studio = ORDNER.parent / 'studio'
        bauer = (studio / 'spurfigurarten.js').read_text(encoding='utf-8')
        rumpf = self._rumpf(bauer, 'async modell(spur, beiKoerper) {', '\n        },')
        self.assertIn('Spurdazkleidung.humanbody(modell, vorgabe);', rumpf)
        self.assertLess(rumpf.index('await modell.bauen('), rumpf.index('Spurdazkleidung.humanbody('))
        spur = (studio / 'spurdazkleidung.js').read_text(encoding='utf-8')
        self.assertIn('DazkleidungAblage.laden(modell, stuecke)', spur)
        self.assertIn('vorgabe?.[DazkleidungAblage.FELD]', spur)

    def test_knochennamen_auch_entschaerft(self):
        """Im Studio heißen die SCHLÜSSEL `DEF-breast_L` (`Clipanimation.namenEntschaerfen`) —
        nur mit der Blender-Schreibweise fand `mitThreeNamen` dort fast keinen Knochen."""
        rumpf = self._rumpf(self._text('genesis9/dazkleidung.js'), 'static mitThreeNamen(haut, skelett) {',
                            '\n    }')
        self.assertIn("(nach[n] || nach[n.replace(/\\./g, '_')])?.name ?? n", rumpf)
