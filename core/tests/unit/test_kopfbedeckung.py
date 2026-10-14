# -*- coding: utf-8 -*-
"""Mesh to 3D, 12.10.2026: ein Hut ist Zubehör, nicht Haar (`Sapienshaar.kopfbedeckung`, `Meshfigurkleidung._kopfbedeckung`).

Anlass (Zauberer, Lauf `…12.04.48`): die Farbregel der Haarmaske hielt den Hut für Haar (125.597 Flächen an der Krempe, 34.238 am Kegel); Sapiens nennt dieselben Flächen zu 88 % `Apparel`. Das Haar-Objekt war ein Hut
mit Strähnen, und die Kopfhaut bekam die Hutfarbe (graue Kappe). Kunstdaten (Flächen mit Stimmen je Klasse), keine Datenbank.
Sabotage-Gegenprobe: in `Sapienshaar.kopfbedeckung` `apparel > cls.HUT_VERHAELTNIS * haar` durch `apparel > 0` ersetzen → `test_unter_dem_verhaeltnis_ist_es_haar` wird rot; die Zeile `stueck[hut] = …ZUBEHOER` streichen → `test_der_hut_wird_zubehoer`.
"""

import os
import unittest
from types import SimpleNamespace

import numpy as np

from core.dienste.meshfigurkleidung import Meshfigurkleidung
from core.dienste.sapienshaar import Sapienshaar
from Kleidung.sapienszuordnung import Sapienszuordnung

from ._pruefablage import Pruefablage

APPAREL = Sapienszuordnung.NAMEN.index('Apparel')
HAIR = Sapienszuordnung.NAMEN.index('Hair')


def _klassen(n, apparel=0.0, haar=0.0):
    k = np.zeros((n, len(Sapienszuordnung.NAMEN)), dtype=np.float32)
    k[:, APPAREL], k[:, HAIR] = apparel, haar
    return k


class KopfbedeckungTest(unittest.TestCase):
    def test_haar_bleibt_haar(self):
        klassen = _klassen(100, haar=50.0)
        self.assertFalse(Sapienshaar.kopfbedeckung(np.ones(100, bool), klassen, np.full(100, 5.0)).any())

    def test_ein_hut_wird_erkannt(self):
        klassen = np.concatenate([_klassen(100, haar=50.0), _klassen(100, apparel=40.0, haar=5.0)])
        kandidaten = np.ones(200, bool)
        hut = Sapienshaar.kopfbedeckung(kandidaten, klassen, np.full(200, 5.0))
        self.assertEqual(int(hut.sum()), 100)
        self.assertTrue(hut[100:].all() and not hut[:100].any())

    def test_unter_dem_verhaeltnis_ist_es_haar(self):
        """Apparel 10 gegen Hair 8 (1,25 < 1,5): eine strittige Fläche gilt als Haar."""
        klassen = _klassen(100, apparel=10.0, haar=8.0)
        self.assertFalse(Sapienshaar.kopfbedeckung(np.ones(100, bool), klassen, np.full(100, 5.0)).any())

    def test_nur_flaechen_der_haarmaske_koennen_hut_sein(self):
        klassen = _klassen(100, apparel=40.0, haar=1.0)
        kandidaten = np.zeros(100, bool)
        kandidaten[:50] = True
        hut = Sapienshaar.kopfbedeckung(kandidaten, klassen, np.full(100, 5.0))
        self.assertEqual(int(hut.sum()), 50)
        self.assertFalse(hut[50:].any())

    def test_ein_kleiner_fleck_ist_kein_hut(self):
        """Ein Haarreif oder ein Fleck (unter `HUT_MIN_CM2`) bleibt, wo er war."""
        klassen = _klassen(3, apparel=40.0, haar=1.0)
        self.assertFalse(Sapienshaar.kopfbedeckung(np.ones(3, bool), klassen, np.full(3, 5.0)).any())      # 15 cm²


