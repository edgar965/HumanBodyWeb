# -*- coding: utf-8 -*-
u"""Ein GarmentCode-Stueck ist ein eigenes Objekt, keine Beigabe der Figur.

BEFUND (Edgar, 08.09.2026: „Kleid GarmentCode auswaehlen als Objekt und
loeschen funktioniert nicht - das ganze Modell wird geloescht.")

Das Stueck hing nur ueber `group.add()` an der Figur. Auswaehlbar ist aber,
was in `inst.clothMeshes` steht — `getSelectableSubMeshes` liest genau diese
Ablage. Ein Klick auf das Kleid fand dort nichts, fiel in `interaction.js`
auf `fn.selectCharacter(charId)` durch, und ausgewaehlt war die FIGUR.
Entf loeschte danach die ganze Figur mitsamt Koerper, Haaren und allem.

Der Eintrag wirkt an vier weiteren Stellen, alle vorher unversorgt:
`Character.dispose` gibt das Netz frei, `updateVertexCount` zaehlt es mit,
`menubar` blendet es mit „Kleider ausblenden" aus, und `_removeSubMesh`
raeumt es einzeln ab.

Geprueft wird am QUELLTEXT: Die Klasse haengt an Three.js und ist in Node
nicht ladbar. Ein Quelltexttest ist schwaecher als eine Messung — die
Messung dazu steht im Browser (08.09.2026: Klick auf das Kleid waehlt
`gc_kleid`, Entf laesst die Figur stehen). Er faengt den Fall ab, dass
jemand die Zeilen beim naechsten Umbau verliert.
"""
import re

from django.conf import settings
from django.test import SimpleTestCase


class GarmentcodeObjektTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.quelle = settings.BASE_DIR.joinpath(
            'static', 'viewer', 'scene',
            'garmentcode_anziehen.js').read_text(encoding='utf-8')

    def _rumpf(self, name):
        treffer = re.search(r'static %s\([^)]*\)\s*\{(.*?)\n    \}'
                            % name, self.quelle, re.S)
        self.assertIsNotNone(treffer, '%s nicht gefunden' % name)
        return treffer.group(1)

    def test_einhaengen_traegt_in_clothmeshes_ein(self):
        u"""Ohne diese Zeile ist das Stueck kein waehlbares Teilnetz."""
        rumpf = self._rumpf('einhaengen')
        self.assertIn('clothMeshes[GarmentcodeAnziehen.schluessel(stueck)]',
                      rumpf,
                      'Ohne den Eintrag waehlt ein Klick auf das Stueck die '
                      'ganze Figur — und Entf loescht sie')

    def test_entfernen_raeumt_den_eintrag_mit_weg(self):
        u"""Sonst zeigt die Auswahl ein Stueck, das es nicht mehr gibt."""
        rumpf = self._rumpf('entfernen')
        self.assertIn('delete figur.clothMeshes[schluessel]', rumpf,
                      'Ein verwaister Eintrag laesst `dispose()` spaeter '
                      'ueber ein freigegebenes Netz laufen')

    def test_schluessel_kollidiert_mit_keinem_aufraeumzweig(self):
        u"""`gar_`, `bld_`, `prim_`, `tpl_` haben in `_removeSubMesh` je
        eigene Zweige, die Listen fuehren, die es hier nicht gibt."""
        rumpf = self._rumpf('schluessel')
        treffer = re.search(r'return `([a-z_]+)\$\{rein\}`', rumpf)
        self.assertIsNotNone(treffer, 'Kein Praefix im Schluessel')
        praefix = treffer.group(1)
        for fremd in ('gar_', 'bld_', 'prim_', 'tpl_'):
            self.assertNotEqual(praefix, fremd)
            self.assertFalse(praefix.startswith(fremd),
                             'Praefix %r geraet in den %r-Zweig von '
                             '_removeSubMesh' % (praefix, fremd))

    def test_beschriftung_schlaegt_den_schluessel(self):
        u"""Im Auswahlmenue soll „kleid (GarmentCode)" stehen, nicht `gc_kleid`."""
        auswahl = settings.BASE_DIR.joinpath(
            'static', 'viewer', 'scene',
            'teilnetz_auswahl.js').read_text(encoding='utf-8')
        self.assertIn('mesh.userData?.beschriftung || key', auswahl)
        self.assertIn('userData.beschriftung', self._rumpf('einhaengen'))
