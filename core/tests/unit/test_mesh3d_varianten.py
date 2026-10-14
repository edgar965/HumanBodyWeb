# -*- coding: utf-8 -*-
"""Varianten, Vergleich, Abnahme und die Vorgaben des Wegs „netz“ (13.10.2026, Konzept „Mesh-3D ohne Nacharbeit“). Nicht gelaufen — läuft nur auf Ansage.

Ohne Blender, GPU und Datenbank: die Aufträge sind Ordner unter einer umgebogenen `OBJECTS_ROOT` (`Pruefablage`), Netz und Masken sind Kunstdaten.

    DateiTest        `varianten.json`: ohne Datei oder kaputt keine Varianten, Hin und Zurück, ein `haupt` ohne Eintrag gilt nicht
    AnlegenTest      `Mesh3dvarianten.anlegen`: unbekanntes Feld, Weg „teile“, nichts zu rechnen, zu viele — jeweils mit Grund und ohne etwas anzulegen
    VergleichTest    Dominanz: nur wer in allen gewerteten Zeilen nicht schlechter und in einer deutlich besser ist; Rauschen zählt nicht; zu wenige Zeilen geben keine Empfehlung
    FlaechenTest     `Meshfigurobjektflaechen` (schreiben, lesen, leeren) und `Meshfigurabnahmeobjekte` (Doppelte, Waisen, Hut, Hautband)
    NebenlaufTest    `Meshfigurnebenlauf.voraussetzungen`: nur laufende Fäden, nur die aus `NEBEN_NACH`
    WegTest          Vorgaben des Wegs „netz“, `POST /api/mesh3d/anlegen/` ohne Grundfigur → 400
    VerdrahtungTest  Wächter (Quelltext gelesen): Routen, Karte, Auswahl „Ausgabe“, Haken in Löschen, Kopie, Start und Vorschau

Sabotage-Gegenprobe: in `Mesh3dvergleich._schlaegt` `d <= tol` zu `d <= 1e9` → `test_dominanz_*` rot; `Meshfigurabnahmeobjekte.messen` ohne `doppelt` → `FlaechenTest` rot; `NEBEN_NACH` leeren →
`NebenlaufTest` rot; die Prüfung der Grundfigur in `Mesh3dendpunkte.anlegen` streichen → `test_anlegen_ohne_grundfigur` rot; `varianten.json` aus `Ordnerkopie.NIE_NAMEN` nehmen → `test_kopie_nimmt_varianten_nicht_mit` rot.
"""

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import RequestFactory, SimpleTestCase, override_settings

from core.api.mesh3d import Mesh3dendpunkte
from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportweg import Blendimportweg
from core.dienste.mesh3dvarianten import Mesh3dvarianten
from core.dienste.mesh3dvergleich import Mesh3dvergleich
from core.dienste.meshfigurabnahmeobjekte import Meshfigurabnahmeobjekte
from core.dienste.meshfigurlauf import Meshfigurlauf
from core.dienste.meshfigurnebenlauf import Meshfigurnebenlauf
from core.dienste.meshfigurobjektflaechen import Meshfigurobjektflaechen
from core.dienste.ordnerkopie import Ordnerkopie

from ._pruefablage import Pruefablage

WEB = Path(__file__).resolve().parents[3]
KENNUNG = '2026.10.13.10.00.00'


class _Ablage(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='mesh3dvarianten_', dir=Pruefablage.wurzel()))
        self.umlenkung = override_settings(OBJECTS_ROOT=self.tmp)
        self.umlenkung.enable()
        self.ablage = Blendimportablage(KENNUNG)
        self.ablage.anlegen()

    def tearDown(self):
        self.umlenkung.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _stand(self, **felder):
        self.ablage.stand_schreiben({'kennung': KENNUNG, 'status': 'fertig', 'bereich': 'mesh3d', 'weg': 'netz', 'quelle': {'name': 'Probe'}, 'einstellungen': {'kleidung_zug': 'nah', 'basis': 'feminine', 'pose': 'sam'}, **felder})