class AusbreitenTest(unittest.TestCase):
    """`Sapienshaar.ausbreiten`: ungesehene Hutflächen (Rückseite, Innenseite der Krempe) über der Krempe gehören dazu.

    Anlass: am Zauberer blieben 44.889 Hutflächen (974 cm², 61 % ohne jede Sapiens-Stimme) als Punktwolke im Haar-Objekt. Kette aus zehn Flächen (0–9), Höhe = Nummer in cm.
    Sabotage-Gegenprobe: die Bedingung `hoehe >= grenze` streichen → `test_unter_der_krempe_bleibt_haar` wird rot; `connected_components` durch `frei` ersetzen → `test_nur_zusammenhaengendes_wird_hut` rot.
    """

    @staticmethod
    def _kette(n):
        from scipy.sparse import diags

        return diags([np.ones(n - 1), np.ones(n - 1)], [-1, 1], format='csr')

    def _lauf(self, hut, kandidaten, hoehe):
        mask = lambda ids: np.isin(np.arange(10), ids)           # noqa: E731 — Dictionary gewollt: Kurzschreibweise der Prüfung
        return np.flatnonzero(Sapienshaar.ausbreiten(mask(hut), mask(kandidaten), self._kette(10), np.asarray(hoehe, dtype=float)))

    def test_ungesehene_nachbarn_ueber_der_krempe_kommen_dazu(self):
        hoehe = np.arange(10) * 0.01 + 1.0
        self.assertEqual(self._lauf([0, 1], [2, 3, 4], hoehe).tolist(), [0, 1, 2, 3, 4])

    def test_unter_der_krempe_bleibt_haar(self):
        """Flächen 2–4 liegen 10 cm unter der Hutunterkante (0,02 m Puffer): das Haar unter der Krempe bleibt, wo es war."""
        hoehe = np.array([2.0, 2.0, 1.9, 1.9, 1.9, 2.0, 2.0, 2.0, 2.0, 2.0])
        self.assertEqual(self._lauf([0, 1], [2, 3, 4, 5], hoehe).tolist(), [0, 1])

    def test_nur_zusammenhaengendes_wird_hut(self):
        """Fläche 3 fehlt in der Kette (gesehenes Haar, kein Kandidat): 4 und 5 hängen nicht mehr am Hut."""
        hoehe = np.full(10, 2.0)
        self.assertEqual(self._lauf([0, 1], [2, 4, 5], hoehe).tolist(), [0, 1, 2])

    def test_ohne_hut_bleibt_alles_wie_es_war(self):
        self.assertEqual(self._lauf([], [2, 3, 4], np.full(10, 2.0)).tolist(), [])

    def test_die_haarmaske_hat_die_flaechenmitten_die_anwenden_liest(self):
        """Attrappen-Wächter (`attrappen-signatur.md`): `anwenden` liest `haarmaske.mitte`, `.nachbarn()` und `.inhalt` — die echte Klasse muss sie führen."""
        from pathlib import Path

        quelle = (Path(__file__).resolve().parents[4] / 'Haar' / 'haarmaske.py').read_text(encoding='utf-8')
        for name in ('self.mitte = ', 'self.inhalt = ', 'def nachbarn(self)'):
            self.assertIn(name, quelle)


