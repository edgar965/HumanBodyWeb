# -*- coding: utf-8 -*-
"""Paket `Edgar` (`2d3DIterationen/Edgar`): Antwortdeutung, Bewertung und Nachbesserungsprompt (05.10.2026, Nachbesserung durch einen Claude-Agenten).

Kunstdaten: ein kleiner Zustand im Aufbau des Zustands von „Randy" (gemessen mit `ProjektTemp/_wegwerf/edgar/zustand_struktur.py`), Dateien in einem Ordner unter `ProjektTemp`.
Ohne Django-Datenbank, ohne Server, ohne Claude. Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

import json
import shutil
import tempfile
from pathlib import Path

from django.test import SimpleTestCase
from Edgar.antwortdeutung import Antwortdeutung
from Edgar.auftragsfehler import Agentenfehler
from Edgar.bewertung import Bewertung
from Edgar.nachbesserungsprompt import Nachbesserungsprompt
from Edgar.rundenstand import Rundenstand

PROJEKTTEMP = Path(__file__).resolve().parents[3] / 'ProjektTemp'


def _antwort(**felder):
    basis = {'urteil': 'Hut zu flach.', 'kommentar': 'Hut höher.', 'abweichungen': [{'teil': 'Hut', 'vorlage': 'hoch', 'render': 'flach', 'schwere': 1, 'massnahme': 'Krone'}],
             'aufrufe': ["m.kleid_anteil('hut', 1.0)"], 'fertig': False}
    return dict(basis, **felder)


class DieAntwortdeutung(SimpleTestCase):
    def test_json_aus_text_mit_codezaun_und_geplauder(self):
        roh = 'Hier mein Ergebnis:\n```json\n%s\n```\nViel Erfolg!' % json.dumps(_antwort())
        self.assertEqual(Antwortdeutung.deuten(roh)['aufrufe'], ["m.kleid_anteil('hut', 1.0)"])

    def test_text_ohne_json_ist_ein_agentenfehler(self):
        with self.assertRaises(Agentenfehler):
            Antwortdeutung.deuten('Ich weiß es nicht.')

    def test_rezeptzeilen_leere_zaeune_und_kommentare_fallen_weg(self):
        zeilen = Antwortdeutung.zeilen("```\n\n# Kommentar\nm.kleid_aus('a')\n  m.kleid_aus('b')  \n```")
        self.assertEqual(zeilen, ["m.kleid_aus('a')", "m.kleid_aus('b')"])

    def test_eine_zeile_ohne_m_punkt_wird_abgelehnt(self):
        with self.assertRaises(Agentenfehler):
            Antwortdeutung.zeilen(["m.kleid_aus('a')", "kleid_aus('b')"])

    def test_zu_viele_zeilen_werden_abgelehnt(self):
        with self.assertRaises(Agentenfehler):
            Antwortdeutung.zeilen(["m.kleid_aus('a')"] * (Antwortdeutung.MAX_AUFRUFE + 1))

    def test_ohne_kommentar_gilt_das_urteil_und_der_kommentar_wird_gekuerzt(self):
        ohne = Antwortdeutung.deuten(_antwort(kommentar=''))
        self.assertEqual(ohne['kommentar'], 'Hut zu flach.')
        lang = Antwortdeutung.deuten(_antwort(kommentar='x' * 9000))
        self.assertEqual(len(lang['kommentar']), Antwortdeutung.MAX_KOMMENTAR)

    def test_unbekannte_schwere_wird_zu_drei_und_offene_zaehlt_eins_und_zwei(self):
        deutung = Antwortdeutung.deuten(_antwort(abweichungen=[{'teil': 'a', 'schwere': 1}, {'teil': 'b', 'schwere': 2}, {'teil': 'c', 'schwere': 3}, {'teil': 'd', 'schwere': 9}]))
        self.assertEqual([a['schwere'] for a in deutung['abweichungen']], [1, 2, 3, 3])
        self.assertEqual(Antwortdeutung.offene(deutung['abweichungen']), 2)

    def test_das_schema_verlangt_alle_felder(self):
        self.assertEqual(set(Antwortdeutung.SCHEMA['required']), {'urteil', 'abweichungen', 'kommentar', 'aufrufe', 'fertig'})


class DieBewertung(SimpleTestCase):
    def test_jeder_abschnitt_hat_titel_gilt_und_punkte_mit_beleg(self):
        daten = Bewertung().fuer_seite()
        self.assertGreaterEqual(len(daten['abschnitte']), 5)
        for ab in daten['abschnitte']:
            self.assertTrue(ab['titel'] and ab['gilt'] and isinstance(ab['fuer_agent'], bool), ab['id'])
            for p in ab['punkte']:
                self.assertTrue(p['text'] and p['beleg'], '%s ohne Beleg: %s' % (ab['id'], p['text'][:40]))

    def test_der_agent_bekommt_nur_markierte_abschnitte_und_randy_als_beispiele(self):
        daten = Bewertung().fuer_seite()
        text = Bewertung().fuer_agent()
        for ab in daten['abschnitte']:
            self.assertEqual(ab['titel'] in text, ab['fuer_agent'], ab['id'])
        self.assertIn('Beispiele aus dem Auftrag Randy', text)
        self.assertLess(text.index('Maßstab und Arbeitsweise'), text.index('Beispiele aus dem Auftrag Randy'))


class DerNachbesserungsprompt(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='edgar_prompt_', dir=str(PROJEKTTEMP)))
        for unter, name in (('vorbereitet', 'a_1.png'), ('iterationen', 'runde_003_vergleich.png'), ('iterationen', 'runde_003_kopf.png'), ('iterationen', 'runde_003_ansicht_+000.png')):
            (self.ordner / unter).mkdir(exist_ok=True)
            (self.ordner / unter / name).write_bytes(b'x')
        self.zustand = {
            'name': 'Test', 'kennung': '2026.01.01.00.00.00', 'laeuft': False, 'status': 'wartet', 'optionen': {'iterationen': {'modus': 'begutachtung'}},
            'bilder': [{'datei': 'a_1.png', 'original': 'a_1.png', 'rolle': 'vorne', 'erkannt': 'vorne'}, {'datei': 'b.png', 'original': 'b.png', 'rolle': 'aus'}],
            'ergebnis': {'kreislauf': {'runde_bester': 3}, 'begutachtung': {'rezept': [{'runde': 3, 'aufrufe': ["m.kleid_aus('x')"], 'kommentar': 'k'}]},
                         'iterationen': [{'runde': 3, 'art': 'begutachtung', 'uebernommen': True, 'note': {'gesamt': 0.7, 'teilnoten': {'foto': 0.4}}, 'kommentar': 'K3',
                                          'dateien': {'vergleich': 'runde_003_vergleich.png', 'kopf': 'runde_003_kopf.png'},
                                          'je_ansicht': [{'original': 'a_1.png', 'winkel': 0.0, 'render': 'runde_003_ansicht_+000.png'}]}]}}
        self.stand = Rundenstand(self.zustand, self.ordner)
        self.funktionen = {'objekt': 'm', 'funktionen': [{'name': 'kleid_aus', 'signatur': '(kennung)', 'text': 'Ablegen'}]}

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def test_der_rundenstand_findet_vorlagen_ohne_aus_und_die_bilder_der_letzten_runde(self):
        self.assertEqual([v['pfad'].name for v in self.stand.vorlagebilder()], ['a_1.png'])
        self.assertEqual(self.stand.vorlagebilder()[0]['winkel'], '0.0°')
        bilder = self.stand.bilder_letzte_runde()
        self.assertEqual((bilder['tafel'].name, bilder['kopf'].name, len(bilder['ansichten'])), ('runde_003_vergleich.png', 'runde_003_kopf.png', 1))
        self.assertEqual((self.stand.nummer, self.stand.beste, self.stand.modus), (3, 3, 'begutachtung'))

    def test_fehlende_dateien_fehlen_statt_zu_werfen(self):
        (self.ordner / 'iterationen' / 'runde_003_kopf.png').unlink()
        self.assertIsNone(self.stand.bilder_letzte_runde()['kopf'])

    def test_der_prompt_nennt_pfade_stand_funktionen_bewertung_und_ausgabe(self):
        text = Nachbesserungsprompt(self.stand, self.funktionen, 'BEWERTUNGSTEXT').text()
        for erwartet in ('nächste Runde (4)', 'a_1.png', 'runde_003_vergleich.png', 'KLEINER IST BESSER', "m.kleid_aus('x')", '`m.kleid_aus(kennung)`', 'BEWERTUNGSTEXT', '## Ausgabe'):
            self.assertIn(erwartet, text)
        self.assertNotIn('Herkunft:', text)                      # der Herkunftsvermerk der Vorgabe ist für Menschen
        self.assertNotIn('b.png', text)                          # Rolle „aus" zählt nicht

    def test_der_prompt_nennt_die_teile_der_letzten_runde_und_ohne_teile_keine_zeile(self):
        # ohne `teile` zuerst: der Rundenstand teilt die Runden-Dicts mit dem Zustand, ein späteres Eintragen wirkte auch auf `self.stand`
        self.assertNotIn('trägt (Kennungen', Nachbesserungsprompt(self.stand, self.funktionen, 'B').text())
        self.zustand['ergebnis']['iterationen'][0]['teile'] = {'g9_base_shirt': 1, 'mavick_hair': 1, 'weg': 0}
        stand = Rundenstand(self.zustand, self.ordner)
        self.assertEqual(stand.teile_text(), 'g9_base_shirt, mavick_hair')            # Anteil 0 trägt das Modell nicht
        self.assertIn('trägt (Kennungen für `m.kleid_*` und `m.haar_*`): g9_base_shirt, mavick_hair.', Nachbesserungsprompt(stand, self.funktionen, 'B').text())

    def test_die_vorgabe_sagt_was_die_bilder_nicht_zeigen(self):
        text = Nachbesserungsprompt(self.stand, self.funktionen, 'B').text()
        for erwartet in ('Was die Bilder zeigen — und was nicht', 'Namen und Wirkung', 'Teile anlegen'):
            self.assertIn(erwartet, text)

    def test_eine_reparatur_haengt_die_meldung_des_servers_an(self):
        text = Nachbesserungsprompt(self.stand, self.funktionen, 'B', reparatur='Rezept: unbekannter Aufruf').text()
        self.assertIn('Dein letztes Rezept wurde vom Server abgelehnt', text)
        self.assertIn('unbekannter Aufruf', text)

    def test_das_rezept_zeigt_ganze_bloecke_und_meldet_gekuerztes(self):
        viele = [{'runde': n, 'aufrufe': ["m.kleid_aus('%d')" % n] * 5, 'kommentar': ''} for n in range(1, 40)]
        self.zustand['ergebnis']['begutachtung']['rezept'] = viele
        text = Rundenstand(self.zustand, self.ordner).rezept_text(runden=39, zeichen=300)
        self.assertTrue(text.startswith('# … ältere Runden nicht gezeigt'))
        self.assertIn('# Runde 39', text)
        self.assertTrue(all(z == '' or z.startswith(('#', 'm.')) for z in text.splitlines()))     # kein mittendrin abgeschnittener Aufruf
