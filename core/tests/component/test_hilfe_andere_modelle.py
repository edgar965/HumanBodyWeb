# -*- coding: utf-8 -*-
u"""Hilfe -> Architektur -> Andere Modelle: die Seite steht, ihre Zahlen
kommen aus Python, und die Bildrouten geben nur die eigenen Bilder her.

Edgar (17.09.2026): „mach diese Liste als HTML-Datei: Hilfe - Architektur -
Andere Modelle" — „ich brauche ganze Körper, mach getrennte Liste für nur
Kopf" — „schreibe in die Liste auch MakeHuman, mein HumanBody, UMA, SMPL
und SMPL-X, mach die alle rot und vergib denen auch einen Rang". Geprueft:

1. Die Seite antwortet, haengt im Menue und laesst die djangoBase-Seiten
   stehen (dort ist das Projekt am 27.08.2026 schon einmal hineingelaufen).
2. Jede Quelle beider Listen, jedes Urteil und jede Adresse steht auf der
   Seite; beide Tabellen sind djangoBase-Tabellen; ohne Rang heisst so; der
   Rang folgt der Vergleichszahl (Dreiecke der hoechsten Stufe).
3. Die fuenf eigenen Figurarten stehen rot und mit Rang in der Koerperliste.
4. Die Bildrouten liefern nur bekannte Ordner und Dateinamen — ein `..`
   oder ein fremder Name ist eine 404, nie ein Pfad in die Platte.
"""
from pathlib import Path
from unittest import mock

from django.test import Client, SimpleTestCase
from django.urls import resolve, reverse
from django.utils.html import escape

from core.dienste.figurbilder import Figurbilder
from core.dienste.figurkoepfe import Figurkoepfe
from core.dienste.figurquellen import Figurquellen
from core.dienste.figurquellenlinks import Figurquellenlinks
from core.tests.unit._pruefablage import Pruefablage

#: Seit 17.09.2026 auch Genesis 9 — als Figurart im Haus, privat (Daz-EULA).
EIGENE = ('HumanBody (MB-Lab-Netz)', 'MakeHuman (MPFB2)',
          'UMA (Unity Multipurpose Avatar)', 'SMPL-X', 'SMPL', 'Daz Genesis 9')