class DateiTest(_Ablage):
    def test_ohne_datei_gibt_es_keine_varianten(self):
        self.assertEqual(Mesh3dvarianten.lesen(KENNUNG), {'eintraege': [], 'haupt': None, 'vorher': {}})

    def test_eine_kaputte_datei_ist_kein_absturz(self):
        Mesh3dvarianten.pfad(KENNUNG).write_text('{kaputt', encoding='utf-8')
        self.assertEqual(Mesh3dvarianten.lesen(KENNUNG)['eintraege'], [])

    def test_hin_und_zurueck(self):
        eintrag = {'id': 'a', 'kennung': '2026.10.13.10.01.00', 'feld': 'kleidung_zug', 'wert': 'ignorieren', 'titel': 'x'}
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': [eintrag], 'haupt': 'a', 'vorher': {'kleidung_zug': 'nah'}})
        gelesen = Mesh3dvarianten.lesen(KENNUNG)
        self.assertEqual(gelesen['eintraege'], [eintrag])
        self.assertEqual((gelesen['haupt'], gelesen['vorher']), ('a', {'kleidung_zug': 'nah'}))

    def test_ein_haupt_ohne_eintrag_gilt_nicht(self):
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': [], 'haupt': 'weg'})
        self.assertIsNone(Mesh3dvarianten.lesen(KENNUNG)['haupt'])

    def test_unbekanntes_feld(self):
        with self.assertRaises(ValueError):
            Mesh3dvarianten.feld('scham')

    def test_aktuell_hat_die_vorgaben_des_katalogs(self):
        self.assertEqual(Mesh3dvarianten.aktuell({}, 'kleidung_zug'), 'weich')
        self.assertEqual(Mesh3dvarianten.aktuell({}, 'pose'), 'aus')
        self.assertEqual(Mesh3dvarianten.aktuell({'einstellungen': {'basis': 'masculine'}}, 'basis'), 'masculine')


class AnlegenTest(_Ablage):
    def setUp(self):
        super().setUp()
        self.umgebung = [mock.patch('core.dienste.mesh3dvarianten.Blendimportarbeiter.lebt', return_value=False), mock.patch('core.dienste.mesh3dvarianten.Blendimportarbeiter.laufender', return_value=None),
                         mock.patch('core.dienste.mesh3dvariantenlauf.Mesh3dvariantenlauf.lebt', return_value=False), mock.patch.object(Mesh3dvarianten, '_hauptauftrag', return_value=None)]
        for m in self.umgebung:
            m.start()

    def tearDown(self):
        for m in self.umgebung:
            m.stop()
        super().tearDown()

    def test_unbekanntes_feld(self):
        self._stand()
        with self.assertRaises(ValueError):
            Mesh3dvarianten.anlegen(KENNUNG, 'scham')

    def test_nur_der_weg_netz(self):
        self._stand(weg='teile')
        with self.assertRaisesRegex(ValueError, 'Weg'):
            Mesh3dvarianten.anlegen(KENNUNG, 'kleidung_zug')
        self.assertFalse(Mesh3dvarianten.pfad(KENNUNG).exists())

    def test_ein_unbekannter_wert(self):
        self._stand()
        with self.assertRaisesRegex(ValueError, 'Unbekannter Wert'):
            Mesh3dvarianten.anlegen(KENNUNG, 'kleidung_zug', ['gibtsnicht'])

    def test_nichts_zu_rechnen_wenn_jeder_wert_schon_da_ist(self):
        self._stand()                                                              # Hauptausgabe: nah
        eintraege = [{'id': w, 'kennung': 'k' + w, 'feld': 'kleidung_zug', 'wert': w, 'titel': w} for w in ('ignorieren', 'weich')]
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': eintraege})
        with self.assertRaisesRegex(ValueError, 'Nichts zu rechnen'):
            Mesh3dvarianten.anlegen(KENNUNG, 'kleidung_zug')

    def test_der_wert_des_ersten_laufs_nach_dem_uebernehmen_zaehlt_als_vorhanden(self):
        self._stand(einstellungen={'kleidung_zug': 'ignorieren', 'basis': 'feminine', 'pose': 'sam'})
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': [{'id': 'a', 'kennung': 'ka', 'feld': 'kleidung_zug', 'wert': 'ignorieren', 'titel': 'x'},
                                                          {'id': 'b', 'kennung': 'kb', 'feld': 'kleidung_zug', 'wert': 'weich', 'titel': 'y'}], 'vorher': {'kleidung_zug': 'nah'}})
        with self.assertRaisesRegex(ValueError, 'Nichts zu rechnen'):
            Mesh3dvarianten.anlegen(KENNUNG, 'kleidung_zug')                      # nah hat der erste Lauf, ignorieren die übernommene Variante, weich die andere

    def test_zu_viele_varianten(self):
        self._stand()
        voll = [{'id': str(i), 'kennung': 'k%d' % i, 'feld': 'basis', 'wert': 'x', 'titel': 't'} for i in range(Mesh3dvarianten.HOECHSTENS)]
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': voll})
        with self.assertRaisesRegex(ValueError, 'Höchstens'):
            Mesh3dvarianten.anlegen(KENNUNG, 'kleidung_zug')

    def test_ein_laufender_import_sperrt(self):
        self._stand()
        with mock.patch('core.dienste.mesh3dvarianten.Blendimportarbeiter.lebt', return_value=True), self.assertRaisesRegex(ValueError, 'rechnet'):
            Mesh3dvarianten.anlegen(KENNUNG, 'kleidung_zug')


