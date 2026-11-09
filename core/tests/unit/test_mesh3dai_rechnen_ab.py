"""Start ab „meshanpassung“: `Mesh3dairechenlauf.vorlauf_fehlt` und `vorbereiten(ab=…)` (06.11.2026).
    1  alles da: nichts fehlt, Schritte davor „übernommen“, ab dem Start offen
    2  fehlt die Figur des eingestellten Geschlechts: `vorlauf_fehlt` nennt sie, `vorbereiten` wirft, kein neuer Stand
    3  die Figur des anderen Geschlechts zählt nicht
    4  unbekannter Schritt: `ValueError`
    5  ein Start ab einem späteren Schritt prüft den Vorlauf nicht
    6  ein ganzer Lauf ohne `ab` prüft den Vorlauf nicht
    7  API: `ab` kommt an, fehlender Vorlauf ist 400 mit Satz, kaputter Rumpf rechnet nichts
Sabotage (von Hand): in `vorlauf_fehlt` `not any` zu `any` → Fall 1 und 2 rot; in `vorbereiten` den Vergleich mit `AB_GESCHLECHT` entfernen → Fall 5 rot.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import RequestFactory

from core.api.mesh3dairechnen import Mesh3dairechnenendpunkte
from core.dienste.mesh3dairechenlauf import Mesh3dairechenlauf


class _Ablage(unittest.TestCase):
    databases = []

    def setUp(self):
        ablage = tempfile.TemporaryDirectory(dir=settings.TOOLS_ROOT / 'ProjektTemp')
        self.addCleanup(ablage.cleanup)
        self.wurzel = Path(ablage.name)
        self.test = self.wurzel / 'probe'
        self.test.mkdir()
        leitung = mock.patch('core.dienste.mesh3daitest.Mesh3daitest.ordner', return_value=self.wurzel)
        leitung.start()
        self.addCleanup(leitung.stop)
        schlange = mock.patch.object(Mesh3dairechenlauf, '_warteschlange_eintragen')
        schlange.start()
        self.addCleanup(schlange.stop)
        fassungen = mock.patch('core.dienste.mesh3dairechenlauf.Mesh3daikifassungen.lesen', return_value={})
        fassungen.start()
        self.addCleanup(fassungen.stop)
        self.geschlecht('maennlich')

    def geschlecht(self, g):
        (self.test / 'einstellung.json').write_text(json.dumps({'geschlecht': g}), encoding='utf-8')

    def datei(self, name):
        p = self.test / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{}', encoding='utf-8')

    def vorlauf(self, g='maennlich'):
        for name in ('test.json', 'form.npz', 'vorstufe/lauf/apose.npz', 'form_%s/modell.json' % g, 'ergebnis_Form_%s.npz' % g):
            self.datei(name)


class TestVorlauf(_Ablage):
    def test_alles_da(self):
        self.vorlauf()
        lauf = Mesh3dairechenlauf('probe')
        self.assertEqual(lauf.vorlauf_fehlt(), [])
        stand = lauf.vorbereiten(ab=Mesh3dairechenlauf.AB_GESCHLECHT)
        je = {s['schluessel']: s for s in stand['schritte']}
        self.assertTrue(je['rig']['uebernommen'])
        self.assertTrue(je['foto']['uebernommen'])
        self.assertEqual(je['meshanpassung']['status'], 'offen')
        self.assertEqual(je['pruefung']['status'], 'offen')
        self.assertEqual(stand['ab'], 'meshanpassung')

    def test_figur_fehlt(self):
        self.vorlauf()
        (self.test / 'form_maennlich' / 'modell.json').unlink()
        lauf = Mesh3dairechenlauf('probe')
        self.assertEqual(lauf.vorlauf_fehlt(), ['form_maennlich/modell.json'])
        with self.assertRaisesRegex(ValueError, 'form_maennlich/modell.json'):
            lauf.vorbereiten(ab='meshanpassung')
        self.assertIsNone(lauf.stand())

    def test_anderes_geschlecht_zaehlt_nicht(self):
        self.vorlauf('weiblich')
        self.assertEqual(Mesh3dairechenlauf('probe').vorlauf_fehlt(), ['form_maennlich/modell.json', 'ergebnis_Form_maennlich.npz'])

    def test_unbekannter_schritt(self):
        with self.assertRaisesRegex(ValueError, 'gibt es nicht'):
            Mesh3dairechenlauf('probe').vorbereiten(ab='gibtsnicht')

    def test_spaeterer_schritt_prueft_nicht(self):
        self.assertEqual(Mesh3dairechenlauf('probe').vorbereiten(ab='pruefung')['ab'], 'pruefung')

    def test_ganzer_lauf_prueft_nicht(self):
        self.assertIsNone(Mesh3dairechenlauf('probe').vorbereiten()['ab'])


class TestEndpunkt(_Ablage):
    def post(self, rumpf):
        anfrage = RequestFactory().post('/x/', data=rumpf, content_type='application/json')
        with mock.patch('core.api.mesh3dairechnen.Mesh3dairechenschlange.laeuft', return_value=None), \
                mock.patch('core.dienste.mesh3dairechenschlange.Mesh3dairechenschlange._einreihen') as eingereiht:
            antwort = Mesh3dairechnenendpunkte.starten(anfrage, 'probe')
        return antwort, eingereiht

    def test_ab_kommt_an(self):
        self.vorlauf()
        antwort, eingereiht = self.post('{"ab": "meshanpassung"}')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(json.loads(antwort.content)['stand']['ab'], 'meshanpassung')
        eingereiht.assert_called_once_with('probe')

    def test_vorlauf_fehlt_ist_400(self):
        antwort, eingereiht = self.post('{"ab": "meshanpassung"}')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('fehlt', json.loads(antwort.content)['error'])
        eingereiht.assert_not_called()

    def test_kaputter_rumpf(self):
        antwort, eingereiht = self.post('[1, 2]')
        self.assertEqual(antwort.status_code, 400)
        eingereiht.assert_not_called()