class SeiteAndereModelle(SimpleTestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.antwort = Client().get(reverse('hilfe_andere_modelle'))
        cls.text = cls.antwort.content.decode('utf-8')

    def test_antwortet_unter_deutscher_adresse(self):
        self.assertEqual(self.antwort.status_code, 200)
        self.assertEqual(reverse('hilfe_andere_modelle'),
                         '/hilfe/architektur/andere-modelle/')

    def test_haengt_im_menue_und_djangobase_bleibt_erreichbar(self):
        self.assertIn('href="/hilfe/architektur/andere-modelle/"', self.text)
        self.assertIn('Architektur', self.text)
        # `resolve` statt GET: Die Versionen-Seite fragt GitHub (6,8 s) —
        # gefragt ist nur, dass der eigene Praefix djangoBase nicht verdeckt.
        self.assertIn('djangobase', resolve('/hilfe/versionen/').func.__module__)

    def test_jede_quelle_jedes_urteil_jede_adresse_steht_auf_der_seite(self):
        for kennung, liste in (('koerper', Figurquellen.rangliste()),
                               ('kopf', Figurkoepfe.rangliste())):
            for e in liste:
                self.assertIn(escape(e['name']), self.text)
                self.assertIn(escape(e['urteil']), self.text)
                self.assertIn('id="%s-%s"' % (kennung, e['ordner']), self.text)
        for adresse in Figurquellenlinks.alle():
            self.assertIn('href="%s"' % escape(adresse), self.text)
        self.assertIn(escape(Figurquellen.BEFUND), self.text)

    def test_beide_tabellen_sind_djangobase_tabellen(self):
        for kennung in ('koerper', 'kopf'):
            self.assertIn('id="andereModelle-%s"' % kennung, self.text)
            self.assertIn('data-sort-key="hilfe-andere-modelle-%s"' % kennung,
                          self.text)
        self.assertEqual(self.text.count('class="db-tabelle sortable am-tabelle"'), 2)
        self.assertEqual(self.text.count('class="db-tabelle-rahmen"'), 2)
        # Je Tabelle zwei Spalten ohne Sortierung: Webseite und Bild.
        self.assertEqual(self.text.count('data-sort-aus="1"'), 4)
        self.assertEqual(self.text.count('<th data-sort-aus="1">Webseite</th>'), 2)

    def test_rang_und_ohne_rang(self):
        for e in Figurquellen.mit_rang() + Figurkoepfe.mit_rang():
            self.assertIn('data-sort="%d"' % e['rang'], self.text)
        self.assertIn('Rang 1 bis %d' % len(Figurquellen.mit_rang()), self.text)
        ohne = len(Figurquellen.ohne_rang()) + len(Figurkoepfe.ohne_rang())
        # Tabelle und Karte nennen es je einmal.
        self.assertEqual(self.text.count('>ohne Rang<'), 2 * ohne)

    def test_der_rang_folgt_der_vergleichszahl(self):
        for liste in (Figurquellen, Figurkoepfe):
            mit = liste.mit_rang()
            dichten = [e['hoechst_dreiecke'] for e in mit]
            self.assertEqual(dichten, sorted(dichten, reverse=True))
            self.assertEqual([e['rang'] for e in mit], list(range(1, len(mit) + 1)))
            for e in liste.ohne_rang():
                self.assertTrue(e['hoechst_dreiecke'] is None or e.get('ohne_rang'),
                                e['name'])

    def test_die_vergleichszahl_steht_in_beiden_tabellen(self):
        for e in Figurquellen.mit_rang() + Figurkoepfe.mit_rang():
            self.assertIn('data-sort="%d">%s<' % (e['hoechst_dreiecke'],
                                                  e['hoechst_text']), self.text)

    def test_die_eigenen_figurarten_stehen_rot_und_mit_rang(self):
        eigene = [e for e in Figurquellen.rangliste() if e.get('eigen')]
        self.assertEqual(sorted(e['name'] for e in eigene), sorted(EIGENE))
        for e in eigene:
            self.assertIsNotNone(e['rang'], e['name'])
        # Je eigene Zeile: die Tabellenzeile und die Karte tragen `am-eigen`.
        self.assertEqual(self.text.count('<tr class="am-eigen">'), len(eigene))
        self.assertEqual(self.text.count('class="am-karte am-eigen"'), len(eigene))
        self.assertFalse(any(e.get('eigen') for e in Figurkoepfe.rangliste()))

    def test_mb_lab_original_steht_zum_vergleich_neben_humanbody(self):
        u"""Edgar: „eine Zeile MB-Lab, damit wir vergleichen können, ob ich
        mehr oder weniger habe" — dasselbe Basisnetz; bis zum 17.09.2026
        rendert das Original mit drei Unterteilungen mehr, seitdem rechnet
        der Port dieselben drei Stufen: gleich viel, Nachbarränge."""
        zeilen = {e['ordner']: e for e in Figurquellen.rangliste()}
        hb, mblab = zeilen['00_eigene_Renderings'], zeilen['MB-Lab']
        self.assertEqual((hb['punkte'], hb['vierecke']),
                         (mblab['punkte'], mblab['vierecke']))
        self.assertEqual(mblab['hoechst_dreiecke'], hb['hoechst_dreiecke'])
        self.assertEqual(abs(mblab['rang'] - hb['rang']), 1)
        self.assertEqual(self.text.count('<tr class="am-ursprung">'), 1)
        self.assertEqual(self.text.count('class="am-karte am-ursprung"'), 1)

    def test_die_lesehilfe_rechnet_mit_den_zeilen_der_tabelle(self):
        zeilen = {e['ordner']: e for e in Figurquellen.rangliste()}
        hb, g9 = zeilen['00_eigene_Renderings'], zeilen['11_Daz_Genesis9']
        self.assertIn('Lesehilfe', self.text)
        self.assertIn('%s Punkte, %s Vierecke, %s Dreiecke' % (
            hb['basis_punkte_text'], hb['basis_vierecke_text'],
            hb['basis_dreiecke_text']), self.text)
        self.assertIn('%s → %s Dreiecke' % (g9['stufen_text'], g9['hoechst_text']),
                      self.text)

    def test_jede_zeile_hat_einen_linkblock(self):
        for e in Figurquellen.rangliste() + Figurkoepfe.rangliste():
            schluessel = e.get('linkschluessel', e['ordner'])
            self.assertTrue(Figurquellenlinks.fuer(schluessel), schluessel)


class Bildrouten(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.client = Client()
        self.ordner = '00_eigene_Renderings'
        self.dateien = Figurbilder.dateien(self.ordner)

    def test_fremde_pfade_sind_keine_bilder(self):
        for ordner, datei in (('..', 'LINKS.md'), (self.ordner, '..'),
                              (self.ordner, 'LINKS.md'),
                              ('gibt_es_nicht', 'x.png'),
                              (self.ordner, '.htaccess.png')):
            with self.subTest(ordner=ordner, datei=datei):
                self.assertIsNone(Figurbilder.quelle(ordner, datei))
                self.assertIsNone(Figurbilder.vorschau(ordner, datei))
        self.assertEqual(self.client.get(
            '/hilfe/architektur/andere-modelle/bild/gibt_es_nicht/x.png'
        ).status_code, 404)

    def test_original_und_vorschau_kommen_als_bild(self):
        if not self.dateien:
            self.skipTest('keine Renderings unter %s' % Figurbilder.ORDNER)
        datei = self.dateien[0]
        antwort = self.client.get(reverse('hilfe_andere_modelle_bild',
                                          args=[self.ordner, datei]))
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort['Content-Type'], Figurbilder.typ(datei))
        antwort.close()
        with Pruefablage.ordner('figurbilder_') as ablage, \
                mock.patch.object(Figurbilder, 'ABLAGE', Path(ablage)):
            antwort = self.client.get(reverse('hilfe_andere_modelle_vorschau',
                                              args=[self.ordner, datei]))
            self.assertEqual(antwort.status_code, 200)
            self.assertEqual(antwort['Content-Type'], 'image/jpeg')
            antwort.close()
            ziel = Path(ablage) / self.ordner / (datei + '.jpg')
            self.assertTrue(ziel.is_file())
            self.assertLess(ziel.stat().st_size,
                            (Figurbilder.ORDNER / self.ordner / datei).stat().st_size)
