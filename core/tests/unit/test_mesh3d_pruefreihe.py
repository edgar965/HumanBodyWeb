# -*- coding: utf-8 -*-
"""Die Prüfreihe der Testaufträge von Mesh-3D (13.10.2026, `Mesh3dpruefreihe`, `Mesh3dmesswerte`) — Edgar: „Testcases, die checken, dass an den Jobs im ‚Test‘-Bereich nichts kaputt geht". Nicht gelaufen — läuft nur auf Ansage.

    RegelnTest      jede Regel (max/min/nahe/gleich) an Grenzfällen; `None` im Ist („nicht gemessen“) besteht nie; Werte ohne Regel werden nicht bewertet
    InvariantenTest die Regeln OHNE Soll (`INVARIANTEN`): ein neues Modell im Test-Reiter wird geprüft; „nicht gemessen“ ist dort „offen“, kein Fehler; die Animationswahl ist die mit den wenigsten Spitzen
    SollTest        `aufnehmen` und `laden` über eine Datei (umgebogen); die Datei im Repository: jeder Eintrag nennt nur bekannte Werte, jeder Testauftrag mit Soll hat Name und Datum
    HandTest        die Hand-Messung an Kunstdaten: starr verschobene Hand → Verformung 0; aufgerissene Hand → groß; Handpunkte mit Untergrenze werden gezählt (`hand_untergrenze`)
    WaechterTest    Quelltext: die Mindestluft gilt nicht an Händen (`_luft_je_punkt`), der Befehl `mesh3d_pruefreihe` gibt es, `kleidungsluft_mm` und `hautband` stehen im Katalog

Sabotage: in `einhalten` bei `max` `+ absolut` streichen → `test_max_toleranz_grenzfall` rot; in `Mesh3dmesswerte._hand` `mindest` ignorieren (`untergrenze = 0`) → `test_untergrenze_an_der_hand_wird_gezaehlt` rot;
in `_luft_je_punkt` den Handtest streichen → `WaechterTest.test_die_mindestluft_gilt_nicht_an_haenden` rot.
"""

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.mesh3dmesswerte import Mesh3dmesswerte
from core.dienste.mesh3dpruefreihe import Mesh3dpruefreihe as P

from ._pruefablage import Pruefablage

WEB = Path(__file__).resolve().parents[3]


class RegelnTest(SimpleTestCase):
    def test_max_toleranz_grenzfall(self):
        # figur_netz_mm: max, 25 % + 0,4 mm → Soll 2,0 darf bis 2,9 steigen
        self.assertTrue(P.einhalten('figur_netz_mm', 2.9, 2.0))
        self.assertFalse(P.einhalten('figur_netz_mm', 2.91, 2.0))
        self.assertTrue(P.einhalten('figur_netz_mm', 1.0, 2.0), 'besser ist immer in Ordnung')

    def test_unterkante_darf_hoechstens_sechs_millimeter_steigen(self):
        self.assertTrue(P.einhalten('kleidung_unterkante_m', 0.882, 0.876))
        self.assertFalse(P.einhalten('kleidung_unterkante_m', 0.883, 0.876))

    def test_nahe_und_gleich(self):
        self.assertTrue(P.einhalten('kleidung_flaechen', 100_000 * 1.08, 100_000))
        self.assertFalse(P.einhalten('kleidung_flaechen', 100_000 * 1.09, 100_000))
        self.assertTrue(P.einhalten('teile', ['bag', 'hat'], ['bag', 'hat']))
        self.assertFalse(P.einhalten('teile', ['hat'], ['bag', 'hat']))
        self.assertTrue(P.einhalten('hautband_art', 'umfaerben', 'umfaerben'))

    def test_hand_untergrenze_muss_null_sein(self):
        self.assertTrue(P.einhalten('hand_untergrenze', 0, 0))
        self.assertFalse(P.einhalten('hand_untergrenze', 1, 0))

    def test_nicht_gemessen_besteht_nie(self):
        zeilen = P.bewerten({'hoehe_cm': None}, {'hoehe_cm': 199.7})
        self.assertEqual([(z[0], z[3], z[4]) for z in zeilen], [('hoehe_cm', False, 'nicht gemessen')])

    def test_werte_ohne_regel_werden_nicht_bewertet(self):
        self.assertEqual(P.bewerten({'unbekannt': 1}, {'unbekannt': 1}), [])

    def test_jede_regel_hat_eine_bekannte_art(self):
        for name, (art, rel, absolut) in P.REGELN.items():
            self.assertIn(art, ('max', 'min', 'nahe', 'gleich'), name)
            self.assertGreaterEqual(rel, 0)
            self.assertGreaterEqual(absolut, 0)


