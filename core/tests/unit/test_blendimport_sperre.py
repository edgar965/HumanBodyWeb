# -*- coding: utf-8 -*-
"""Blender-Import: kein zweiter Import neben einem laufenden, und die Normalen-Grenze ist wählbar (08.10.2026).

Edgar: „wenn ich jetzt einen neuen Import starte … werden all diese Schritte automatisch ausgeführt?" — Antwort „ja, aber nicht
gleichzeitig starten": Nichts hielt den zweiten Lauf auf, beide hätten GPU (Backen, „Mesh to 3D") und Kerne geteilt.

1. `Blendimportarbeiter.laufender` nennt den Import, dessen Arbeitsprozess lebt UND dessen Stand „läuft" sagt — eine alte
   PID-Datei, deren Nummer Windows an einen fremden Prozess vergeben hat, sperrt nicht. Der eigene Import zählt nicht.
2. Die Endpunkte `starten` und `neu` antworten 409 mit der Kennung und dem Schritt des laufenden Imports; es entsteht kein
   neuer Import, der Arbeitsprozess startet nicht.
3. Die Normalen-Grenze kommt aus dem Dialog (`normalen_grenze`): 35° säubert ein Texel mit 60° Kippung, 70° lässt es, `aus`
   ändert nichts. Fällt in eine Kachel mehr als `WARN_PROZENT`, steht eine Warnung in der Statuszeile.

Sabotage-Gegenprobe: in `laufender` die Prüfung `stand().get('status') == 'laeuft'` entfernen → `SperreTest.test_2` rot;
`kennung != ausser` entfernen → `test_3` rot; in `_belegt` `return None` statt der Antwort → `test_4` rot; in `_saeubern`
`grad` nicht durchreichen → `NormalenGrenzeTest.test_1` rot; die Schwelle in `_warnen` entfernen → `test_2` rot.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

import json
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import RequestFactory, SimpleTestCase, override_settings

from core.api.blendimport import Blendimportendpunkte
from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportarbeiter import Blendimportarbeiter
from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.blendimporthaut import Blendimporthaut
from core.dienste.blendimportnormalen import Blendimportnormalen
from core.tests.unit._pruefablage import Pruefablage


class SperreTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        gebaut = Pruefablage.ordner('blendimport_')
        self.wurzel = gebaut.__enter__()
        self.addCleanup(gebaut.__exit__, None, None, None)
        umlenkung = override_settings(OBJECTS_ROOT=self.wurzel)
        umlenkung.enable()
        self.addCleanup(umlenkung.disable)
        self.lebende = set()
        arbeiter = mock.patch.object(Blendimportarbeiter, 'lebt', side_effect=lambda ablage: ablage.kennung in self.lebende)
        arbeiter.start()
        self.addCleanup(arbeiter.stop)

    def _import(self, kennung, status, lebt):
        Blendimportablage(kennung).stand_schreiben({'kennung': kennung, 'status': status, 'schritt': 'haut'})
        if lebt:
            self.lebende.add(kennung)

    def test_1_ohne_importe_ist_nichts_belegt(self):
        self.assertIsNone(Blendimportarbeiter.laufender())

    def test_2_nur_ein_lebender_prozess_mit_laufendem_stand_sperrt(self):
        self._import('2026.10.08.10.00.00', 'laeuft', lebt=False)     # Prozess tot (Absturz): keine Sperre
        self._import('2026.10.08.11.00.00', 'fertig', lebt=True)      # PID wiederverwendet: keine Sperre
        self.assertIsNone(Blendimportarbeiter.laufender())
        self._import('2026.10.08.12.00.00', 'laeuft', lebt=True)
        self.assertEqual(Blendimportarbeiter.laufender(), '2026.10.08.12.00.00')

    def test_3_der_eigene_import_zaehlt_nicht(self):
        self._import('2026.10.08.12.00.00', 'laeuft', lebt=True)
        self.assertIsNone(Blendimportarbeiter.laufender(ausser='2026.10.08.12.00.00'))
        self._import('2026.10.08.13.00.00', 'laeuft', lebt=True)
        self.assertEqual(Blendimportarbeiter.laufender(ausser='2026.10.08.12.00.00'), '2026.10.08.13.00.00')

    def test_4_starten_und_neu_antworten_409_ohne_etwas_anzulegen(self):
        self._import('2026.10.08.12.00.00', 'laeuft', lebt=True)
        self._import('2026.10.08.09.00.00', 'fertig', lebt=False)
        vorher = Blendimportablage.alle()
        anfrage = RequestFactory().post('/api/character/blendimport/starten/', data=json.dumps({'werte': {}}),
                                        content_type='application/json')
        with mock.patch.object(Blendimportarbeiter, 'starten') as starten:
            antwort = Blendimportendpunkte.starten(anfrage)
            neu = Blendimportendpunkte.neu(RequestFactory().post('/x/', data='{}', content_type='application/json'),
                                           '2026.10.08.09.00.00')
        self.assertEqual(antwort.status_code, 409)
        text = json.loads(antwort.content)['error']
        self.assertIn('2026.10.08.12.00.00', text)
        self.assertIn('haut', text)
        self.assertEqual(neu.status_code, 409)
        starten.assert_not_called()
        self.assertEqual(Blendimportablage.alle(), vorher, 'kein neuer Import angelegt')

    def test_5_ist_nichts_belegt_antwortet_belegt_mit_none(self):
        self.assertIsNone(Blendimportendpunkte._belegt())


class NormalenGrenzeTest(SimpleTestCase):
    databases = set()

    def _haut(self, grenze, melden=None):
        # `_warnen` schreibt die Kennung der Ablage ins Log — eine Attrappe mit Kennung genügt.
        return Blendimporthaut(SimpleNamespace(kennung='2026.10.08.00.00.00'), None, {'netze': []}, [], 8192, melden, grenze)

    def _karte(self):
        karte = np.zeros((40, 40, 3), dtype=np.uint8)
        karte[:, :] = Blendimportnormalen.FLACH
        karte[20, 20] = (238, 128, 191)     # n = (0,866 | 0 | 0,5): 60° Kippung
        return karte

    def test_1_die_grenze_aus_dem_dialog_bestimmt_was_flach_wird(self):
        karte = self._karte()
        streng, anteil_streng = self._haut('35')._saeubern(karte, None)
        locker, anteil_locker = self._haut('70')._saeubern(karte, None)
        aus, anteil_aus = self._haut('aus')._saeubern(karte, None)
        vorgabe, _ = self._haut(None)._saeubern(karte, None)
        self.assertEqual(tuple(streng[20, 20]), Blendimportnormalen.FLACH)
        self.assertGreater(anteil_streng, 0.0)
        self.assertEqual(tuple(locker[20, 20]), (238, 128, 191))
        self.assertEqual(anteil_locker, 0.0)
        self.assertTrue(np.array_equal(aus, karte))
        self.assertEqual(anteil_aus, 0.0)
        self.assertEqual(tuple(vorgabe[20, 20]), Blendimportnormalen.FLACH, '60° liegt über der Vorgabe von 50°')

    def test_2_viele_geaenderte_texel_warnen_in_der_statuszeile(self):
        meldungen = []
        haut = self._haut(None, lambda anteil, text: meldungen.append(text))
        haut.normalen_flach = {'1002': 1.2, '1004': Blendimportnormalen.WARN_PROZENT + 0.5}
        haut._warnen(1002)
        self.assertEqual(meldungen, [], 'unter der Schwelle bleibt es still')
        haut._warnen(1004)
        self.assertEqual(len(meldungen), 1)
        self.assertIn('Kachel 1004', meldungen[0])
        self.assertIn('Grenze', meldungen[0])

    def test_3_der_dialog_kennt_die_wahl_und_prueft_sie(self):
        self.assertEqual(Blendimporteinstellungen.pruefen({})['normalen_grenze'], '50')
        self.assertEqual(Blendimporteinstellungen.pruefen({'normalen_grenze': 'aus'})['normalen_grenze'], 'aus')
        self.assertEqual(Blendimporteinstellungen.pruefen({'normalen_grenze': '999'})['normalen_grenze'], '50')
