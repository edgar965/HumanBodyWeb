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

    databases = set()

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

    databases = set()
    #: Die fuenf Knoepfe (Edgar, 08.09.2026: Vorschau 2D und 3D
    #: neben Bauen 2D, 3D und 2D+3D). Vorher waren es drei
    #: (`gc-schnitt`, `gc-drapieren`, `gc-erzeugen`). Am selben Tag
    #: fiel das SCHNITTMUSTERBILD im Reiter weg, nicht der Knopf.
    KNOEPFE = {
        'gc-vorschau-2d': "'vorschau2d'",
        'gc-vorschau-3d': "'vorschau3d'",
        'gc-bauen-2d': "'2d'",
        'gc-bauen-3d': "'3d'",
        'gc-bauen-beides': "'komplett'",
    }

    def test_die_vorlage_fuehrt_alle_knoepfe(self):
        _, quelle = _lesen('templates', '_garmentcode_panel.html')
        for kennung in GarmentcodeZweiDTest.KNOEPFE:
            self.assertIn('id="%s"' % kennung, quelle)

    def test_vorschau_und_bauen_sind_beschriftet(self):
        u"""Edgar suchte die „Vorschau"-Knoepfe und fand sie nicht — sie
        hiessen nur „2D" und „3D". Die Gruppennamen stehen deshalb im
        Markup, nicht nur im Titel-Attribut."""
        _, quelle = _lesen('templates', '_garmentcode_panel.html')
        self.assertIn('gc-knopfgruppe">Vorschau<', quelle)
        self.assertIn('gc-knopfgruppe">Bauen<', quelle)

    def test_alle_fuenf_knoepfe_sind_verdrahtet(self):
        _, quelle = _lesen('static', 'viewer', 'scene', 'garmentcode.js')
        for kennung, modus in GarmentcodeZweiDTest.KNOEPFE.items():
            self.assertIn("'%s': %s," % (kennung, modus), quelle)
        self.assertIn('GarmentcodeReiter.KNOEPFE', quelle)

    def test_der_ablauf_kennt_alle_moden(self):
        _, quelle = _lesen('static', 'viewer', 'scene',
                           'garmentcode_ablauf.js')
        anfang = quelle.index('static async dreid(')
        rumpf = quelle[anfang:]
        self.assertIn("modus === 'vorschau3d'", rumpf)
        self.assertIn("modus === '2d' || modus === 'vorschau2d'", rumpf)
        self.assertIn('GarmentcodePanels.zeigen', rumpf)
        self.assertIn('GarmentcodePanels.entfernen', rumpf)
        self.assertIn('GarmentcodeVorschau3d.zeigen', rumpf)
        # Das Vorschaunetz muss beim Drapieren weichen — sonst liegen zwei
        # Stuecke an derselben Stelle.
        self.assertIn('GarmentcodeVorschau3d.entfernen', rumpf)

    def test_beide_dreid_wege_verlangen_einen_schnitt(self):
        u"""`vorschau3d` liest den Ergebnisordner; ohne die Wache liefe sie
        auf dem Schnitt der vorigen Figur — dieselbe Falle wie bei „3D".

        Die Liste selbst steht seit dem 09.09.2026 in
        `garmentcode_schritte.js` — dort haengt ebenfalls daran, ob ein
        Schnittschritt in den Plan kommt. Der Ablauf VERWEIST darauf; zwei
        Listen desselben Inhalts liefen beim naechsten neuen Modus
        auseinander, und dann baut der eine Weg einen Schnitt, den der
        andere nicht erwartet. Genau das haelt dieser Fall fest.
        """
        _, quelle = _lesen('static', 'viewer', 'scene',
                           'garmentcode_ablauf.js')
        self.assertIn('static NUR3D = GarmentcodeSchritte.NUR3D;', quelle)
        self.assertIn('GarmentcodeAblauf.NUR3D.includes(modus)', quelle)
        _, plan = _lesen('static', 'viewer', 'scene',
                         'garmentcode_schritte.js')
        self.assertIn("static NUR3D = ['3d', 'vorschau3d'];", plan)

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
        u"""`.btn-toggle` setzt `width:100%`; ohne `hb-fest` nimmt der
        schmale Knopf die ganze Zeile und quetscht den Nachbarn.

        Im DOM gemessen (07.09.2026): 198,9 px fuer „2D", 65,4 px fuer den
        Nachbarn, dessen Text vierzeilig umbrach. Mit `hb-fest` sitzen die
        fuenf Knoepfe bei 54, 56, 54, 58 und 97 px, alle einzeilig
        (nachgemessen 08.09.2026).
        """
        _, quelle = _lesen('templates', '_garmentcode_panel.html')
        for kennung in ('gc-vorschau-2d', 'gc-vorschau-3d',
                        'gc-bauen-2d', 'gc-bauen-3d'):
            zeile = [z for z in quelle.splitlines()
                     if 'id="%s"' % kennung in z][0]
            self.assertIn('hb-fest', zeile, kennung)
