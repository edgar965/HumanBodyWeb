# -*- coding: utf-8 -*-
"""Ein Neubau der Morph-Ablage lässt keine Lücke (`G9morphfamilieschreiber.leeren` / `aufraeumen`, 17.10.2026).

WARUM (Edgar, 17.10.2026: „lebensalter Regler jung funktioniert nicht"): `leeren()` löschte alle Regler vor dem Neubau; der Neubau (HumanBody ~100 s, MakeHuman Minuten) legte sie erst
nach und nach wieder an. Wer in der Zeit den Lebensalter-Schieber bewegte, bekam ein Netz ohne `mh:macro_Alter_*` — ein Schieber, der nichts tut. Zusagen:

1. Nach `leeren()` ist jeder alte Regler weiter lesbar (nichts ist gelöscht), `deltas` liefert ihn.
2. `bestand_schreiben` — der Abschluss jedes Neubaus — räumt weg, was der Lauf nicht neu geschrieben hat (einen Regler, den es nicht mehr gibt); neu Geschriebenes bleibt.
3. Ein Regler, der im Neubau nur noch einen Steckbrief bekommt (übergangen), verliert seine `.npz`, behält den Steckbrief und steht dann unter `uebergangene()`.
4. Ohne `leeren()` löscht `bestand_schreiben` nichts (ein Bauer ohne Neubau-Start räumt nicht auf).

FEHLERBILD OHNE DIESE TESTS: Wer `leeren()` wieder löscht, macht jedes Neubauen zu einem Fenster, in dem Schieber wirkungslos sind — ohne Fehler, ohne Log.
Gefahren am 17.10.2026 (auf Ansage „Teste alle Morphs"): grün. Sabotage-Gegenprobe gefahren: `aufraeumen` löscht nichts → Fall 2 und 3 rot. Nicht gefahren: in `leeren` die Dateien wieder löschen → Fall 1 müsste rot werden.
"""
import shutil
import time
from pathlib import Path

from django.test import SimpleTestCase
from Genesis9.hbmorphe import G9hbmorphe
from Genesis9.morphfamilieschreiber import G9morphfamilieschreiber


class _Ordner:
    """Den Ablageordner fuer die Dauer eines Tests umlenken."""

    def __init__(self):
        self.pfad = Path(__file__).parent / 'tmp_morphneubau'
        self.alt = G9hbmorphe.ordner

    def __enter__(self):
        shutil.rmtree(self.pfad, ignore_errors=True)
        G9hbmorphe.ordner = classmethod(lambda cls: self.pfad)
        G9hbmorphe.vergessen()
        return self.pfad

    def __exit__(self, *_):
        G9hbmorphe.ordner = self.alt
        G9hbmorphe.vergessen()
        G9hbmorphe._neubau_start = None
        shutil.rmtree(self.pfad, ignore_errors=True)


def _alt_machen():
    """Die Marge der Dateizeiten abwarten: was jetzt liegt, ist vor dem Start des Neubaus geschrieben."""
    time.sleep((G9morphfamilieschreiber.MARGE_NS / 1e9) + 0.1)


class NeubauTest(SimpleTestCase):
    databases = set()

    def _zwei_alte(self):
        G9hbmorphe.ablegen('Nose_Width', [1], [[0.01, 0, 0]], [[0, 0, 0]])
        G9hbmorphe.ablegen('Chin_Tone', [2], [[0, 0.01, 0]], [[0, 0, 0]])
        G9hbmorphe.bestand_schreiben({'zahl': 2})
        _alt_machen()

    def test_1_nach_leeren_ist_jeder_alte_regler_noch_da(self):
        with _Ordner():
            self._zwei_alte()
            G9hbmorphe.leeren()
            for name in ('hb:Nose_Width', 'hb:Chin_Tone'):
                self.assertTrue(G9hbmorphe.vorhanden(name), name)
                self.assertIsNotNone(G9hbmorphe.deltas(name, 1.0), '%s muss mitten im Neubau lesbar sein' % name)
            self.assertEqual({r['name'] for r in G9hbmorphe.liste()}, {'hb:Nose_Width', 'hb:Chin_Tone'})

    def test_2_der_abschluss_raeumt_weg_was_der_lauf_nicht_neu_schrieb(self):
        with _Ordner() as ordner:
            self._zwei_alte()
            G9hbmorphe.leeren()
            G9hbmorphe.ablegen('Nose_Width', [1], [[0.02, 0, 0]], [[0, 0, 0]])           # neu geschrieben
            G9hbmorphe.bestand_schreiben({'zahl': 1})
            self.assertTrue(G9hbmorphe.vorhanden('hb:Nose_Width'))
            self.assertFalse(G9hbmorphe.vorhanden('hb:Chin_Tone'), 'nicht neu geschrieben = gibt es nicht mehr')
            self.assertFalse((ordner / 'Chin_Tone.json').is_file())
            self.assertTrue((ordner / 'bestand.json').is_file())
            _n, d = G9hbmorphe.deltas('hb:Nose_Width', 1.0)
            self.assertAlmostEqual(float(d[0][0]), 0.02, places=6, msg='die neue Fassung, nicht die alte')

    def test_3_ein_uebergangener_regler_behaelt_nur_den_steckbrief(self):
        with _Ordner():
            self._zwei_alte()
            G9hbmorphe.leeren()
            G9hbmorphe.steckbrief_schreiben('Chin_Tone', {'uebergangen': 'wirkt auf Genesis nicht'})
            G9hbmorphe.bestand_schreiben({'zahl': 0})
            self.assertFalse(G9hbmorphe.vorhanden('hb:Chin_Tone'))
            self.assertEqual([u['kennung'] for u in G9hbmorphe.uebergangene()], ['Chin_Tone'])

    def test_4_ohne_neubau_start_loescht_der_abschluss_nichts(self):
        with _Ordner():
            self._zwei_alte()
            G9hbmorphe.bestand_schreiben({'zahl': 2})
            self.assertTrue(G9hbmorphe.vorhanden('hb:Nose_Width'))
            self.assertTrue(G9hbmorphe.vorhanden('hb:Chin_Tone'))