class InvariantenTest(SimpleTestCase):
    """Regeln ohne Soll: ein NEUES Modell im Test-Reiter wird geprüft, auch wenn noch niemand ein Soll aufgenommen hat."""

    GUT = {'status': 'fertig', 'fehler': [], 'hand_untergrenze': 0, 'abnahme_doppelt': 0, 'animation_wahl_beste': True}

    def test_ein_guter_lauf_besteht_alle(self):
        zeilen = P.invarianten(self.GUT)
        self.assertEqual({z[0] for z in zeilen}, set(P.INVARIANTEN))
        self.assertTrue(all(z[3] is True for z in zeilen))

    def test_jede_verletzung_wird_gemeldet(self):
        for name, schlecht in (('status', 'gescheitert'), ('fehler', ['haar']), ('hand_untergrenze', 3), ('abnahme_doppelt', 6614), ('animation_wahl_beste', False)):
            zeilen = {z[0]: z for z in P.invarianten({**self.GUT, name: schlecht})}
            self.assertIs(zeilen[name][3], False, name)
            self.assertTrue(zeilen[name][4], 'die Verletzung braucht einen Satz Erklärung: %s' % name)
            self.assertTrue(all(z[3] is True for n, z in zeilen.items() if n != name), 'nur %s ist verletzt' % name)

    def test_nicht_gemessen_ist_offen_und_kein_fehler(self):
        zeilen = {z[0]: z for z in P.invarianten({'status': 'fertig'})}
        self.assertIsNone(zeilen['hand_untergrenze'][3])
        self.assertEqual(zeilen['hand_untergrenze'][4], 'offen (nicht gemessen)')

    def test_was_im_soll_steht_wird_dort_bewertet(self):
        zeilen = P.invarianten(self.GUT, ausser={'status': 'fertig', 'fehler': []})
        self.assertNotIn('status', {z[0] for z in zeilen})
        self.assertNotIn('fehler', {z[0] for z in zeilen})

    def test_ein_auftrag_ohne_soll_faellt_durch(self):
        messung = {**self.GUT, 'hand_untergrenze': 308}
        with mock.patch.object(P, 'laden', return_value={}), mock.patch.object(Mesh3dmesswerte, '__init__', lambda s, k: None), \
                mock.patch.object(Mesh3dmesswerte, 'alle', lambda s: messung):
            zeilen, ok = P.pruefen('2026.10.99.00.00.00')
        self.assertFalse(ok)
        self.assertEqual([z[0] for z in zeilen if z[3] is False], ['hand_untergrenze'])

    def test_ein_auftrag_ohne_soll_besteht_mit_guten_werten(self):
        with mock.patch.object(P, 'laden', return_value={}), mock.patch.object(Mesh3dmesswerte, '__init__', lambda s, k: None), \
                mock.patch.object(Mesh3dmesswerte, 'alle', lambda s: dict(self.GUT)):
            self.assertTrue(P.pruefen('2026.10.99.00.00.00')[1])

    def test_die_animationswahl_ist_die_mit_den_wenigsten_spitzen(self):
        gut = {'kleidung': {'gewaehlt': 'weich_0.5', 'kandidaten': {'basis': {'spitzen': 0.003}, 'weich_0.5': {'spitzen': 0.0014}, 'weich_1': {'spitzen': 0.002}}}}
        self.assertIs(Mesh3dmesswerte.wahl_beste(gut), True)
        schlecht = {'kleidung': {'gewaehlt': 'basis', 'kandidaten': {'basis': {'spitzen': 0.003}, 'weich_0.5': {'spitzen': 0.0014}}}}
        self.assertIs(Mesh3dmesswerte.wahl_beste(schlecht), False)
        zweites = {**gut, 'hat': schlecht['kleidung']}
        self.assertIs(Mesh3dmesswerte.wahl_beste(zweites), False, 'JEDES Objekt zählt')
        rueckfall = {'kleidung': {'gewaehlt': 'basis', 'grund': 'zu wenige Bilder'}}
        self.assertIs(Mesh3dmesswerte.wahl_beste(rueckfall), True, 'ein Rückfall auf basis mit Grund ist kein Fehler')
        self.assertIsNone(Mesh3dmesswerte.wahl_beste({}))

    def test_die_angenommene_gewebe_regel_ist_die_wahl_und_die_verworfene_kein_kandidat(self):
        # Ballerina `…14.11.28.16`: weich_0.5 0,0007, die Gewebe-Regel darauf 0,0001 und angenommen → die Wahl ist gut (vorher meldete die Reihe „nicht die beste“)
        kandidaten = {'basis': {'spitzen': 0.0044}, 'weich_0.5': {'spitzen': 0.0007}, 'gewebe': {'spitzen': 0.0001}}
        angenommen = {'kleidung': {'gewaehlt': 'weich_0.5', 'kandidaten': kandidaten, 'gewebe': {'angewandt': True}}}
        self.assertIs(Mesh3dmesswerte.wahl_beste(angenommen), True)
        # verworfen (Zauberer: die Robe hinge an den Armen): `gewebe` steht trotzdem unter den Kandidaten, mit weniger Spitzen — es zählt nicht
        verworfen = {'kleidung': {'gewaehlt': 'weich_0.5', 'kandidaten': kandidaten, 'gewebe': {'angewandt': False}}}
        self.assertIs(Mesh3dmesswerte.wahl_beste(verworfen), True)
        # …und die Prüfung bleibt scharf: ist ein anderer der drei Kandidaten besser als die Wahl, fällt es auf, mit und ohne Gewebe
        schlecht = {'kleidung': {'gewaehlt': 'basis', 'kandidaten': kandidaten, 'gewebe': {'angewandt': False}}}
        self.assertIs(Mesh3dmesswerte.wahl_beste(schlecht), False)

    def test_soll_ohne_testauftrag_wird_gemeldet(self):
        # 14.10.2026: zwei von drei Soll-Aufträgen (Edgar, Zauberer) gab es nicht mehr; die Reihe prüfte sie nie und meldete „alles bestanden“
        soll = {'A': {'name': 'Ballerina', 'soll': {}}, 'B': {'name': 'Zauberer', 'soll': {}}, 'C': {}}
        with mock.patch.object(P, 'laden', return_value=soll):
            self.assertEqual(P.verwaist(['A']), [('B', 'Zauberer'), ('C', 'C')])
            self.assertEqual(P.verwaist(['A', 'B', 'C']), [])
            with mock.patch.object(P, 'testauftraege', return_value=['A', 'B']):
                self.assertEqual(P.verwaist(), [('C', 'C')])

    def test_ein_auftrag_ohne_lauf_ist_offen_und_kein_fehler(self):
        # „Test Wiederholen Schnitt“: angelegt, nie gestartet — die Reihe meldete „NICHT bestanden“, weil der Status nicht `fertig` war
        for stand in ('neu', 'laeuft'):
            zeilen = {z[0]: z for z in P.invarianten({'status': stand})}
            self.assertIsNone(zeilen['status'][3], stand)
            self.assertIn('offen', zeilen['status'][4])
        for stand in ('gescheitert', 'angehalten'):
            self.assertIs({z[0]: z for z in P.invarianten({'status': stand})}['status'][3], False, '%s bleibt ein Fehler' % stand)
        with mock.patch.object(P, 'laden', return_value={}), mock.patch.object(Mesh3dmesswerte, '__init__', lambda s, k: None), \
                mock.patch.object(Mesh3dmesswerte, 'alle', lambda s: {'status': 'neu'}):
            self.assertTrue(P.pruefen('2026.10.99.00.00.00')[1])


