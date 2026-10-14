# -*- coding: utf-8 -*-
"""Die Adresse eines Mesh-3D-Auftrags mit dem Namen darin (13.10.2026, `Mesh3dlink`) — Edgar: „/mesh-3D/2026.10.11.21.18.17/ → neu: /mesh-3D/edgar_2026.10.11.21.18.17/“.

    NameTest      Umlaute, Sonderzeichen, Länge, leer
    OrtTest       `<name>_<kennung>`, die Kennung wird auch mit falschem oder fehlendem Namen gefunden, Unsinn nicht
    SeiteTest     die Seite antwortet auf die gültige Adresse mit 200, auf die reine Kennung und auf einen alten Namen mit der Umleitung auf die gültige, auf Unsinn mit 404 (Zustand attrappiert)
    VerdrahtungTest  Wächter (Quelltext): Route nimmt `<str:ort>`, Tabelle, Kopie und Anlegen liefern den Namenslink, die Liste klickt auf den Link der Zeile

Nicht gelaufen — läuft nur auf Ansage. Sabotage: in `Mesh3dendpunkte.seite` den Vergleich `ort != gueltig` streichen → `test_alte_adresse_leitet_um` rot; in `name_im_link` die Umlaut-Tabelle streichen → `test_umlaute_werden_ausgeschrieben` rot.
"""

from pathlib import Path
from unittest import mock

from django.test import Client, SimpleTestCase

from core.dienste.mesh3dlink import Mesh3dlink

WEB = Path(__file__).resolve().parents[3]
KENNUNG = '2026.10.11.21.18.17'


class NameTest(SimpleTestCase):
    def test_umlaute_werden_ausgeschrieben(self):
        self.assertEqual(Mesh3dlink.name_im_link('Polstertänzer neu'), 'polstertaenzer_neu')
        self.assertEqual(Mesh3dlink.name_im_link('Straße & Müll!'), 'strasse_muell')

    def test_gross_klein_und_leerzeichen(self):
        self.assertEqual(Mesh3dlink.name_im_link('Spiralballerina ohne Zweitarm'), 'spiralballerina_ohne_zweitarm')
        self.assertEqual(Mesh3dlink.name_im_link('  Edgar - S1 (nah)  '), 'edgar_s1_nah')

    def test_leer_und_zu_lang(self):
        self.assertEqual(Mesh3dlink.name_im_link(''), '')
        self.assertEqual(Mesh3dlink.name_im_link('   '), '')
        self.assertEqual(Mesh3dlink.name_im_link('!!!'), '')
        lang = Mesh3dlink.name_im_link('a' * 100)
        self.assertEqual(len(lang), Mesh3dlink.NAME_MAX)
        self.assertFalse(lang.endswith('_'))


class OrtTest(SimpleTestCase):
    def test_pfad_enthaelt_name_und_kennung(self):
        self.assertEqual(Mesh3dlink.pfad(KENNUNG, 'Edgar'), '/mesh-3D/edgar_%s/' % KENNUNG)

    def test_ohne_brauchbaren_namen_nur_die_kennung(self):
        self.assertEqual(Mesh3dlink.ort(KENNUNG, ''), KENNUNG)
        self.assertEqual(Mesh3dlink.pfad(KENNUNG, '???'), '/mesh-3D/%s/' % KENNUNG)

    def test_kennung_wird_gefunden_mit_richtigem_falschem_oder_fehlendem_namen(self):
        for ort in ('edgar_%s' % KENNUNG, 'falsch_%s' % KENNUNG, KENNUNG, 'zwei_woerter_%s' % KENNUNG):
            self.assertEqual(Mesh3dlink.kennung_aus(ort), KENNUNG, ort)

    def test_unsinn_hat_keine_kennung(self):
        for ort in ('unsinn', 'edgar_2026.10.11', '', None, 'edgar_%s_zusatz' % KENNUNG, 'EDGAR_%s' % KENNUNG):
            self.assertIsNone(Mesh3dlink.kennung_aus(ort), ort)


class SeiteTest(SimpleTestCase):
    databases = set()

    def _antwort(self, pfad):
        zustand = {'name': 'Edgar', 'format': 'glb'}
        with mock.patch('core.api.mesh3d.Mesh3dzustand.von', side_effect=lambda k: zustand if k == KENNUNG else None), \
                mock.patch('core.api.mesh3d.render', side_effect=lambda request, vorlage, kontext: __import__('django.http', fromlist=['HttpResponse']).HttpResponse('seite')):
            return Client(HTTP_HOST='127.0.0.1').get(pfad)

    def test_gueltige_adresse_zeigt_die_seite(self):
        self.assertEqual(self._antwort('/mesh-3D/edgar_%s/' % KENNUNG).status_code, 200)

    def test_alte_adresse_leitet_um(self):
        r = self._antwort('/mesh-3D/%s/' % KENNUNG)
        self.assertEqual((r.status_code, r['Location']), (302, '/mesh-3D/edgar_%s/' % KENNUNG))

    def test_alter_name_leitet_auf_den_neuen_um(self):
        r = self._antwort('/mesh-3D/falsch_%s/' % KENNUNG)
        self.assertEqual((r.status_code, r['Location']), (302, '/mesh-3D/edgar_%s/' % KENNUNG))

    def test_unsinn_und_unbekannte_kennung_sind_404(self):
        self.assertEqual(self._antwort('/mesh-3D/unsinn/').status_code, 404)
        self.assertEqual(self._antwort('/mesh-3D/edgar_2099.01.01.00.00.00/').status_code, 404)


class VerdrahtungTest(SimpleTestCase):
    def _text(self, *teile):
        return WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_route_nimmt_den_ort(self):
        self.assertIn("path('mesh-3D/<str:ort>/', Mesh3dendpunkte.seite", self._text('core', 'urls_mesh3d.py'))

    def test_tabelle_kopie_und_anlegen_liefern_den_namenslink(self):
        self.assertIn('Mesh3dlink.pfad(kennung, quelle.get(', self._text('core', 'dienste', 'mesh3dtabelle.py'))
        self.assertIn("'url': Mesh3dlink.pfad(kennung, name)", self._text('core', 'api', 'mesh3dkopie.py'))
        self.assertIn("'link': Mesh3dlink.pfad(kennung", self._text('core', 'api', 'mesh3d.py'))
        self.assertIn('antwort.link', self._text('static', 'viewer', 'mesh3d', 'mesh3dneu.js'))

    def test_die_liste_klickt_auf_den_link_der_zeile(self):
        self.assertIn('a[href^="/mesh-3D/"]', self._text('static', 'viewer', 'mesh3d', 'mesh3dliste.js'))