class KopfAnkerTest(unittest.TestCase):
    """`Sapienshaar.kopf_anker` (13.10.2026): die Bestandteile der Gruppe „kopf“ (SAM 3) sind der Anker, von dem die Ausbreitung der Kopfbedeckung ausgeht.

    Anlass: Spiralballerina — 379 von 899 Flächen des Haar-Objekts berührten den Kopfschmuck, 467 waren von Sapiens nie gesehen. Streifen aus 40 Flächen, Fläche i hat die Ecken i, i+1, i+2, je 2 cm².
    Sabotage-Gegenprobe: in `kopf_anker` `teil['gruppe'] == 'kopf'` durch `True` ersetzen → `test_nur_die_gruppe_kopf_ist_anker` wird rot; die Prüfung `datei.is_file()` streichen → `test_ohne_datei_gibt_es_keinen_anker` wirft.
    """

    N = 40

    def _ablegen(self, ordner, gruppe='kopf', treffer=2):
        stimmen = np.zeros((self.N, 1), dtype=np.float32)
        stimmen[:15, 0] = 10.0                                         # SAM 3 sieht den Begriff auf den Flächen 0–14 (30 cm², über `MIN_CM2` 20)
        np.savez(os.path.join(ordner, 'teile_flaechen.npz'), flaechen=self.N, begriffe=np.array(['headdress']), gruppen=np.array([gruppe]), stimmen=stimmen,
                 treffer=np.array([treffer]), bestwert=np.array([0.9]), pixel=np.full(self.N, 10.0, dtype=np.float32))

    def _anker(self, ordner, anzahl=None):
        schritt = Sapienshaar.__new__(Sapienshaar)
        schritt.ablage = SimpleNamespace(arbeit=lambda name='': os.path.join(ordner, name))          # wie in den übrigen Tests ein Pfad als Text
        flaechen = np.stack([np.arange(self.N), np.arange(self.N) + 1, np.arange(self.N) + 2], axis=1)
        return schritt.kopf_anker(SimpleNamespace(flaechen=flaechen, inhalt=np.full(self.N, 2e-4)), self.N if anzahl is None else anzahl)

    def test_ein_kopf_bestandteil_ist_der_anker(self):
        with Pruefablage.ordner() as ordner:
            self._ablegen(ordner)
            anker = self._anker(ordner)
        self.assertEqual(np.flatnonzero(anker).tolist(), list(range(15)))

    def test_nur_die_gruppe_kopf_ist_anker(self):
        with Pruefablage.ordner() as ordner:
            self._ablegen(ordner, gruppe='requisit')
            self.assertFalse(self._anker(ordner).any())

    def test_ohne_datei_gibt_es_keinen_anker(self):
        with Pruefablage.ordner() as ordner:
            self.assertFalse(self._anker(ordner).any())

    def test_zu_einem_anderen_netz_gibt_es_keinen_anker(self):
        with Pruefablage.ordner() as ordner:
            self._ablegen(ordner)
            self.assertFalse(self._anker(ordner, anzahl=self.N + 5).any())

    def test_ein_begriff_in_einer_ansicht_ist_kein_bestandteil_und_kein_anker(self):
        with Pruefablage.ordner() as ordner:
            self._ablegen(ordner, treffer=1)                         # `Bestandteile.MIN_ANSICHTEN` = 2
            self.assertFalse(self._anker(ordner).any())

    def test_die_ausbreitung_geht_vom_anker_aus_und_laesst_klares_haar_stehen(self):
        """Wie `anwenden` sie ruft: Kandidaten = Haarmaske ohne die Flächen, die Sapiens eindeutig als Haar sieht."""
        from scipy.sparse import diags

        with Pruefablage.ordner() as ordner:
            self._ablegen(ordner)
            anker = self._anker(ordner)
        haarmaske = np.zeros(self.N, dtype=bool)
        haarmaske[15:30] = True                                        # Haarmaske: 15–29
        klar_haar = np.zeros(self.N, dtype=bool)
        klar_haar[22:30] = True                                        # Sapiens sieht 22–29 eindeutig als Haar
        kette = diags([np.ones(self.N - 1), np.ones(self.N - 1)], [-1, 1], format='csr')
        hut = Sapienshaar.ausbreiten(anker, haarmaske & ~klar_haar, kette, np.full(self.N, 2.0)) & ~anker
        self.assertEqual(np.flatnonzero(hut).tolist(), list(range(15, 22)))

    def test_anwenden_ruft_den_anker_mit_dem_klaren_haar(self):
        """Verdrahtung: `anwenden` benutzt `kopf_anker` und schließt klares Sapiens-Haar von den Kandidaten aus (Quelltext)."""
        from pathlib import Path

        quelle = (Path(__file__).resolve().parents[2] / 'dienste' / 'sapienshaar.py').read_text(encoding='utf-8')
        anwenden = quelle[quelle.index('def anwenden'):quelle.index('HUT_VERHAELTNIS')]
        self.assertIn('self.kopf_anker(haarmaske, anzahl_flaechen)', anwenden)
        self.assertIn('neu & ~klar_haar', anwenden)


