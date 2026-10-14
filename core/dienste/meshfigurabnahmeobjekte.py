# -*- coding: utf-8 -*-
"""Meshfigurabnahmeobjekte — Abnahme der Objekte eines Laufs: Flächen je Objekt, Doppelte, Waisen, Hut (13.10.2026).

Frage: Gehört jede erkannte Netzfläche zu genau einem Objekt? Kleidung, Haar und die Bestandteile bauen ihr Objekt je aus einer Flächenmaske (`Meshfigurobjektflaechen`); wer eine Fläche bekommt,
entscheiden mehrere Stellen mit eigenen Regeln. Gemessen am 13.10.2026: dieselbe GLB, dieselben Optionen — im einen Lauf standen 0 der 5.862 Hutflächen in der Kleidung, im anderen alle; `kleidung.glb`
29.527 gegen 32.760 Flächen. Das sah ohne Vergleich zweier Läufe niemand.

* **Doppelt:** eine Fläche in zwei oder mehr Objekten (müsste 0 sein).
* **Waisen:** eine erkannte Fläche (Haar, Kopfbedeckung, langer Bart, Kleidungsmaske), die in keinem Objekt steht. Das Hautband am Rand der Kleidung (`Kleidungsrand.hautband`) fehlt mit Absicht und
  steht getrennt (`davon_hautrand`); ein Rest darüber ist ein Befund, kein Fehler — die Schwelle `WAISEN_ANTEIL` ist eine Setzung.
* **Hut:** wo die Flächen der Kopfbedeckung (`haar_maske.npz`, `kopfbedeckung`) gelandet sind: Kleidung, Haar, ein Bestandteil — oder nirgends.
"""

import numpy as np

from .meshfigurobjektflaechen import Meshfigurobjektflaechen

__all__ = ['Meshfigurabnahmeobjekte']


class Meshfigurabnahmeobjekte:
    #: Mehr Waisen als dieser Anteil der erkannten Flächen (ohne das Hautband) — und mehr Hutflächen ohne Objekt als dieser Anteil des Huts — sind ein Befund. Eine Setzung, an einem Modell gesehen
    #: (Spiralballerina: vor der Reihenfolge-Korrektur 0 bis 3.217 Hutflächen von 36.091 in der Kleidung; danach 689 Waisen = Hautband, 3 Hutflächen ohne Objekt).
    WAISEN_ANTEIL = 0.01

    def __init__(self, lauf):
        self.lauf = lauf
        self.ablage = lauf.ablage
        self.job = lauf.job

    def messen(self, scan):
        masken = Meshfigurobjektflaechen.lesen(self.ablage)
        flaechen = len(scan.flaechen)
        passend = {n: m for n, m in masken.items() if len(m) == flaechen}
        verworfen = sorted(set(masken) - set(passend))
        if not passend:
            return {'hinweis': 'Keine Objekte aufgezeichnet', 'verworfen': verworfen}
        inhalt = np.asarray(scan.flaecheninhalte(), dtype=np.float64) * 1e4
        zaehler = np.sum([m.astype(np.int16) for m in passend.values()], axis=0)
        belegt = zaehler > 0
        erkannt = self._erkannt(flaechen)
        waise = {quelle: int((m & ~belegt).sum()) for quelle, m in erkannt.items()}
        alle_erkannt = np.logical_or.reduce(list(erkannt.values())) if erkannt else np.zeros(flaechen, dtype=bool)
        waisen = int((alle_erkannt & ~belegt).sum())
        hautrand = int(((self.job.ergebnis.get('kleidung') or {}).get('objekt_hautrand') or {}).get('flaechen') or 0)
        rest = max(0, waisen - hautrand)
        doppelt = int((zaehler > 1).sum())
        hut = self._hut(erkannt.get('hut'), passend, belegt)
        hinweise = self._hinweise(doppelt, hut, rest, int(alle_erkannt.sum()))
        return {
            'objekte': {n: {'flaechen': int(m.sum()), 'cm2': round(float(inhalt[m].sum()), 0)} for n, m in passend.items()},
            'doppelt': doppelt,
            'doppelt_je_paar': self._paare(passend),
            'erkannt': int(alle_erkannt.sum()),
            'waisen': waisen,
            'waisen_je_quelle': waise,
            'davon_hautrand': hautrand,
            'waisen_rest': rest,
            'hut': hut,
            'verworfen': verworfen,
            'hinweise': hinweise,
            'urteil': 'Befund' if hinweise else 'in Ordnung',
        }

    def _erkannt(self, flaechen):
        """`{quelle: (F,) bool}` — was die Erkennung als Haar, Hut, Bart oder Kleidung benannt hat (Masken der Schritte „haar" und „kleidung")."""
        aus = {}
        for datei, felder in (('haar_maske.npz', (('haar', 'haar'), ('kopfbedeckung', 'hut'), ('langer_bart', 'langer_bart'))), ('kleidung_maske.npz', (('kleidung', 'kleidung'),))):
            pfad = self.ablage.arbeit(datei)
            if not pfad.is_file():
                continue
            with np.load(pfad) as d:
                for schluessel, quelle in felder:
                    if schluessel in d.files and len(d[schluessel]) == flaechen and d[schluessel].any():
                        aus[quelle] = np.asarray(d[schluessel], dtype=bool)
        return aus

    @staticmethod
    def _hut(hut, masken, belegt):
        if hut is None:
            return None
        return {'flaechen': int(hut.sum()), 'in_kleidung': int((hut & masken['kleidung']).sum()) if 'kleidung' in masken else 0,
                'in_haar': int((hut & masken['haar']).sum()) if 'haar' in masken else 0,
                'in_teilen': {n[len('teil_'):]: int((hut & m).sum()) for n, m in masken.items() if n.startswith('teil_') and (hut & m).any()},
                'nirgends': int((hut & ~belegt).sum())}

    @staticmethod
    def _paare(masken):
        namen = sorted(masken)
        aus = {}
        for i, a in enumerate(namen):
            for b in namen[i + 1:]:
                n = int((masken[a] & masken[b]).sum())
                if n:
                    aus['%s+%s' % (a, b)] = n
        return aus

    def _hinweise(self, doppelt, hut, rest, erkannt):
        aus = []
        if doppelt:
            aus.append('%d Flächen stehen in zwei Objekten' % doppelt)
        # Gemessen am dritten Lauf der Spiralballerina: 3 von 5.862 Hutflächen fehlen — das Hautband am Rand der Kleidung, kein Befund. Darum auch hier der Anteil.
        if hut and hut['nirgends'] / max(1, hut['flaechen']) > self.WAISEN_ANTEIL:
            aus.append('%d Hutflächen stehen in keinem Objekt' % hut['nirgends'])
        if erkannt and rest / erkannt > self.WAISEN_ANTEIL:
            aus.append('%d erkannte Flächen (%.1f %%) stehen in keinem Objekt, ohne das Hautband' % (rest, 100.0 * rest / erkannt))
        return aus