class KopierenTest(SimpleTestCase):
    """`--rechnen` rechnet eine KOPIE: ohne Daten, solange die Quelldatei da ist; sonst (Weg „netz“) mit Daten ab der Segmentierung — beim ersten Lauf (14.10.2026) scheiterte der Zauberer an „Die Datei … gibt es nicht mehr“."""

    def _kopierer(self, datei, weg, mit_koerper):
        aufrufe = []

        class Falsch:
            def __init__(self, kennung):
                self.stand = {'quelle': {'datei': datei}, 'weg': weg}
                self.quelle = SimpleNamespace(arbeit=lambda name: SimpleNamespace(is_file=lambda: mit_koerper))

            def ohne_ergebnis(self):
                aufrufe.append('ohne')
                if not (datei and Path(datei).exists()):
                    raise ValueError('Die Datei gibt es nicht mehr')
                return 'K-ohne'

            def mit_daten(self):
                aufrufe.append('mit')
                return 'K-mit'

        return Falsch, aufrufe

    def _lauf(self, datei, weg, mit_koerper):
        falsch, aufrufe = self._kopierer(datei, weg, mit_koerper)
        with mock.patch('core.dienste.mesh3dkopie.Mesh3dkopie', falsch):
            try:
                return P.kopieren('2026.10.99.00.00.00'), aufrufe
            except ValueError as fehler:
                return str(fehler), aufrufe

    def test_mit_quelldatei_ohne_daten_und_von_vorn(self):
        ergebnis, aufrufe = self._lauf(__file__, 'netz', True)
        self.assertEqual(ergebnis, ('K-ohne', None))
        self.assertEqual(aufrufe, ['ohne'])

    def test_ohne_quelldatei_beim_weg_netz_mit_daten_ab_der_segmentierung(self):
        ergebnis, aufrufe = self._lauf(r'A:\gibt\es\nicht.glb', 'netz', True)
        self.assertEqual(ergebnis, ('K-mit', 'segmentierung'))
        self.assertEqual(aufrufe, ['mit'])

    def test_ohne_quelldatei_beim_weg_teile_bleibt_der_fehler(self):
        ergebnis, _ = self._lauf(r'A:\gibt\es\nicht.blend', 'teile', True)
        self.assertEqual(ergebnis, 'Die Datei gibt es nicht mehr')

    def test_ohne_quelldatei_und_ohne_koerper_bleibt_der_fehler(self):
        ergebnis, _ = self._lauf(r'A:\gibt\es\nicht.glb', 'netz', False)
        self.assertEqual(ergebnis, 'Die Datei gibt es nicht mehr')


