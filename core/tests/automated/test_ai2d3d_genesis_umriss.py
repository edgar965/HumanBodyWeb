# -*- coding: utf-8 -*-
"""Der Umriss des Genesis-Ergebnisses (schwarz) liegt auf dem Umriss der Person im Foto (blau) — Feld 3 der Blöcke „Körper vorne und hinten“ auf der Jobseite.

WARUM: Edgar, 29.10.2026 nachts, mit einem Bild von Feld 3 (Lauf 2026.10.28.22.50): „das ist sowas von Schwachsinn!! siehe dir das Bild an, den Unterschied zwischen den linien
siehst du. Das soll als Fehlerfall gelten. Melde dich erst, wenn die gemessenen blauen und schwarzen Linien übereinstimmen“. Der Ellbogen-Test war bis dahin grün an der
geometrischen Figur (grün) — Schwarz stand daneben, und keine Prüfung maß es. Schwarz kam damals aus `block_koerper_vorne.json` (Stand nurjob4 vom 27.10.2026, eine andere Figur);
dieser Stand liegt als `daten/ai2d3d_edgartrip_block_koerper_vorne_nurjob4.json` bei und MUSS durchfallen.

Gemessen wird, was der Lauf ablegt (`<Job>/abnahme/training.json`): je Foto `koerper.vorlage` (Rand der Person im Foto) und `koerper.genesis.ergebnis` (Rand der Genesis-Figur samt
Augen und Hüllen in derselben Kamera, `Genesisumriss` in `mesh_auf_genesis.py`), Pixel des Fotos, jeder 4. Punkt. Je Punkt der Abstand zum nächsten Punkt der anderen Seite, beide
Richtungen. Bewertet je Zelle eines Rasters von ZELLE_MM (der Fehler ist örtlich: ein Ellbogen, eine Hand — ein Mittel über den ganzen Körper verdeckt ihn): in jeder Zelle mit
mindestens MIN_PUNKTE Punkten Median ≤ 5 mm und 90 % ≤ 15 mm — die Grenzen des Auftrags EdgarTrip für den Umriss (Median 5, Max 15), statt des Maximums das 90-%-Quantil, damit ein
einzelnes Randpixel der Segmentierung nicht allein entscheidet.

Nur lesen, nie schreiben. Ohne training.json wird übersprungen; ein Lauf ohne Genesis-Ergebnis fällt durch (Schwarz fehlt = nicht übereinstimmend).

    manage.py test core.tests.automated.test_ai2d3d_genesis_umriss
"""

import json
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase


class Ai2d3dGenesisUmriss(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'
    ZELLE_MM = 60.0
    MIN_PUNKTE = 5
    MEDIAN_MM, P90_MM = 5.0, 15.0
    #: Gegenprobe: so weit verschoben muss die Prüfung durchfallen (mm)
    SCHUB_MM = 20.0
    BILD_EDGAR = Path(__file__).parent / 'daten' / 'ai2d3d_edgartrip_block_koerper_vorne_nurjob4.json'

    @staticmethod
    def naechst(a, b):
        """(len(a),) Abstand je Punkt von a zum nächsten in b (px)."""
        aus = np.empty(len(a))
        for i in range(0, len(a), 512):
            aus[i:i + 512] = np.sqrt(((a[i:i + 512, None] - b[None]) ** 2).sum(2)).min(1)
        return aus

    @classmethod
    def zellen(cls, vorlage, ergebnis, mm_je_px):
        """[(Mitte der Zelle px, Median mm, 90 % mm, Punkte)] je Zelle mit genug Punkten; leer, wenn eine Seite keine Punkte hat."""
        v, e = np.asarray(vorlage, dtype=np.float64).reshape(-1, 2), np.asarray(ergebnis, dtype=np.float64).reshape(-1, 2)
        if not len(v) or not len(e):
            return []
        d = np.concatenate([cls.naechst(v, e), cls.naechst(e, v)]) * mm_je_px
        p = np.concatenate([v, e])
        groesse = cls.ZELLE_MM / mm_je_px
        z = np.floor(p / groesse).astype(np.int64)
        aus = []
        for zelle in np.unique(z, axis=0):
            drin = (z == zelle).all(1)
            w = d[drin]
            if len(w) >= cls.MIN_PUNKTE:
                aus.append(((zelle + 0.5) * groesse, float(np.median(w)), float(np.quantile(w, 0.9)), int(len(w))))
        return aus

    @classmethod
    def schlecht(cls, zellen):
        return [z for z in zellen if z[1] > cls.MEDIAN_MM or z[2] > cls.P90_MM]

    @staticmethod
    def _text(datei, zellen, schlecht):
        schlimm = sorted(schlecht, key=lambda z: -z[2])[:6]
        return '%s: %d von %d Zellen über der Grenze%s' % (datei, len(schlecht), len(zellen), (' — z. B. ' + '; '.join(
            'bei (%d, %d) px Median %.1f / 90 %% %.1f mm' % (m[0], m[1], med, p90) for m, med, p90, _n in schlimm)) if schlimm else '')

    def _daten(self):
        datei = Path(settings.OBJECTS_ROOT) / 'ai2d3d' / self.JOB / 'abnahme' / 'training.json'
        if not datei.is_file():
            self.skipTest('kein Lauf: %s fehlt' % datei)
        daten = json.loads(datei.read_text(encoding='utf-8'))
        fotos = {nr: f for nr, f in daten['fotos'].items() if f.get('koerper')}
        if not fotos:
            self.skipTest('Lauf %s hat den Körper nicht gerechnet' % daten.get('lauf'))
        return daten['lauf'], fotos

    def test_schwarz_genesis_liegt_auf_blau_foto(self):
        lauf, fotos = self._daten()
        ohne = [f['datei'] for f in fotos.values() if not f['koerper'].get('genesis')]
        self.assertFalse(ohne, 'Lauf %s: kein Genesis-Ergebnis in %s — mesh_auf_genesis.py %s' % (lauf, ohne, lauf))
        texte, fehler = [], 0
        for f in fotos.values():
            z = self.zellen(f['koerper']['vorlage'], f['koerper']['genesis']['ergebnis'], f['mm_je_px'])
            s = self.schlecht(z)
            self.assertTrue(z, '%s: nichts gemessen' % f['datei'])
            fehler += len(s)
            texte.append(self._text(f['datei'], z, s))
        self.assertEqual(fehler, 0, 'Lauf %s, Grenze je %d-mm-Zelle Median %.0f / 90 %% %.0f mm — %s' % (lauf, self.ZELLE_MM, self.MEDIAN_MM, self.P90_MM, ' | '.join(texte)))

    def test_gegenprobe_bild_von_edgar_faellt_durch(self):
        """Der Stand, den Edgar am 29.10.2026 als Fehlerfall gezeigt hat: blau und schwarz aus dem Block (Umrisse der Eigenregler)."""
        b = json.loads(self.BILD_EDGAR.read_text(encoding='utf-8'))
        for f in b['fotos'].values():
            v = [p for u in f['umrisse'] for p in u['vorlage'] if p]
            e = [p for u in f['umrisse'] for p in u['ergebnis'] if p]
            z = self.zellen(v, e, f['mm_je_px'])
            self.assertTrue(z)
            self.assertTrue(self.schlecht(z), '%s: Edgars Fehlerfall besteht — %s' % (f['datei'], self._text(f['datei'], z, [])))

    def test_gegenprobe_foto_gegen_foto_besteht(self):
        _lauf, fotos = self._daten()
        for f in fotos.values():
            z = self.zellen(f['koerper']['vorlage'], f['koerper']['vorlage'], f['mm_je_px'])
            self.assertTrue(z)
            self.assertFalse(self.schlecht(z), self._text(f['datei'], z, self.schlecht(z)))

    def test_gegenprobe_foto_verschoben_faellt_durch(self):
        _lauf, fotos = self._daten()
        for f in fotos.values():
            v = np.asarray(f['koerper']['vorlage'])
            z = self.zellen(v, v + [self.SCHUB_MM / f['mm_je_px'], 0.0], f['mm_je_px'])
            self.assertGreater(len(self.schlecht(z)), len(z) // 2, self._text(f['datei'], z, self.schlecht(z)))

    def test_gegenprobe_kunstfall_delle_faellt_durch(self):
        """Ohne Job: ein Arm als zwei Linien 160 mm auseinander, schwarz mit einer 20 mm tiefen, 40 mm langen Delle an einer Seite."""
        mm_je_px = 0.5
        y = np.arange(-400, 401, 2.0)
        blau = np.concatenate([np.stack([np.full_like(y, -160.0), y], 1), np.stack([np.full_like(y, 160.0), y], 1)])
        delle = np.where(np.abs(y) <= 40, 40.0, 0.0)
        schwarz = np.concatenate([np.stack([-160.0 + delle, y], 1), np.stack([np.full_like(y, 160.0), y], 1)])
        self.assertFalse(self.schlecht(self.zellen(blau, blau, mm_je_px)))
        self.assertTrue(self.schlecht(self.zellen(blau, schwarz, mm_je_px)))
