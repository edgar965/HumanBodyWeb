# -*- coding: utf-8 -*-
"""Wächter für die Ursprungsprüfung — schreibende Anfragen von fremden Seiten.

WARUM DIESER TEST EXISTIERT (13.08.2026)
----------------------------------------
Es gibt keine Anmeldung. Wer den Browser des Nutzers dazu bringt, eine Anfrage
zu schicken, hat damit alles, was er braucht. 35 Endpunkte in `character_api`
tragen `@csrf_exempt`, 20 davon schreiben oder löschen. Am laufenden Server
gemessen:

    POST /api/character/bvh-manage/  Content-Type: text/plain  Origin: fremd
       -> {"error": "Unknown action: gibtesnicht"}   HTTP 400

Die Ansicht wurde also erreicht — die Absage kam erst aus der Ansicht selbst,
nicht von einer Prüfung. Ein `<form enctype="text/plain">` auf einer beliebigen
Webseite reicht dafür aus; dieser Inhaltstyp löst keine Vorabfrage aus.

Die Tests prüfen beide Richtungen: Fremdes muss abprallen, Eigenes muss
weiterhin durchkommen. Der zweite Teil ist der wichtigere — eine Sperre, die
auch die eigene Oberfläche aussperrt, wird beim ersten Ärger wieder entfernt.
"""
import uuid

from django.test import TestCase
from django.urls import reverse


class GleicherUrsprungTest(TestCase):
    """Django gibt sich im Test als Host `testserver` aus."""

    EIGEN = 'http://testserver'
    FREMD = 'https://boese.example'
    ZIEL = '/api/character/bvh-manage/'
    RUMPF = '{"action":"gibtesnicht","category":"x","name":"y"}'

    # ------------------------------------------------------------ Muss abprallen

    def test_fremder_origin_wird_abgewiesen(self):
        """DER GEMESSENE ANGRIFF: fremde Seite, einfacher Inhaltstyp."""
        a = self.client.post(self.ZIEL, data=self.RUMPF, content_type='text/plain',
                             headers={'origin': self.FREMD})
        self.assertEqual(a.status_code, 403)
        self.assertNotIn('Unknown action', a.content.decode('utf-8'),
                         'die Ansicht wurde trotzdem ausgefuehrt')

    def test_sec_fetch_site_cross_site_wird_abgewiesen(self):
        """Das Feld setzt der Browser selbst; eine Schadseite kann es nicht fälschen."""
        for wert in ('cross-site', 'same-site'):
            with self.subTest(wert=wert):
                a = self.client.post(self.ZIEL, data=self.RUMPF,
                                     content_type='text/plain',
                                     headers={'sec-fetch-site': wert})
                self.assertEqual(a.status_code, 403)

    def test_anderer_port_ist_ein_anderer_ursprung(self):
        a = self.client.post(self.ZIEL, data=self.RUMPF, content_type='text/plain',
                             headers={'origin': 'http://testserver:9000'})
        self.assertEqual(a.status_code, 403)

    # ------------------------------------------------------------- Muss durchkommen

    def test_eigene_oberflaeche_kommt_durch(self):
        """Antwort 400 heisst: Die Ansicht lief und mochte die Daten nicht —
        die Prüfung hat sie also durchgelassen."""
        a = self.client.post(self.ZIEL, data=self.RUMPF,
                             content_type='application/json',
                             headers={'origin': self.EIGEN,
                                      'sec-fetch-site': 'same-origin'})
        self.assertEqual(a.status_code, 400)

    def test_ohne_browserfelder_kommt_durch(self):
        """curl, eigene Skripte, die Tests selbst: kein Origin, kein Sec-Fetch-Site.

        Das ist Absicht — wer ohne Browser anfragt, sitzt schon am Rechner. Der
        Angriff braucht gerade den Browser, und der schickt die Felder immer."""
        a = self.client.post(self.ZIEL, data=self.RUMPF,
                             content_type='application/json')
        self.assertEqual(a.status_code, 400)

    def test_lesende_anfragen_werden_nicht_geprueft(self):
        """Sonst würde jedes Bild und jede Verknüpfung von aussen geprüft."""
        a = self.client.get('/api/ui-prefs/', headers={'sec-fetch-site': 'cross-site'})
        self.assertEqual(a.status_code, 200)

    # ------------------------------------------------------- Methodenschutz

    def test_loeschen_per_get_ist_nicht_mehr_moeglich(self):
        """`photo_analysis_delete` hing an einem `<a href>` — also an einem GET,
        das Dateien löscht. Ein `<img src>` auf einer fremden Seite hätte
        gereicht; GET wird von der Ursprungsprüfung bewusst nicht erfasst.
        Deshalb `@require_POST` und im Template ein POST."""
        ziel = reverse('photo_analysis_delete', args=[uuid.uuid4()])
        self.assertEqual(self.client.get(ziel).status_code, 405)
