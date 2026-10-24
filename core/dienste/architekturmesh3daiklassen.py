# -*- coding: utf-8 -*-
"""Architekturmesh3daiklassen — die Klassen des Rechencodes und wer wen ruft, für Hilfe → Architektur → Mesh3DAI (24.10.2026).

Edgar, 24.10.2026: „update /hilfe/architektur/mesh3dai/ mit dem genauen Code, inkl. Kopf KI und allen Änderungen der letzten Tage“ — „Füge alle neuen Klassen ein, die du erstellt hast, für tests,
für Kleideranpassung, mit Aufruf Logik“. Nichts davon steht von Hand hier: gelesen wird beim Aufruf der Ordner `A:\\3DTools\\mesh3dai\\` (Rechencode seit 23.10.2026) mit `ast` —
je Modul die Klassen (Name, erste Zeile, Datum aus dem Text), die Importe anderer Module des Ordners (auch in Funktionen) und die als Unterprozess gestarteten Skripte (Zeichenketten `…py`, die es
im Ordner gibt). Die Schritte des Rechenlaufs (`Mesh3dairechenlauf.SCHRITTE`) geben je Schritt das Skript; was von dort über Importe und gestartete Skripte erreichbar ist, läuft in diesem
Schritt. Eine Klasse steht beim ERSTEN Schritt, der sie erreicht; was kein Schritt erreicht (Training, Messungen, Werkzeug), steht unter „nicht in der Kette“.
Gemerkt wird je Stand des Ordners (Zahl und jüngste Änderung der Dateien) — 198 Module lesen kostet ~0,5 s.
"""

import ast
import re
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmesh3daiklassen']

DATUM = re.compile(r'\((\d{1,2})\.(\d{1,2})\.(\d{4})')


