# -*- coding: utf-8 -*-
"""Die Standardanimation je Mesh-3D-Auftrag (13.10.2026, `Mesh3danimationswahl`). Nicht gelaufen — läuft nur auf Ansage.

Ohne Datenbank, GPU und Server: die Aufträge sind Ordner unter einer umgebogenen `OBJECTS_ROOT`, die BVH-Bibliothek ein Ordner mit leeren `.bvh`-Dateien.

    WahlTest         Vorgabe DanceKurz, Speichern und Lesen, Pfadsprünge und fehlende Dateien abgelehnt, kaputte Datei, fehlende Wahl fällt auf die Vorgabe
    EndpunktTest     GET/POST `/api/mesh3d/<kennung>/animation/`: Zustand mit Kategorien, ungültige Wahl 400 (nichts geschrieben), unbekannter Auftrag 404
    VerdrahtungTest  Wächter (Quelltext gelesen): Route, Zustand, `Mesh3dbewegung` nimmt die Wahl, Auswahl unter der Leiste, Bühne ruft das Feld, die Kopie nimmt die Datei mit

Sabotage-Gegenprobe: in `Mesh3danimationswahl.zerlegen` die Prüfung auf `..` streichen → `test_pfadsprung_wird_abgelehnt` rot; `gewaehlt` ohne `or self.standardwert()` → `test_ohne_datei_gilt_die_vorgabe` rot;
in `Mesh3dbewegung.rechnen` `Mesh3danimationswahl(...)` weglassen → `test_bewegung_nimmt_die_wahl` rot; `animation.json` in `Ordnerkopie.NIE_NAMEN` aufnehmen → `test_kopie_nimmt_die_wahl_mit` rot.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import RequestFactory, SimpleTestCase, override_settings

from core.api.mesh3danimation import Mesh3danimationsendpunkte
from core.daten.blendimportablage import Blendimportablage
from core.dienste.bvhverzeichnis import Bvhverzeichnis
from core.dienste.mesh3danimationswahl import Mesh3danimationswahl
from core.dienste.ordnerkopie import Ordnerkopie

from ._pruefablage import Pruefablage

WEB = Path(__file__).resolve().parents[3]
KENNUNG = '2026.10.13.10.00.00'


class _Ablage(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='mesh3danimation_', dir=Pruefablage.wurzel()))
        self.umlenkung = override_settings(OBJECTS_ROOT=self.tmp)
        self.umlenkung.enable()
        self.ablage = Blendimportablage(KENNUNG)
        self.ablage.anlegen()
        self.ablage.stand_schreiben({'kennung': KENNUNG, 'status': 'neu', 'bereich': 'mesh3d', 'weg': 'netz', 'quelle': {'name': 'Probe'}, 'einstellungen': {}})
        self.bvh = self.tmp / 'bibliothek'
        for kategorie, namen in (('A_Results', ('DanceKurz', 'Arabesque')), ('Daz', ('Dance',)), ('Leer', ())):
            (self.bvh / kategorie).mkdir(parents=True)
            for name in namen:
                (self.bvh / kategorie / (name + '.bvh')).write_text('HIERARCHY', encoding='utf-8')
        self.verzeichnis = Bvhverzeichnis(wurzel=self.bvh)

    def tearDown(self):
        self.umlenkung.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _wahl(self):
        return Mesh3danimationswahl(KENNUNG, verzeichnis=self.verzeichnis)


class WahlTest(_Ablage):
    def test_ohne_datei_gilt_die_vorgabe(self):
        wahl = self._wahl()
        self.assertEqual(wahl.gewaehlt(), 'A_Results/DanceKurz')
        zustand = wahl.zustand()
        self.assertTrue(zustand['standard'])
        self.assertFalse(zustand['fehlt'])
        self.assertTrue(wahl.pfad().endswith('DanceKurz.bvh'))

    def test_speichern_und_lesen(self):
        zustand = self._wahl().setzen('A_Results/Arabesque')
        self.assertEqual((zustand['wahl'], zustand['standard']), ('A_Results/Arabesque', False))
        self.assertEqual(json.loads((self.ablage.ordner() / 'animation.json').read_text(encoding='utf-8')), {'bvh': 'A_Results/Arabesque'})
        neu = self._wahl()           # frische Instanz liest von der Platte
        self.assertEqual(neu.gewaehlt(), 'A_Results/Arabesque')
        self.assertTrue(neu.pfad().endswith('Arabesque.bvh'))

    def test_pfadsprung_wird_abgelehnt(self):
        for wert in ('../x', 'A_Results/../Daz/Dance', 'A_Results/a/b', 'A_Results', '', None, 'A_Results\\Arabesque', '/Arabesque'):
            with self.assertRaises(ValueError, msg=repr(wert)):
                self._wahl().setzen(wert)
        self.assertFalse((self.ablage.ordner() / 'animation.json').exists())

    def test_eine_unbekannte_animation_wird_abgelehnt(self):
        for wert in ('A_Results/gibtsnicht', 'Nirgends/Arabesque', 'Leer/Arabesque'):
            with self.assertRaises(ValueError, msg=wert):
                self._wahl().setzen(wert)
        self.assertFalse((self.ablage.ordner() / 'animation.json').exists())

    def test_eine_verschwundene_wahl_faellt_auf_die_vorgabe_zurueck(self):
        self._wahl().setzen('A_Results/Arabesque')
        (self.bvh / 'A_Results' / 'Arabesque.bvh').unlink()
        wahl = self._wahl()
        zustand = wahl.zustand()
        self.assertTrue(zustand['fehlt'])
        self.assertEqual(zustand['wahl'], 'A_Results/Arabesque')       # die Seite zeigt die Wahl samt Hinweis, wechselt nicht still
        self.assertTrue(wahl.pfad().endswith('DanceKurz.bvh'))

    def test_fehlt_auch_die_vorgabe_gibt_es_keinen_pfad(self):
        (self.bvh / 'A_Results' / 'DanceKurz.bvh').unlink()
        self.assertEqual(self._wahl().pfad(), '')        # dann nimmt `Mesh3dbewegung` den Tanz der Bibliothek

    def test_eine_kaputte_datei_ist_kein_absturz(self):
        (self.ablage.ordner() / 'animation.json').write_text('{kaputt', encoding='utf-8')
        self.assertEqual(self._wahl().gewaehlt(), 'A_Results/DanceKurz')
        (self.ablage.ordner() / 'animation.json').write_text('[1, 2]', encoding='utf-8')
        self.assertEqual(self._wahl().gewaehlt(), 'A_Results/DanceKurz')

    def test_die_kategorien_ohne_die_leeren(self):
        namen = [k['name'] for k in self._wahl().kategorien()]
        self.assertEqual(namen, ['A_Results', 'Daz'])
        self.assertEqual(self._wahl().kategorien()[0]['anzahl'], 2)


class EndpunktTest(_Ablage):
    def _anfrage(self, methode, kennung=KENNUNG, **rumpf):
        fabrik = RequestFactory()
        request = fabrik.post('/x/', data=json.dumps(rumpf), content_type='application/json') if methode == 'POST' else fabrik.get('/x/')
        with mock.patch.object(Bvhverzeichnis, 'wurzel', return_value=str(self.bvh)):
            return Mesh3danimationsendpunkte.wahl(request, kennung)

    def test_get_liefert_wahl_und_kategorien(self):
        antwort = self._anfrage('GET')
        daten = json.loads(antwort.content)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(daten['wahl'], 'A_Results/DanceKurz')
        self.assertEqual([k['name'] for k in daten['kategorien']], ['A_Results', 'Daz'])

    def test_post_speichert_und_antwortet_mit_dem_neuen_zustand(self):
        daten = json.loads(self._anfrage('POST', bvh='Daz/Dance').content)
        self.assertEqual((daten['wahl'], daten['standard']), ('Daz/Dance', False))
        self.assertEqual(self._wahl().gewaehlt(), 'Daz/Dance')

    def test_post_mit_ungueltiger_wahl_ist_400_und_aendert_nichts(self):
        antwort = self._anfrage('POST', bvh='../Daz/Dance')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('error', json.loads(antwort.content))
        self.assertEqual(self._wahl().gewaehlt(), 'A_Results/DanceKurz')

    def test_unbekannter_auftrag_ist_404(self):
        self.assertEqual(self._anfrage('GET', kennung='2026.01.01.00.00.00').status_code, 404)


class VerdrahtungTest(SimpleTestCase):
    def _text(self, *teile):
        return (WEB.joinpath(*teile)).read_text(encoding='utf-8')

    def test_die_route_steht_in_den_urls(self):
        text = self._text('core', 'urls_mesh3d.py')
        self.assertIn("api/mesh3d/<kennung:kennung>/animation/", text)
        self.assertIn('Mesh3danimationsendpunkte.wahl', text)

    def test_der_zustand_nennt_die_standardanimation(self):
        self.assertIn("'animation': Mesh3danimationswahl(kennung).zustand()", self._text('core', 'dienste', 'mesh3dzustand.py'))

    def test_bewegung_nimmt_die_wahl(self):
        self.assertIn('Mesh3danimationswahl(self.ablage.kennung).pfad()', self._text('core', 'dienste', 'mesh3dbewegung.py'))

    def test_die_auswahl_steht_unter_der_leiste(self):
        text = self._text('templates', 'mesh3d_auftrag.html')
        self.assertLess(text.index('id="animations-leiste"'), text.index('id="anim-wahl"'))
        self.assertLess(text.index('id="anim-wahl"'), text.index('id="animation-meldung"'))
        self.assertIn('id="anim-wahl-kategorie"', text)
        self.assertIn('id="anim-wahl-datei"', text)

    def test_die_buehne_ruft_das_feld_und_rechnet_nach_der_wahl(self):
        text = self._text('static', 'viewer', 'mesh3d', 'mesh3dbuehne.js')
        self.assertIn("import { Mesh3danimationswahlfeld } from './mesh3danimationswahlfeld.js'", text)
        self.assertIn('this.wahl.zeigen(z.animation)', text)
        self.assertIn('_nachWahl()', text)

    def test_kopie_nimmt_die_wahl_mit(self):
        self.assertNotIn('animation.json', Ordnerkopie.NIE_NAMEN)
