# -*- coding: utf-8 -*-
"""Architekturmesh3dairechenlauf — Abschnitt „Rechnen per Knopf: die Kette im Projekt“ der Seite Hilfe → Architektur → Mesh3DAI (24.10.2026).

Edgar, 24.10.2026: „update /hilfe/architektur/mesh3dai/ mit dem genauen Code, inkl. Kopf KI und allen Änderungen der letzten Tage“. Aus dem Code gelesen beim Aufruf:
die Schritte (`Mesh3dairechenlauf.SCHRITTE`, Aufruf genau so, wie der Arbeitsprozess ihn startet), die Netze (`Mesh3daikifassungen`), die Testfälle der Kostüm-Prüfung
(`mesh3dai/mesh3dai_kostuem_pruefung.py`: `FASSUNG`, `TEXTE` und die Zeilen `#:` darüber, per `ast` — kein Import des Rechencodes in den Server), der jüngste fertige Rechenlauf eines Tests
(`_test/<k>/rechnen/stand.json`) und dessen jüngste Prüfung (`_test/<k>/kostuem/lauf_*.json`). Von Hand: `NEU` (Änderungen der letzten Tage, Zahlen aus `.claude/rules/mesh3dai-rechenlauf.md`).
"""

import ast
import json
import re
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmesh3dairechenlauf']


