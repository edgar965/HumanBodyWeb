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
Seit 30.10.2026 rechnet ein Wert, der älter als `MERKEN_S`, aber jünger als `HINTERGRUND_S` ist, ein Hintergrundfaden neu, und die Seite bekommt bis dahin den gemerkten: der Gang über
alle Tests (16.876 Verzeichnisse, 0,9 s, `ProjektTemp/_wegwerf/liste_messen/mesh3dai_liste_zeit.py --abgelaufen`) lag sonst alle 30 s im Aufruf von /mesh-3D-AI/ und wurde unter
der Last des Studios zu mehreren Sekunden (Edgar: „wenn ich /studio/ öffne, und schnell eine andere Seite klicke, dauert es ewig“). Älter als `HINTERGRUND_S` wird wie
bisher im Aufruf gerechnet — die Spalte zeigt nie einen Stand von vor Stunden.

    Mesh3dairechendatum.letztes(job) -> None | {'zeit': float (Unix), 'was': Text, 'datei': Pfad relativ zu mesh3dai/}
    Mesh3dairechendatum.test(kennung) -> dasselbe für einen Test (nur `_test/<kennung>/**`)
"""

import logging
import os
import threading
import time

from .mesh3daipaare import Mesh3daipaare
from .mesh3daitrainingsdatum import Mesh3daitrainingsdatum

logger = logging.getLogger('core')

__all__ = ['Mesh3dairechendatum']


class Mesh3dairechendatum:
    NIE = frozenset({'einstellung.json', 'name.json'})
    MERKEN_S = 30
    HINTERGRUND_S = 600          # Setzung: so alt darf ein gezeigter Wert höchstens sein, während der Hintergrundfaden den neuen rechnet
    WARTEN_S = 2.0               # erst nach der Seite, die ihn auslöste — im selben Prozess nähme er ihr sonst die GIL (die Liste braucht warm 0,4 s)
    _gemerkt = {}
    _offen = {}                  # Schlüssel → Rechnung, die der Hintergrundfaden noch erneuern soll
    _faden = None
    _sperre = threading.Lock()

    @classmethod
    def letztes(cls, job):
        return cls._gemerkt_oder((job['id'], job['ordner'], bool(job.get('paar'))), lambda: cls._rechnen(job))

    @classmethod
    def test(cls, kennung):
        """Dasselbe für einen Test (`_test/<kennung>/**`, Reiter „Test“; 23.10.2026, Edgar: „warum ist da kein neuer Output???“ — die Spalte las `test.json` → `gerechnet`, das nur der
        Testlauf schreibt; Kostüm- und Kleiderläufe blieben unsichtbar)."""
        return cls._gemerkt_oder(('test', kennung), lambda: cls._test_rechnen(kennung))

    @classmethod
    def _test_rechnen(cls, kennung):
        wurzel = Mesh3daipaare.ordner()
        wert = cls._neueste(wurzel / '_test' / kennung, 8, cls._testschritt)
        if wert:
            wert['datei'] = os.path.relpath(wert['datei'], wurzel).replace('\\', '/')
        return wert

    @classmethod
    def _gemerkt_oder(cls, schluessel, rechnen):
        alt = cls._gemerkt.get(schluessel)
        alter = time.monotonic() - alt[0] if alt else None
        if alter is not None and alter < cls.MERKEN_S:
            return alt[1]
        if alter is not None and alter < cls.HINTERGRUND_S:
            with cls._sperre:
                cls._offen[schluessel] = rechnen
                if cls._faden is None:
                    cls._faden = threading.Timer(cls.WARTEN_S, cls._erneuern)
                    cls._faden.name, cls._faden.daemon = 'Mesh3dairechendatum', True
                    cls._faden.start()
            return alt[1]
        wert = rechnen()
        cls._gemerkt[schluessel] = (time.monotonic(), wert)
        return wert

    @classmethod
    def _erneuern(cls):
        """Der Hintergrundfaden: die offenen Schlüssel nacheinander neu rechnen, dann enden."""
        while True:
            with cls._sperre:
                if not cls._offen:
                    cls._faden = None
                    return
                schluessel, rechnen = cls._offen.popitem()
            try:
                cls._gemerkt[schluessel] = (time.monotonic(), rechnen())
            except Exception:          # noqa: BLE001 — der alte Wert bleibt; der nächste Aufruf nach HINTERGRUND_S rechnet im Aufruf und zeigt den Fehler dort
                logger.exception('Mesh3dairechendatum: %s nicht neu gerechnet', schluessel)

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
            return {'zerlegung': 'Zerlegung', 'vorstufe': 'Vorstufe', 'ziel': 'Ziel', 'kostuem': 'Kostüm'}.get(erster, 'Testkette')
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
