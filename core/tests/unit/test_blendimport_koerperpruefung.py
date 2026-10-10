# -*- coding: utf-8 -*-
"""Wächter nach „export": deckt der Körper der .blend die ganze Figur? (Edgar, 10.10.2026, nach Rosemary Winters).

Rosemary: `body` nur von Kopf bis Mitte Oberschenkel (z 1,353…2,941 m), die Beine nur als Strumpf-Netz `sock` (z −0,225…1,506), Figur 3,28 m — 48 %.
Der Import rechnete Stunden und lieferte eine Figur, die nicht zum Körper passte. Der Wächter hält nach „export" (5 s) an und sagt, was fehlt.
Gemessen an allen gespeicherten Inventaren (`ProjektTemp/_wegwerf/asian/koerper_anteil.py`): 93–100 %.

1. Ein ganzer Körper besteht, auch mit Hut, Stiefeln und Waffe über der Körperhöhe (Fallout ranger: 93 %).
2. Rosemarys Maße halten an; der Text nennt den Anteil, die Spanne des Körpers, das Netz, das darüber hinausreicht, und die Einstellung.
3. „Trotzdem importieren" lässt durch und merkt es im Bericht.
4. Haar zählt zur Figurhöhe nicht (ein langer Zopf unter den Füßen machte sonst jeden Körper „zu kurz"); ohne Körper-Rolle gibt es nichts zu messen.
5. Die Einstellung `unvollstaendig` kennt zwei Werte, die Vorgabe ist „anhalten".

Sabotage-Gegenprobe: `MIN_ANTEIL` auf 0.40 → Fall 2 rot; `FIGUR` um `'haar'` erweitern → Fall 4 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.blendimportkoerperpruefung import Blendimportkoerperpruefung


def _netz(name, z0, z1):
    return {'name': name, 'min': [0.0, 0.0, z0], 'max': [0.3, 0.3, z1]}


def _rollen(**namen):
    return [{'name': n, 'rolle': r} for n, r in namen.items()]


class KoerperpruefungTest(SimpleTestCase):
    databases = set()

    def test_1_ein_ganzer_koerper_besteht_auch_mit_hut_und_waffe(self):
        inventar = {'netze': [_netz('body', 0.00, 1.75), _netz('helm', 1.60, 1.89), _netz('stiefel', -0.02, 0.4)]}
        mass = Blendimportkoerperpruefung.pruefen(inventar, _rollen(body='koerper', helm='kleid', stiefel='kleid'))
        self.assertGreater(mass['anteil'], 0.9)
        self.assertNotIn('unvollstaendig', mass)

    def test_2_strumpf_ueber_den_beinen_deckt_sie_rosemary_besteht(self):
        # Rosemary Winters (10.10.2026): der Körper endet in der Oberschenkelmitte, der Strumpf-Netz `sock` deckt die Beine bis zum Absatz.
        inventar = {'netze': [_netz('body', 1.353, 2.941), _netz('sock', -0.225, 1.506), _netz('hat', 2.270, 3.053)]}
        mass = Blendimportkoerperpruefung.pruefen(inventar, _rollen(body='koerper', sock='kleid', hat='kleid'))
        self.assertGreaterEqual(mass['anteil'], 0.99)
        self.assertNotIn('unvollstaendig', mass)

    def test_2b_fehlende_beine_ohne_kleidung_halten_an_und_der_text_sagt_was_fehlt(self):
        inventar = {'netze': [_netz('body', 1.353, 2.941), _netz('beinrest', -0.225, 1.506)]}
        with self.assertRaises(ValueError) as fehler:
            Blendimportkoerperpruefung.pruefen(inventar, _rollen(body='koerper', beinrest='auge'))
        text = str(fehler.exception)
        self.assertIn('„body"', text)
        self.assertIn('%', text)
        self.assertIn('unten', text)
        self.assertIn('„beinrest"', text, 'das Netz, das unter den Körper reicht')
        self.assertIn('Unvollständiger Körper', text, 'die Einstellung, mit der man es übergeht')

    def test_3_trotzdem_importieren_laesst_durch_und_merkt_es(self):
        inventar = {'netze': [_netz('body', 1.353, 2.941), _netz('beinrest', -0.225, 1.506)]}
        mass = Blendimportkoerperpruefung.pruefen(inventar, _rollen(body='koerper', beinrest='auge'), trotzdem=True)
        self.assertTrue(mass['unvollstaendig'] and mass['trotzdem'])

    def test_4_haar_zaehlt_nicht_zur_figurhoehe_ohne_koerper_nichts_zu_messen(self):
        inventar = {'netze': [_netz('body', 0.0, 1.75), _netz('zopf', -0.8, 1.9)]}
        mass = Blendimportkoerperpruefung.pruefen(inventar, _rollen(body='koerper', zopf='haar'))
        self.assertGreaterEqual(mass['anteil'], 0.99)
        self.assertIsNone(Blendimportkoerperpruefung.messen(inventar, _rollen(zopf='haar')))
        self.assertIsNone(Blendimportkoerperpruefung.pruefen({'netze': []}, []))

    def test_5_die_einstellung_hat_zwei_werte_und_die_vorgabe_haelt_an(self):
        self.assertEqual(Blendimporteinstellungen.pruefen({})['unvollstaendig'], 'anhalten')
        self.assertEqual(Blendimporteinstellungen.pruefen({'unvollstaendig': 'weiter'})['unvollstaendig'], 'weiter')
        self.assertEqual(Blendimporteinstellungen.pruefen({'unvollstaendig': 'irgendwas'})['unvollstaendig'], 'anhalten')