def _spalte(id_, **werte):
    voll = {'figur_netz_rms_mm': 3.0, 'netz_figur_rms_mm': 5.0, 'stoff_im_koerper_prozent': 6.0, 'stoff_tief_prozent': 3.0, 'hand_l_mm': 17.0, 'hand_r_mm': 17.0, 'doppelt': 0, 'waisen_rest': 0}
    voll.update(werte)
    return {'id': id_, 'wert': id_, 'werte': voll, 'status': 'fertig'}


class VergleichTest(SimpleTestCase):
    def test_dominanz_wer_ueberall_mindestens_so_gut_und_einmal_deutlich_besser_ist(self):
        a, b = _spalte('a'), _spalte('b', stoff_im_koerper_prozent=9.0)
        self.assertEqual(Mesh3dvergleich.dominanz([a, b])['id'], 'a')

    def test_dominanz_gemischt_gibt_keine_empfehlung(self):
        a, b = _spalte('a', stoff_im_koerper_prozent=2.0, figur_netz_rms_mm=4.0), _spalte('b')
        self.assertIsNone(Mesh3dvergleich.dominanz([a, b]))                         # a bei Stoff besser, bei Figur→Netz schlechter

    def test_dominanz_unterschiede_im_rauschen_zaehlen_nicht(self):
        a, b = _spalte('a', figur_netz_rms_mm=3.1, hand_l_mm=18.5), _spalte('b')
        self.assertIsNone(Mesh3dvergleich.dominanz([a, b]))

    def test_dominanz_umfaenge_zaehlen_nicht(self):
        a, b = _spalte('a', oberschenkel_cm=51.0), _spalte('b', oberschenkel_cm=103.0)
        self.assertIsNone(Mesh3dvergleich.dominanz([a, b]))                         # ein kleinerer Umfang ist nicht „besser“

    def test_dominanz_zu_wenige_vergleichbare_zeilen(self):
        a = {'id': 'a', 'wert': 'a', 'werte': {'figur_netz_rms_mm': 1.0, 'doppelt': 0}, 'status': 'fertig'}
        b = {'id': 'b', 'wert': 'b', 'werte': {'figur_netz_rms_mm': 9.0, 'doppelt': 0}, 'status': 'fertig'}
        self.assertIsNone(Mesh3dvergleich.dominanz([a, b]))
        self.assertIsNone(Mesh3dvergleich.dominanz([a]))

    def test_werte_aus_der_abnahme_und_ohne_sie(self):
        mit = Mesh3dvergleich.werte({'abnahme': {'figur_netz': {'figur_netz_rms_mm': 2.4}, 'stoff_im_koerper': {'unter_0_prozent': 9.92, 'unter_5mm_prozent': 7.64},
                                                 'abstand_je_teil_mm': {'Hand L': 16.0, 'Hand R': 17.0}, 'masse_cm': {'oberschenkel_umfang': 51.4}, 'hoehe_cm': 193.4,
                                                 'objekte': {'doppelt': 0, 'waisen_rest': 12}}})
        self.assertEqual((mit['figur_netz_rms_mm'], mit['stoff_im_koerper_prozent'], mit['hand_l_mm'], mit['oberschenkel_cm'], mit['waisen_rest']), (2.4, 9.92, 16.0, 51.4, 12.0))
        ohne = Mesh3dvergleich.werte({'vorschau': {'hoehe_cm': 190.0, 'abstand': {'figur_netz_rms_mm': 3.34, 'netz_figur_rms_mm': 8.7}}})   # ein Lauf vor dem 13.10.2026
        self.assertEqual((ohne['figur_netz_rms_mm'], ohne['hoehe_cm'], ohne['stoff_im_koerper_prozent']), (3.34, 190.0, None))


class _Netz:
    """Ein Netz mit `n` Flächen von je 1 cm²."""

    def __init__(self, n):
        self.flaechen = np.zeros((n, 3), dtype=int)

    def flaecheninhalte(self):
        return np.full(len(self.flaechen), 1e-4)


class _Ablage2:
    def __init__(self, ordner):
        self.ordner = Path(ordner)

    def arbeit(self, name=''):
        return self.ordner / name if name else self.ordner


