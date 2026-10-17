# -*- coding: utf-8 -*-
"""Mesh-3D: das Netz eines Auftrags — Kopie ohne Daten, Quelle übernehmen, Neu berechnen (14.10.2026, Edgar).

Anlass: zwei Aufträge (`Edgar2009`, `Edgar1970`) rechneten das ALTE Netz, obwohl eine neue GLB hochgeladen war — die Kopie ohne Daten hatte die Datei der Quelle behalten, der hochgeladene Pfad stand nur im Feld
der Seite, und „Neu berechnen“ las den Stand. Edgar: „nach Klick auf Quelle übernehmen soll das alte Mesh aus der 2. View weg sein und das neue geladen werden“, „bei Kopie ohne Daten — warum machst du
das alte Mesh rein??“

    KopieTest       `ohne_daten`: Datei und Pfad leer, Name und übrige Einstellungen bleiben, Weg bleibt; `ohne_ergebnis` (Prüfreihe) behält die Datei; `mit_daten` ohne Ergebnis ebenfalls
    WechselTest     `_altes_netz_wegraeumen` entfernt `koerper.glb`, `.scan.npz`, `ansicht/`, `netzbearbeitung/` und nichts sonst; `_neues_netz_ablegen` nur beim Weg „netz“, ein Fehler wird gemeldet statt geworfen
    StartTest       `neu` ohne Datei: 400 mit Grund (kein Prozess); mit Datei läuft der alte Weg weiter
    QuelltextTest   Browser: „Neu berechnen“ übernimmt zuerst (`vorStart`), ein neues Netz rechnet von vorn; die Mesh-Ansicht leert sich ohne Netz; kein stehengebliebenes `figurId`

Sabotage-Gegenprobe: in `_anlegen` das `quelle.update(datei='', …)` streichen → `KopieTest.test_1` rot; in `ALTES_NETZ` `'koerper.glb'` streichen → `WechselTest.test_1` rot; die Prüfung in `neu` streichen → `StartTest.test_1`
rot; in `Mesh3dlauf.neu` den Aufruf `vorStart` streichen → `QuelltextTest.test_1` rot.

Nicht gelaufen — läuft nur auf Ansage.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import RequestFactory, SimpleTestCase

from core.api.blendimport import Blendimportendpunkte
from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportarbeiter import Blendimportarbeiter
from core.dienste.mesh3dkopie import Mesh3dkopie
from core.dienste.mesh3dquellwechsel import Mesh3dquellwechsel

from ._pruefablage import Pruefablage

WEB = Path(__file__).resolve().parents[3]
QUELLE = '2026.10.14.10.00.00'


def lesen(*teile):
    return WEB.joinpath(*teile).read_text(encoding='utf-8')


class _Wurzel(SimpleTestCase):
    """Ein Importordner in einer Testablage; `Blendimportablage.wurzel` zeigt dorthin."""
    databases = set()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='mesh3d_quelle_', dir=Pruefablage.wurzel()))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        umbiegen = mock.patch.object(Blendimportablage, 'wurzel', classmethod(lambda cls: self.tmp))
        umbiegen.start()
        self.addCleanup(umbiegen.stop)
        self.datei = self.tmp / 'netz.glb'
        self.datei.write_bytes(b'glb')

    def stand(self, kennung=QUELLE, **zusatz):
        ablage = Blendimportablage(kennung)
        ablage.anlegen()
        stand = {'kennung': kennung, 'status': 'fertig', 'bereich': 'mesh3d', 'weg': 'netz', 'weg_grund': 'ein Netz',
                 'quelle': {'datei': str(self.datei), 'format': 'glb', 'name': 'Edgar', 'kandidaten': [{'datei': 'netz.glb'}]},
                 'einstellungen': {'pfad': str(self.datei), 'name': 'eigen', 'eigener_name': 'Edgar', 'basis': 'masculine', 'pose': 'sam'}, **zusatz}
        ablage.stand_schreiben(stand)
        return ablage


class KopieTest(_Wurzel):
    def _kopie(self):
        self.stand()
        with mock.patch.object(Blendimportarbeiter, 'lebt', return_value=False), mock.patch.object(Mesh3dkopie, 'namen', return_value={'edgar'}):
            return Mesh3dkopie(QUELLE)

    def test_1_ohne_daten_bringt_kein_netz_mit(self):
        kopie = self._kopie()
        with mock.patch.object(Blendimportarbeiter, 'lebt', return_value=False), mock.patch.object(Mesh3dkopie, 'namen', return_value={'edgar'}):
            neu = Blendimportablage(kopie.ohne_daten()).stand()
        self.assertEqual(neu['quelle']['datei'], '')
        self.assertEqual(neu['einstellungen']['pfad'], '')
        self.assertEqual(neu['quelle']['kandidaten'], [])
        self.assertEqual(neu['quelle']['name'], 'Edgar Kopie')
        self.assertEqual(neu['einstellungen']['eigener_name'], 'Edgar Kopie')
        self.assertEqual((neu['einstellungen']['basis'], neu['einstellungen']['pose'], neu['weg'], neu['status']), ('masculine', 'sam', 'netz', 'neu'))
        self.assertEqual(neu['kopie']['umfang'], 'ohne Daten')

    def test_2_ohne_ergebnis_behaelt_die_datei(self):
        kopie = self._kopie()
        with mock.patch.object(Blendimportarbeiter, 'lebt', return_value=False), mock.patch.object(Mesh3dkopie, 'namen', return_value={'edgar'}):
            neu = Blendimportablage(kopie.ohne_ergebnis()).stand()
        self.assertEqual(neu['quelle']['datei'], str(self.datei))
        self.assertEqual(neu['einstellungen']['pfad'], str(self.datei))

    def test_3_mit_daten_ohne_ergebnis_ist_die_kopie_mit_netz(self):
        kopie = self._kopie()
        with mock.patch.object(Blendimportarbeiter, 'lebt', return_value=False), mock.patch.object(Mesh3dkopie, 'namen', return_value={'edgar'}):
            neu = Blendimportablage(kopie.mit_daten()).stand()
        self.assertEqual(neu['quelle']['datei'], str(self.datei))

    def test_4_ohne_ergebnis_verlangt_die_datei(self):
        self.datei.unlink()
        kopie = self._kopie()
        with mock.patch.object(Blendimportarbeiter, 'lebt', return_value=False), self.assertRaises(ValueError):
            kopie.ohne_ergebnis()


class WechselTest(_Wurzel):
    def _wechsel(self):
        ablage = self.stand()
        return Mesh3dquellwechsel(QUELLE), ablage

    def test_1_das_alte_netz_ist_weg_der_rest_bleibt(self):
        wechsel, ablage = self._wechsel()
        arbeit = ablage.arbeit()
        arbeit.mkdir(parents=True, exist_ok=True)
        for name in ('koerper.glb', 'koerper.glb.scan.npz'):
            (arbeit / name).write_bytes(b'x')
        for ordner in ('ansicht', 'netzbearbeitung', 'pose'):
            (arbeit / ordner).mkdir()
            (arbeit / ordner / 'datei.bin').write_bytes(b'x')
        wechsel._altes_netz_wegraeumen()
        self.assertFalse((arbeit / 'koerper.glb').exists())
        self.assertFalse((arbeit / 'koerper.glb.scan.npz').exists())
        self.assertFalse((arbeit / 'ansicht').exists())
        self.assertFalse((arbeit / 'netzbearbeitung').exists())
        self.assertTrue((arbeit / 'pose' / 'datei.bin').exists(), 'was nicht zum Netz gehört, bleibt')

    def test_2_wegraeumen_ohne_etwas_zu_raeumen_wirft_nicht(self):
        wechsel, _ = self._wechsel()
        wechsel._altes_netz_wegraeumen()

    def test_3_nur_beim_weg_netz_wird_das_neue_netz_abgelegt(self):
        wechsel, _ = self._wechsel()
        with mock.patch('core.dienste.blendimportnetz.Blendimportnetz') as netz:
            netz.return_value.schreiben.return_value = {'dreiecke': 5}
            self.assertEqual(wechsel._neues_netz_ablegen('x.glb', 'netz'), {'dreiecke': 5})
            netz.return_value.schreiben.assert_called_once_with('x.glb')
            netz.reset_mock()
            self.assertIsNone(wechsel._neues_netz_ablegen('x.blend', 'teile'))
            netz.return_value.schreiben.assert_not_called()

    def test_4_ein_fehler_beim_ablegen_wird_gemeldet_nicht_geworfen(self):
        wechsel, _ = self._wechsel()
        with mock.patch('core.dienste.blendimportnetz.Blendimportnetz') as netz:
            netz.return_value.schreiben.side_effect = ValueError('kein Netz')
            self.assertEqual(wechsel._neues_netz_ablegen('x.glb', 'netz'), {'fehler': 'kein Netz'})


class StartTest(_Wurzel):
    def _neu(self, kennung):
        anfrage = RequestFactory().post('/x/', data=json.dumps({'ab': None}), content_type='application/json')
        return Blendimportendpunkte.neu(anfrage, kennung)

    def test_1_ohne_datei_gibt_400_und_startet_nichts(self):
        ablage = self.stand()
        stand = ablage.stand()
        stand['quelle']['datei'] = ''
        ablage.stand_schreiben(stand)
        with mock.patch.object(Blendimportarbeiter, 'starten') as starten:
            antwort = self._neu(QUELLE)
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('fehlt das Netz', json.loads(antwort.content)['error'])
        starten.assert_not_called()

    def test_2_mit_datei_geht_der_start_weiter(self):
        self.stand()
        with mock.patch.object(Blendimportarbeiter, 'starten', return_value=4711) as starten, mock.patch.object(Blendimportarbeiter, 'lebt', return_value=False), \
                mock.patch.object(Blendimportarbeiter, 'laufender', return_value=None):
            antwort = self._neu(QUELLE)
        self.assertEqual(antwort.status_code, 200)
        starten.assert_called_once()


class QuelltextTest(SimpleTestCase):
    databases = set()

    def test_1_neu_berechnen_uebernimmt_zuerst_und_rechnet_ein_neues_netz_von_vorn(self):
        quelltext = lesen('static', 'viewer', 'mesh3d', 'mesh3dlauf.js')
        self.assertIn('this.seite.quelle.vorStart()', quelltext)
        self.assertIn('if (quelle === false) return;', quelltext)
        self.assertIn('if (quelle?.neues_netz) ab = null;', quelltext)
        quelle = lesen('static', 'viewer', 'mesh3d', 'mesh3dquelle.js')
        self.assertIn('async vorStart()', quelle)
        self.assertIn('offen()', quelle)
        self.assertIn('return antwort;', quelle, '`uebernehmen` meldet die Antwort zurück')

    def test_2_die_mesh_ansicht_leert_sich_ohne_netz(self):
        quelltext = lesen('static', 'viewer', 'mesh3d', 'mesh3dnetzbuehne.js')
        self.assertIn('this._leeren();', quelltext)
        self.assertIn('this.netze.entfernen();', quelltext)
        self.assertIn('this.netze._schluessel = null;', quelltext)

    def test_3_ohne_figur_keine_stehengebliebene_figurid(self):
        quelltext = lesen('static', 'viewer', 'mesh3d', 'mesh3dbuehne.js')
        self.assertIn('this.figurId = null;', quelltext)

    def test_4_die_kopierfrage_sagt_ohne_netz(self):
        self.assertIn('OHNE Netz', lesen('static', 'viewer', 'mesh3d', 'mesh3dkopie.js'))
