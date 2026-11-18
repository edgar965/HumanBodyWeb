# -*- coding: utf-8 -*-
u"""Der dauerhafte Vorrat der Anzeigen (`G9modellvorrat`, `G9vorratanfrage`, `Netzvorratwahl`, 19.10.2026).

Edgar, 19.10.2026: „bei jedem Modell, das gespeichert ist, direkt alles speichern für alle Anzeigen … sodass sie beim Laden schnell angezeigt werden",
„mach die Speicherung einstellbar … Default: alles bis ultrafein".

1. `Netzvorratwahl.behalten`: Stufe 0/1/2 gegen aus/grob/fein/ultrafein; Unbekanntes → Vorgabe ultrafein.
2. Der stabile Schlüssel hängt NICHT an der Code-Fassung (`G9antworten.schluessel(…, fassung='stabil')`), der normale schon.
3. `G9vorratanfrage.liefern` (17.11.2026: jeder Eintrag trägt seine Code-Fassung, Edgar: „fixe das: Nach einer Code-Änderung zeigen sie beim ersten Laden
   noch den alten Stand"):
   a. Treffer im Vorrat der Fassung, Anzeige (Kopf `X-G9-Vorrat`), hier noch nicht → abgelegt; hier mit älterem Code → ersetzt, auch ohne Markierung;
   b. kein Treffer dort, hier mit älterem Code, Vorschau (`X-G9-Vorrat-Vorschau`, Stufe 0) → sofort ausgeliefert mit `X-G9-Vorrat-Alt`, Nachlauf vorgemerkt,
      nichts abgelegt; ohne Vorschau oder auf Stufe 1 → neu gerechnet und mit der jetzigen Fassung ersetzt; hier mit dem jetzigen Code → ausgeliefert, kein
      Nachlauf, nichts abgelegt;
   c. nirgends → gerechnet; abgelegt nur als Anzeige ODER wenn hier ein alter Eintrag lag (frisch ersetzt alt);
   d. Vorab-Füllen (`X-G9-Vorrat-Nur`) → 204 ohne Inhalt; e. eine Fehlerantwort geht unverändert durch;
   f. Einstellung „aus" → hier weder lesen noch ablegen.
4. `G9modellvorrat` hat eigenen Speicher und eigenes Schloss (geerbt wären es die des Antwortvorrats) und keine Code-Fassung im Schlüssel.
5. Der Nachlauf wartet, solange nach einer Vorschau die gewählte Stufe desselben Teils aussteht (`G9vorratnachlauf._ausstehend`, 17.11.2026); zu alte Einträge
   zählen nicht. In 3b meldet die Vorschau „steht aus“, die Stufe 1 „geliefert“, das Vorab-Füllen (3d) nichts.

Sabotage (nicht gelaufen — Tests nur auf Ansage): in `ablegen` das `da is not None or self.markiert` zu `True` → Fall 3c rot; in `holen` das
`not (self.vorschau or self.nur)` streichen → Fall 3b rot (liefert den alten Stand); in `G9modellvorrat` die eigene `_speicher` streichen → Fall 4 rot;
in `liefern` die Meldung `vorschau_gegangen` streichen → Fall 3b rot; in `_steht_aus` das Wegfallen zu alter Einträge streichen → Fall 5 rot.
Geschrieben, nicht gelaufen.
"""
import time
import unittest
from types import SimpleNamespace
from unittest import mock

from django.http import HttpResponse

from core.dienste.g9antworten import G9antworten
from core.dienste.g9antwortvorrat import G9antwortvorrat
from core.dienste.g9modellvorrat import G9modellvorrat
from core.dienste.g9vorratanfrage import G9vorratanfrage
from core.dienste.g9vorratnachlauf import G9vorratnachlauf
from core.dienste.netzvorratwahl import Netzvorratwahl