class Architekturmesh3dairechenlauf:
    #: (Datum, was, gemessen) — Quelle `.claude/rules/mesh3dai-rechenlauf.md` und die Docstrings der genannten Klassen
    NEU = (
        ('23.10.2026', 'Rechencode ins Projekt (`A:\\3DTools\\mesh3dai\\`, 185 Module aus `_wegwerf/`), Rechnen per Knopf mit festen Schritten, Warteschlange (ein Lauf zur Zeit), Netze in '
                       '`ki_fassungen.json`', 'OlesiaWalk per Klick 921 s, edgar_knopf 458 s'),
        ('23.10.2026', 'Kostüm-Weg A: Kleider und Haar aus dem Mesh erkennen (Sapiens2 + SAM 3), ausschneiden, an die Stelle des Eingangs auf die Figur legen (Rückhäutung), Hautmasken; '
                       'Kostüm-Prüfung mit Testfällen (Fassungen 1–5)', 'Hose edgar_knopf „Loch im Stück“ 5 → 0'),
        ('23.10.2026', 'Haut aus der KI (Stufe 2) im Rechenlauf; Zuordnung der Kacheln nach UV-Lage', 'edgar_knopf Hautton ΔE 16,2 → 4,3'),
        ('24.10.2026', 'Haltung aus Gelenken und Enden als CUDA-Graph (`Ikgraph`, 3.000 Schritte, Finger/Zehen/Gesicht Gewicht 0,05); Testfälle „Haltung folgt der KI“ und „Flecken in der Haut“ '
                       '(Fassung 6)', 'Hauptgelenke an 12 Tests 47,4 → 29,1 mm, Hose edgar_knopf Durchstich 40,1 → 6,5 %'),
        ('24.10.2026', 'Testfall „Gesicht wie der Eingang“ (Fassung 7, `Kostuemgesicht`); Kopfnetz gemessen und allein NICHT eingesetzt; Schritt „kopf“ = Kopfnetz + `Kopfangleich`',
         'edgar_knopf Gesichtsmaße 4 → 0 von 11 rot'),
        ('24.10.2026', 'Kostüm-Prüfung auf der Karte statt im GL-Kontext je Bild: ein Renderer je Bildgröße und eine Szene je Messung (`Kostuemrender`, jedes Netz einmal hochgeladen); '
                       'Fenstersumme der Flecken als zwei Streifen statt 31×31-Kern', 'Schritt „kleider“ edgar_knopf 121 → 54 s (py-spy aktiv 112 → 47 s), 694 von 707 Messwerten gleich'),
    )

    @staticmethod
    def _json(p):
        try:
            return json.loads(Path(p).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def kontext(cls):
        from .architekturmesh3daiklassen import Architekturmesh3daiklassen
        from .mesh3daikifassungen import Mesh3daikifassungen
        from .mesh3dairechenlauf import Mesh3dairechenlauf
        f = Mesh3daikifassungen.lesen()
        schritte = []
        for nr, (s, text, argumente) in enumerate(Mesh3dairechenlauf.SCHRITTE, start=1):
            schritte.append({'nr': nr, 'schluessel': s, 'text': text, 'aufruf': 'python14 ' + ' '.join(argumente), 'skript': Architekturmesh3daiklassen.skript(argumente),
                             'fassungen': sorted(set(re.findall(r'\{(\w+)\}', ' '.join(argumente))) & set(f))})
        tests = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_test'
        return {'schritte': schritte, 'fassungen': [{'schluessel': k, 'wert': v, 'text': Mesh3daikifassungen.TEXTE.get(k, '')} for k, v in f.items()],
                'lauf': cls.letzter_lauf(tests), 'pruefung': cls.pruefung(), 'neu': cls.NEU, 'haut': Mesh3dairechenlauf.HAUT,
                'klassen': Architekturmesh3daiklassen.kontext(Mesh3dairechenlauf.SCHRITTE)}

    @classmethod
    def letzter_lauf(cls, tests):
        """Der jüngste fertige Rechenlauf eines Tests: Dauer je Schritt, dazu dessen jüngste Kostüm-Prüfung."""
        beste = None
        for datei in tests.glob('*/rechnen/stand.json'):
            s = cls._json(datei)
            if s and s.get('status') == 'fertig' and s.get('ende') and (beste is None or s['ende'] > beste[0]['ende']):
                beste = (s, datei.parent.parent)
        if beste is None:
            return None
        s, ordner = beste
        laeufe = sorted(ordner.glob('kostuem/lauf_*.json'))
        bericht = cls._json(laeufe[-1]) if laeufe else None
        nachher = (bericht or {}).get('nachher') or {}
        return {'kennung': s.get('kennung'), 'ende': s.get('ende'), 'dauer_s': s.get('dauer_s'), 'ab': s.get('ab'),
                'schritte': [{'schluessel': x.get('schluessel'), 'dauer_s': x.get('dauer_s'), 'uebernommen': x.get('uebernommen', False)} for x in s.get('schritte', [])],
                'pruefung_datei': laeufe[-1].name if laeufe else None, 'prio': nachher.get('prio'),
                'tests': [{'name': n, 'prio': z.get('prio'), 'rot': z.get('nachher'), 'von': z.get('pruefungen'), 'fehler': '; '.join((z.get('fehlertexte') or [])[:2])}
                          for n, z in sorted((nachher.get('tests') or {}).items(), key=lambda kv: (kv[1].get('prio', 9), kv[0]))]}

    @staticmethod
    def pruefung():
        """Testfälle der Kostüm-Prüfung aus dem Quelltext (ast, ohne Import): Fassung, Fassungsgeschichte (Zeilen `#:` vor `FASSUNG`), Prio und Text je Testfall."""
        datei = Path(settings.TOOLS_ROOT) / 'mesh3dai' / 'mesh3dai_kostuem_pruefung.py'
        quelle = datei.read_text(encoding='utf-8')
        klasse = next(k for k in ast.parse(quelle).body if isinstance(k, ast.ClassDef) and k.name == 'Kostuempruefung')
        werte, zeile_fassung = {}, None
        for k in klasse.body:
            if isinstance(k, ast.Assign) and len(k.targets) == 1 and isinstance(k.targets[0], ast.Name) and k.targets[0].id in ('FASSUNG', 'TEXTE'):
                werte[k.targets[0].id] = ast.literal_eval(k.value)
                if k.targets[0].id == 'FASSUNG':
                    zeile_fassung = k.lineno
        zeilen = quelle.splitlines()[klasse.lineno:zeile_fassung - 1] if zeile_fassung else []
        geschichte = []
        for z in zeilen:
            z = z.strip()
            if z.startswith('#:'):
                text = z[2:].strip()
                if geschichte and not re.match(r'^\d+ \(', text):
                    geschichte[-1] += ' ' + text
                else:
                    geschichte.append(text)
        return {'fassung': werte.get('FASSUNG'), 'geschichte': geschichte, 'datei': datei.name,
                'tests': [{'name': n, 'prio': p, 'text': t} for n, (p, t) in sorted((werte.get('TEXTE') or {}).items(), key=lambda kv: kv[1][0])]}
