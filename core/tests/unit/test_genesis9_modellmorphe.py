# -*- coding: utf-8 -*-
"""`G9modellmorphe`: die Eigenform eines importierten Modells bekommt einen Schieber (08.10.2026).

Edgar: „Eigenmorph: Schieber im UI". Der Blender-Import legt über „Mesh to 3D" einen Eigenmorph `eigen:<kennung>` ab; das Modell
trägt ihn mit Wert 1, aber ohne Schieber ließ er sich nicht zurücknehmen. Jetzt kennzeichnet der Import ihn im Steckbrief
(`art: 'modell'`), und der Bereich „Modell-Eigen" des Reglerfelds listet ihn (0…2).

1. `markieren` ergänzt den Steckbrief (art, modell, anzeige), die Zahlen des Morphs bleiben; ohne Morph-Datei und für einen
   Namen ohne `eigen:` ein `ValueError`.
2. Der Bereich listet nur markierte Morphe — keinen unmarkierten, keinen `kopf`-Morph.
3. Von mehreren Läufen desselben Modells zeigt er den NEUESTEN; ein Teilmorph (`mund`) steht eigens, anderes Modell eigens.
4. Der Import (`Blendimportmodell.eigenform_markieren`) kennzeichnet den kürzesten Namen als Hauptmorph, die längeren nach ihrem Rest.
5. `G9reglerplan.bereiche` hängt den Bereich an (Quelltext — der Plan selbst braucht die Daz-Bibliothek).

Sabotage-Gegenprobe: in `bereich` den Vergleich `stand > neueste[…][0]` auf `<` drehen → Fall 3 rot; die Zeile
`G9modellmorphe.bereich()` aus `reglerplan.py` nehmen → Fall 5 rot; `art`-Prüfung weglassen → Fall 2 rot.
"""

import inspect
import os
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.eigenmorphe import G9eigenmorphe
from Genesis9.modellmorphe import G9modellmorphe
from Genesis9.reglerplan import G9reglerplan

from core.dienste.blendimportmodell import Blendimportmodell

from ._pruefablage import Pruefablage


class Genesis9ModellmorpheTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        wurzel = self.enterContext(Pruefablage.ordner('modellmorphe_'))
        umgebung = mock.patch.dict(os.environ, {'HB_OBJECTS_ROOT': wurzel})
        umgebung.start()
        self.addCleanup(umgebung.stop)

    def _morph(self, name, steckbrief=None, alter_ns=None):
        regler = G9eigenmorphe.ablegen(name, [1, 2], [[0.002, 0.0, 0.0], [0.0, 0.003, 0.0]], steckbrief)
        if alter_ns is not None:
            datei = G9eigenmorphe._pfad(regler[len(G9eigenmorphe.PRAEFIX):], '.npz')
            os.utime(datei, ns=(alter_ns, alter_ns))
        return regler

    def _namen(self):
        return [r['name'] for r in G9modellmorphe.bereich()['regler']]

    def test_1_markieren_ergaenzt_den_steckbrief_und_laesst_die_zahlen(self):
        regler = self._morph('cute girl lauf a')
        brief = G9modellmorphe.markieren(regler, 'cute girl')
        self.assertEqual((brief['art'], brief['modell'], brief['anzeige']), ('modell', 'cute girl', 'cute girl · Eigenform'))
        self.assertEqual(brief['punkte'], 2, 'die Zahlen des Morphs bleiben')
        self.assertEqual(G9eigenmorphe.steckbrief('cute_girl_lauf_a')['art'], 'modell', 'steht in der Datei')

    def test_1b_ohne_morph_und_ohne_eigen_ist_ein_fehler(self):
        with self.assertRaises(ValueError):
            G9modellmorphe.markieren('eigen:gibt_es_nicht', 'x')
        with self.assertRaises(ValueError):
            G9modellmorphe.markieren('body_bs_Height', 'x')

    def test_2_der_bereich_listet_nur_markierte_modellmorphe(self):
        self._morph('ohne kennzeichen')
        self._morph('kopf mundform', {'art': 'kopf'})
        G9modellmorphe.markieren(self._morph('cute girl lauf a'), 'cute girl')
        bereich = G9modellmorphe.bereich()
        self.assertEqual((bereich['schluessel'], bereich['name']), ('modell_eigen', 'Modell-Eigen'))
        self.assertEqual(self._namen(), ['eigen:cute_girl_lauf_a'])
        regler = bereich['regler'][0]
        self.assertEqual((regler['min'], regler['max'], regler['vorgabe']), (0.0, G9eigenmorphe.MAX, 0.0))

    def test_2b_ohne_ordner_ist_der_bereich_leer_aber_da(self):
        self.assertEqual(G9modellmorphe.bereich()['regler'], [])

    def test_3_der_neueste_lauf_desselben_modells_gilt(self):
        a = self._morph('cute girl lauf a', alter_ns=1_000_000_000_000_000_000)
        b = self._morph('cute girl lauf b', alter_ns=2_000_000_000_000_000_000)
        G9modellmorphe.markieren(a, 'cute girl')       # schreibt nur die .json: die Zeit der .npz zählt
        G9modellmorphe.markieren(b, 'cute girl')
        self.assertEqual(self._namen(), ['eigen:cute_girl_lauf_b'])
        os.utime(G9eigenmorphe._pfad('cute_girl_lauf_a', '.npz'), ns=(3_000_000_000_000_000_000,) * 2)
        self.assertEqual(self._namen(), ['eigen:cute_girl_lauf_a'])

    def test_3b_teilmorph_und_anderes_modell_stehen_eigens(self):
        G9modellmorphe.markieren(self._morph('cute girl lauf a'), 'cute girl')
        G9modellmorphe.markieren(self._morph('cute girl lauf a mund'), 'cute girl', 'mund')
        G9modellmorphe.markieren(self._morph('anna lauf 1'), 'anna')
        anzeigen = sorted(r['anzeige'] for r in G9modellmorphe.bereich()['regler'])
        self.assertEqual(anzeigen, ['anna · Eigenform', 'cute girl · Eigenform', 'cute girl · Eigenform · mund'])

    def test_4_der_import_kennzeichnet_hauptmorph_und_teil(self):
        self._morph('cute girl lauf a')
        self._morph('cute girl lauf a mund')
        regler = {'eigen:cute_girl_lauf_a': 1.0, 'eigen:cute_girl_lauf_a_mund': 0.5, 'body_bs_Height': 0.2}
        gefunden = Blendimportmodell.eigenform_markieren('cute girl', regler)
        self.assertEqual(gefunden, ['eigen:cute_girl_lauf_a', 'eigen:cute_girl_lauf_a_mund'])
        anzeigen = sorted(r['anzeige'] for r in G9modellmorphe.bereich()['regler'])
        self.assertEqual(anzeigen, ['cute girl · Eigenform', 'cute girl · Eigenform · mund'])

    def test_4b_ein_fehlender_morph_bricht_den_import_nicht(self):
        gefunden = Blendimportmodell.eigenform_markieren('x', {'eigen:fehlt': 1.0})
        self.assertEqual(gefunden, ['eigen:fehlt'])
        self.assertEqual(self._namen(), [])

    def test_5_der_reglerplan_haengt_den_bereich_an(self):
        self.assertIn('G9modellmorphe.bereich()', inspect.getsource(G9reglerplan.bereiche))
