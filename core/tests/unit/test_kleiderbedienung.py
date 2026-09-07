# -*- coding: utf-8 -*-
u"""Zwei Stellen, die im Browser stumm ausfallen (07.09.2026).

Beide Faelle sind an diesem Tag wirklich passiert, und beide sagen im
Browser nichts: keine Ausnahme, kein Eintrag im Log, nur ein Stueck
Kleidung, das nicht mitgeht, und ein Knopf, den es nicht gibt.

1. DIE BINDUNG HAENGT AN DER REIHENFOLGE
   `MhFigur.load()` zieht die Kleidung ZUERST an — die Loeschmaske des
   Koerpers haengt daran. Das Skelett entsteht erst danach, also findet
   `Mhkleidstueck.anlegen` `figur.skelett === null` und laesst ein starres
   `Mesh` haengen. Gemessen: `isSkinnedMesh false`, kein `skinIndex`; der
   Koerper lief, der Anzug blieb stehen (Edgar: „Kleider von MakeHuman
   animieren immer noch nicht"). Am Server lag es nicht — der schickte die
   Gewichte mit, 163 Knochennamen, keiner fehlte im Skelett.

   Der Nachbau ist `_kleiderBinden`, gerufen aus `_hautBinden`. Faellt
   dieser Aufruf weg, ist alles wieder wie vorher — und nichts wird rot.

2. DER 2D-KNOPF
   Gemessen 4,6 s gegen 31 s fuer den ganzen Weg. Fehlt die Verdrahtung
   oder die ID in der Vorlage, sitzt der Knopf da und tut nichts.

Geprueft wird am QUELLTEXT, nicht am Verhalten: Beides haengt an Three.js
und am DOM. Ein Quelltexttest ist schwaecher als eine Messung — er faengt
aber genau den Fall ab, in dem jemand die Zeile beim naechsten Umbau
verliert.
"""
import re

from django.conf import settings
from django.test import SimpleTestCase


def _lesen(*teile):
    pfad = settings.BASE_DIR.joinpath(*teile)
    return pfad, pfad.read_text(encoding='utf-8')


class MakehumanKleiderbindungTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.pfad, self.quelle = _lesen('static', 'viewer', 'scene',
                                        'makehuman', 'mhfigur.js')

    def test_hautbinden_ruft_kleiderbinden(self):
        u"""Der Aufruf steht IM Rumpf von `_hautBinden`, nicht irgendwo."""
        rumpf = re.search(r'_hautBinden\(hautgewichte\)\s*\{(.*?)\n    \}',
                          self.quelle, re.S)
        self.assertIsNotNone(rumpf, '_hautBinden nicht gefunden')
        self.assertIn('this._kleiderBinden()', rumpf.group(1),
                      'Ohne diesen Aufruf bleibt Kleidung, die vor dem '
                      'Skelett angelegt wurde, ein starres Mesh')

    def test_kleiderbinden_nimmt_die_rohgewichte(self):
        u"""Aus `userData`, nicht aus den Attributen der Geometrie.

        Deren Knochennummern gehoeren zum ALTEN Skelett — `_skelettBauen`
        raeumt bei jedem Reglerzug ab und baut neu.
        """
        rumpf = re.search(r'_kleiderBinden\(\)\s*\{(.*?)\n    \}',
                          self.quelle, re.S)
        self.assertIsNotNone(rumpf, '_kleiderBinden fehlt')
        self.assertIn('userData?.hautgewichte', rumpf.group(1))
        self.assertIn('Eigenhaut.binden', rumpf.group(1))

    def test_die_geometrie_wird_nicht_entsorgt(self):
        u"""`Netzentsorgung.entfernen` gibt Geometrie UND Material frei.

        Beide werden im naechsten Atemzug wiederverwendet.
        """
        rumpf = re.search(r'_kleiderBinden\(\)\s*\{(.*?)\n    \}',
                          self.quelle, re.S).group(1)
        # Ohne die Kommentarzeilen: Der Name steht dort in der BEGRUENDUNG,
        # warum gerade NICHT entsorgt wird — ein Treffer darin waere ein
        # Fehlalarm (`~/.claude/rules/analysewerkzeuge.md`).
        code = chr(10).join(z for z in rumpf.splitlines()
                            if not z.strip().startswith('//'))
        self.assertNotIn('Netzentsorgung.entfernen', code)
        self.assertIn('this.group.remove(altes)', code)

    def test_das_stueck_hebt_seine_rohgewichte_auf(self):
        _, quelle = _lesen('static', 'viewer', 'scene', 'makehuman',
                           'mhkleidstueck.js')
        self.assertIn('netz.userData.hautgewichte = daten.hautgewichte',
                      quelle)

    def test_eigenhaut_reicht_userdata_weiter(self):
        u"""`binden()` baut ein NEUES Objekt — ohne diese Zeile ist das
        Stueck nach der ersten Bindung nicht mehr nachbindbar."""
        _, quelle = _lesen('static', 'viewer', 'gemeinsam', 'eigenhaut.js')
        self.assertIn('gebunden.userData = netz.userData', quelle)


