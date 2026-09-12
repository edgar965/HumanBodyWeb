# -*- coding: utf-8 -*-
u"""Auftragstabelle: die Struktur für `djangobase/_tabelle.html`.

Edgar (12.09.2026): „mache die Tabelle mit den Jobs mit der djangoBase
Vorlage für Tabellen, mit sortierbaren Spalten, Checkbox auswählen, Multi-
Select mit Shift und Batch-Delete".

Geprüft ohne Datenbank, an Attrappen: die Spalten (welche sortieren, welche
nicht), die Rohwerte zum Sortieren (Bytes, ISO-Zeit, Statustext), die
Kennungen, an denen das JavaScript hängt, und dass ein Dateiname mit
spitzen Klammern maskiert ankommt.
"""
import datetime
import re
import uuid

from django.test import SimpleTestCase

from core.dienste.auftragstabelle import Auftragstabelle

PIPELINES = [('v4', 'MocapNET v4'), ('gem', 'GEM-SMPL')]


class Auftragsattrappe:
    u"""Was `Auftragstabelle` von einem BVHJob liest."""

    def __init__(self, name='Tanz.mp4', status='complete', pipeline='gem',
                 progress=0, detail='', groesse=4990294):
        self.id = uuid.uuid4()
        self.name = name
        self.status = status
        self.pipeline = pipeline
        self.progress = progress
        self.progress_detail = detail
        self.created_at = datetime.datetime(2026, 9, 12, 17, 26, 46)
        self.video_size = groesse
        self.video_size_display = '4.8 MB'

    def get_pipeline_display(self):
        return dict(PIPELINES).get(self.pipeline, self.pipeline)

    def get_status_display(self):
        return {'processing': 'Processing'}.get(self.status, self.status)


class DieSpalten(SimpleTestCase):

    def setUp(self):
        self.tabelle = Auftragstabelle([], 'videoauftraege-3d', PIPELINES).tabelle()

    def test_schluessel_klasse_und_leertext(self):
        self.assertEqual(self.tabelle['key'], 'videoauftraege-3d')
        self.assertEqual(self.tabelle['klasse'], 'auftragstabelle')
        self.assertEqual(self.tabelle['zeilen'], [])
        self.assertIn('Aufträge', self.tabelle['leer'])

    def test_kaestchen_und_knoepfe_sortieren_nicht_der_rest_schon(self):
        aus = [s['key'] for s in self.tabelle['spalten'] if s.get('sortAus')]
        self.assertEqual(aus, ['wahl', 'verarbeiten', 'aktionen'])
        an = [s['key'] for s in self.tabelle['spalten'] if not s.get('sortAus')]
        self.assertEqual(an, ['name', 'pipeline', 'status', 'groesse', 'erstellt'])

    def test_das_kopfkaestchen_steht_in_der_ersten_spalte(self):
        self.assertIn('id="select-all"', self.tabelle['spalten'][0]['label'])

    def test_die_groesse_ist_eine_zahlenspalte(self):
        groesse = next(s for s in self.tabelle['spalten'] if s['key'] == 'groesse')
        self.assertTrue(groesse['num'])
        self.assertEqual(groesse['label'], 'Größe')


class DieZeile(SimpleTestCase):

    def zeile(self, **wie):
        job = Auftragsattrappe(**wie)
        return job, Auftragstabelle([job], 'k', PIPELINES).zeile(job)

    def test_kennung_und_drahtformat(self):
        job, zeile = self.zeile()
        jid = str(job.id)
        self.assertEqual(zeile['id'], jid)
        html = zeile['html']
        self.assertIn('<td class="kaestchen"><input type="checkbox" '
                      'class="job-check" value="%s">' % jid, html)
        self.assertIn('id="status-%s"' % jid, html)
        self.assertIn('id="pl-%s" data-current="gem"' % jid, html)
        self.assertIn('data-aktion="start" data-auftrag="%s"' % jid, html)
        self.assertIn('data-aktion="delete" data-auftrag="%s"' % jid, html)
        self.assertEqual(html.count('<td'), 8, 'acht Zellen wie der Kopf')

    def test_rohwerte_zum_sortieren(self):
        job, zeile = self.zeile()
        html = zeile['html']
        self.assertIn('<td class="num" data-sort="4990294">4.8 MB</td>', html)
        self.assertIn('<td data-sort="2026-09-12 17:26:46">12.09.2026 17:26</td>',
                      html)
        self.assertIn('data-sort="Fertig"', html)

    def test_endzustaende_deutsch(self):
        for status, text in (('complete', 'Fertig'), ('failed', 'Fehlgeschlagen'),
                             ('pending', 'Wartet')):
            with self.subTest(status=status):
                _, zeile = self.zeile(status=status)
                self.assertIn('> %s</span>' % text, zeile['html'])
                self.assertNotIn('inline-progress', zeile['html'])

    def test_laufend_zeigt_den_fortschritt_und_sortiert_danach(self):
        _, zeile = self.zeile(status='processing', progress=47,
                              detail='SMPLest-X-Reihe: 500 / 1004 Bilder (469 erkannt)')
        html = zeile['html']
        self.assertIn('data-sort="läuft 047"', html)
        self.assertIn('style="width:47%"', html)
        self.assertIn('47%</span>', html)
        # gekürzt auf 30 Zeichen wie `Auftragszeile._statuszelle`
        self.assertIn('SMPLest-X-Reihe: 500 / 1004 Bi</span>', html)

    def test_aktionen_je_zustand(self):
        job, fertig = self.zeile(status='complete')
        self.assertIn('/process/%s/result/' % job.id, fertig['html'])
        self.assertIn('Ergebnis', fertig['html'])
        job, gescheitert = self.zeile(status='failed')
        self.assertIn('href="/process/%s/"' % job.id, gescheitert['html'])
        self.assertIn('> Status</a>', gescheitert['html'])
        self.assertNotIn('result', gescheitert['html'])
        _, wartet = self.zeile(status='pending')
        self.assertNotIn('<a ', wartet['html'])
        self.assertIn('data-aktion="delete"', wartet['html'])

    def test_die_pipelinewahl_hat_die_eigene_vorgewaehlt(self):
        _, zeile = self.zeile(pipeline='v4')
        optionen = re.findall(r'<option value="(\w+)"( selected)?>', zeile['html'])
        self.assertEqual(optionen, [('v4', ' selected'), ('gem', '')])

    def test_ein_dateiname_mit_spitzen_klammern_wird_maskiert(self):
        u"""Der Name kommt aus dem Upload (Befund Nemotron, 16.08.2026)."""
        _, zeile = self.zeile(name='<img src=x onerror=alert(1)>.mp4')
        self.assertNotIn('<img', zeile['html'])
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;.mp4', zeile['html'])
