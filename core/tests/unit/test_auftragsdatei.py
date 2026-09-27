# -*- coding: utf-8 -*-
"""`Auftragsdatei` — Vorschaubilder mit Zwischenspeicher ausliefern (27.09.2026).

Anlass: Edgar, „ladezeit von /modell-aus-dateien/#mesh ist sehr lange". Gemessen waren
50 Vorschaubilder mit 2,86 MB, die wegen `no-store` bei JEDEM Seitenaufruf neu kamen —
der zweite Durchgang kostete 0,99 s, genauso viel wie der erste.

Geprüft wird hier, was leicht wieder kaputtgeht:
* Eine bedingte Anfrage bekommt 304 OHNE Inhalt (der eigentliche Gewinn).
* Eine veraltete Marke bekommt die volle Datei (Sabotage-Gegenprobe — ein Prüfer, der
  immer 304 sagt, wäre schlimmer als keiner).
* `immutable` gibt es NUR mit Kennung in der Adresse. Ohne sie darf die Antwort nicht
  ein Jahr gelten, sonst zeigt der Browser nach einem neuen Lauf das alte Bild.
"""

import tempfile
from pathlib import Path

from django.test import RequestFactory, TestCase

from core.dienste.auftragsdatei import Auftragsdatei


class AuftragsdateiTest(TestCase):

    def setUp(self):
        self.ordner = tempfile.mkdtemp(prefix='auftragsdatei_', dir=str(Path(__file__).resolve().parents[3]
                                                                        / 'ProjektTemp'))
        self.datei = Path(self.ordner) / 'icon.png'
        self.datei.write_bytes(b'\x89PNG\r\n\x1a\n' + b'x' * 120)
        self.anfragen = RequestFactory()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _antwort(self, kennung=None, kopf=None):
        anfrage = self.anfragen.get('/api/mesh/1/datei/ergebnis/icon.png', **(kopf or {}))
        return Auftragsdatei.antwort(anfrage, self.datei, kennung=kennung)

    def test_liefert_marke_und_stand(self):
        antwort = self._antwort()
        self.assertEqual(antwort.status_code, 200)
        self.assertTrue(antwort['ETag'])
        self.assertTrue(antwort['Last-Modified'])

    def test_ohne_kennung_kein_immutable(self):
        """Ohne `?v=` darf nichts dauerhaft gelten — sonst käme ein neues Icon nie an."""
        self.assertEqual(self._antwort()['Cache-Control'], 'no-cache')

    def test_mit_kennung_ein_jahr(self):
        steuerung = self._antwort(kennung='123')['Cache-Control']
        self.assertIn('immutable', steuerung)
        self.assertIn('max-age=%d' % Auftragsdatei.DAUER_S, steuerung)

    def test_bekannte_marke_gibt_304_ohne_inhalt(self):
        marke = self._antwort()['ETag']
        antwort = self._antwort(kopf={'HTTP_IF_NONE_MATCH': marke})
        self.assertEqual(antwort.status_code, 304)
        self.assertEqual(antwort.content, b'')

    def test_veraltete_marke_gibt_die_datei(self):
        """Gegenprobe: Der Prüfer darf nicht einfach immer 304 sagen."""
        antwort = self._antwort(kopf={'HTTP_IF_NONE_MATCH': '"veraltet"'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(b''.join(antwort.streaming_content), self.datei.read_bytes())

    def test_geaenderte_datei_gibt_neue_marke(self):
        alt = self._antwort()['ETag']
        self.datei.write_bytes(b'\x89PNG\r\n\x1a\n' + b'y' * 500)
        self.assertNotEqual(self._antwort()['ETag'], alt)