class SollTest(SimpleTestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='pruefreihe_', dir=Pruefablage.wurzel()))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.datei = mock.patch.object(P, 'DATEI', self.tmp / 'soll.json')
        self.datei.start()
        self.addCleanup(self.datei.stop)

    def test_aufnehmen_und_laden(self):
        messung = {'status': 'fertig', 'hoehe_cm': 199.7, 'hand_untergrenze': 0, 'figur_auftrag': 'x', 'unbekannt': 5, 'haar_flaechen': None}
        with mock.patch.object(Mesh3dmesswerte, '__init__', lambda s, k: setattr(s, 'stand', {'quelle': {'name': 'Edgar'}})), \
                mock.patch.object(Mesh3dmesswerte, 'alle', lambda s: messung):
            zahl = P.aufnehmen(['2026.10.11.21.18.17'], 'Stand gesehen und gut')
        self.assertEqual(zahl, {'2026.10.11.21.18.17': 3})
        geladen = P.laden()['2026.10.11.21.18.17']
        self.assertEqual(geladen['name'], 'Edgar')
        self.assertEqual(geladen['soll'], {'status': 'fertig', 'hoehe_cm': 199.7, 'hand_untergrenze': 0})
        self.assertEqual(geladen['hinweis'], 'Stand gesehen und gut')

    def test_aufnehmen_nimmt_den_schlechtesten_wert_mehrerer_laeufe(self):
        # Die Läufe streuen bei gleichen Eingaben (Ballerina Figur→Netz 3,68 gegen 5,76 mm): bei max-Regeln gilt der größte, bei min-Regeln der kleinste Wert, sonst der des Auftrags selbst
        werte = {'orig': {'status': 'fertig', 'figur_netz_mm': 3.68, 'kleidung_flaechen': 30190, 'hoehe_cm': 193.4},
                 'kopie': {'status': 'gescheitert', 'figur_netz_mm': 5.76, 'kleidung_flaechen': 31000, 'hoehe_cm': 190.0},
                 'kopie2': {'status': 'fertig', 'figur_netz_mm': 4.1}}
        with mock.patch.object(Mesh3dmesswerte, '__init__', lambda s, k: setattr(s, 'kennung', k) or setattr(s, 'stand', {'quelle': {'name': 'Ballerina'}})), \
                mock.patch.object(Mesh3dmesswerte, 'alle', lambda s: werte[s.kennung]):
            P.aufnehmen(['orig'], 'schlechtester Lauf', auch=['kopie', 'kopie2'])
        soll = P.laden()['orig']['soll']
        self.assertEqual(soll['figur_netz_mm'], 5.76, 'max: der größte')
        self.assertEqual(soll['status'], 'fertig', 'gleich: der Wert des Auftrags selbst, nicht der der Kopie')
        self.assertEqual(soll['kleidung_flaechen'], 30190, 'nahe: der Wert des Auftrags selbst')
        self.assertEqual(soll['hoehe_cm'], 193.4)

    def test_fehlende_datei_gibt_nichts(self):
        self.assertEqual(P.laden(), {})

    def test_die_datei_im_repository_nennt_nur_bekannte_werte(self):
        pfad = WEB / 'core' / 'daten' / 'mesh3dpruefreihe.json'
        if not pfad.is_file():
            self.skipTest('noch kein Soll aufgenommen')
        daten = json.loads(pfad.read_text(encoding='utf-8'))['auftraege']
        for kennung, eintrag in daten.items():
            self.assertTrue(eintrag.get('name') and eintrag.get('aufgenommen'), kennung)
            for name in eintrag['soll']:
                self.assertIn(name, P.REGELN, '%s: %s hat keine Regel' % (kennung, name))


