# -*- coding: utf-8 -*-
u"""Der dauerhafte Vorrat der Anzeigen (`G9modellvorrat`, `G9vorratanfrage`, `Netzvorratwahl`, 19.10.2026).

Edgar, 19.10.2026: „bei jedem Modell, das gespeichert ist, direkt alles speichern für alle Anzeigen … sodass sie beim Laden schnell angezeigt werden",
„mach die Speicherung einstellbar … Default: alles bis ultrafein".

1. `Netzvorratwahl.behalten`: Stufe 0/1/2 gegen aus/grob/fein/ultrafein; Unbekanntes → Vorgabe ultrafein.
2. Der stabile Schlüssel hängt NICHT an der Code-Fassung (`G9antworten.schluessel(…, fassung='stabil')`), der normale schon.
3. `G9vorratanfrage.liefern`:
   a. Treffer im Vorrat der Fassung, Anzeige (Kopf `X-G9-Vorrat`), hier noch nicht → abgelegt;
   b. kein Treffer dort, aber hier → sofort ausgeliefert, Nachlauf vorgemerkt, nichts abgelegt (das tut der Nachlauf);
   c. nirgends → gerechnet; abgelegt nur als Anzeige ODER wenn hier ein alter Eintrag lag (frisch ersetzt alt);
   d. Vorab-Füllen (`X-G9-Vorrat-Nur`) → 204 ohne Inhalt; e. eine Fehlerantwort geht unverändert durch;
   f. Einstellung „aus" → hier weder lesen noch ablegen.
4. `G9modellvorrat` hat eigenen Speicher und eigenes Schloss (geerbt wären es die des Antwortvorrats) und keine Code-Fassung.

Sabotage (nicht gelaufen — Tests nur auf Ansage): in `ablegen` das `self.markiert or da` zu `True` → Fall 3c rot; in `holen` das `self.alt = True` streichen
→ Fall 3b rot (legt den alten Stand erneut ab); in `G9modellvorrat` die eigene `_speicher` streichen → Fall 4 rot. Geschrieben, nicht gelaufen.
"""
import unittest
from types import SimpleNamespace
from unittest import mock

from django.http import HttpResponse

from core.dienste.g9antwortvorrat import G9antwortvorrat
from core.dienste.g9antworten import G9antworten
from core.dienste.g9modellvorrat import G9modellvorrat
from core.dienste.g9vorratanfrage import G9vorratanfrage
from core.dienste.netzvorratwahl import Netzvorratwahl


class G9modellvorratTest(unittest.TestCase):

    @staticmethod
    def anfrage(markiert=True, nur=False):
        kopf = {}
        if markiert:
            kopf['X-G9-Vorrat'] = '1'
        if nur:
            kopf['X-G9-Vorrat-Nur'] = '1'
        return SimpleNamespace(headers=kopf)

    def lauf(self, regulaer, dauer, rechnen=b'neu', markiert=True, nur=False, da=False, wahl='ultrafein'):
        u"""Ein `liefern` mit Attrappen; Rückgabe (Antwort, gemerkt, vorgemerkt, gerechnet)."""
        gerechnet = []

        def neu():
            gerechnet.append(1)
            return rechnen
        with mock.patch.object(Netzvorratwahl, 'gewaehlt', return_value=wahl), \
                mock.patch.object(G9vorratanfrage, 'stufe', return_value=1), \
                mock.patch.object(G9modellvorrat, 'holen', return_value=dauer), \
                mock.patch.object(G9modellvorrat, 'vorhanden', return_value=da), \
                mock.patch.object(G9modellvorrat, 'merken') as merken, \
                mock.patch('core.dienste.g9vorratnachlauf.G9vorratnachlauf.vormerken') as vormerken:
            antwort = G9vorratanfrage(self.anfrage(markiert, nur), 'stabil_x').liefern(regulaer, neu, 'application/x-humanbody-netz')
        return antwort, merken.call_args_list, vormerken.call_count, len(gerechnet)

    def test_1_behalten(self):
        self.assertEqual([Netzvorratwahl.behalten(s, 'ultrafein') for s in (0, 1, 2)], [True, True, True])
        self.assertEqual([Netzvorratwahl.behalten(s, 'fein') for s in (0, 1, 2)], [True, True, False])
        self.assertEqual([Netzvorratwahl.behalten(s, 'grob') for s in (0, 1, 2)], [True, False, False])
        self.assertEqual([Netzvorratwahl.behalten(s, 'aus') for s in (0, 1, 2)], [False, False, False])
        self.assertEqual(Netzvorratwahl.aus({'netzvorrat': 'unsinn'}), 'ultrafein')
        self.assertEqual(Netzvorratwahl.aus({}), 'ultrafein')

    def test_2_stabiler_schluessel(self):
        def schluessel(fassung, stabil):
            with mock.patch.object(G9antworten, 'fassung', return_value=fassung):
                return G9antworten.schluessel('koerper', 'basis', {'regler': {}}, None, None, 'u16', fassung='stabil' if stabil else None)
        self.assertNotEqual(schluessel('a', False), schluessel('b', False))
        self.assertEqual(schluessel('a', True), schluessel('b', True))

    def test_3_liefern(self):
        antwort, gemerkt, vorgemerkt, gerechnet = self.lauf(b'fassung', None)                         # a
        self.assertEqual((antwort.content, len(gemerkt), vorgemerkt, gerechnet), (b'fassung', 1, 0, 0))
        antwort, gemerkt, vorgemerkt, gerechnet = self.lauf(None, b'alt', da=True)                      # b
        self.assertEqual((antwort.content, len(gemerkt), vorgemerkt, gerechnet), (b'alt', 0, 1, 0))
        antwort, gemerkt, _, gerechnet = self.lauf(None, None)                                          # c, Anzeige
        self.assertEqual((antwort.content, len(gemerkt), gerechnet), (b'neu', 1, 1))
        _, gemerkt, _, _ = self.lauf(None, None, markiert=False)                                         # c, Reglerzug
        self.assertEqual(len(gemerkt), 0)
        _, gemerkt, _, _ = self.lauf(None, None, markiert=False, da=True)                               # c, frisch ersetzt alt
        self.assertEqual(len(gemerkt), 1)
        antwort, _, _, _ = self.lauf(b'fassung', None, nur=True)                                         # d
        self.assertEqual((antwort.status_code, antwort.content), (204, b''))
        fehler = HttpResponse(status=404)
        antwort, gemerkt, _, _ = self.lauf(None, None, rechnen=fehler)                                   # e
        self.assertIs(antwort, fehler)
        self.assertEqual(len(gemerkt), 0)
        antwort, gemerkt, vorgemerkt, gerechnet = self.lauf(None, b'alt', wahl='aus')                   # f
        self.assertEqual((antwort.content, len(gemerkt), vorgemerkt, gerechnet), (b'neu', 0, 0, 1))

    def test_4_eigene_ablage(self):
        self.assertIsNot(G9modellvorrat._speicher, G9antwortvorrat._speicher)
        self.assertIsNot(G9modellvorrat._schloss, G9antwortvorrat._schloss)
        self.assertEqual(G9modellvorrat.fassung(), 'stabil')
        self.assertNotEqual(G9modellvorrat.ORDNER, G9antwortvorrat.ORDNER)


if __name__ == '__main__':
    unittest.main()