class KleidungsschrittTest(unittest.TestCase):
    """`Meshfigurkleidung._kopfbedeckung`: die Flächen aus `haar_maske.npz` werden Zubehör."""

    def setUp(self):
        self._ablage = Pruefablage.ordner()
        self.ordner = self._ablage.__enter__()
        self.addCleanup(self._ablage.__exit__, None, None, None)
        self.schritt = Meshfigurkleidung.__new__(Meshfigurkleidung)
        self.schritt.ablage = SimpleNamespace(arbeit=lambda name='': os.path.join(self.ordner, name))
        self.inhalt = np.full(10, 1e-4)                                          # je 1 cm²
        self.regel = SimpleNamespace(inhalt=self.inhalt, abschliessen=lambda stueck: {'stueck': np.asarray(stueck, dtype=np.int8), 'kleidung': np.asarray(stueck) > 0})
        self.maske = {'stueck': np.array([1, 1, 2, 0, 0, 0, 0, 0, 0, 0], dtype=np.int8)}

    def _hut_ablegen(self, hut, **mehr):
        np.savez(os.path.join(self.ordner, 'haar_maske.npz'), haar=np.zeros(10, bool), kopfbedeckung=np.asarray(hut, bool), **mehr)

    def test_der_hut_wird_zubehoer(self):
        from Kleidung.kleidungsmaske import Kleidungsmaske

        self._hut_ablegen([0, 0, 0, 0, 0, 0, 1, 1, 1, 0])
        neu, bericht = self.schritt._kopfbedeckung(self.maske, self.regel)
        self.assertEqual(neu['stueck'].tolist(), [1, 1, 2, 0, 0, 0, 4, 4, 4, 0])
        self.assertEqual(Kleidungsmaske.ZUBEHOER, 4)
        self.assertEqual(bericht, {'flaechen': 3, 'cm2': 3.0})
        self.assertEqual(self.maske['stueck'].tolist(), [1, 1, 2, 0, 0, 0, 0, 0, 0, 0], 'die Eingabe bleibt unverändert')

    def test_ohne_hut_bleibt_alles(self):
        self._hut_ablegen([0] * 10)
        neu, bericht = self.schritt._kopfbedeckung(self.maske, self.regel)
        self.assertIs(neu, self.maske)
        self.assertIsNone(bericht)

    def test_ohne_ablage_oder_mit_alter_ablage_bleibt_alles(self):
        neu, bericht = self.schritt._kopfbedeckung(self.maske, self.regel)           # keine Datei
        self.assertIs(neu, self.maske)
        np.savez(os.path.join(self.ordner, 'haar_maske.npz'), haar=np.zeros(10, bool))   # Ablage von vor dem 12.10.2026: ohne `kopfbedeckung`
        neu, bericht = self.schritt._kopfbedeckung(self.maske, self.regel)
        self.assertIs(neu, self.maske)
        self.assertIsNone(bericht)

    def test_eine_ablage_fuer_ein_anderes_netz_zaehlt_nicht(self):
        self._hut_ablegen([1, 1, 1])                                          # 3 statt 10 Flächen
        neu, bericht = self.schritt._kopfbedeckung(self.maske, self.regel)
        self.assertIs(neu, self.maske)
        self.assertIsNone(bericht)


if __name__ == '__main__':
    unittest.main()
