# -*- coding: utf-8 -*-
"""Blender-Import: kein zweiter Import neben einem laufenden, und die Normalen-Grenze ist wählbar (08.10.2026).

Edgar: „wenn ich jetzt einen neuen Import starte … werden all diese Schritte automatisch ausgeführt?" — Antwort „ja, aber nicht
gleichzeitig starten": Nichts hielt den zweiten Lauf auf, beide hätten GPU (Backen, „Mesh to 3D") und Kerne geteilt.

1. `Blendimportarbeiter.laufender` nennt den Import, dessen Arbeitsprozess lebt UND dessen Stand „läuft" sagt — eine alte
   PID-Datei, deren Nummer Windows an einen fremden Prozess vergeben hat, sperrt nicht. Der eigene Import zählt nicht.
2. Die Endpunkte `starten` und `neu` REIHEN EIN (seit 14.10.2026, vorher 409): Antwort `wartet` mit der Kennung des Imports davor,
   der Arbeitsprozess startet mit `einreihen` (`Blendimportwarteschlange`).
3. Die Normalen-Grenze kommt aus dem Dialog (`normalen_grenze`): 35° säubert ein Texel mit 60° Kippung, 70° lässt es, `aus`
   ändert nichts. Fällt in eine Kachel mehr als `WARN_PROZENT`, steht eine Warnung in der Statuszeile.

4. `laufend` nennt den Import, der gerade rechnet (Leiste oben und Dialog nach dem Neuladen der Seite); ein Doppelklick auf
   „Importieren" startet genau einen Import — `_STARTSPERRE` hält Prüfung und Start zusammen (Fall 7, mit Gegenprobe Fall 8).

Sabotage-Gegenprobe: in `laufender` die Prüfung `stand().get('status') == 'laeuft'` entfernen → `SperreTest.test_2` rot;
`kennung != ausser` entfernen → `test_3` rot; in `_hinter` `return None` statt der Kennung → `test_4` rot; in `_saeubern`
`grad` nicht durchreichen → `NormalenGrenzeTest.test_1` rot; die Schwelle in `_warnen` entfernen → `test_2` rot.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

import contextlib
import json
import threading
import time
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

    def _import(self, kennung, status, lebt, quelle=None):
        stand = {'kennung': kennung, 'status': status, 'schritt': 'haut'}
        if quelle:
            stand['quelle'] = quelle
        Blendimportablage(kennung).stand_schreiben(stand)
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

    def test_4_starten_und_neu_reihen_ein_statt_409(self):
        """Seit 14.10.2026 (Edgar: „keine Gaga-Meldung, sondern eine normale Meldung, dass der Job in eine Queue eingereiht wird"): ein zweiter Start wird EINGEREIHT — Antwort 200 mit `wartet`,
        der Arbeitsprozess startet mit `einreihen`, hinter dem Import, der rechnet. Kein 409."""
        self._import('2026.10.08.12.00.00', 'laeuft', lebt=True)
        # Mit Netz: ohne `quelle.datei` lehnt `neu` seither mit 400 ab (die Kopie ohne Daten bringt keines mit).
        self._import('2026.10.08.09.00.00', 'fertig', lebt=False, quelle={'datei': 'figur.blend'})
        anfrage = RequestFactory().post('/api/character/blendimport/starten/', data=json.dumps({'werte': {}}),
                                        content_type='application/json')
        werte = {'pfad': 'x', 'name': 'ordner', 'eigener_name': ''}
        stand = mock.patch.multiple(
            'core.api.blendimport', Blendimportquelle=mock.Mock(return_value=mock.Mock(steckbrief=lambda: {'name': 'X'})),
            Blendimporteinstellungen=mock.Mock(pruefen=lambda w: werte, speichern=lambda w: w))
        with stand, mock.patch.object(Blendimportarbeiter, 'starten', return_value=4711) as starten:
            antwort = Blendimportendpunkte.starten(anfrage)
            neu = Blendimportendpunkte.neu(RequestFactory().post('/x/', data='{}', content_type='application/json'), '2026.10.08.09.00.00')
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertTrue(daten['wartet'])
        self.assertEqual(daten['hinter'], '2026.10.08.12.00.00')
        self.assertEqual(neu.status_code, 200)
        self.assertTrue(json.loads(neu.content)['wartet'])
        self.assertEqual(starten.call_count, 2)
        for aufruf in starten.call_args_list:
            self.assertTrue(aufruf.kwargs['einreihen'])
            self.assertEqual(aufruf.kwargs['hinter'], '2026.10.08.12.00.00')

    def test_5_ist_nichts_belegt_reiht_nichts_ein(self):
        self.assertIsNone(Blendimportendpunkte._hinter())

    def test_6_laufend_nennt_den_import_der_gerade_rechnet(self):
        """Leiste und Dialog fragen es nach dem Neuladen der Seite."""
        leer = json.loads(Blendimportendpunkte.laufend(RequestFactory().get('/x/')).content)
        self.assertEqual(leer, {'kennung': None})
        Blendimportablage('2026.10.08.12.00.00').stand_schreiben({'kennung': '2026.10.08.12.00.00', 'status': 'laeuft', 'schritt': 'haut',
                                                                  'quelle': {'name': 'cute girl'}})
        self.lebende.add('2026.10.08.12.00.00')
        antwort = json.loads(Blendimportendpunkte.laufend(RequestFactory().get('/x/')).content)
        self.assertEqual((antwort['kennung'], antwort['status'], antwort['schritt'], antwort['name']),
                         ('2026.10.08.12.00.00', 'laeuft', 'haut', 'cute girl'))

    def _doppelklick(self, sperre=None):
        """Zwei `starten`-Anfragen gleichzeitig (Doppelklick); der Arbeitsprozess braucht eine Weile, bis sein Stand „läuft" sagt."""
        gestartet, antworten = [], []

        def langsam_starten(ablage, ab=None, einreihen=False, hinter=None):
            time.sleep(0.4)
            gestartet.append((ablage.kennung, einreihen))
            Blendimportablage(ablage.kennung).stand_schreiben({'kennung': ablage.kennung, 'status': 'laeuft', 'schritt': 'export'})
            self.lebende.add(ablage.kennung)
            return 4711

        def klick():
            anfrage = RequestFactory().post('/x/', data=json.dumps({'werte': {}}), content_type='application/json')
            antworten.append(json.loads(Blendimportendpunkte.starten(anfrage).content)['wartet'])

        werte = {'pfad': 'x', 'name': 'ordner', 'eigener_name': ''}
        stand = mock.patch.multiple(
            'core.api.blendimport', Blendimportquelle=mock.Mock(return_value=mock.Mock(steckbrief=lambda: {'name': 'X'})),
            Blendimporteinstellungen=mock.Mock(pruefen=lambda w: werte, speichern=lambda w: w))
        with stand, mock.patch.object(Blendimportarbeiter, 'starten', side_effect=langsam_starten):
            with mock.patch.object(Blendimportendpunkte, '_STARTSPERRE', sperre or Blendimportendpunkte._STARTSPERRE):
                faeden = [threading.Thread(target=klick) for _ in range(2)]
                for faden in faeden:
                    faden.start()
                    time.sleep(0.05)
                for faden in faeden:
                    faden.join()
        return gestartet, sorted(antworten)

    def test_7_ein_doppelklick_rechnet_einen_import_und_reiht_den_zweiten_ein(self):
        gestartet, antworten = self._doppelklick()
        self.assertEqual(len(gestartet), 2)
        self.assertEqual(sorted(e for _, e in gestartet), [False, True], 'der erste rechnet, der zweite wartet')
        self.assertEqual(antworten, [False, True])

    def test_8_gegenprobe_ohne_die_sperre_rechnen_beide(self):
        """Beweist, dass Fall 7 die Sperre sieht: ohne sie sieht der zweite den ersten nicht und beide würden sofort rechnen."""
        gestartet, antworten = self._doppelklick(sperre=contextlib.nullcontext())
        self.assertEqual(len(gestartet), 2)
        self.assertEqual([e for _, e in gestartet], [False, False])
        self.assertEqual(antworten, [False, False])


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
        streng, anteil_streng = self._haut('35').nach.saeubern(karte, None)
        locker, anteil_locker = self._haut('70').nach.saeubern(karte, None)
        aus, anteil_aus = self._haut('aus').nach.saeubern(karte, None)
        vorgabe, _ = self._haut(None).nach.saeubern(karte, None)
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
        haut.nach.normalen_flach = {'1002': 1.2, '1004': Blendimportnormalen.WARN_PROZENT + 0.5}
        haut.nach.warnen(1002)
        self.assertEqual(meldungen, [], 'unter der Schwelle bleibt es still')
        haut.nach.warnen(1004)
        self.assertEqual(len(meldungen), 1)
        self.assertIn('Kachel 1004', meldungen[0])
        self.assertIn('Grenze', meldungen[0])

    def test_3_der_dialog_kennt_die_wahl_und_prueft_sie(self):
        self.assertEqual(Blendimporteinstellungen.pruefen({})['normalen_grenze'], '50')
        self.assertEqual(Blendimporteinstellungen.pruefen({'normalen_grenze': 'aus'})['normalen_grenze'], 'aus')
        self.assertEqual(Blendimporteinstellungen.pruefen({'normalen_grenze': '999'})['normalen_grenze'], '50')
