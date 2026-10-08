# -*- coding: utf-8 -*-
u"""Die Befunde vom 06.10.2026 zu Neulauf und Kopie von „2D3D Kleider" — Kunstdaten, keine Aufträge, keine Grafikkarte.

1. `Iterationsarchiv`: Runden eines Auftrags beiseitelegen, wenn Fotos, Netz oder Körper neu rechnen — Eintrag und Dateien, nichts gelöscht, ohne Runden nichts.
2. `Engine2d3dKleiderauftragsablagen`: Dateien mit dem Kürzel der Quelle unter dem Kürzel des Ziels neu anlegen, nichts überschreiben, Text umsetzen, zurücknehmen.

Sabotage: in `Iterationsarchiv.beiseite` die `pop`-Schleife weglassen → Fall 1 rot (die Runden stehen weiter im Ergebnis, die neue Iteration 0 träte wieder gegen sie an); in
`Engine2d3dKleiderauftragsablagen.dateien` das Kürzel als Teilwort zulassen (`'*%s*'` ohne Wortgrenze) → Fall 3 rot (die Datei eines Auftrags mit längerer Kennung ginge mit).
"""
import json
from pathlib import Path
from types import SimpleNamespace

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderauftragsablagen import Engine2d3dKleiderauftragsablagen
from core.dienste.iterationsarchiv import Iterationsarchiv

from ._pruefablage import Pruefablage


class _Ablage:
    """Wie `Engine2d3dKleiderablage.iterationen`: der Ordner `iterationen/` eines Auftrags."""

    def __init__(self, ordner):
        self.ordner = Path(ordner)

    def iterationen(self, name=''):
        return self.ordner / name if name else self.ordner


class ArchivTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _job():
        runden = [{'runde': n, 'art': 'ausgang' if n == 0 else 'begutachtung', 'note': {'gesamt': 0.4 - 0.01 * n}} for n in range(3)]
        ergebnis = {'iterationen': runden, 'kreislauf': {'runde_bester': 2, 'modell': {'x': 1}, 'note': {'gesamt': 0.38}}, 'begutachtung': {'zustand': 'wartet'},
                    'netz': {'bleibt': True}}
        return SimpleNamespace(kennung='2026.10.06.14.10.22', ergebnis=ergebnis)

    def test_1_runden_gehen_beiseite_ohne_etwas_zu_loeschen(self):
        with Pruefablage.ordner('archiv_') as ordner:
            ablage = _Ablage(ordner)
            (ablage.iterationen() / 'nachbesserung').mkdir()
            (ablage.iterationen() / 'nachbesserung' / 'zustand.json').write_text('{}', encoding='utf-8')
            for name in ('runde_000_vergleich.png', 'runde_001_kopf.png', 'runde_002_formbezug.npz', 'andere.txt'):
                (ablage.iterationen() / name).write_bytes(b'x')
            job = self._job()
            zeile = Iterationsarchiv(job, ablage).beiseite('Schritt „netz“ neu gerechnet')
            self.assertEqual((zeile['runden'], zeile['beste'], zeile['gesamt'], zeile['dateien']), (3, 2, 0.38, 3))
            for schluessel in ('iterationen', 'kreislauf', 'begutachtung'):
                self.assertNotIn(schluessel, job.ergebnis)
            self.assertEqual(job.ergebnis['netz'], {'bleibt': True})
            self.assertEqual(job.ergebnis['fruehere_runden'], [zeile])
            ziel = ablage.iterationen() / zeile['ordner']
            self.assertEqual(sorted(p.name for p in ziel.iterdir() if p.name.startswith('runde_')),
                             ['runde_000_vergleich.png', 'runde_001_kopf.png', 'runde_002_formbezug.npz'])
            self.assertEqual([r['runde'] for r in json.loads((ziel / Iterationsarchiv.DATEI).read_text(encoding='utf-8'))['iterationen']], [0, 1, 2])
            # Was nicht zu den Runden gehört, bleibt liegen — auch der Unterordner der Nachbesserung.
            self.assertTrue((ablage.iterationen() / 'andere.txt').is_file())
            self.assertTrue((ablage.iterationen() / 'nachbesserung' / 'zustand.json').is_file())
            self.assertFalse((ablage.iterationen() / 'runde_000_vergleich.png').exists())

    def test_2_ohne_runden_nichts_und_ein_zweites_mal_nichts(self):
        with Pruefablage.ordner('archiv_') as ordner:
            leer = SimpleNamespace(kennung='x', ergebnis={'netz': {}})
            self.assertIsNone(Iterationsarchiv(leer, _Ablage(ordner)).beiseite('grund'))
            self.assertNotIn('fruehere_runden', leer.ergebnis)
            job = self._job()
            Iterationsarchiv(job, _Ablage(ordner)).beiseite('erstens')
            self.assertIsNone(Iterationsarchiv(job, _Ablage(ordner)).beiseite('zweitens'))   # zwei Schritte in einem Lauf legen nicht zweimal weg
            self.assertEqual(len(job.ergebnis['fruehere_runden']), 1)

    def test_3_nur_die_schritte_die_fotos_netz_oder_koerper_neu_erzeugen(self):
        for name in ('vorbereitung', 'netz', 'koerper'):
            self.assertTrue(Iterationsarchiv.veraltet_durch(name), name)
        for name in ('segmentierung', 'grundfigur', 'kleiderstuecke', 'iterationen', 'export', 'film', 'speichern'):
            self.assertFalse(Iterationsarchiv.veraltet_durch(name), name)


