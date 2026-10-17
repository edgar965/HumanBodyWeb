# -*- coding: utf-8 -*-
"""Blender-Import: ein zweiter Import wartet in der Schlange (14.10.2026, Edgar: „eine normale Meldung, dass der Job in eine Queue eingereiht wird").

1. `rechnender` nennt nur Importe, die rechnen (Prozess lebt, Stand „läuft", nicht `wartet`) — ein Wartender hält sich nicht selbst auf.
2. `wartende` ordnet nach der Zeit des Einreihens; ein toter Wartender zählt nicht.
3. `hinter` nennt den, der den neuen Import aufhält: den rechnenden, sonst den letzten Wartenden.
4. `einreihen` setzt `wartet`, den Schritt „warteschlange" und einen Text, der den Namen des Imports davor nennt.
5. `abwarten` im Arbeitsprozess: rechnet erst, wenn niemand rechnet und der Import der erste Wartende ist (liefert dann True und nimmt `wartet` zurück); ist er angehalten, liefert es False.

Sabotage-Gegenprobe: in `rechnender` die Prüfung `not stand.get('wartet')` entfernen → `test_1` rot; in `wartende` die Sortierung entfernen → `test_2` rot; in `abwarten` die Prüfung `wartende()[:1] == [kennung]`
entfernen → `test_5` rot.

Nicht gelaufen — läuft nur auf Ansage.
"""

from unittest import mock

from django.test import SimpleTestCase, override_settings

from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportarbeiter import Blendimportarbeiter
from core.dienste.blendimportwarteschlange import Blendimportwarteschlange
from core.tests.unit._pruefablage import Pruefablage


class WarteschlangeTest(SimpleTestCase):
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
        takt = mock.patch.object(Blendimportwarteschlange, 'TAKT_S', 0.01)
        takt.start()
        self.addCleanup(takt.stop)

    def _import(self, kennung, status='laeuft', lebt=True, wartet=False, eingereiht='', name=None):
        stand = {'kennung': kennung, 'status': status, 'schritt': 'haut', 'quelle': {'name': name or kennung}}
        if wartet:
            stand.update(wartet=True, eingereiht=eingereiht, schritt='warteschlange')
        Blendimportablage(kennung).stand_schreiben(stand)
        if lebt:
            self.lebende.add(kennung)
        return Blendimportablage(kennung)

    def test_1_ein_wartender_zaehlt_nicht_als_rechnend(self):
        self._import('2026.10.14.10.00.00', wartet=True, eingereiht='2026-10-14T10:00:00')
        self.assertIsNone(Blendimportwarteschlange.rechnender())
        self._import('2026.10.14.09.00.00')
        self.assertEqual(Blendimportwarteschlange.rechnender(), '2026.10.14.09.00.00')
        self.assertIsNone(Blendimportwarteschlange.rechnender(ausser='2026.10.14.09.00.00'))

    def test_2_wartende_nach_der_zeit_des_einreihens_ohne_tote(self):
        self._import('2026.10.14.10.00.00', wartet=True, eingereiht='2026-10-14T10:05:00')
        self._import('2026.10.14.11.00.00', wartet=True, eingereiht='2026-10-14T10:01:00')
        self._import('2026.10.14.12.00.00', wartet=True, eingereiht='2026-10-14T10:00:00', lebt=False)
        self.assertEqual(Blendimportwarteschlange.wartende(), ['2026.10.14.11.00.00', '2026.10.14.10.00.00'])

    def test_3_hinter_nennt_den_rechnenden_sonst_den_letzten_wartenden(self):
        self.assertIsNone(Blendimportwarteschlange.hinter())
        self._import('2026.10.14.10.00.00', wartet=True, eingereiht='2026-10-14T10:05:00')
        self.assertEqual(Blendimportwarteschlange.hinter(), '2026.10.14.10.00.00')
        self._import('2026.10.14.09.00.00')
        self.assertEqual(Blendimportwarteschlange.hinter(), '2026.10.14.09.00.00')

    def test_4_einreihen_setzt_stand_und_nennt_den_import_davor(self):
        self._import('2026.10.14.09.00.00', name='cute girl')
        ablage = self._import('2026.10.14.10.00.00', status='neu', lebt=False)
        text = Blendimportwarteschlange.einreihen(ablage, '2026.10.14.09.00.00')
        stand = ablage.stand()
        self.assertTrue(stand['wartet'])
        self.assertEqual(stand['schritt'], 'warteschlange')
        self.assertIn('cute girl', text)
        self.assertEqual(stand['detail'], text)
        self.assertTrue(stand['eingereiht'])

    def test_5_abwarten_rechnet_erst_wenn_niemand_rechnet_und_er_der_erste_ist(self):
        vorne = self._import('2026.10.14.09.00.00')
        erster = self._import('2026.10.14.10.00.00', wartet=True, eingereiht='2026-10-14T10:00:00')
        zweiter = self._import('2026.10.14.11.00.00', wartet=True, eingereiht='2026-10-14T10:05:00')
        schlaf = []

        def schlafen(sekunden):
            schlaf.append(sekunden)
            if len(schlaf) == 2:                                 # der Import davor ist fertig
                self.lebende.discard('2026.10.14.09.00.00')
                vorne.stand_schreiben({**vorne.stand(), 'status': 'fertig'})
            if len(schlaf) == 5:                                 # der erste Wartende rechnet (jetzt „läuft" er ohne `wartet`)
                self.assertFalse(erster.stand().get('wartet'))
                erster.stand_schreiben({**erster.stand(), 'status': 'fertig'})
                self.lebende.discard('2026.10.14.10.00.00')

        with mock.patch('core.dienste.blendimportwarteschlange.time.sleep', side_effect=schlafen):
            self.assertTrue(Blendimportwarteschlange.abwarten(erster), 'der erste Wartende kommt an die Reihe, sobald niemand mehr rechnet')
            self.assertFalse(erster.stand()['wartet'])
            self.assertTrue(Blendimportwarteschlange.abwarten(zweiter), 'danach der zweite, wenn der erste fertig ist')

    def test_6_ein_angehaltener_wartender_rechnet_nicht(self):
        self._import('2026.10.14.09.00.00')
        ablage = self._import('2026.10.14.10.00.00', wartet=True, eingereiht='2026-10-14T10:00:00')
        stand = ablage.stand()
        stand.update(status='angehalten', wartet=False)
        ablage.stand_schreiben(stand)
        self.assertFalse(Blendimportwarteschlange.abwarten(ablage))
