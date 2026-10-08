# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> ARP Modell und der Eintrag „cute girl" in „Andere Modelle" (Edgar, 08.10.2026).

WARUM: „mach eine neue Seite Hilfe - Architektur - ARP Modell mit diesen Infos und füge alle Infos zum Mesh typ rein. Füge
das Modell auch in die Seite …/andere-modelle/ ein mit den Infos". Zwei Seiten tragen dieselben Eckdaten (Punkte,
Dreiecke, Endabstand); der Test hält sie zusammen, statt dass eine ihre Zahl still ändert, und prüft, dass die Bilder
da sind, auf die die Seiten zeigen.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase
from django.urls import reverse
from django.utils.html import escape

from core.dienste.arpmodell import Arpmodell
from core.dienste.figurquellen import Figurquellen
from core.dienste.figurquellenblender import Figurquellenblender
from core.dienste.figurquellenlinks import Figurquellenlinks


class SeiteArpModell(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.antwort = Client().get(reverse('hilfe_architektur_arp'))
        cls.text = cls.antwort.content.decode('utf-8')

    def test_antwortet_und_haengt_im_menue(self):
        self.assertEqual(self.antwort.status_code, 200)
        self.assertEqual(reverse('hilfe_architektur_arp'), '/hilfe/architektur/arp-modell/')
        self.assertIn('href="/hilfe/architektur/arp-modell/"', self.text)

    def test_die_knochenkarte_nennt_zu_jedem_segment_der_karte_eine_zeile(self):
        """Haupt-Segmente (ohne Fingerglieder) stehen einzeln in der Tabelle, die Finger in einer Sammelzeile."""
        from Genesis9.arpknochenkarte import G9arpknochenkarte

        einzeln = [s for s in G9arpknochenkarte.SEGMENTE if not s[0].endswith(('1', '2', '3'))]
        self.assertEqual(len(einzeln), len(Arpmodell.KNOCHENKARTE) - 1)
        self.assertEqual(len(G9arpknochenkarte.SEGMENTE) - len(einzeln), 15)

    def test_jedes_netz_und_jedes_meshmerkmal_steht_auf_der_seite(self):
        for name, *_ in Arpmodell.NETZE:
            self.assertIn('<code>%s</code>' % escape(name), self.text, name)
        for merkmal, befund, _wirkung in Arpmodell.MESHTYP:
            self.assertIn(Arpmodell.auszeichnen(befund), self.text, merkmal)
        self.assertIn('<code>custom_normal</code>', self.text)    # Rückticks der Dienst-Texte sind <code> geworden

    def test_knochenkarte_und_messung_stehen_auf_der_seite(self):
        for segment, *_ in Arpmodell.KNOCHENKARTE:
            self.assertIn('<strong>%s</strong>' % segment, self.text)
        for groesse, wert, _beleg in Arpmodell.MESSUNG:
            self.assertIn(escape(groesse), self.text)
            self.assertIn(escape(wert), self.text)

    def test_konzept_c_und_die_fragen_stehen_da(self):
        for satz in ('Konzept C im Einzelnen', 'Würde ein anderes Rig', 'Was „Mesh to 3D" verliert', 'Auto-Rig Pro',
                     'Herkunft und Lizenz'):
            self.assertIn(satz, self.text, satz)       # Vorlagentext, nicht maskiert

    def test_die_bilder_gibt_es(self):
        bilder = settings.BASE_DIR / 'static' / 'img' / 'arp_modell'
        for datei in ('original_vorn.jpg', 'original_seite.jpg', 'original_gesicht.jpg', 'genesis_import_vorn.jpg'):
            self.assertTrue((Path(bilder) / datei).is_file(), datei)
            self.assertIn('/static/img/arp_modell/%s' % datei, self.text)


class EintragAndereModelle(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.antwort = Client().get(reverse('hilfe_andere_modelle'))
        cls.text = cls.antwort.content.decode('utf-8')
        cls.zeile = next(e for e in Figurquellen.rangliste() if e['ordner'] == Figurquellenblender.ZEILEN[0]['ordner'])

    def test_die_zeile_hat_rang_und_steht_blau_in_tabelle_und_karte(self):
        self.assertIsNotNone(self.zeile['rang'])
        self.assertEqual(self.text.count('<tr class="am-blend">'), 1)
        self.assertEqual(self.text.count('class="am-karte am-blend"'), 1)
        self.assertIn('id="koerper-%s"' % self.zeile['ordner'], self.text)

    def test_die_eckdaten_stimmen_mit_der_seite_arp_modell_ueberein(self):
        """Körper: Punkte und Dreiecke der Netz-Tabelle = die der Rangliste; der Endabstand steht in beiden Seiten."""
        koerper = next(n for n in Arpmodell.NETZE if n[0] == 'body')
        self.assertEqual((koerper[2], koerper[3]), (self.zeile['punkte'], self.zeile['dreiecke']))
        for wert in Figurquellenblender.ENDABSTAND_RMS:
            self.assertIn(wert, self.zeile['urteil'])
            self.assertTrue(any(wert in w for _g, w, _b in Arpmodell.MESSUNG), wert)

    def test_die_vorschaubilder_zeigen_auf_vorhandene_dateien(self):
        for adresse, _text in self.zeile['vorschau_statisch']:
            self.assertTrue((Path(settings.BASE_DIR) / adresse.lstrip('/')).is_file(), adresse)
            self.assertIn('src="%s"' % adresse, self.text)

    def test_der_linkblock_fuehrt_auf_die_beiden_seiten(self):
        adressen = [adresse for _t, adresse in Figurquellenlinks.fuer('cute_girl_arp')]
        self.assertEqual(adressen, ['/hilfe/architektur/arp-modell/', '/hilfe/architektur/genesis/'])
