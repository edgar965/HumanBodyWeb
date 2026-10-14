# -*- coding: utf-8 -*-
"""Die Reiter der Seite „Mesh-3D“ (13.10.2026): Edgar: „mach mir in /mesh-3D/ einen neuen Reiter, das soll eine Kopie der aktuellen Seite sein, aber nur mit ausgewählten Testaufträgen.
Es soll möglich sein, Jobs aus einem Tab zum anderen zu verschieben.“ Nicht gelaufen — läuft nur auf Ansage.

Ohne Blender, ohne GPU, ohne Datenbank: die Aufträge sind leere Ordner mit Kennung unter einer umgebogenen `OBJECTS_ROOT` (`Pruefablage`, im Projekt, nicht auf C:).

    ReiterTest       Zuordnung: ohne Datei alles im ersten Reiter, Verschieben zählt nur echte Wechsel, der erste Reiter hält keinen Eintrag, unbekannter Reiter/Auftrag schreibt nichts, eine
                     Kopie erbt den Reiter der Quelle, eine kaputte Datei ist kein Absturz
    EndpunktTest     `POST /api/mesh3d/reiter/verschieben/`: 200 mit Zahl, 400 ohne Auftrag / mit unbekanntem Reiter / mit unbekannter Kennung
    TabelleTest      jede Tabelle hat ihren eigenen Speicherschlüssel (Sortierung, Spaltenbreiten); der des ersten Reiters bleibt `mesh3d`
    VerdrahtungTest  Wächter (Quelltext gelesen): Route, Leiste und Knöpfe in der Vorlage, Liste und Formular rufen die Endpunkte

Sabotage-Gegenprobe: in `Mesh3dreiter.setzen` die Prüfung `unbekannt` streichen → `test_4` rot; `gewechselt` auf `len(kennungen)` setzen → `test_2` rot; `Mesh3dreiter.erben` leeren →
`test_5` rot; den Schlüssel in `Mesh3dtabelle.tabelle` immer `mesh3d` nennen → `TabelleTest` rot; `Seitenreiter.binden` aus der Vorlage streichen → `test_vorlage` rot.
"""

import json
import shutil
import tempfile
from pathlib import Path

from django.test import RequestFactory, SimpleTestCase, override_settings

from core.api.mesh3dreiter import Mesh3dreiterendpunkte
from core.daten.blendimportablage import Blendimportablage
from core.dienste.mesh3dreiter import Mesh3dreiter
from core.dienste.mesh3dtabelle import Mesh3dtabelle

from ._pruefablage import Pruefablage

WEB = Path(__file__).resolve().parents[3]
KENNUNGEN = ['2026.10.13.10.00.00', '2026.10.13.10.00.01', '2026.10.13.10.00.02']


class _Ablage(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='mesh3dreiter_', dir=Pruefablage.wurzel()))
        self.umlenkung = override_settings(OBJECTS_ROOT=self.tmp)
        self.umlenkung.enable()
        for kennung in KENNUNGEN:
            Blendimportablage(kennung).ordner().mkdir(parents=True)

    def tearDown(self):
        self.umlenkung.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _datei(self):
        return json.loads(Mesh3dreiter.pfad().read_text(encoding='utf-8'))


class ReiterTest(_Ablage):
    def test_1_ohne_datei_steht_alles_im_ersten_reiter(self):
        self.assertEqual(Mesh3dreiter.zuordnung(), {})
        aus = Mesh3dreiter.aufteilen(KENNUNGEN)
        self.assertEqual(aus[Mesh3dreiter.erster()], KENNUNGEN)
        self.assertEqual(aus['test'], [])
        self.assertFalse(Mesh3dreiter.pfad().exists())

    def test_2_verschieben_zaehlt_nur_echte_wechsel(self):
        self.assertEqual(Mesh3dreiter.setzen(KENNUNGEN[:2], 'test'), 2)
        self.assertEqual(Mesh3dreiter.setzen(KENNUNGEN[:2], 'test'), 0)            # schon dort
        self.assertEqual(Mesh3dreiter.setzen([KENNUNGEN[0], KENNUNGEN[2]], 'test'), 1)
        aus = Mesh3dreiter.aufteilen(KENNUNGEN)
        self.assertEqual(aus['test'], KENNUNGEN)
        self.assertEqual(aus[Mesh3dreiter.erster()], [])

    def test_3_zurueck_in_den_ersten_reiter_nimmt_den_eintrag_aus_der_datei(self):
        Mesh3dreiter.setzen(KENNUNGEN, 'test')
        Mesh3dreiter.setzen([KENNUNGEN[1]], Mesh3dreiter.erster())
        self.assertEqual(sorted(self._datei()), [KENNUNGEN[0], KENNUNGEN[2]])
        self.assertEqual(Mesh3dreiter.von(KENNUNGEN[1]), Mesh3dreiter.erster())

    def test_4_unbekannter_reiter_und_unbekannter_auftrag_schreiben_nichts(self):
        with self.assertRaises(ValueError):
            Mesh3dreiter.setzen(KENNUNGEN, 'gibtsnicht')
        with self.assertRaises(ValueError):
            Mesh3dreiter.setzen([KENNUNGEN[0], '2026.01.01.00.00.00'], 'test')
        self.assertFalse(Mesh3dreiter.pfad().exists())

    def test_5_eine_kopie_erbt_den_reiter_der_quelle(self):
        Mesh3dreiter.setzen([KENNUNGEN[0]], 'test')
        Mesh3dreiter.erben(KENNUNGEN[0], KENNUNGEN[1])
        Mesh3dreiter.erben(KENNUNGEN[2], KENNUNGEN[2])       # Quelle im ersten Reiter: nichts zu erben
        self.assertEqual(Mesh3dreiter.von(KENNUNGEN[1]), 'test')
        self.assertEqual(Mesh3dreiter.von(KENNUNGEN[2]), Mesh3dreiter.erster())

    def test_6_eine_kaputte_datei_ist_kein_absturz(self):
        Mesh3dreiter.pfad().write_text('{kaputt', encoding='utf-8')
        self.assertEqual(Mesh3dreiter.zuordnung(), {})
        Mesh3dreiter.pfad().write_text(json.dumps({KENNUNGEN[0]: 'gibtsnicht', KENNUNGEN[1]: 'test'}), encoding='utf-8')
        self.assertEqual(Mesh3dreiter.zuordnung(), {KENNUNGEN[1]: 'test'})                 # ein unbekannter Reiter zählt als „erster“

    def test_7_ein_eintrag_ohne_auftrag_wird_beim_naechsten_schreiben_aufgeraeumt(self):
        Mesh3dreiter.pfad().write_text(json.dumps({'2026.01.01.00.00.00': 'test'}), encoding='utf-8')
        Mesh3dreiter.setzen([KENNUNGEN[0]], 'test')
        self.assertEqual(list(self._datei()), [KENNUNGEN[0]])


