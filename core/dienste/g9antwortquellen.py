# -*- coding: utf-8 -*-
u"""G9antwortquellen — woraus eine gespeicherte Netzantwort folgt, und ihre Fassung als Inhalts-Hash (12.10.2026).

ANLASS (Edgar: „auch das Laden eines Modells im Charakter soll schnell gehen!!"): Der Schluessel jeder Netzantwort im Vorrat
(`G9antworten`, `Genesis9/ablage/antworten/`) trug die JUENGSTE AENDERUNGSZEIT ALLER Dateien in `Genesis9/`, `core/api/` und
`core/daten/`. Jede Aenderung in einem dieser Ordner machte jede gespeicherte Antwort ungueltig — auch die an einer Seite, die mit Netzen
nichts zu tun hat (`core/api/mesh3d.py`, `blendimport.py`, ...). Am 11.10.2026 waren es 36 Neustarts des Servers; im Log
(`logs/django.log`, 18:00-18:02) kostete dieselbe Figur dreimal hintereinander 15-21 s, 4-7 s und 4-8 s je Kaefig-Anfrage und erst
beim vierten Laden 0,12-0,25 s (Vorrat). Die Rechnung selbst: Kaefig kalt 4,7 s, feine Stufe kalt 3,4 s, warm 2,0 s (`ProjektTemp/_wegwerf/
mesh3d/ladeprofil.py`).

JETZT zwei Aenderungen:

1. **Inhalt statt Zeit.** Die Fassung ist ein Hash der Dateiinhalte: ein blosses Speichern ohne Aenderung, ein zurueckgenommener Edit oder
   ein Neustart aendern sie nicht.
2. **Nur, was die Antworten wirklich brauchen.** `core/api` und `core/daten` gehen nicht mehr als ganze Ordner ein, sondern als die Huelle
   der Module, die von den Stellen aus erreichbar sind, die Antworten rechnen oder ausliefern (`WURZELN`): jeder `import` (auch der
   in einer Funktion) im Baum von `core/`, per Quelltext gelesen (`ast`), bis nichts Neues mehr dazukommt. Ein Modul, das keine
   Netzantwort erreicht, kann sie auch nicht aendern. `Genesis9/` und die Einzeldateien aus `G9antworten.QUELLEN` bleiben wie bisher.

Was die Huelle NICHT sieht, steht wie vorher im Docstring von `g9antworten.py` (eine geaenderte Daz-Bibliothek: dafuer `vergessen()`);
dazu kommt: ein Modul, das nur ueber `importlib` oder einen Namen aus einer Einstellung geladen wird, gehoert in `QUELLEN`.
"""
import ast
import hashlib
from pathlib import Path

__all__ = ['G9antwortquellen']


class G9antwortquellen:
    u"""Die Dateien einer Fassung und ihr Hash."""

    #: Von hier aus wird die Huelle gesucht (relativ zu `HumanBodyWeb/`): die Stellen, die Netzantworten rechnen oder ausliefern.
    WURZELN = ('core/api/g9figur.py', 'core/api/g9garderobe.py', 'core/dienste/g9antworten.py',
               'core/dienste/werkzeugkoerper.py')

    # ------------------------------------------------------------- Huelle

    @classmethod
    def huelle(cls, web):
        u"""Alle Dateien im Projekt (`web` = `HumanBodyWeb/`), die von den `WURZELN` aus importiert werden — sie selbst eingeschlossen."""
        gesehen, offen = set(), [Path(web) / rel for rel in cls.WURZELN]
        while offen:
            datei = offen.pop()
            if datei in gesehen or not datei.is_file():
                continue
            gesehen.add(datei)
            try:
                baum = ast.parse(datei.read_bytes())
            except (OSError, SyntaxError, ValueError):
                continue
            offen.extend(cls._importe(datei, baum, Path(web)))
        return sorted(gesehen)

    @staticmethod
    def _importe(datei, baum, web):
        u"""Die Dateien, die `datei` importiert (relativ oder `core.…`) — Module und, bei `from x import name`, ein Untermodul `name`."""
        aus = []
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.ImportFrom):
                if knoten.level:
                    basis = datei.parent
                    for _ in range(knoten.level - 1):
                        basis = basis.parent
                    teile = knoten.module.split('.') if knoten.module else []
                elif knoten.module and knoten.module.split('.')[0] == 'core':
                    basis, teile = web, knoten.module.split('.')
                else:
                    continue
                ziel = basis.joinpath(*teile) if teile else basis
                namen = [ziel] + [ziel / a.name for a in knoten.names if a.name != '*']
            elif isinstance(knoten, ast.Import):
                namen = [web.joinpath(*a.name.split('.')) for a in knoten.names if a.name.split('.')[0] == 'core']
            else:
                continue
            for pfad in namen:
                for kandidat in (pfad.with_suffix('.py'), pfad / '__init__.py'):
                    if kandidat.is_file():
                        aus.append(kandidat)
        return aus

    # ------------------------------------------------------------- Fassung

    @classmethod
    def dateien(cls, tools, quellen):
        u"""`quellen` (relativ zur Wurzel `tools`: Datei oder Ordner mit `*.py`) plus die Huelle von `HumanBodyWeb/`."""
        tools = Path(tools)
        alle = set(cls.huelle(tools / 'HumanBodyWeb'))
        for rel in quellen:
            pfad = tools / rel
            if pfad.is_file():
                alle.add(pfad)
            elif pfad.is_dir():
                alle.update(pfad.glob('*.py'))
        return sorted(alle)

    @classmethod
    def fassung(cls, tools, quellen):
        u"""Kurzer Hash ueber Pfad und Inhalt aller Dateien — dieselbe Fassung, solange kein Byte anders ist."""
        tools = Path(tools)
        h = hashlib.sha1()
        for datei in cls.dateien(tools, quellen):
            try:
                inhalt = datei.read_bytes()
            except OSError:
                continue
            h.update(datei.relative_to(tools).as_posix().encode('utf-8'))
            h.update(b'\0')
            h.update(inhalt)
            h.update(b'\0')
        return h.hexdigest()[:16]
