# -*- coding: utf-8 -*-
"""Die drei Anatomien als eigene Klassen: Penis, Vagina, Anus (Edgar, 10.10.2026: „mach extra Klassen für Penis, Vagina, Anus").

1. `G9anatomien` kennt genau `penis`, `vagina`, `anus`; der alte Schlüssel `scham` geht auf `G9vagina`, Unbekanntes auf nichts.
2. Jede Anatomie ist eine eigene Klasse mit eigenem Schlüssel; Reglernamen sind getrennt (`sch_…` Vagina, `pen_…` Penis, Anus keine).
3. Der Reglername findet seine Anatomie (`von_regler`), das Stück findet seine über die `.ersetzt.json` (`von_stueck`) — auch mit dem alten Schlüssel.
4. `G9standardmorphe` erkennt die Regler beider Anatomien als feste Regler (`art_von` = `anatomie`), sonst nichts.
5. Der Anus trägt keine Regler und baut nichts — er sagt es mit einem Fehler, statt still nichts zu tun.

Sabotage-Gegenprobe: `ALT = ('scham',)` in `G9vagina` streichen macht Fall 1 und 3 rot; `PRAEFIX = 'pen_'` in `G9penis` auf `'sch_'` macht Fall 2 rot;
`von_regler` ohne Penis macht Fall 3 und 4 rot; `bauen` im Anus ohne `ValueError` macht Fall 5 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""
import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.anatomie import G9anatomie
from Genesis9.anatomien import G9anatomien
from Genesis9.anus import G9anus
from Genesis9.penis import G9penis
from Genesis9.standardmorphe import G9standardmorphe
from Genesis9.stueckersatz import G9stueckersatz
from Genesis9.vagina import G9vagina

from ._pruefablage import Pruefablage


class AnatomienTest(SimpleTestCase):
    databases = set()

    def test_1_die_registratur_kennt_drei_und_uebersetzt_den_alten_namen(self):
        self.assertEqual(sorted(G9anatomien.schluessel()), ['anus', 'penis', 'vagina'])
        self.assertIs(G9anatomien.fuer('penis'), G9penis)
        self.assertIs(G9anatomien.fuer('vagina'), G9vagina)
        self.assertIs(G9anatomien.fuer('anus'), G9anus)
        self.assertIs(G9anatomien.fuer('scham'), G9vagina, 'der alte Schlüssel')
        self.assertEqual(G9anatomien.normal('scham'), 'vagina')
        for unsinn in ('tier', '', None, 5, ['penis']):
            self.assertIsNone(G9anatomien.fuer(unsinn), repr(unsinn))
            self.assertEqual(G9anatomien.normal(unsinn), '')

    def test_2_jede_anatomie_ist_eine_eigene_klasse_mit_eigenem_schluessel_und_eigenen_reglernamen(self):
        klassen = (G9penis, G9vagina, G9anus)
        for k in klassen:
            self.assertTrue(issubclass(k, G9anatomie), k.__name__)
        self.assertEqual(len({k.SCHLUESSEL for k in klassen}), 3)
        namen = {k: {e[0] for e in k.eintraege()} for k in klassen}
        self.assertTrue(namen[G9penis] and all(n.startswith('pen_') for n in namen[G9penis]))
        self.assertTrue(namen[G9vagina] and all(n.startswith('sch_') for n in namen[G9vagina]))
        self.assertEqual(namen[G9anus], set())
        self.assertFalse(namen[G9penis] & namen[G9vagina], 'ein Reglername darf nur einer Anatomie gehören')
        self.assertEqual(len(G9penis.regler()), len(G9penis.eintraege()))
        self.assertEqual(len(G9vagina.regler()), len(G9vagina.eintraege()))

    def test_3_der_reglername_findet_seine_anatomie_und_das_stueck_die_seine(self):
        self.assertIs(G9anatomien.von_regler('sch_damm_laenge'), G9vagina)
        self.assertIs(G9anatomien.von_regler('pen_hoden_vor'), G9penis)
        self.assertIsNone(G9anatomien.von_regler('form_weite_unten'))
        gebaut = Pruefablage.ordner('anatomien_')
        ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        duf = ordner / 'Stueck.duf'
        duf.write_text('{}', encoding='utf-8')
        pfad = G9stueckersatz.pfad(duf)
        for geschrieben, erwartet in (('penis', G9penis), ('vagina', G9vagina), ('scham', G9vagina), ('anus', G9anus)):
            pfad.write_text(json.dumps({'anatomie': geschrieben}), encoding='utf-8')
            with mock.patch('Genesis9.garderobe.G9garderobe.datei', return_value=duf), \
                    mock.patch('Genesis9.garderobe.G9garderobe.eintrag', return_value={'kennung': 'x'}):
                self.assertIs(G9anatomien.von_stueck('x'), erwartet, geschrieben)
        pfad.write_text('{}', encoding='utf-8')
        with mock.patch('Genesis9.garderobe.G9garderobe.datei', return_value=duf), \
                mock.patch('Genesis9.garderobe.G9garderobe.eintrag', return_value={'kennung': 'x'}):
            self.assertIsNone(G9anatomien.von_stueck('x'), 'ein Stück ohne Anatomie trägt keine Regler')

    def test_4_die_festen_regler_erkennen_beide_anatomien_aber_nicht_fremdes(self):
        for name in ('pen_laenge', 'sch_gesamt_fuelle'):
            self.assertTrue(G9standardmorphe.ist_standard(name), name)
            self.assertEqual(G9standardmorphe.art_von(name), 'anatomie', name)
        self.assertEqual(G9standardmorphe.art_von('op_curl'), 'haar')
        self.assertIsNone(G9standardmorphe.art_von('mein_morph'))
        self.assertFalse(G9standardmorphe.ist_standard('mein_morph'))

    def test_5_der_anus_hat_keine_regler_und_baut_nichts(self):
        self.assertEqual(G9anus.regler(), [])
        self.assertFalse(G9anus.gehoert('pen_laenge'))
        with self.assertRaises(ValueError):
            G9anus.bauen('x', 'irgendwas')
