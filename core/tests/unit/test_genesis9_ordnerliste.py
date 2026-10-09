# -*- coding: utf-8 -*-
u"""Die Ordnerliste der Garderobe-Antwort (`G9ordnerliste`) und die einmal geholte Daz-Tabelle (09.10.2026).

Edgar: „warum dauert laden des Characters ewig". `GET /api/character/genesis9-figur/garderobe/` brauchte 21–25 s, weil
je Eintrag (634) Verzeichnisse neu aufgezählt wurden (`ProjektTemp/_wegwerf/garderobe_antwort_profil.py`):

1. `passend` ist `Path.glob(vorn + '*' + hinten)` — auch ohne Rücksicht auf Groß/Klein (Windows) und mit leerem Mittelteil.
2. `namen` merkt den Ordner kurz; `vergessen` zeigt eine neue Datei sofort (Schreiber im selben Prozess).
3. Ohne Ordner: leer, kein Fehler.
4. `G9dazkategorien.vorgabe(eintrag, tabelle)` gibt dasselbe wie `vorgabe(eintrag)` — die Tabelle nur einmal geholt.
5. `G9eigenstand.veraltet` sieht höchstens einmal je `FRIST_S` in den Ordner.

Sabotage: `passend` ohne `.lower()` -> Fall 1 rot; `vergessen` leer -> Fall 2 rot; `vorgabe` ignoriert `tabelle` -> Fall 4 bleibt
grün, aber der Zähler in Fall 4 (`tabelle()` einmal) wird rot.

Gelaufen am 09.10.2026 (Gesamtlauf auf Ansage): gruen.
"""
import tempfile
import time
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.dazkategorien import G9dazkategorien
from Genesis9.eigenstand import G9eigenstand
from Genesis9.ordnerliste import G9ordnerliste
from Genesis9.pfade import G9pfade

WEGWERF = Path(__file__).resolve().parent / '_wegwerf'

DSX = u"""<Assets>
  <Asset VALUE="People/Genesis 9/Clothing/Neu/Rock.duf">
   <ContentType VALUE="Follower/Wardrobe/Skirt"/>
   <Categories><Category VALUE="/Default/Wardrobe/Skirts"/></Categories>
  </Asset></Assets>"""


class Ordnerliste(SimpleTestCase):

    def _ordner(self):
        WEGWERF.mkdir(exist_ok=True)
        t = tempfile.TemporaryDirectory(dir=WEGWERF)
        self.addCleanup(t.cleanup)
        return Path(t.name)

    def test_1_passend_wie_glob(self):
        namen = ['hemd__a_f1.json', 'HEMD__B_F1.JSON', 'hemd___f1.json', 'hemd__c_f2.json', 'rock__a_f1.json', 'hemd_f1.json']
        self.assertEqual(G9ordnerliste.passend(namen, 'hemd__', '_f1.json'),
                         ['hemd__a_f1.json', 'HEMD__B_F1.JSON', 'hemd___f1.json'])

    def test_2_vergessen_zeigt_die_neue_datei_sofort(self):
        ordner = self._ordner()
        (ordner / 'a.json').write_text('{}')
        self.assertEqual(G9ordnerliste.namen(ordner), ('a.json',))
        (ordner / 'b.json').write_text('{}')
        self.assertEqual(G9ordnerliste.namen(ordner), ('a.json',), 'innerhalb der Frist gemerkt')
        G9ordnerliste.vergessen(ordner)
        self.assertEqual(sorted(G9ordnerliste.namen(ordner)), ['a.json', 'b.json'])

    def test_3_ohne_ordner_leer(self):
        self.assertEqual(G9ordnerliste.namen(self._ordner() / 'fehlt'), ())

    def test_4_vorgabe_mit_und_ohne_tabelle_gleich(self):
        bib = self._ordner()
        (bib / 'Runtime' / 'Support').mkdir(parents=True)
        (bib / 'Runtime' / 'Support' / 'DAZ_3D_1_Neu.dsx').write_text(DSX, encoding='utf-8')
        eintrag = {'art': 'kleidung', 'datei': 'Neu/Rock.duf', 'wurzel': 'People/Genesis 9/Clothing', 'name': 'Rock'}
        with mock.patch.object(G9pfade, 'bibliothek', classmethod(lambda cls: bib)), \
                mock.patch.object(G9pfade, 'vorhanden', classmethod(lambda cls: True)), \
                mock.patch.object(G9pfade, 'eigene', classmethod(lambda cls: bib / 'fehlt')):
            G9dazkategorien.vergessen()
            self.addCleanup(G9dazkategorien.vergessen)
            ohne = G9dazkategorien.vorgabe(eintrag)
            with mock.patch.object(G9dazkategorien, 'tabelle', wraps=G9dazkategorien.tabelle) as zaehler:
                tabelle = G9dazkategorien.tabelle()
                mit = [G9dazkategorien.vorgabe(eintrag, tabelle) for _ in range(50)]
                self.assertEqual(zaehler.call_count, 1, 'die Tabelle wird EINMAL geholt, nicht je Eintrag')
        self.assertEqual(set(mit), {ohne})
        self.assertEqual(ohne, u'Röcke')

    def test_5_eigenstand_sieht_hoechstens_einmal_je_frist_hin(self):
        ordner = self._ordner()
        (ordner / 'Runtime' / 'Support').mkdir(parents=True)
        with mock.patch.object(G9pfade, 'eigene', classmethod(lambda cls: ordner)), \
                mock.patch.object(G9eigenstand, '_stand', None), mock.patch.object(G9eigenstand, '_geprueft', 0.0):
            self.assertFalse(G9eigenstand.veraltet(), 'der erste Aufruf merkt sich nur den Stand')
            (ordner / 'Runtime' / 'Support' / 'x.dsx').write_text('x')
            self.assertFalse(G9eigenstand.veraltet(), 'innerhalb der Frist wird nicht in den Ordner gesehen')
            G9eigenstand._geprueft = time.monotonic() - G9eigenstand.FRIST_S - 0.1
            with mock.patch.object(G9eigenstand, 'vergessen'):
                self.assertTrue(G9eigenstand.veraltet(), 'nach der Frist ist die neue .dsx bemerkt')
