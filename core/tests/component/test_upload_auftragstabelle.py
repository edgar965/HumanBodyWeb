# -*- coding: utf-8 -*-
u"""/process/VideoToBVH/ und /process/: die Auftragsliste ist eine
djangoBase-Tabelle.

Edgar (12.09.2026): „mache die Tabelle mit den Jobs mit der djangoBase
Vorlage für Tabellen, mit sortierbaren Spalten, Checkbox auswählen, Multi-
Select mit Shift und Batch-Delete".

Was die Seite liefern muss, damit `tabellen_auto.js` (Sortierung, Breiten),
`zeilenwahl.js` (Kästchen, Shift-Bereich) und `auftragsliste.js`
(Löschknopf) greifen: die Vorlage `djangobase/_tabelle.html` mit ihrem
Rahmen und Schlüssel, `tabellen.css` VOR `auftragstabelle.css` (sonst kein
Zellgitter — so stand die Tabelle bis zu diesem Tag da), je Zeile
`data-id` und ein Kästchen, im Kopf das Kopfkästchen ohne Sortierpfeil.

Die Aufträge entstehen in der Testdatenbank; die Videodatei gibt es nicht
(`Dateigroessen` zeigt dann 0 B), es wird nichts auf die Platte geschrieben.
"""
import re

from django.test import Client, TestCase

from core.models import BVHJob


class DieAuftragstabelle(TestCase):

    DREID = '/process/VideoToBVH/'
    ZWEID = '/process/'

    def setUp(self):
        self.fertig = BVHJob.objects.create(
            name='Tanz.mp4', video_file='uploads/probe_tanz.mp4',
            pipeline='gem', status='complete')
        self.laeuft = BVHJob.objects.create(
            name='Lauf.mp4', video_file='uploads/probe_lauf.mp4',
            pipeline='hybrid_gem', status='processing', progress=47,
            progress_detail='SMPLest-X-Reihe: 500 / 1004 Bilder')
        self.zweid = BVHJob.objects.create(
            name='Flach.mp4', video_file='uploads/probe_flach.mp4',
            pipeline='mediapipe', status='failed')
        self.client = Client()

    def seite(self, adresse):
        antwort = self.client.get(adresse)
        self.assertEqual(antwort.status_code, 200)
        return antwort.content.decode('utf-8')

    def tabelle(self, text):
        u"""Das Markup zwischen `id="auftragsliste"` und dem Tabellenende."""
        anfang = text.index('id="auftragsliste"')
        return text[anfang:text.index('</table>', anfang)]

    def test_die_dreid_seite_rendert_die_djangobase_vorlage(self):
        text = self.seite(self.DREID)
        tabelle = self.tabelle(text)
        self.assertIn('<div class="db-tabelle-rahmen">', tabelle)
        self.assertIn('<table class="db-tabelle sortable auftragstabelle" '
                      'data-sort-key="videoauftraege-3d">', tabelle)
        self.assertNotIn('processed-table', tabelle)
        self.assertNotIn('id="jobTable"', text, 'altes Drahtformat')

    def test_die_zweid_seite_dieselbe_vorlage_mit_eigenem_schluessel(self):
        tabelle = self.tabelle(self.seite(self.ZWEID))
        self.assertIn('data-sort-key="videoauftraege-2d"', tabelle)
        self.assertIn('data-id="%s"' % self.zweid.id, tabelle)
        self.assertNotIn('data-id="%s"' % self.fertig.id, tabelle,
                         '3D-Aufträge gehören nicht auf die 2D-Seite')

    def test_tabellen_css_vor_auftragstabelle_css(self):
        for adresse in (self.DREID, self.ZWEID):
            with self.subTest(adresse=adresse):
                text = self.seite(adresse)
                gitter = text.index('/static/djangobase/css/tabellen.css')
                eigen = text.index('css/auftragstabelle.css')
                self.assertLess(gitter, eigen)

    def test_jede_zeile_traegt_kennung_und_kaestchen(self):
        tabelle = self.tabelle(self.seite(self.DREID))
        for job in (self.fertig, self.laeuft):
            with self.subTest(job=job.name):
                self.assertIn('<tr data-id="%s">' % job.id, tabelle)
                self.assertIn('class="job-check" value="%s"' % job.id, tabelle)
                self.assertIn('id="status-%s"' % job.id, tabelle)
                self.assertIn('id="pl-%s"' % job.id, tabelle)
        self.assertNotIn('data-id="%s"' % self.zweid.id, tabelle)

    def test_kopfkaestchen_ohne_sortierpfeil_knoepfe_ohne_sortierung(self):
        tabelle = self.tabelle(self.seite(self.DREID))
        koepfe = re.findall(r'<th[\s>][^>]*>', tabelle)
        self.assertEqual(len(koepfe), 8)
        aus = [k for k in koepfe if 'data-sort-aus="1"' in k]
        self.assertEqual(len(aus), 3)
        self.assertIn('data-key="wahl"', aus[0])
        kopf = re.search(r'<th[^>]*data-key="wahl"[^>]*>(.*?)</th>', tabelle, re.S)
        self.assertIn('<input type="checkbox" id="select-all"', kopf.group(1))
        self.assertIn('data-key="groesse"', ''.join(koepfe))

    def test_der_loeschknopf_beginnt_gesperrt_mit_null(self):
        text = self.seite(self.DREID)
        knopf = re.search(r'<button[^>]*id="bulk-delete-btn"[^>]*>(.*?)</button>',
                          text, re.S)
        self.assertIn('disabled', knopf.group(0))
        self.assertIn('Auswahl löschen (<span id="bulk-count">0</span>)',
                      knopf.group(1))

    def test_zustand_und_fortschritt_stehen_in_der_zeile(self):
        tabelle = self.tabelle(self.seite(self.DREID))
        self.assertIn('data-sort="Fertig"', tabelle)
        self.assertIn('/process/%s/result/' % self.fertig.id, tabelle)
        self.assertIn('data-sort="läuft 047"', tabelle)
        self.assertIn('style="width:47%"', tabelle)
        self.assertIn('href="/process/%s/"' % self.laeuft.id, tabelle)
