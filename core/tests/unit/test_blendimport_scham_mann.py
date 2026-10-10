# -*- coding: utf-8 -*-
"""Männliche Anatomie als Stück (Edgar, 09.10.2026: „Ein Penis", „ich importiere gleich ein Mesh mit Penis"): die Einstellung `scham = mann`.

Ein Mesh mit Penis gab es zum Prüfen nicht (Recherche `ProjektTemp/_wegwerf/penissuche/ergebnis.md`: kein lokales Modell, keines mit freier Lizenz und
gesicherter Anatomie im Netz). Gebaut ist deshalb nur, was ohne ein solches Mesh prüfbar ist — dieselbe Saat, derselbe Schnitt, dieselben Gewichte wie bei
der Scham (die Saat wächst für hängende Hoden und einen hochstehenden Penis, `test_blendimport_scham_kasten.py`), aber:

1. Der Dialog kennt den Wert `mann` und lässt ihn durch die Prüfung; Unbekanntes fällt weiter auf die Vorgabe.
2. `Blendimportstuecke` baut bei `mann` ein Stück „<Name> Genitalien" mit `anatomie = penis`, bei `objekt` „<Name> Scham" mit `anatomie = vagina` (bis
   10.10.2026 `scham`), bei `figur` gar keins.
3. `G9stueckersatz` schreibt und liest `penis`; `G9schammorphe.ist_anatomie` ist dafür FALSCH — das Stück trägt nicht die weiblichen Scham-Regler (Hügel,
   Lippen, Haube, Eingang, Damm), sondern die des Penis (`test_anatomien.py`).
4. Die Nachformung der Scham entfällt auch bei `mann` (das Stück ersetzt sie).

Sabotage-Gegenprobe: `('mann', …)` aus dem Katalog streichen macht Fall 1 rot; `self.anatomie = 'penis' if …` zu `'scham'` macht Fall 2 rot; `'penis'` aus `ANATOMIEN`
streichen macht Fall 3 rot; `== 'scham'` in `ist_anatomie` zu `!= ''` macht Fall 3 rot; `in ('objekt', 'mann')` in `_nachformung` zu `== 'objekt'` macht Fall 4 rot.

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""
import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.schammorphe import G9schammorphe
from Genesis9.stueckersatz import G9stueckersatz

from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.blendimportlauf import Blendimportlauf
from core.dienste.blendimportstuecke import Blendimportstuecke

from ._pruefablage import Pruefablage


class SchamMannTest(SimpleTestCase):
    databases = set()

    def _stuecke(self, scham):
        with mock.patch('core.dienste.blendimportstuecke.Blendimportlage'):
            return Blendimportstuecke(mock.Mock(), mock.Mock(), {'netze': []}, [], 'Daven', scham=scham)

    def test_1_der_dialog_kennt_mann_und_prueft_den_rest_wie_bisher(self):
        werte = Blendimporteinstellungen.pruefen({'pfad': 'x', 'scham': 'mann'})
        self.assertEqual(werte['scham'], 'mann')
        self.assertEqual(Blendimporteinstellungen.pruefen({'pfad': 'x', 'scham': 'quatsch'})['scham'], 'objekt')
        self.assertEqual(Blendimporteinstellungen.pruefen({'pfad': 'x', 'scham': 'figur'})['scham'], 'figur')

    def test_2_mann_baut_genitalien_mit_anatomie_penis_objekt_baut_scham(self):
        mann, frau, figur = self._stuecke('mann'), self._stuecke('objekt'), self._stuecke('figur')
        koerper = {'rolle': 'scham', 'name': 'body'}
        self.assertTrue(mann.scham_objekt)
        self.assertEqual(mann.anatomie, 'penis')
        self.assertEqual(mann.anzeige(koerper), 'Daven Genitalien')
        self.assertTrue(frau.scham_objekt)
        self.assertEqual(frau.anatomie, 'vagina')
        self.assertEqual(frau.anzeige(koerper), 'Daven Scham')
        self.assertFalse(figur.scham_objekt)

    def test_3_penis_wird_geschrieben_und_gelesen_aber_traegt_keine_scham_regler(self):
        gebaut = Pruefablage.ordner('mann_')
        ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        duf = ordner / 'Genitalien.duf'
        duf.write_text('{}', encoding='utf-8')
        pfad = G9stueckersatz.schreiben(duf, [], haut_tiefe_mm=30, anatomie='penis', eigene_gewichte=True)
        self.assertEqual(json.loads(pfad.read_text(encoding='utf-8'))['anatomie'], 'penis')
        self.assertIn('penis', G9stueckersatz.ANATOMIEN)
        with mock.patch('Genesis9.garderobe.G9garderobe.datei', return_value=duf), \
                mock.patch('Genesis9.garderobe.G9garderobe.eintrag', return_value={'kennung': 'x'}):
            self.assertEqual(G9stueckersatz.anatomie_fuer({}), 'penis')
            self.assertFalse(G9schammorphe.ist_anatomie('x'), 'der Penis darf nicht die weiblichen Scham-Regler tragen')

    def test_4_die_nachformung_der_scham_entfaellt_auch_bei_mann(self):
        for scham, entfaellt in (('mann', True), ('objekt', True), ('figur', False)):
            lauf = Blendimportlauf.__new__(Blendimportlauf)
            lauf.stand = {'einstellungen': {'scham': scham}, 'quelle': {'name': 'x'}, 'rollen': []}
            gemerkt = {}
            lauf.ergebnis = lambda schritt, wert, g=gemerkt: g.update({schritt: wert})
            lauf.inventar = lambda: {}
            lauf.ablage = mock.Mock()
            lauf.melden = lambda *a: None
            with mock.patch('core.dienste.blendimportnachformung.Blendimportnachformung') as nachformung, \
                    mock.patch.object(Blendimportlauf, '_unterkleid', side_effect=lambda job, bericht: bericht):
                nachformung.return_value.formen.return_value = {'ok': True}
                lauf._nachformung(mock.Mock())
            self.assertEqual('aus' in gemerkt['nachformung'], entfaellt, scham)
