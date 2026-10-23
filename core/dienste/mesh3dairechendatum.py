# -*- coding: utf-8 -*-
"""Mesh3dairechendatum — wann für einen Job von Mesh3D-AI zuletzt etwas gerechnet wurde (20.10.2026).

Edgar: „dann mach in diese Tabelle eine neue Spalte, wo steht zuletzt gerechnet“ — neben „Zuletzt trainiert“ (`Mesh3daitrainingsdatum`), weil die Läufe des Tages (Vorstufe, Kleider, Schnitt) das
Trainingsdatum nicht ändern. Gezählt wird die jüngste Änderungszeit einer Datei, die ein Rechenschritt schreibt, an diesen Stellen (jede mit einer Bezeichnung im Klartext):
  * `<Job>/_laeufe/<lauf>/*` — `wege*` = Vorstufe, sonst Training (bei Tripo-Jobs: Testkette, die Läufe dort sind Ergebnisse der Kette);
  * `<Job>/proben/<nr>/*` und die Dateien im Jobordner = Datensatz; `<Job>/vorstufe/**` = Vorstufe; `<Job>/kleider_ki/<nr>/{form,zerlegung,kleider}/**` = Ergebnisfigur, Zerlegung, Kleider;
  * `_test/<id>/**` (Tripo-Jobs) — Kleider, Zerlegung, Vorstufe, Ergebnisfigur, Ziel, Form, Ergebnis, Testkette;
  * `_bild3d/<Job>_*/**` = künstliche Tripo-Netze;
  * das jüngste gemeinsame Training, das den Job nennt (`Mesh3daitrainingsdatum`, `wo=('vorstufe',)`).
Nicht gezählt: `einstellung.json` und `name.json` (schreibt der Server auf einen Klick), Nebendateien `*.neu`, beiseitegelegte Stände (`*_vor_*`, `verworfen*`, `vergleich_*`, `_diagnose`).
Ein Lauf, der gerade schreibt, zählt mit (seine Dateien sind schon da). Je Job 30 s gemerkt — der Datensatz hat bis 190 Probenordner.

    Mesh3dairechendatum.letztes(job) -> None | {'zeit': float (Unix), 'was': Text, 'datei': Pfad relativ zu mesh3dai/}
"""

import os
import time

from .mesh3daipaare import Mesh3daipaare
from .mesh3daitrainingsdatum import Mesh3daitrainingsdatum

__all__ = ['Mesh3dairechendatum']


class Mesh3dairechendatum:
    NIE = frozenset({'einstellung.json', 'name.json'})
    MERKEN_S = 30
    _gemerkt = {}

    @classmethod
    def letztes(cls, job):
        schluessel = (job['id'], job['ordner'], bool(job.get('paar')))
        jetzt = time.monotonic()
        alt = cls._gemerkt.get(schluessel)
        if alt and jetzt - alt[0] < cls.MERKEN_S:
            return alt[1]
        wert = cls._rechnen(job)
        cls._gemerkt[schluessel] = (jetzt, wert)
        return wert

    @classmethod
    def _rechnen(cls, job):
        wurzel = Mesh3daipaare.ordner()
        paar = bool(job.get('paar'))
        kandidaten = []
        ordner = wurzel / job['ordner']
        if ordner.is_dir():
            kandidaten.append(cls._neueste(ordner, 1, lambda teile: 'Datensatz'))
            kandidaten.append(cls._neueste(ordner / '_laeufe', 2, lambda teile: 'Vorstufe' if teile[-1].startswith('wege') else ('Testkette' if paar else 'Training')))
            kandidaten.append(cls._neueste(ordner / 'proben', 2, lambda teile: 'Datensatz'))
            kandidaten.append(cls._neueste(ordner / 'vorstufe', 6, lambda teile: 'Vorstufe'))
            kandidaten.append(cls._neueste(ordner / 'kleider_ki', 8, cls._probenschritt))
        test = wurzel / '_test' / job['id']
        if test.is_dir():
            kandidaten.append(cls._neueste(test, 8, cls._testschritt))
        bild3d = wurzel / '_bild3d'
        if bild3d.is_dir():
            vorne = job['ordner'] + '_'
            with os.scandir(bild3d) as eintraege:
                for e in eintraege:
                    if e.is_dir() and e.name.startswith(vorne):
                        kandidaten.append(cls._neueste(e.path, 3, lambda teile: 'Künstliche Tripo-Netze'))
        gemeinsam = Mesh3daitrainingsdatum.letztes(job['ordner'], wo=('vorstufe',))
        if gemeinsam:
            kandidaten.append({'zeit': gemeinsam['zeit'], 'was': 'Training', 'datei': '_vorstufe/laeufe/%s/lauf_ergebnis.json' % gemeinsam['lauf']})
        kandidaten = [k for k in kandidaten if k]
        if not kandidaten:
            return None
        best = max(kandidaten, key=lambda k: k['zeit'])
        if not best['datei'].startswith('_vorstufe/'):
            best['datei'] = os.path.relpath(best['datei'], wurzel).replace('\\', '/')
        return best

    @staticmethod
    def _probenschritt(teile):
        """`kleider_ki/<nr>/<schritt>/…` → Klartext."""
        schritt = teile[1] if len(teile) > 2 else ''
        return {'form': 'Ergebnisfigur', 'zerlegung': 'Zerlegung'}.get(schritt, 'Kleider')

    @staticmethod
    def _testschritt(teile):
        """`_test/<id>/…` → Klartext."""
        if len(teile) > 1:
            erster = teile[0]
            if erster.startswith('kleider_'):
                return 'Kleider'
            if erster.startswith('form_'):
                return 'Ergebnisfigur'
            return {'zerlegung': 'Zerlegung', 'vorstufe': 'Vorstufe', 'ziel': 'Ziel'}.get(erster, 'Testkette')
        name = teile[0]
        if name.startswith('form'):
            return 'Form'
        if name.startswith('ergebnis'):
            return 'Ergebnis'
        return 'Testkette'

    @classmethod
    def _ausgelassen(cls, name):
        return name in cls.NIE or name.endswith('.neu') or '_vor_' in name or name.startswith(('verworfen', 'vergleich_', '_diagnose'))

    @classmethod
    def _neueste(cls, ordner, tiefe, bezeichnung, teile=()):
        """Jüngste Datei unter `ordner` bis `tiefe` Ebenen (1 = nur die Dateien darin) → {'zeit', 'was', 'datei'} oder None. `os.scandir` liefert die Zeit unter Windows ohne eigenen Dateizugriff."""
        best = None
        try:
            eintraege = list(os.scandir(ordner))
        except OSError:
            return None
        for e in eintraege:
            if cls._ausgelassen(e.name):
                continue
            try:
                if e.is_dir(follow_symlinks=False):
                    if tiefe > 1:
                        k = cls._neueste(e.path, tiefe - 1, bezeichnung, teile + (e.name,))
                        if k and (best is None or k['zeit'] > best['zeit']):
                            best = k
                    continue
                zeit = e.stat().st_mtime
            except OSError:
                continue
            if best is None or zeit > best['zeit']:
                best = {'zeit': zeit, 'datei': e.path, 'teile': teile + (e.name,)}
        if best is not None and 'teile' in best:
            best['was'] = bezeichnung(best.pop('teile'))
        return best