class HandTest(SimpleTestCase):
    def _messen(self, rest, mindest, teil):
        tmp = Path(tempfile.mkdtemp(prefix='handmessung_', dir=Pruefablage.wurzel()))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        np.savez(tmp / 'rest.npz', rest=rest, gewicht=np.zeros(len(rest)), mindest=mindest)
        np.savez(tmp / 'genesis_ende.npz', teil=teil)
        m = Mesh3dmesswerte.__new__(Mesh3dmesswerte)
        m.ordner = SimpleNamespace(arbeit=lambda name: tmp / name)
        return m._hand()

    def _hand(self):
        teil = np.array([7] * 50 + [11] * 50 + [2] * 10)
        return teil, np.zeros((110, 3)), np.zeros((110, 3))

    def test_starr_verschobene_hand_ist_nicht_verformt(self):
        teil, rest, mindest = self._hand()
        rest[teil == 7] = [0.02, 0.0, 0.0]
        rest[teil == 11] = [0.0, 0.03, 0.0]
        w = self._messen(rest, mindest, teil)
        self.assertAlmostEqual(w['hand_verformung_mm'], 0.0, places=3)
        self.assertEqual(w['hand_untergrenze'], 0)

    def test_aufgerissene_hand_wird_gross(self):
        teil, rest, mindest = self._hand()
        rest[np.flatnonzero(teil == 7)[:10]] = [0.03, 0.0, 0.0]
        w = self._messen(rest, mindest, teil)
        self.assertGreater(w['hand_verformung_mm'], 8.0)

    def test_untergrenze_an_der_hand_wird_gezaehlt(self):
        teil, rest, mindest = self._hand()
        mindest[np.flatnonzero(teil == 11)[:7]] = [0.0, 0.004, 0.0]
        mindest[100:] = [0.0, 0.004, 0.0]          # der Rumpf zählt nicht
        w = self._messen(rest, mindest, teil)
        self.assertEqual(w['hand_untergrenze'], 7)