class EndpunktTest(_Ablage):
    def _post(self, rumpf):
        anfrage = RequestFactory().post('/api/mesh3d/reiter/verschieben/', json.dumps(rumpf), content_type='application/json')
        antwort = Mesh3dreiterendpunkte.verschieben(anfrage)
        return antwort.status_code, json.loads(antwort.content)

    def test_verschieben_antwortet_mit_der_zahl(self):
        status, daten = self._post({'ids': KENNUNGEN[:2], 'reiter': 'test'})
        self.assertEqual((status, daten['ok'], daten['verschoben']), (200, True, 2))
        self.assertEqual(Mesh3dreiter.von(KENNUNGEN[0]), 'test')

    def test_ohne_auftrag_unbekannter_reiter_und_unbekannte_kennung_sind_400(self):
        self.assertEqual(self._post({'ids': [], 'reiter': 'test'})[0], 400)
        self.assertEqual(self._post({'ids': KENNUNGEN, 'reiter': 'gibtsnicht'})[0], 400)
        self.assertEqual(self._post({'ids': ['2026.01.01.00.00.00'], 'reiter': 'test'})[0], 400)
        self.assertFalse(Mesh3dreiter.pfad().exists())

    def test_nur_post(self):
        antwort = Mesh3dreiterendpunkte.verschieben(RequestFactory().get('/api/mesh3d/reiter/verschieben/'))
        self.assertEqual(antwort.status_code, 405)


class TabelleTest(SimpleTestCase):
    databases = set()

    def test_jede_tabelle_hat_ihren_eigenen_speicherschluessel(self):
        self.assertEqual(Mesh3dtabelle([]).tabelle()['key'], 'mesh3d')
        self.assertEqual(Mesh3dtabelle([]).tabelle(Mesh3dreiter.erster())['key'], 'mesh3d')
        self.assertEqual(Mesh3dtabelle([]).tabelle('test')['key'], 'mesh3d-test')

    def test_das_alle_kaestchen_ist_keine_id(self):
        """Zwei Tabellen auf einer Seite: eine Id im Kopf stünde zweimal im Dokument."""
        label = Mesh3dtabelle([]).tabelle()['spalten'][0]['label']
        self.assertIn('class="mesh3d-alle"', label)
        self.assertNotIn(' id=', label)


class VerdrahtungTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _text(*teile):
        return WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_route(self):
        self.assertIn("path('api/mesh3d/reiter/verschieben/', Mesh3dreiterendpunkte.verschieben", self._text('core', 'urls_mesh3d.py'))

    def test_vorlage(self):
        vorlage = self._text('templates', 'mesh3d.html')
        self.assertIn('id="mesh3d-reiter"', vorlage)
        self.assertIn('data-reiterfeld="{{ r.schluessel }}"', vorlage)
        self.assertIn('data-aktion="verschieben"', vorlage)
        self.assertIn("Seitenreiter.binden(document.getElementById('mesh3d-reiter')", vorlage)
        self.assertNotIn('id="mesh3d-bulk-delete"', vorlage)          # Knöpfe je Reiter: keine festen Ids

    def test_liste_und_formular(self):
        self.assertIn('/api/mesh3d/reiter/verschieben/', self._text('static', 'viewer', 'mesh3d', 'mesh3dliste.js'))
        neu = self._text('static', 'viewer', 'mesh3d', 'mesh3dneu.js')
        self.assertIn('#mesh3d-reiter [role="tab"][aria-selected="true"]', neu)
        self.assertIn('reiter }', neu)
        self.assertIn('Mesh3dreiter.setzen([kennung], rumpf[\'reiter\'])', self._text('core', 'api', 'mesh3d.py'))
        self.assertIn('Mesh3dreiter.erben(kennung, neue[-1])', self._text('core', 'api', 'mesh3dkopie.py'))