class GarmentcodeZweiDTest(SimpleTestCase):

    databases = []

    def test_die_vorlage_fuehrt_beide_knoepfe(self):
        _, quelle = _lesen('templates', '_garmentcode_panel.html')
        self.assertIn('id="gc-schnitt"', quelle)
        self.assertIn('id="gc-erzeugen"', quelle)

    def test_der_2d_knopf_dehnt_sich_nicht(self):
        u"""`.btn-toggle` setzt `width:100%`; ohne `hb-fest` nimmt der
        schmale Knopf die ganze Zeile und quetscht den Nachbarn.

        Im DOM gemessen: 198,9 px fuer „2D", 65,4 px fuer „Fuer diese Figur
        bauen", dessen Text vierzeilig umbrach. Mit `hb-fest`: 54,2 und
        210,0 px, beide einzeilig.
        """
        _, quelle = _lesen('templates', '_garmentcode_panel.html')
        zeile = [z for z in quelle.splitlines() if 'id="gc-schnitt"' in z][0]
        self.assertIn('hb-fest', zeile)

    def test_alle_drei_knoepfe_sind_verdrahtet(self):
        u"""Edgar, 07.09.2026: „insgesamt dann 3 Buttons"."""
        _, quelle = _lesen('static', 'viewer', 'scene', 'garmentcode.js')
        for kennung, modus in (('gc-schnitt', "'2d'"),
                               ('gc-drapieren', "'3d'"),
                               ('gc-erzeugen', "'komplett'")):
            self.assertIn("getElementById('%s')" % kennung, quelle)
            self.assertIn('this.bauen(%s)' % modus, quelle)

    def test_der_ablauf_kennt_die_drei_moden(self):
        _, quelle = _lesen('static', 'viewer', 'scene',
                           'garmentcode_ablauf.js')
        anfang = quelle.index('static async dreid(')
        rumpf = quelle[anfang:]
        self.assertIn("if (modus === '2d')", rumpf)
        self.assertIn('GarmentcodePanels.zeigen', rumpf)
        self.assertIn('GarmentcodePanels.entfernen', rumpf)

    def test_3d_prueft_ob_der_schnitt_zur_figur_gehoert(self):
        u"""Sonst drapiert „3D" nach einem Figurwechsel den Schnitt der
        vorigen — dieselbe Falle wie am 06.09.2026, als ein Bau ohne
        Morphs den Ergebnisordner ueberschrieb und eine Stunde Messlaeufe
        auf dem falschen Schnitt rechneten.
        """
        _, quelle = _lesen('static', 'viewer', 'scene',
                           'garmentcode_ablauf.js')
        self.assertIn('schnittPasst(reiter, figur, vorlage)', quelle)
        anfang = quelle.index('static schnittPasst(')
        ende = quelle.index(chr(10) + '    }', anfang)
        rumpf = quelle[anfang:ende]
        self.assertIn('reiter.schnittVon.figur === figur.id', rumpf)
        self.assertIn('reiter.schnittVon.vorlage === vorlage', rumpf)

    def test_die_schmalen_knoepfe_tragen_hb_fest(self):
        _, quelle = _lesen('templates', '_garmentcode_panel.html')
        for kennung in ('gc-schnitt', 'gc-drapieren'):
            zeile = [z for z in quelle.splitlines()
                     if 'id="%s"' % kennung in z][0]
            self.assertIn('hb-fest', zeile, kennung)
