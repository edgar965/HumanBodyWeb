# -*- coding: utf-8 -*-
"""Der Ellbogen der geometrischen Figur (2d-3d-AI, Jobseite Zeile 1, Bild 2) liegt am Umriss der Person im Foto.

WARUM: Edgar, 28.10.2026: „Ellbogen und Hand kaputt“ — „entwickle einen Testcase der den Ellbogen als falsch hat. Du hast die Bilder, du hast die Umrisse in den Jobs. Mach den
Testcase, dann fixe so lange bis der grün ist“ — „mit fixen meinte ich, dass du den allgemeinen Code für alle Jobs anpasst, bis der Testfall für den Edgar Job OK ist“.
Gesehen vorher (Lauf 2026.10.28.21.05, `ProjektTemp/_wegwerf/ai2d3d/diag_stellen.py`): am rechten Ellbogen von vorn 20,6 cm² Person ohne Figur, von hinten 36,0 cm² — eine Delle
an der Innenseite, Ober- und Unterarm daneben deckungsgleich.

Gemessen wird, was der Lauf selbst ablegt (`form_direkt.py` → `<Job>/abnahme/training.json`, `Traininggeometrie`): je Foto der Umriss der Person (`koerper.vorlage`), der Umriss der
Figur (`koerper.ergebnis`, beide jeder 4. Punkt, Pixel des Fotos) und die Gelenke der Figur (`koerper.gelenke`). Im Umkreis RADIUS_MM um den Ellbogen der Figur: je Punkt der
Abstand zum nächsten Punkt der anderen Seite, beide Richtungen. Grenzen = Auftrag EdgarTrip, Umriss Haut (`.claude/rules/ai2d3d.md`): Median ≤ 5 mm, Max ≤ 15 mm. Liegt im Umkreis
kein Umriss (Profil: der Arm liegt vor dem Rumpf), ist der Ellbogen dort nicht messbar und zählt nicht.

Nur lesen, nie schreiben. Der Test hängt am letzten Lauf des Jobs; ohne Lauf wird er übersprungen.

    manage.py test core.tests.automated.test_ai2d3d_geometrie_ellbogen
"""

import json
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase


class Ai2d3dGeometrieEllbogen(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'
    RADIUS_MM = 60.0
    MEDIAN_MM, MAX_MM = 5.0, 15.0
    ELLBOGEN = ('ellbogen_l', 'ellbogen_r')
    #: Gegenprobe: so weit verschoben muss die Prüfung durchfallen (mm)
    SCHUB_MM = 20.0

    @staticmethod
    def abstaende(vorlage, ergebnis, mitte, radius_px):
        """(N,) px: je Punkt von Foto und Figur im Umkreis der Abstand zum nächsten Punkt der anderen Seite (ganze Seite, nicht nur im Umkreis); None, wenn eine Seite dort fehlt."""
        v, e, m = np.asarray(vorlage, dtype=np.float64), np.asarray(ergebnis, dtype=np.float64), np.asarray(mitte, dtype=np.float64)
        nv, ne = np.linalg.norm(v - m, axis=1) <= radius_px, np.linalg.norm(e - m, axis=1) <= radius_px
        if not nv.any() or not ne.any():
            return None
        zu_figur = np.sqrt(((v[nv][:, None] - e[None]) ** 2).sum(2)).min(1)
        zu_foto = np.sqrt(((e[ne][:, None] - v[None]) ** 2).sum(2)).min(1)
        return np.concatenate([zu_figur, zu_foto])

    @classmethod
    def pruefen(cls, vorlage, ergebnis, mitte, mm_je_px):
        """(Median mm, Max mm, Punkte) oder None (nicht messbar)."""
        d = cls.abstaende(vorlage, ergebnis, mitte, cls.RADIUS_MM / mm_je_px)
        if d is None:
            return None
        d = d * mm_je_px
        return float(np.median(d)), float(d.max()), int(len(d))

    def _daten(self):
        datei = Path(settings.OBJECTS_ROOT) / 'ai2d3d' / self.JOB / 'abnahme' / 'training.json'
        if not datei.is_file():
            self.skipTest('kein Lauf: %s fehlt' % datei)
        daten = json.loads(datei.read_text(encoding='utf-8'))
        fotos = {nr: f for nr, f in daten['fotos'].items() if f.get('koerper')}
        if not fotos:
            self.skipTest('Lauf %s hat den Körper nicht gerechnet' % daten.get('lauf'))
        ohne = [f['datei'] for f in fotos.values() if not f['koerper'].get('gelenke')]
        self.assertFalse(ohne, 'Lauf %s ohne Gelenke der Figur in %s — mit form_direkt.py --aus=<Lauf> neu ausgeben' % (daten.get('lauf'), ohne))
        return daten['lauf'], fotos

    def _messen(self, fotos, ergebnis_von=None):
        """{(Foto, Ellbogen): (Median, Max, Punkte) oder None}; `ergebnis_von(foto)` ersetzt den Umriss der Figur (Gegenprobe)."""
        aus = {}
        for f in fotos.values():
            k = f['koerper']
            ergebnis = ergebnis_von(f) if ergebnis_von else k['ergebnis']
            for name in self.ELLBOGEN:
                aus[(f['datei'], name)] = self.pruefen(k['vorlage'], ergebnis, k['gelenke'][name], f['mm_je_px'])
        return aus

    @classmethod
    def _zu_weit(cls, werte):
        return {s: w for s, w in werte.items() if w is not None and (w[0] > cls.MEDIAN_MM or w[1] > cls.MAX_MM)}

    @staticmethod
    def _text(werte):
        return '; '.join('%s %s: Median %.1f, Max %.1f mm (%d Punkte)' % (f, n, *w) if w else '%s %s: nicht messbar' % (f, n) for (f, n), w in sorted(werte.items()))

    def test_ellbogen_der_geometrischen_figur_liegt_am_umriss_des_fotos(self):
        lauf, fotos = self._daten()
        werte = self._messen(fotos)
        gemessen = [w for w in werte.values() if w is not None]
        self.assertGreaterEqual(len(gemessen), 2, 'Lauf %s: kaum ein Ellbogen messbar — %s' % (lauf, self._text(werte)))
        zu_weit = self._zu_weit(werte)
        self.assertFalse(zu_weit, 'Lauf %s, Grenze Median %.0f / Max %.0f mm — über der Grenze: %s. Alle: %s' % (
            lauf, self.MEDIAN_MM, self.MAX_MM, self._text(zu_weit), self._text(werte)))

    def test_gegenprobe_foto_gegen_foto_besteht(self):
        _lauf, fotos = self._daten()
        werte = self._messen(fotos, lambda f: f['koerper']['vorlage'])
        self.assertTrue(any(w is not None for w in werte.values()))
        self.assertFalse(self._zu_weit(werte), self._text(werte))

    def test_gegenprobe_foto_verschoben_faellt_durch(self):
        _lauf, fotos = self._daten()
        werte = self._messen(fotos, lambda f: (np.asarray(f['koerper']['vorlage']) + [self.SCHUB_MM / f['mm_je_px'], 0.0]).tolist())
        gemessen = {s: w for s, w in werte.items() if w is not None}
        self.assertTrue(gemessen)
        self.assertEqual(set(self._zu_weit(gemessen)), set(gemessen), self._text(werte))

    def test_gegenprobe_delle_am_ellbogen_faellt_durch(self):
        """Kunstfall ohne Job: ein Arm als Rechteck (Breite 80 mm), die Figur mit einer 20 mm tiefen, 40 mm langen Delle an einer Seite neben dem Ellbogen."""
        mm_je_px = 0.5
        y = np.arange(-400, 401, 2.0)
        foto = np.concatenate([np.stack([np.full_like(y, -80.0), y], 1), np.stack([np.full_like(y, 80.0), y], 1)])
        delle = np.where(np.abs(y) <= 40, 40.0, 0.0)
        figur = np.concatenate([np.stack([-80.0 + delle, y], 1), np.stack([np.full_like(y, 80.0), y], 1)])
        heil = self.pruefen(foto, foto, (0.0, 0.0), mm_je_px)
        kaputt = self.pruefen(foto, figur, (0.0, 0.0), mm_je_px)
        self.assertIsNotNone(heil)
        self.assertIsNotNone(kaputt)
        self.assertFalse(self._zu_weit({('kunst', 'heil'): heil}))
        self.assertTrue(self._zu_weit({('kunst', 'delle'): kaputt}), kaputt)