class FlaechenTest(SimpleTestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='objektflaechen_', dir=Pruefablage.wurzel()))
        self.ablage = _Ablage2(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _maske(self, n, *bereiche):
        m = np.zeros(n, dtype=bool)
        for von, bis in bereiche:
            m[von:bis] = True
        return m

    def test_schreiben_lesen_leeren(self):
        Meshfigurobjektflaechen.schreiben(self.ablage, 'kleidung', self._maske(10, (0, 4)))
        Meshfigurobjektflaechen.schreiben(self.ablage, 'teil_hat', self._maske(10, (4, 6)))
        gelesen = Meshfigurobjektflaechen.lesen(self.ablage)
        self.assertEqual(sorted(gelesen), ['kleidung', 'teil_hat'])
        self.assertEqual(int(gelesen['kleidung'].sum()), 4)
        Meshfigurobjektflaechen.leeren(self.ablage)
        self.assertEqual(Meshfigurobjektflaechen.lesen(self.ablage), {})

    def _lauf(self, ergebnis=None):
        return SimpleNamespace(ablage=self.ablage, job=SimpleNamespace(ergebnis=ergebnis or {}))

    def test_doppelte_waisen_und_hut(self):
        n = 20
        np.savez_compressed(self.ablage.arbeit('haar_maske.npz'), haar=self._maske(n, (0, 3)), kopfbedeckung=self._maske(n, (10, 16)), langer_bart=self._maske(n))
        np.savez_compressed(self.ablage.arbeit('kleidung_maske.npz'), kleidung=self._maske(n, (3, 10)))
        Meshfigurobjektflaechen.schreiben(self.ablage, 'haar', self._maske(n, (0, 4)))                 # Fläche 3 steht auch in der Kleidung: doppelt
        Meshfigurobjektflaechen.schreiben(self.ablage, 'kleidung', self._maske(n, (3, 9)))             # Fläche 9 fehlt: Waise der Kleidung
        Meshfigurobjektflaechen.schreiben(self.ablage, 'teil_hat', self._maske(n, (10, 13)))           # vom Hut nur drei von sechs Flächen: drei Waisen
        a = Meshfigurabnahmeobjekte(self._lauf()).messen(_Netz(n))
        self.assertEqual(a['doppelt'], 1)
        self.assertEqual(a['doppelt_je_paar'], {'haar+kleidung': 1})
        self.assertEqual(a['hut'], {'flaechen': 6, 'in_kleidung': 0, 'in_haar': 0, 'in_teilen': {'hat': 3}, 'nirgends': 3})
        self.assertEqual((a['waisen'], a['waisen_je_quelle']['hut'], a['waisen_je_quelle']['kleidung']), (4, 3, 1))
        self.assertEqual(a['urteil'], 'Befund')
        self.assertTrue(any('Hutflächen' in h for h in a['hinweise']))

    def test_das_hautband_ist_keine_waise_aus_versehen(self):
        n = 200
        np.savez_compressed(self.ablage.arbeit('haar_maske.npz'), haar=self._maske(n), kopfbedeckung=self._maske(n), langer_bart=self._maske(n))
        np.savez_compressed(self.ablage.arbeit('kleidung_maske.npz'), kleidung=self._maske(n, (0, 100)))
        Meshfigurobjektflaechen.schreiben(self.ablage, 'kleidung', self._maske(n, (0, 99)))            # eine Fläche fehlt: das Hautband am Rand
        a = Meshfigurabnahmeobjekte(self._lauf({'kleidung': {'objekt_hautrand': {'flaechen': 1}}})).messen(_Netz(n))
        self.assertEqual((a['waisen'], a['davon_hautrand'], a['waisen_rest']), (1, 1, 0))
        self.assertEqual(a['urteil'], 'in Ordnung')

    def test_ohne_aufzeichnung_nur_ein_hinweis(self):
        self.assertIn('hinweis', Meshfigurabnahmeobjekte(self._lauf()).messen(_Netz(5)))

    def test_eine_maske_in_falscher_laenge_wird_verworfen(self):
        Meshfigurobjektflaechen.schreiben(self.ablage, 'haar', self._maske(7, (0, 2)))
        Meshfigurobjektflaechen.schreiben(self.ablage, 'kleidung', self._maske(5, (0, 2)))
        a = Meshfigurabnahmeobjekte(self._lauf()).messen(_Netz(5))
        self.assertEqual(a['verworfen'], ['haar'])


class NebenlaufTest(SimpleTestCase):
    def test_nur_laufende_faeden_aus_neben_nach(self):
        faden = object()
        lauf = SimpleNamespace(NEBEN_NACH=Meshfigurlauf.NEBEN_NACH)
        self.assertEqual(Meshfigurnebenlauf.voraussetzungen(lauf, {'haar': (faden, None, {})}, 'kleidung'), (faden,))
        self.assertEqual(Meshfigurnebenlauf.voraussetzungen(lauf, {}, 'kleidung'), ())                 # Neulauf ab „kleidung“: kein Haar-Faden
        self.assertEqual(Meshfigurnebenlauf.voraussetzungen(lauf, {'haar': (faden, None, {})}, 'haar'), ())
        self.assertEqual(Meshfigurnebenlauf.voraussetzungen(SimpleNamespace(), {'haar': (faden, None, {})}, 'kleidung'), ())   # eine Unterklasse ohne Tabelle wartet auf nichts


class WegTest(SimpleTestCase):
    def test_vorgaben_des_wegs_netz(self):
        self.assertEqual(Blendimportweg.VORGABEN_NETZ, {'pose': 'sam', 'kleidung_zug': 'ignorieren'})
        self.assertTrue(set(Blendimportweg.VORGABEN_NETZ) <= set(Blendimportweg.MODELLABHAENGIG))

    def test_anlegen_ohne_grundfigur(self):
        anfrage = RequestFactory().post('/api/mesh3d/anlegen/', data=json.dumps({'format': 'glb', 'werte': {'pfad': 'x.glb'}}), content_type='application/json')
        antwort = Mesh3dendpunkte.anlegen(anfrage)
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('Grundfigur', json.loads(antwort.content)['error'])

    def test_anlegen_mit_unbekannter_grundfigur(self):
        anfrage = RequestFactory().post('/api/mesh3d/anlegen/', data=json.dumps({'format': 'glb', 'werte': {'pfad': 'x.glb', 'basis': 'kind'}}), content_type='application/json')
        self.assertEqual(Mesh3dendpunkte.anlegen(anfrage).status_code, 400)

    def test_kopie_nimmt_varianten_nicht_mit(self):
        self.assertTrue({'varianten.json', 'varianten.pid', 'varianten.log'} <= Ordnerkopie.NIE_NAMEN)


class VerdrahtungTest(SimpleTestCase):
    def _text(self, *teile):
        return WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_routen_karte_und_ausgabe(self):
        urls = self._text('core', 'urls_mesh3d.py')
        for name in ('mesh3d_varianten', 'mesh3d_varianten_uebernehmen', 'mesh3d_varianten_loeschen', 'mesh3d_varianten_anhalten'):
            self.assertIn("name='%s'" % name, urls)
        vorlage = self._text('templates', 'mesh3d_auftrag.html')
        for kennung in ('id="varianten-karte"', 'id="varianten-vergleiche"', 'id="buehne-ausgabe"', 'id="varianten-anhalten"'):
            self.assertIn(kennung, vorlage)
        seite = self._text('static', 'viewer', 'mesh3d', 'mesh3dseite.js')
        self.assertIn('new Mesh3dvarianten(this)', seite)
        self.assertIn('einstellungSetzen', seite)
        self.assertIn('ausgabeWaehlen', self._text('static', 'viewer', 'mesh3d', 'mesh3dbuehne.js'))
        self.assertIn("'kleidung_zug'", self._text('static', 'viewer', 'mesh3d', 'mesh3dquelle.js'))

    def test_formular_erbt_nichts_vom_letzten_auftrag(self):
        neu = self._text('static', 'viewer', 'mesh3d', 'mesh3dneu.js')
        self.assertIn("NICHT_ERBEN = ['pose', 'pose_drehung', 'kleidung_zug']", neu)
        self.assertIn("this.werte.basis = ''", neu)

    def test_haken_in_loeschen_start_vorschau_und_zustand(self):
        self.assertIn('alle_entfernen', self._text('core', 'dienste', 'blendimportloeschen.py'))
        self.assertIn('haupt_loesen', self._text('core', 'dienste', 'blendimportarbeiter.py'))
        vorschau = self._text('core', 'dienste', 'meshfigurvorschau.py')
        self.assertIn('Meshfigurabnahme.sicher(self.lauf)', vorschau)
        self.assertIn('Meshfigurobjektflaechen.leeren', vorschau)
        self.assertIn("'varianten': Mesh3dvergleich.von", self._text('core', 'dienste', 'mesh3dzustand.py'))
        for datei in ('meshfigurkleidung.py', 'meshfigurhaar.py', 'meshfigurteile.py'):
            self.assertIn('Meshfigurobjektflaechen.schreiben', self._text('core', 'dienste', datei), datei)
