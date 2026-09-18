# -*- coding: utf-8 -*-
"""Auftragskennung: Datum und Uhrzeit als Adresse der Auftragsseiten.

WARUM (Edgar, 16.09.2026: „änder die Verzeichnisnamen der Process Seiten …
in der Form http://127.0.0.1:8081/process/2026.09.16.22.00.12/result"):

1. Die Kennung ist die ORTSZEIT (Europe/Berlin) — 20:00:12 UTC im September
   heißt `…22.00.12`, nicht `…20.00.12`.
2. Zwei Aufträge in derselben Sekunde: der zweite bekommt die nächste freie
   Sekunde, die Form bleibt.
3. Der URL-Konverter nimmt nur diese Form — eine UUID passt nicht, damit die
   alten Adressen bei der Weiterleitung landen.
4. Verdrahtung: `core/urls.py` registriert den Konverter und führt die
   Weiterleitung; `auftragszeile.js` baut den Ergebnis-Link aus
   `daten.kennung` des Zustands-JSON; die Vorlagen verlinken `job.kennung`.

Sabotage-Gegenprobe: in `Auftragskennung.frei` die Schleife entfernen →
Fall 2 rot (zweite Kennung gleich der ersten).
"""

import re
from datetime import UTC, datetime

from django.conf import settings
from django.test import SimpleTestCase

from core.daten.auftragskennung import Auftragskennung
from core.daten.kennungskonverter import Kennungskonverter

VORLAGEN = settings.BASE_DIR / 'templates'


class AuftragskennungTest(SimpleTestCase):
    ZEIT = datetime(2026, 9, 16, 20, 0, 12, 345678, tzinfo=UTC)

    def test_kennung_ist_die_ortszeit_auf_die_sekunde(self):
        self.assertEqual(Auftragskennung.aus(self.ZEIT), '2026.09.16.22.00.12')
        self.assertEqual(len(Auftragskennung.aus(self.ZEIT)), Auftragskennung.LAENGE)
        self.assertEqual(Auftragskennung.aus(datetime(2026, 1, 5, 7, 8, 9)), '2026.01.05.07.08.09')

    def test_zwei_auftraege_in_einer_sekunde_ruecken_auf(self):
        belegt = set()
        erste = Auftragskennung.frei(self.ZEIT, belegt.__contains__)
        belegt.add(erste)
        zweite = Auftragskennung.frei(self.ZEIT, belegt.__contains__)
        belegt.add(zweite)
        dritte = Auftragskennung.frei(self.ZEIT, belegt.__contains__)
        self.assertEqual(
            (erste, zweite, dritte), ('2026.09.16.22.00.12', '2026.09.16.22.00.13', '2026.09.16.22.00.14')
        )

    def test_konverter_nimmt_nur_die_kennungsform(self):
        muster = re.compile(Kennungskonverter.regex)
        self.assertTrue(muster.fullmatch('2026.09.16.22.00.12'))
        for falsch in (
            '75b11525-e8ca-4fdb-903f-28467c7db670',
            '2026.09.16',
            '2026-09-16-22-00-12',
            '2026.09.16.22.00.12x',
            '',
        ):
            self.assertIsNone(muster.fullmatch(falsch), falsch)
            self.assertFalse(Auftragskennung.passt(falsch), falsch)
        self.assertEqual(Kennungskonverter.to_url('2026.09.16.22.00.12'), '2026.09.16.22.00.12')

    def test_urls_seiten_und_tabelle_nennen_die_kennung(self):
        urls = AuftragskennungTest._text(settings.BASE_DIR / 'core' / 'urls.py')
        self.assertIn("register_converter(Kennungskonverter, 'kennung')", urls)
        for pfad in ('', 'start/', 'stop/', 'result/', 'delete/'):
            self.assertIn("path('process/<kennung:kennung>/%s'" % pfad, urls)
        self.assertNotIn("path('process/<uuid:job_id>/', Webseiten", urls)
        self.assertIn("path('process/<uuid:job_id>/<path:rest>', Auftragsweiterleitung.alt)", urls)
        zeile = AuftragskennungTest._text(
            settings.BASE_DIR / 'static' / 'js' / 'auftraege' / 'auftragszeile.js'
        )
        self.assertIn('return `/process/${daten.kennung}/result/`;', zeile)
        self.assertNotIn('/process/${this.id}/', zeile)
        for vorlage, marken in (
            (
                'job_status.html',
                ("{% url 'start_processing' job.kennung %}", "{% url 'job_result' job.kennung %}"),
            ),
            ('job_result.html', ("{% url 'job_status' job.kennung %}",)),
            ('processed.html', ("{% url 'job_result' job.kennung %}", "{% url 'delete_job' job.kennung %}")),
        ):
            text = AuftragskennungTest._text(VORLAGEN / vorlage)
            for marke in marken:
                self.assertIn(marke, text, vorlage)
            self.assertNotIn("'job_status' job.id", text, vorlage)
            self.assertNotIn("'job_result' job.id", text, vorlage)

    @staticmethod
    def _text(pfad):
        return pfad.read_text(encoding='utf-8')
