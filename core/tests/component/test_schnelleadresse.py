# -*- coding: utf-8 -*-
u"""Wer ueber `localhost` kommt, landet auf 127.0.0.1.

WARUM DAS EINEN TEST BRAUCHT (Edgar, 09.09.2026: „http://localhost:8081/
humanbody/scene/ baut sich sehr langsam auf")
=====================================================================
Die Weiterleitung ist eine Abkuerzung mit drei scharfen Kanten, und jede
davon waere still: Ein weitergeleiteter POST verliert seinen Rumpf, ein
weitergeleitetes ES-Modul laedt wegen der fremden Herkunft gar nicht, und
ein `301` bliebe im Browser stehen, auch wenn der Server spaeter auf beiden
Adressfamilien lauscht.

Die Messung, die dahintersteht, und die Nebenwirkung auf `localStorage`
stehen in `ui/schnelleadresse.py`.
"""
from django.test import RequestFactory, TestCase, override_settings

from ui.schnelleadresse import Schnelleadresse


HTML = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'


class Weiterleitung(TestCase):

    databases = set()

    def setUp(self):
        self.werk = RequestFactory()
        self.schicht = Schnelleadresse(lambda anfrage: 'durchgereicht')

    def _seite(self, pfad='/humanbody/scene/', host='localhost:8081',
               accept=HTML):
        return self.werk.get(pfad, HTTP_HOST=host, HTTP_ACCEPT=accept)

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'])
    def test_seite_ueber_localhost_wird_umgeleitet(self):
        antwort = self.schicht(self._seite())
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'],
                         'http://127.0.0.1:8081/humanbody/scene/')

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'])
    def test_die_abfrage_bleibt_erhalten(self):
        u"""Ohne sie kaeme die Seite ohne ihre Parameter an."""
        anfrage = self._seite('/humanbody/scene/?figur=3&reiter=garmentcode')
        antwort = self.schicht(anfrage)
        self.assertEqual(
            antwort['Location'],
            'http://127.0.0.1:8081/humanbody/scene/?figur=3&reiter=garmentcode')

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'])
    def test_kein_dauerhafter_umzug(self):
        u"""301 bliebe im Browser stehen — auch nach einem Serverumbau."""
        self.assertEqual(self.schicht(self._seite()).status_code, 302)

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'])
    def test_ueber_127_bleibt_alles_wie_es_ist(self):
        anfrage = self._seite(host='127.0.0.1:8081')
        self.assertEqual(self.schicht(anfrage), 'durchgereicht')

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'])
    def test_ein_modul_wird_nicht_umgeleitet(self):
        u"""Ein ES-Modul von fremder Herkunft laedt ohne CORS-Kopf NICHT.

        Eine noch offene `localhost`-Seite wuerde dadurch kaputtgehen statt
        schneller zu werden — der Browser schickt fuer Module kein
        `text/html` im `Accept`.
        """
        anfrage = self._seite('/statik/v-1/viewer/scene/main.js', accept='*/*')
        self.assertEqual(self.schicht(anfrage), 'durchgereicht')

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'])
    def test_ein_post_wird_nicht_umgeleitet(self):
        u"""Beim Weiterleiten ginge der Rumpf verloren."""
        anfrage = self.werk.post('/api/garmentcode/drapieren/', {'a': '1'},
                                 HTTP_HOST='localhost:8081', HTTP_ACCEPT=HTML)
        self.assertEqual(self.schicht(anfrage), 'durchgereicht')

    @override_settings(DEBUG=True, ALLOWED_HOSTS=['*'])
    def test_ohne_accept_kopf_nicht(self):
        u"""`curl http://localhost:8081/...` meint die Adresse so, wie sie ist."""
        anfrage = self.werk.get('/humanbody/scene/', HTTP_HOST='localhost:8081')
        self.assertEqual(self.schicht(anfrage), 'durchgereicht')

    @override_settings(DEBUG=False, ALLOWED_HOSTS=['*'])
    def test_im_betrieb_nicht(self):
        u"""Dort entscheidet der Vorschaltserver ueber Namen."""
        self.assertEqual(self.schicht(self._seite()), 'durchgereicht')

    def test_sie_haengt_wirklich_in_der_kette(self):
        u"""Sonst prueft dieser Test nur seine eigene Kopie."""
        from django.conf import settings
        self.assertIn('ui.schnelleadresse.Schnelleadresse',
                      settings.MIDDLEWARE)
        # Und zwar VOR allem anderen: Eine Anfrage, die ohnehin weiterzieht,
        # soll keine Sitzung anlegen und keine Ansicht rechnen.
        self.assertEqual(settings.MIDDLEWARE[0],
                         'ui.schnelleadresse.Schnelleadresse')