class Architekturmesh3daiklassen:
    STARTER = 'mesh3dai_stimmen_lauf.py'           # nimmt nur die Sperre und startet das Skript dahinter
    TEXT_MAX = 320
    _merk = {}

    @staticmethod
    def ordner():
        return Path(settings.TOOLS_ROOT) / 'mesh3dai'

    @classmethod
    def _stand(cls):
        dateien = list(cls.ordner().glob('*.py'))
        return len(dateien), max((p.stat().st_mtime_ns for p in dateien), default=0)

    @classmethod
    def _text(cls, doc):
        """Erster Absatz eines Docstrings, gekürzt."""
        if not doc:
            return ''
        absatz = ' '.join(doc.strip().split('\n\n')[0].split())
        return absatz if len(absatz) <= cls.TEXT_MAX else absatz[:cls.TEXT_MAX].rsplit(' ', 1)[0] + ' …'

    @staticmethod
    def _datum(*texte):
        """Jüngstes Datum „(TT.MM.JJJJ“ in den Texten → 'JJJJ-MM-TT' oder ''."""
        alle = ['%s-%02d-%02d' % (j, int(m), int(t)) for text in texte if text for t, m, j in DATUM.findall(text)]
        return max(alle) if alle else ''

    @classmethod
    def module(cls):
        """{Modul: {'datei', 'klassen': [{name, text, datum}], 'importe': set, 'startet': set, 'text'}} — gemerkt je Stand des Ordners."""
        stand = cls._stand()
        if cls._merk.get('stand') == stand:
            return cls._merk['module']
        namen = {p.stem for p in cls.ordner().glob('*.py')}
        module = {}
        for p in sorted(cls.ordner().glob('*.py')):
            try:
                baum = ast.parse(p.read_text(encoding='utf-8'))
            except (SyntaxError, UnicodeDecodeError, OSError) as fehler:
                module[p.stem] = {'datei': p.name, 'klassen': [], 'importe': set(), 'startet': set(), 'text': 'nicht lesbar: %s' % fehler, 'datum': ''}
                continue
            mdoc = ast.get_docstring(baum) or ''
            importe, startet = set(), set()
            for knoten in ast.walk(baum):
                if isinstance(knoten, ast.ImportFrom) and knoten.module in namen and knoten.level == 0:
                    importe.add(knoten.module)
                elif isinstance(knoten, ast.Import):
                    importe.update(a.name for a in knoten.names if a.name in namen)
                elif isinstance(knoten, ast.Constant) and isinstance(knoten.value, str) and knoten.value.endswith('.py') and knoten.value[:-3] in namen:
                    startet.add(knoten.value[:-3])
            importe.discard(p.stem)
            startet.discard(p.stem)
            klassen = [{'name': k.name, 'text': cls._text(ast.get_docstring(k)) or cls._text(mdoc), 'datum': cls._datum(ast.get_docstring(k), mdoc)}
                       for k in baum.body if isinstance(k, ast.ClassDef)]
            module[p.stem] = {'datei': p.name, 'klassen': klassen, 'importe': importe, 'startet': startet, 'text': cls._text(mdoc), 'datum': cls._datum(mdoc)}
        cls._merk = {'stand': stand, 'module': module}
        return module

    @classmethod
    def _erreichbar(cls, module, start):
        gesehen, offen = set(), [start]
        while offen:
            m = offen.pop()
            if m in gesehen or m not in module:
                continue
            gesehen.add(m)
            offen.extend(module[m]['importe'] | module[m]['startet'])
        return gesehen

    @classmethod
    def skript(cls, argumente):
        """Das Skript eines Schritts: die erste `.py` der Argumente, die nicht der Starter der Sperre ist."""
        return next((a[:-3] for a in argumente if a.endswith('.py') and a != cls.STARTER), None)

    @classmethod
    def kontext(cls, schritte):
        """schritte = `Mesh3dairechenlauf.SCHRITTE` → {'gruppen': [{schritt, text, skript, klassen: [...]}], 'zahlen': {...}}."""
        module = cls.module()
        klassen_von = {m: [k['name'] for k in d['klassen']] for m, d in module.items()}
        gerufen = {m: set() for m in module}
        for m, d in module.items():
            for z in d['importe'] | d['startet']:
                if z in gerufen:
                    gerufen[z].add(m)

        def namen(ms):
            aus = []
            for m in sorted(ms):
                aus.extend(klassen_von.get(m) or [module[m]['datei']])
            return aus

        zugeteilt, gruppen = set(), []
        for nr, (schluessel, text, argumente) in enumerate(schritte, start=1):
            sk = cls.skript(argumente)
            erreicht = cls._erreichbar(module, sk) if sk else set()
            neu = sorted(erreicht - zugeteilt)
            zugeteilt |= erreicht
            gruppen.append({'nr': nr, 'schritt': schluessel, 'text': text, 'skript': (sk + '.py') if sk else None, 'erreicht': len(erreicht),
                            'klassen': cls._zeilen(module, neu, namen, gerufen, sk)})
        rest = sorted(set(module) - zugeteilt)
        gruppen.append({'nr': None, 'schritt': 'ohne', 'text': 'nicht in der Kette (Training, Messungen, Werkzeug, Testseite)', 'skript': None, 'erreicht': len(rest),
                        'klassen': cls._zeilen(module, rest, namen, gerufen, None)})
        alle = [k for g in gruppen for k in g['klassen']]
        return {'gruppen': gruppen, 'ordner': str(cls.ordner()),
                'zahlen': {'module': len(module), 'klassen': sum(len(d['klassen']) for d in module.values()), 'in_der_kette': len(zugeteilt),
                           'neu_seit_22': sum(1 for k in alle if k['datum'] >= '2026-10-22')}}

    @staticmethod
    def _zeilen(module, ms, namen, gerufen, skript):
        zeilen = []
        for m in ms:
            d = module[m]
            ruft = namen(d['importe'])
            startet = [module[s]['datei'] for s in sorted(d['startet'])]
            von = namen(gerufen[m])
            for k in (d['klassen'] or [{'name': None, 'text': d['text'], 'datum': d['datum']}]):
                zeilen.append({'klasse': k['name'], 'datei': d['datei'], 'text': k['text'], 'datum': k['datum'], 'ruft': ruft, 'startet': startet, 'von': von,
                               'skript': m == skript})
        zeilen.sort(key=lambda z: z['datei'])
        zeilen.sort(key=lambda z: z['datum'], reverse=True)          # jüngste zuerst, das Skript des Schritts ganz oben
        zeilen.sort(key=lambda z: not z['skript'])
        return zeilen