class WaechterTest(SimpleTestCase):
    def _text(self, *teile):
        return WEB.parent.joinpath(*teile).read_text(encoding='utf-8') if teile[0] == 'meshto3d' else WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_die_mindestluft_gilt_nicht_an_haenden(self):
        text = self._text('meshto3d', 'meshfigur_registrierungruhe.py')
        self.assertIn('def _luft_je_punkt', text)
        self.assertIn('(self.abstand.FINGER, self.abstand.HAND)', text)
        self.assertGreaterEqual(text.count('self._luft_je_punkt()'), 2, 'ruhe_rest UND _nachschub')
        # Luft 0 allein ließ eine Untergrenze (Weg bis zur Fläche) an der Hand stehen: beide Stellen verlangen `luft > 0`
        self.assertGreaterEqual(text.count('& (luft > 0)'), 2, 'ragt in ruhe_rest UND neu in _nachschub')

    def test_haar_ist_nicht_kleidung_und_wird_nach_dem_bereinigen_abgezogen(self):
        text = self._text('core', 'dienste', 'meshfigurkleidung.py')
        self.assertIn('Meshfigurhaarabzug.abziehen(self.ablage, maske, regel)', text)
        # nach dem Bereinigen: das Füllen von Löchern und das Glätten des Rands holten Haarflächen sonst zurück in den Stoff
        self.assertLess(text.index('self._bereinigen(maske, regel,'), text.index('Meshfigurhaarabzug.abziehen(self.ablage, maske, regel)'))
        self.assertIn('haar & (stueck > 0) & (stueck != cls.ZUBEHOER)', self._text('core', 'dienste', 'meshfigurhaarabzug.py'))

    def test_befehl_und_optionen_gibt_es(self):
        self.assertTrue((WEB / 'core' / 'management' / 'commands' / 'mesh3d_pruefreihe.py').is_file())
        katalog = self._text('core', 'dienste', 'meshfigurkleidungsoptionen.py')
        self.assertIn("'schluessel': 'hautband'", katalog)
        self.assertIn("'schluessel': 'kleidungsluft_mm'", katalog)

    def test_animationspruefung_ist_eine_option_beider_kataloge_mit_vorgabe_an(self):
        self.assertIn("'schluessel': 'animationspruefung'", self._text('core', 'dienste', 'meshfiguranimationsoptionen.py'))
        self.assertIn("'schluessel': 'animationspruefung'", self._text('core', 'dienste', 'blendimporteinstellungen.py'))
        self.assertIn('Meshfiguranimationsoptionen.KATALOG', self._text('core', 'dienste', 'meshfiguroptionen.py'))