class AblagenTest(SimpleTestCase):
    databases = set()
    ALT, NEU = 'j20261006003338', 'j20261006142055'

    def _ablagen(self, wurzel):
        ordner = [Path(wurzel) / n for n in ('kleidtexturen', 'kleidmorphe', 'eigenmorphe')]
        for o in ordner:
            o.mkdir()

        class Unter(Engine2d3dKleiderauftragsablagen):
            @staticmethod
            def ordner():
                return ordner
        return Unter('2026.10.06.00.33.38', '2026.10.06.14.20.55'), ordner

    def test_1_dateien_unter_dem_neuen_kuerzel_ohne_die_der_quelle_zu_aendern(self):
        with Pruefablage.ordner('ablagen_') as wurzel:
            a, (tex, morph, koerper) = self._ablagen(wurzel)
            (tex / ('g9_base_shirt__shirt__foto_%s_f1.png' % self.ALT)).write_bytes(b'PNG')
            (tex / ('g9_base_shirt__foto_%s_f1.json' % self.ALT)).write_text(json.dumps({'kuerzel': self.ALT, 'n': 3}), encoding='utf-8')
            (morph / ('g9_base_shirt__netz_b1s4_%s_f1.npz' % self.ALT)).write_bytes(b'NPZ')
            (koerper / ('ort_rumpftiefe_%s.npz' % self.ALT)).write_bytes(b'NPZ')
            self.assertEqual(a.kopieren(), 4)
            self.assertEqual(sorted(p.name for p in tex.iterdir()), sorted([
                'g9_base_shirt__shirt__foto_%s_f1.png' % self.ALT, 'g9_base_shirt__foto_%s_f1.json' % self.ALT,
                'g9_base_shirt__shirt__foto_%s_f1.png' % self.NEU, 'g9_base_shirt__foto_%s_f1.json' % self.NEU]))
            self.assertEqual((tex / ('g9_base_shirt__shirt__foto_%s_f1.png' % self.NEU)).read_bytes(), b'PNG')
            neu = json.loads((tex / ('g9_base_shirt__foto_%s_f1.json' % self.NEU)).read_text(encoding='utf-8'))
            self.assertEqual(neu, {'kuerzel': self.NEU, 'n': 3})                  # Text umgesetzt
            alt = json.loads((tex / ('g9_base_shirt__foto_%s_f1.json' % self.ALT)).read_text(encoding='utf-8'))
            self.assertEqual(alt['kuerzel'], self.ALT)                            # die Quelle bleibt
            self.assertTrue((morph / ('g9_base_shirt__netz_b1s4_%s_f1.npz' % self.NEU)).is_file())
            self.assertTrue((koerper / ('ort_rumpftiefe_%s.npz' % self.NEU)).is_file())

    def test_2_nichts_wird_ueberschrieben_und_zuruecknehmen_raeumt_nur_das_eigene(self):
        with Pruefablage.ordner('ablagen_') as wurzel:
            a, (tex, _morph, koerper) = self._ablagen(wurzel)
            (koerper / ('ort_a_%s.npz' % self.ALT)).write_bytes(b'neu')
            (koerper / ('ort_b_%s.npz' % self.ALT)).write_bytes(b'neu')
            vorhanden = koerper / ('ort_a_%s.npz' % self.NEU)
            vorhanden.write_bytes(b'ALT')
            self.assertEqual(a.kopieren(), 1)
            self.assertEqual(vorhanden.read_bytes(), b'ALT')
            self.assertEqual(a.schon_da, ['ort_a_%s.npz' % self.NEU])
            a.zuruecknehmen()
            self.assertTrue(vorhanden.is_file())                                   # was schon da war, bleibt
            self.assertFalse((koerper / ('ort_b_%s.npz' % self.NEU)).exists())

    def test_3_das_kuerzel_gilt_nur_als_ganzes_wort(self):
        with Pruefablage.ordner('ablagen_') as wurzel:
            a, (tex, _morph, _koerper) = self._ablagen(wurzel)
            (tex / ('x__foto_%s7_f1.png' % self.ALT)).write_bytes(b'andere Kennung')      # längere Kennung (Sekunden mit Bruchteil) ist ein anderer Auftrag
            (tex / ('x__foto_%s_f1.png' % self.ALT)).write_bytes(b'gleiche')
            self.assertEqual([q.name for q, _z in a.dateien()], ['x__foto_%s_f1.png' % self.ALT])

    def test_4_text_umsetzen_kennung_und_kuerzel(self):
        a = Engine2d3dKleiderauftragsablagen('2026.10.06.00.33.38', '2026.10.06.14.20.55')
        text = '{"pfad": "…/2026.10.06.00.33.38/arbeit", "regler": "g9_base_shirt.eigen.huelle_%s", "fremd": "j20261006003339"}' % self.ALT
        self.assertTrue(a.enthaelt(text))
        umgesetzt = a.ersetzen(text)
        self.assertIn('/2026.10.06.14.20.55/arbeit', umgesetzt)
        self.assertIn('huelle_%s"' % self.NEU, umgesetzt)
        self.assertIn('j20261006003339', umgesetzt)                                   # ein anderes Kürzel bleibt
        self.assertFalse(a.enthaelt(umgesetzt))