class G9modellvorratTest(unittest.TestCase):

    JETZT, ALT = 'f_jetzt', 'f_alt'

    @staticmethod
    def anfrage(markiert=True, nur=False, vorschau=False):
        kopf = {}
        if markiert:
            kopf['X-G9-Vorrat'] = '1'
        if nur:
            kopf['X-G9-Vorrat-Nur'] = '1'
        if vorschau:
            kopf['X-G9-Vorrat-Vorschau'] = '1'
        return SimpleNamespace(headers=kopf, path='/n/x/netz/')

    def lauf(self, regulaer, dauer, rechnen=b'neu', markiert=True, nur=False, da=None, wahl='ultrafein', vorschau=False, stufe=1):
        u"""Ein `liefern` mit Attrappen; `dauer` (Bytes, Fassung) oder None, `da` die Fassung des Eintrags hier (None: keiner).
        Rückgabe (Antwort, gemerkt, vorgemerkt, gerechnet); die Meldungen an den Nachlauf in `self.gemeldet` (Vorschau gegangen, Stufe geliefert)."""
        gerechnet = []

        def neu():
            gerechnet.append(1)
            return rechnen
        with mock.patch.object(Netzvorratwahl, 'gewaehlt', return_value=wahl), \
                mock.patch.object(G9vorratanfrage, 'stufe', return_value=stufe), \
                mock.patch.object(G9modellvorrat, 'lesen', return_value=dauer), \
                mock.patch.object(G9modellvorrat, 'fassung_von', return_value=da), \
                mock.patch.object(G9modellvorrat, 'merken') as merken, \
                mock.patch.object(G9vorratnachlauf, 'vormerken') as vormerken, \
                mock.patch.object(G9vorratnachlauf, 'vorschau_gegangen') as gegangen, \
                mock.patch.object(G9vorratnachlauf, 'stufe_geliefert') as geliefert:
            anfrage = self.anfrage(markiert, nur, vorschau)
            antwort = G9vorratanfrage(anfrage, 'stabil_x', self.JETZT).liefern(regulaer, neu, 'application/x-humanbody-netz')
        self.gemeldet = (gegangen.call_count, geliefert.call_count)
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
        _, gemerkt, _, _ = self.lauf(b'fassung', None, markiert=False, da=self.ALT)                       # a, ersetzt alten Code
        self.assertEqual([tuple(g.args) for g in gemerkt], [('stabil_x', b'fassung', self.JETZT)])
        _, gemerkt, _, _ = self.lauf(b'fassung', None, da=self.JETZT)                                    # a, liegt schon so
        self.assertEqual(len(gemerkt), 0)
        alt = (b'alt', self.ALT)
        antwort, gemerkt, vorgemerkt, gerechnet = self.lauf(None, alt, da=self.ALT, vorschau=True, stufe=0)   # b, Vorschau
        self.assertEqual((antwort.content, len(gemerkt), vorgemerkt, gerechnet), (b'alt', 0, 1, 0))
        self.assertEqual(antwort['X-G9-Vorrat-Alt'], '1')
        self.assertEqual(self.gemeldet, (1, 0))                                                         # Vorschau: Stufe steht aus
        for vorschau, stufe in ((False, 0), (True, 1)):                                                 # b, keine Vorschau
            antwort, gemerkt, vorgemerkt, gerechnet = self.lauf(None, alt, da=self.ALT, vorschau=vorschau, stufe=stufe)
            self.assertEqual((antwort.content, vorgemerkt, gerechnet), (b'neu', 0, 1))
            self.assertEqual(self.gemeldet, (0, stufe))                                                 # Stufe 1: geliefert
            self.assertEqual([tuple(g.args) for g in gemerkt], [('stabil_x', b'neu', self.JETZT)])
            self.assertFalse(antwort.has_header('X-G9-Vorrat-Alt'))
        antwort, gemerkt, vorgemerkt, gerechnet = self.lauf(None, (b'da', self.JETZT), da=self.JETZT)    # b, jetziger Code
        self.assertEqual((antwort.content, len(gemerkt), vorgemerkt, gerechnet), (b'da', 0, 0, 0))
        antwort, gemerkt, _, gerechnet = self.lauf(None, None)                                          # c, Anzeige
        self.assertEqual((antwort.content, len(gemerkt), gerechnet), (b'neu', 1, 1))
        _, gemerkt, _, _ = self.lauf(None, None, markiert=False)                                         # c, Reglerzug
        self.assertEqual(len(gemerkt), 0)
        _, gemerkt, _, _ = self.lauf(None, None, markiert=False, da=self.ALT)                           # c, frisch ersetzt alt
        self.assertEqual(len(gemerkt), 1)
        antwort, _, _, _ = self.lauf(b'fassung', None, nur=True)                                         # d
        self.assertEqual((antwort.status_code, antwort.content), (204, b''))
        self.assertEqual(self.gemeldet, (0, 0))                                                         # Vorab-Füllen ist nicht die Stufe
        fehler = HttpResponse(status=404)
        antwort, gemerkt, _, _ = self.lauf(None, None, rechnen=fehler)                                   # e
        self.assertIs(antwort, fehler)
        self.assertEqual(len(gemerkt), 0)
        antwort, gemerkt, vorgemerkt, gerechnet = self.lauf(None, (b'alt', self.ALT), wahl='aus')       # f
        self.assertEqual((antwort.content, len(gemerkt), vorgemerkt, gerechnet), (b'neu', 0, 0, 1))

    def test_4_eigene_ablage(self):
        self.assertIsNot(G9modellvorrat._speicher, G9antwortvorrat._speicher)
        self.assertIsNot(G9modellvorrat._schloss, G9antwortvorrat._schloss)
        self.assertEqual(G9modellvorrat.fassung(), 'stabil')
        self.assertNotEqual(G9modellvorrat.ORDNER, G9antwortvorrat.ORDNER)

    def test_5_nachlauf_wartet_auf_die_stufe(self):
        with mock.patch.dict(G9vorratnachlauf._ausstehend, clear=True):
            self.assertFalse(G9vorratnachlauf._steht_aus())
            G9vorratnachlauf.vorschau_gegangen('/n/a/netz/')
            G9vorratnachlauf.vorschau_gegangen('/n/b/netz/')
            G9vorratnachlauf.stufe_geliefert('/n/a/netz/')
            self.assertTrue(G9vorratnachlauf._steht_aus())                                              # b fehlt noch
            G9vorratnachlauf.stufe_geliefert('/n/b/netz/')
            self.assertFalse(G9vorratnachlauf._steht_aus())
            G9vorratnachlauf._ausstehend['/n/c/netz/'] = time.time() - G9vorratnachlauf.HOECHSTENS_WARTEN_S - 1
            self.assertFalse(G9vorratnachlauf._steht_aus())                                             # zu alt: zählt nicht
            self.assertEqual(G9vorratnachlauf._ausstehend, {})


if __name__ == '__main__':
    unittest.main()
