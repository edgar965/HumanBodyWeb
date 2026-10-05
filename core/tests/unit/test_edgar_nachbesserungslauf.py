# -*- coding: utf-8 -*-
"""Paket `Edgar`: Nachbesserungslauf, Zustand, Prozess und Agentenaufruf mit Attrappen (05.10.2026).

Attrappe statt Server (`_Klient`: Zustände nacheinander, Antworten auf „Runde bestellen") und statt Claude (`_Agent`: fertige Antworten). Kein Netz, kein Prozess, keine Wartezeit
(`Rundenlauf.TAKT_S` und `GPU_TAKT_S` stehen auf 0). Die Dateien liegen in einem Ordner unter `ProjektTemp`. Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Edgar.agentenaufruf import Agentenaufruf
from Edgar.auftragsfehler import Auftragsfehler
from Edgar.nachbesserungslauf import Nachbesserungslauf
from Edgar.nachbesserungsprozess import Nachbesserungsprozess
from Edgar.nachbesserungszustand import Nachbesserungszustand
from Edgar.rundenlauf import Rundenlauf

PROJEKTTEMP = Path(__file__).resolve().parents[3] / 'ProjektTemp'
ANTWORT = {'urteil': 'Hut zu flach.', 'kommentar': 'Hut höher.', 'fertig': False, 'aufrufe': ["m.kleid_anteil('hut', 1.0)", "m.kleid_aus('x')"],
           'abweichungen': [{'teil': 'Hut', 'vorlage': 'hoch', 'render': 'flach', 'schwere': 1, 'massnahme': 'Krone'}]}


def _zustand(nummer, laeuft=False):
    runden = [{'runde': n, 'note': {'gesamt': 1.0 - 0.1 * n}, 'uebernommen': True, 'dateien': {}, 'je_ansicht': []} for n in range(1, nummer + 1)]
    return {'name': 'T', 'kennung': 'k', 'laeuft': laeuft, 'status': 'laeuft' if laeuft else 'wartet', 'bilder': [], 'ergebnis': {'iterationen': runden, 'begutachtung': {'rezept': []}}}


class _Klient:
    def __init__(self, zustaende, antworten=((200, {'pid': 1}),)):
        self.zustaende, self.antworten, self.gesendet = list(zustaende), list(antworten), []

    def zustand(self):
        return self.zustaende.pop(0) if len(self.zustaende) > 1 else self.zustaende[0]

    def funktionen(self, voll=True):
        return {'objekt': 'm', 'funktionen': []}

    def katalog(self):
        return {'auftrag': {'fotostuecke': {'hose': 'eigen_foto_x_hose'}, 'hemd': 'g9_base_shirt', 'startfrisur': 'mavick_hair', 'kandidaten': ['mavick_hair'], 'frisur': {}},
                'startrezept': ["m.kleid_nur('g9_base_shirt', 'eigen_foto_x_hose')", "m.haar_nur('mavick_hair')"],
                'garderobe': {'kleidung': ['g9_base_shirt'], 'haar': ['mavick_hair'], 'eigene': [], 'requisiten': []}, 'regler': {}, 'koerper': {}, 'schnitt': {}, 'fehler': []}

    def begutachten(self, aufrufe, kommentar, nutzer=None):
        self.gesendet.append((aufrufe, kommentar))
        return self.antworten.pop(0) if len(self.antworten) > 1 else self.antworten[0]


class _Agent:
    def __init__(self, *antworten):
        self.antworten, self.prompts = list(antworten), []

    def fragen(self, prompt, schema=None, abbrechen=None, bilder=()):
        self.prompts.append(prompt)
        antwort = self.antworten.pop(0) if len(self.antworten) > 1 else self.antworten[0]
        return {'antwort': antwort, 'dauer_s': 2.0, 'kosten_usd': 0.1, 'zuege': 3, 'modell': 'attrappe'}


class DerNachbesserungslauf(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='edgar_lauf_', dir=str(PROJEKTTEMP)))
        for halter in (mock.patch.object(Rundenlauf, 'TAKT_S', 0), mock.patch.object(Rundenlauf, 'GPU_TAKT_S', 0)):
            halter.start()
            self.addCleanup(halter.stop)

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _lauf(self, klient, agent, runden=1):
        return Nachbesserungslauf(klient, self.ordner, runden, agent=agent)

    def test_eine_iteration_vom_prompt_bis_zur_neuen_runde(self):
        klient, agent = _Klient([_zustand(1), _zustand(2)]), _Agent(ANTWORT)
        lauf = self._lauf(klient, agent)
        self.assertEqual(lauf.ausfuehren(), 'fertig')
        zustand = lauf.zustand.lesen()
        self.assertEqual((zustand['status'], zustand['pid'], len(zustand['eintraege'])), ('fertig', None, 1))
        eintrag = zustand['eintraege'][0]
        self.assertEqual((eintrag['runde'], eintrag['uebernommen'], eintrag['offen']), (2, True, 1))
        self.assertAlmostEqual(eintrag['kosten_usd'], 0.1)
        self.assertEqual(klient.gesendet, [("m.kleid_anteil('hut', 1.0)\nm.kleid_aus('x')", 'Hut höher.')])
        self.assertTrue(lauf.zustand.datei_der_runde(2, 'prompt', 'md').is_file())
        self.assertEqual(json.loads(lauf.zustand.datei_der_runde(2, 'antwort', 'json').read_text(encoding='utf-8'))['antwort']['kommentar'], 'Hut höher.')

    def test_ein_abgelehntes_rezept_geht_einmal_mit_der_meldung_zurueck_an_den_agenten(self):
        klient = _Klient([_zustand(1), _zustand(2)], [(400, {'error': 'Rezept: unbekannter Aufruf kleid_anteil'}), (200, {'pid': 1})])
        agent = _Agent(ANTWORT)
        self.assertEqual(self._lauf(klient, agent).ausfuehren(), 'fertig')
        self.assertEqual(len(agent.prompts), 2)
        self.assertIn('unbekannter Aufruf kleid_anteil', agent.prompts[1])
        self.assertNotIn('abgelehnt', agent.prompts[0])

    def test_zweimal_abgelehnt_endet_mit_fehler_und_ohne_dritten_versuch(self):
        klient = _Klient([_zustand(1)], [(400, {'error': 'Rezept: kaputt'})])
        agent = _Agent(ANTWORT)
        lauf = self._lauf(klient, agent)
        self.assertEqual(lauf.ausfuehren(), 'fehler')
        self.assertEqual(len(agent.prompts), 2)
        self.assertIn('kaputt', lauf.zustand.lesen()['meldung'])

    def test_eine_nicht_verwertbare_antwort_wird_einmal_repariert(self):
        agent = _Agent('Das kann ich nicht.', ANTWORT)
        klient = _Klient([_zustand(1), _zustand(2)])
        self.assertEqual(self._lauf(klient, agent).ausfuehren(), 'fertig')
        self.assertIn('nicht verwertbar', agent.prompts[1])

    def test_schreibt_der_agent_kein_rezept_endet_der_lauf_ohne_runde(self):
        klient, agent = _Klient([_zustand(1)]), _Agent(dict(ANTWORT, aufrufe=[], fertig=True))
        lauf = self._lauf(klient, agent, runden=3)
        self.assertEqual(lauf.ausfuehren(), 'fertig')
        zustand = lauf.zustand.lesen()
        self.assertEqual(klient.gesendet, [])
        self.assertIn('kein weiteres Rezept', zustand['meldung'])
        self.assertTrue(zustand['eintraege'][0]['ergebnis'].startswith('kein Rezept'))

    def test_ist_die_grafikkarte_belegt_wird_neu_versucht(self):
        klient = _Klient([_zustand(1), _zustand(2)], [(409, {'error': 'Grafikkarte belegt'}), (200, {'pid': 1})])
        self.assertEqual(self._lauf(klient, _Agent(ANTWORT)).ausfuehren(), 'fertig')
        self.assertEqual(len(klient.gesendet), 2)

    def test_ein_rechnender_auftrag_ist_ein_fehler(self):
        lauf = self._lauf(_Klient([_zustand(1, laeuft=True)]), _Agent(ANTWORT))
        self.assertEqual(lauf.ausfuehren(), 'fehler')
        self.assertIn('rechnet', lauf.zustand.lesen()['meldung'])

    def test_ohne_runde_wird_genau_eine_runde_bestellt_und_das_startrezept_geht_voran(self):
        klient, agent = _Klient([_zustand(0), _zustand(1)]), _Agent(ANTWORT)
        lauf = self._lauf(klient, agent)
        self.assertEqual(lauf.ausfuehren(), 'fertig')
        self.assertEqual(len(klient.gesendet), 1)                                           # keine Ausgangsrunde (Edgar: genau EINE Iteration)
        zeilen = klient.gesendet[0][0].splitlines()
        self.assertEqual(zeilen[:2], ["m.kleid_nur('g9_base_shirt', 'eigen_foto_x_hose')", "m.haar_nur('mavick_hair')"])
        self.assertEqual(zeilen[2:], ANTWORT['aufrufe'])                                     # danach die Zeilen der KI
        self.assertEqual(len(agent.prompts), 1)
        self.assertIn('Es gibt noch KEINE Runde', agent.prompts[0])
        self.assertIn('Ausgangslage — Startrezept', agent.prompts[0])
        self.assertEqual(len(lauf.zustand.lesen()['eintraege']), 1)

    def test_der_prompt_hat_den_katalog_der_namen_und_die_vollen_funktionstexte(self):
        klient, agent = _Klient([_zustand(0), _zustand(1)]), _Agent(ANTWORT)
        self._lauf(klient, agent).ausfuehren()
        for erwartet in ('Was es gibt — nur diese Namen benutzen', 'eigen_foto_x_hose', 'g9_base_shirt', 'mavick_hair'):
            self.assertIn(erwartet, agent.prompts[0])

    def test_ein_abgelehntes_rezept_ohne_runde_nennt_die_verschobenen_zeilennummern(self):
        klient = _Klient([_zustand(0), _zustand(1)], [(400, {'error': 'Rezept: Zeile 3: kleid_nur — „x" ist kein Stück'}), (200, {'pid': 1})])
        agent = _Agent(ANTWORT)
        self.assertEqual(self._lauf(klient, agent).ausfuehren(), 'fertig')
        self.assertIn('Zeilennummern zählen die 2 Zeilen des Startrezepts mit', agent.prompts[1])

    def test_fehlt_der_katalog_endet_der_lauf_vor_dem_agentenaufruf(self):
        klient, agent = _Klient([_zustand(0)]), _Agent(ANTWORT)
        klient.katalog = mock.Mock(side_effect=Auftragsfehler('GET …/rezeptkatalog/: HTTP 500'))
        lauf = self._lauf(klient, agent)
        self.assertEqual(lauf.ausfuehren(), 'fehler')
        self.assertEqual(agent.prompts, [])                                                 # ein Prompt ohne Namen lässt die KI raten

    def test_endet_die_runde_ohne_neue_nummer_steht_der_grund_im_fehler(self):
        zustand = _zustand(1)
        zustand['error'] = 'Arbeitsprozess abgestürzt'
        lauf = self._lauf(_Klient([_zustand(1), zustand]), _Agent(ANTWORT))
        self.assertEqual(lauf.ausfuehren(), 'fehler')
        self.assertIn('Keine neue Runde', lauf.zustand.lesen()['meldung'])

    def test_die_flagge_vor_dem_start_haelt_an_bevor_der_agent_gefragt_wird(self):
        agent = _Agent(ANTWORT)
        lauf = self._lauf(_Klient([_zustand(1)]), agent)
        lauf.zustand.anhalten_anfordern()
        self.assertEqual(lauf.ausfuehren(), 'angehalten')
        self.assertEqual(agent.prompts, [])


class DerZustandUndDerProzess(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='edgar_zustand_', dir=str(PROJEKTTEMP)))

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def test_ohne_datei_oder_mit_kaputter_datei_der_leere_anfangszustand(self):
        z = Nachbesserungszustand(self.ordner)
        self.assertEqual(z.lesen()['status'], 'bereit')
        z.ordner.mkdir(parents=True)
        z.datei.write_text('{kaputt', encoding='utf-8')
        self.assertEqual(z.lesen()['status'], 'bereit')

    def test_schreiben_mischt_atomar_und_neu_setzt_zurueck_und_nimmt_die_flagge_weg(self):
        z = Nachbesserungszustand(self.ordner)
        z.neu(3, 4711)
        z.eintrag({'i': 1})
        z.anhalten_anfordern()
        self.assertTrue(z.anhalten_verlangt())
        self.assertFalse(z.datei.with_name(z.datei.name + '.neu').exists())
        z.neu(2, 1)
        stand = z.lesen()
        self.assertEqual((stand['status'], stand['runden'], stand['eintraege'], z.anhalten_verlangt()), ('laeuft', 2, [], False))

    def test_ein_lauf_ohne_prozess_steht_danach_auf_abgebrochen(self):
        z = Nachbesserungszustand(self.ordner)
        z.neu(1, 2_000_000_000)                                       # keine solche PID
        stand = Nachbesserungsprozess(self.ordner).lesen()
        self.assertEqual((stand['status'], stand['pid']), ('abgebrochen', None))

    def test_ein_start_bei_laufendem_lauf_wird_abgelehnt(self):
        prozess = Nachbesserungsprozess(self.ordner)
        with mock.patch.object(Nachbesserungsprozess, 'lebt', return_value=True):
            prozess.zustand.neu(1, 1234)
            from Edgar.auftragsfehler import Auftragsfehler
            with self.assertRaises(Auftragsfehler):
                prozess.starten('uuid', 1)


class DerAgentenaufruf(SimpleTestCase):
    def test_der_befehl_beschraenkt_den_agenten_auf_lesen_und_den_auftragsordner(self):
        agent = Agentenaufruf(verzeichnisse=['A:/auftrag'], modell='opus', budget_usd=2)
        with mock.patch.object(Agentenaufruf, 'programm', return_value='claude.exe'):
            befehl = agent.befehl({'type': 'object'})
        for erwartet in (['-p'], ['--tools', 'Read'], ['--permission-mode', 'dontAsk'], ['--strict-mcp-config'], ['--setting-sources', 'local'], ['--no-session-persistence'],
                         ['--add-dir', 'A:/auftrag'], ['--model', 'opus'], ['--max-budget-usd', '2']):
            teil = ' '.join(befehl)
            self.assertIn(' '.join(erwartet), teil)
        self.assertNotIn('Bash', ' '.join(befehl))

    def test_auswerten_nimmt_structured_output_sonst_result_und_meldet_fehler(self):
        ok = Agentenaufruf._auswerten(json.dumps({'structured_output': {'a': 1}, 'result': 'x', 'total_cost_usd': 0.2, 'num_turns': 2, 'modelUsage': {'m': {}}}))
        self.assertEqual((ok['antwort'], ok['kosten_usd'], ok['modell']), ({'a': 1}, 0.2, 'm'))
        self.assertEqual(Agentenaufruf._auswerten(json.dumps({'result': '{"a": 2}'}))['antwort'], '{"a": 2}')
        from Edgar.auftragsfehler import Agentenfehler
        for kaputt in ('kein json', json.dumps({'is_error': True, 'result': 'Limit'}), json.dumps({'result': ''})):
            with self.assertRaises(Agentenfehler):
                Agentenaufruf._auswerten(kaputt)
