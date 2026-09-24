# -*- coding: utf-8 -*-
"""Eine Figur, eine Klasse: `Modell` mit `bauen()`, für alle Seiten.

WARUM (Edgar, 13.09.2026: „modell Female1 geändert, aber auf
/humanbody/bvh-studio/ werden die Lippen, Augenbrauen, Fingernägel usw.
nicht angezeigt" — dann: „Alle HTML-Seiten wie Theatre, BVH Studio, Szene
usw. sollen die Figur NICHT selber bauen, sondern eine globale Klasse
nutzen … Von der sollen HumanBody, UMA, MakeHuman ableiten und die
Bauen-Methode implementieren"): Jede Seite baute ihre Figur selbst, und
jede vergaß etwas anderes. Jetzt liegt `Modell` in `gemeinsam/`, die Arten
erben und implementieren `bauen()`, und die Seiten rufen sie.

Geprüft am Text der Module (sie importieren `three`, in Node nicht ladbar):

1. `Modell` hat `bauen()` (wirft) und die fünf Arten erben davon und
   implementieren `async bauen(`; keine hängt an `scene/state.js`.
2. `HumanbodyModell.koerper`: Lippen VOR der Häutung und den Details,
   Details nach dem Einhängen; `bauen` ruft `Modellzubehoer`.
3. Die Seiten bauen nicht selbst: BVH Studio (`spurfigurarten.js`), Theatre
   (`vorgabefigur.js`, `figurwahl.js` für UMA), Ergebnisseite
   (`mesh_loading.js`), Animationsseite (`animation/netz.js`), Modellseite
   (`viewer/mesh.js`) und Szene (`CharacterInstance extends HumanbodyModell`,
   `UmaFigur extends UmaModell`, …) — keiner ruft `Koerpernetz.netz` noch
   selbst, keiner die alten Bauer (`Spurzubehoer`, `Figurnetz`).

Sabotage-Gegenprobe: `Lippenbau.abspalten` in `koerper()` hinter
`this.group.add` → Fall 2 rot; `extends HumanbodyModell` in `character.js`
→ `extends Object` → Fall 3 rot.
"""

import re
import unittest

from django.conf import settings

VIEWER = settings.BASE_DIR / 'static' / 'viewer'
GEMEINSAM = VIEWER / 'gemeinsam'
THEATRE = settings.BASE_DIR / 'TheatreJS' / 'src'
ARTEN = {
    'humanbodymodell.js': 'HumanbodyModell',
    'umamodell.js': 'UmaModell',
    'makehumanmodell.js': 'MakehumanModell',
    'smplmodell.js': 'SmplModell',
    'umapythonmodell.js': 'UmapythonModell',
    'genesis9modell.js': 'Genesis9Modell',
}
#: Seite → (Datei, was sie vom Modell ruft)
SEITEN = {
    # Seit 15.09.2026 wählt `spurfigurarten.js` die Klasse je Figurart — dort steht der Bau.
    'BVH Studio': (VIEWER / 'studio' / 'spurfigurarten.js', 'await modell.bauen({'),
    'Theatre': (THEATRE / 'laden' / 'vorgabefigur.js', 'await modell.bauen({ zubehoer: true })'),
    'Theatre UMA': (THEATRE / 'studio' / 'figurwahl.js', 'new UmaModell('),
    'Ergebnisseite': (VIEWER / 'result_character' / 'mesh_loading.js', 'await modell.koerper('),
    'Animationsseite': (VIEWER / 'animation' / 'netz.js', 'await modell.koerper()'),
    'Modellseite': (VIEWER / 'viewer' / 'mesh.js', 'await modell.koerper()'),
}
SZENE = {
    'character.js': 'class CharacterInstance extends HumanbodyModell {',
    'uma/umafigur.js': 'class UmaFigur extends UmaModell {',
    'makehuman/mhfigur.js': 'class MhFigur extends MakehumanModell {',
    'smpl/smplfigur.js': 'class SmplFigur extends SmplModell {',
    'umapython/umapythonfigur.js': 'class UmapythonFigur extends UmapythonModell {',
    'genesis9/genesis9figur.js': 'class Genesis9Figur extends Genesis9Modell {',
}
ALTE_BAUER = (
    'studio/spurzubehoer.js',
    'studio/spurhaut.js',
    'studio/spurdetails.js',
    'scene/figurbasis.js',
)


class ModellHierarchie(unittest.TestCase):
    databases = set()

    def test_modell_und_die_sechs_arten(self):
        basis = ModellHierarchie._text(GEMEINSAM / 'modell.js')
        self.assertIn('export class Modell {', basis)
        self.assertIn('async bauen(optionen = {}) {', basis)
        self.assertIn('ist nicht implementiert', basis)
        for datei, klasse in ARTEN.items():
            text = ModellHierarchie._text(GEMEINSAM / datei)
            self.assertIn('export class %s extends Modell {' % klasse, text)
            self.assertRegex(text, r'\n    async bauen\(', datei)
            self.assertNotIn('state.js', text, datei)
            self.assertNotIn("from '../scene/", text, datei)

    def test_humanbody_koerper_in_der_richtigen_reihenfolge(self):
        text = ModellHierarchie._text(GEMEINSAM / 'humanbodymodell.js')
        rumpf = text[text.index('async koerper(') : text.index('async _erzeugt(')]
        lippen = rumpf.index('Lippenbau.abspalten(netz, daten.lippen);')
        haut = rumpf.index('this._gehaeutet(netz, skelettdaten, gewichte)')
        gruppe = rumpf.index('this.group.add(this.bodyMesh);')
        details = rumpf.index('this.detailsAnwenden();')
        self.assertLess(lippen, haut)
        self.assertLess(haut, gruppe)
        self.assertLess(gruppe, details)
        self.assertIn('new Modellzubehoer(this, haarfarben).laden()', text)
        self.assertIn('haeuten(skelettdaten, gewichte) {', text)

    def test_die_seiten_bauen_nicht_selbst(self):
        for name, (pfad, aufruf) in SEITEN.items():
            text = ModellHierarchie._text(pfad)
            self.assertIn(aufruf, text, name)
            self.assertNotIn('Koerpernetz.netz(', text, name)
        for datei, kopf in SZENE.items():
            self.assertIn(kopf, ModellHierarchie._text(VIEWER / 'scene' / datei), datei)
        for alt in ALTE_BAUER:
            self.assertFalse((VIEWER / alt).exists(), alt)
        self.assertFalse((THEATRE / 'laden' / 'figurnetz.js').exists())
        alte = re.compile(r'Spurzubehoer|Spurhaut\b|Spurdetails|Figurnetz\.|Kleidungsnetz')
        kommentar = ('*', '//', '/*')
        for pfad in list(VIEWER.rglob('*.js')) + list(THEATRE.rglob('*.js')):
            treffer = [
                z
                for z in ModellHierarchie._text(pfad).splitlines()
                if alte.search(z) and not z.lstrip().startswith(kommentar)
            ]
            self.assertEqual(treffer, [], str(pfad))

    @staticmethod
    def _text(pfad):
        return pfad.read_text(encoding='utf-8')
