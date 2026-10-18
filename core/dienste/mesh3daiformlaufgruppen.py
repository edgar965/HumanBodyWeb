# -*- coding: utf-8 -*-
"""Mesh3daiformlaufgruppen — Einstellungen, Ergebnis je Gruppe und Vergleich mit dem vorigen Lauf für /mesh-3D-AI/formtraining/<lauf>/ (18.10.2026).

Textabellen (Klasse `doku`, keine Datensortierung): je Tabelle `{'kopf': [Spalten], 'zeilen': [[{text, klasse, titel}] | {'gruppe': Überschrift}]}`, gerendert von `_mesh3dai_doku_tabelle.html`.
  * Gruppen: `lauf_ergebnis.json` → `zusammen` (Jobs Training, Jobs Prüfposen, Formvarianten Training, Prüfformen) — Zeile je Messgröße, Spalte je Gruppe. Vorstufen-Läufe haben kein `zusammen`.
  * Vergleich: dieselben Gruppen des Vorgängers (`Mesh3daiformlauf.vorgaenger`); Δ grün/rot nur bei Fehlermaßen (kleiner ist besser), nie bei Bezugsgrößen. Unterscheiden sich die Läufe in Figuren,
    Wolken, Reglern oder Formmaß, steht es darüber — dann messen die Zahlen nicht dasselbe.
"""

from .mesh3daiformlaufnamen import Mesh3daiformlaufnamen as N
from .mesh3daiformzellen import Mesh3daiformzellen as Z

__all__ = ['Mesh3daiformlaufgruppen']


class Mesh3daiformlaufgruppen:
    #: nicht als Einstellung zeigen (eigene Karten oder zu groß)
    OHNE = ('verlauf', 'je_figur', 'zusammen', 'figur_quelle', 'ausgelassen', 'kopf_gruppe')
    #: was zwei Läufe vergleichbar macht — weicht eines ab, steht es über dem Vergleich
    VERGLEICHBAR = ('netz', 'kopf', 'formmass', 'eingang', 'formkopf', 'formregler_datei', 'training_daten', 'formvarianten', 'epochen', 'punkte_je_probe', 'drehung_grad',
                    'farbe', 'saat', 'wolken', 'proben_alle', 'proben')
    SCHWELLE = 0.05   # kleinere Δ sind Rundung (die Dateien tragen eine Nachkommastelle)

    @classmethod
    def einstellungen(cls, ergebnis):
        zeilen = [[{'text': N.name(k), 'titel': k}, {'text': cls.wert(v)}] for k, v in ergebnis.items() if k not in cls.OHNE]
        return {'kopf': ['Einstellung', 'Wert'], 'zeilen': zeilen} if zeilen else None

    @classmethod
    def gruppen(cls, ergebnis):
        zusammen = ergebnis.get('zusammen') or {}
        if not isinstance(zusammen, dict) or not zusammen:
            return None
        namen = list(zusammen)
        schluessel = cls._schluessel(zusammen.values())
        zeilen = [[{'text': N.name(k), 'titel': k, 'klasse': 'mesh3dai-bezug' if N.bezug(k) else ''}]
                  + [{'text': cls.zahl((zusammen[g] or {}).get(k)), 'klasse': 'num'} for g in namen] for k in schluessel]
        return {'kopf': ['Messgröße'] + namen, 'zeilen': zeilen}

    @classmethod
    def vergleich(cls, ergebnis, vorher):
        """Zeile je (Gruppe, Messgröße) in beiden Läufen: vorher · jetzt · Δ. Gruppen aus `zusammen`; haben die Läufe keine gemeinsame (Vorstufen-Läufe schreiben keins),
        je Figur und Gruppe aus `je_figur`. None ohne Gemeinsames."""
        jetzt_z, vorher_z = ergebnis.get('zusammen') or {}, (vorher or {}).get('zusammen') or {}
        if not any(g in vorher_z for g in jetzt_z):
            jetzt_z, vorher_z = cls._je_figur(ergebnis), cls._je_figur(vorher)
        gemeinsam = [g for g in jetzt_z if g in vorher_z]
        if not gemeinsam:
            return None
        zeilen = []
        for g in gemeinsam:
            a, b = vorher_z[g] or {}, jetzt_z[g] or {}
            schluessel = [k for k in cls._schluessel([b]) if k in a]
            if not schluessel:
                continue
            zeilen.append({'gruppe': g})
            for k in schluessel:
                zeilen.append([{'text': N.name(k), 'titel': k, 'klasse': 'mesh3dai-bezug' if N.bezug(k) else ''},
                               {'text': cls.zahl(a.get(k)), 'klasse': 'num'}, {'text': cls.zahl(b.get(k)), 'klasse': 'num'}, cls._delta(k, a.get(k), b.get(k))])
        return {'kopf': ['Messgröße', 'vorher', 'jetzt', 'Δ'], 'zeilen': zeilen} if zeilen else None

    @classmethod
    def unterschiede(cls, ergebnis, vorher):
        """Einstellungen, in denen sich die beiden Läufe unterscheiden — `[(Name, vorher, jetzt)]`."""
        aus = []
        for k in cls.VERGLEICHBAR:
            a, b = (vorher or {}).get(k), ergebnis.get(k)
            if a != b and (a is not None or b is not None):
                aus.append((N.name(k), cls.wert(a), cls.wert(b)))
        return aus

    @staticmethod
    def _je_figur(ergebnis):
        """`je_figur` als Gruppen „<Figur> · <Gruppe>“ mit flachen Zahlen (verschachtelte als `oben.unten`)."""
        je = (ergebnis or {}).get('je_figur') or {}
        return {'%s · %s' % (figur, N.GRUPPEN.get(g, g)): N.flach(werte) for figur, gruppen in je.items() if isinstance(gruppen, dict)
                for g, werte in gruppen.items() if isinstance(werte, dict)}

    @staticmethod
    def _schluessel(gruppen):
        aus = []
        for g in gruppen:
            for k, v in (g or {}).items():
                if k not in aus and isinstance(v, (int, float)) and not isinstance(v, bool):
                    aus.append(k)
        return aus

    @classmethod
    def _delta(cls, k, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return {'text': '—', 'klasse': 'num'}
        d = b - a
        klasse = 'num'
        if N.fehler(k) and abs(d) >= cls.SCHWELLE:
            klasse += ' mesh3dai-besser' if d < 0 else ' mesh3dai-schlechter'
        text = ('%+d' % d) if isinstance(a, int) and isinstance(b, int) else ('%+.1f' % d).replace('.', ',')
        return {'text': text, 'klasse': klasse, 'titel': 'jetzt − vorher' + (' (kleiner ist besser)' if N.fehler(k) else '')}

    @staticmethod
    def zahl(v):
        if v is None:
            return '—'
        if isinstance(v, bool):
            return 'ja' if v else 'nein'
        if isinstance(v, int):
            return Z.zahl(v)
        if isinstance(v, float):
            return Z.mm(v) if abs(v) >= 0.1 or v == 0 else ('%.3f' % v).replace('.', ',')
        return str(v)

    @classmethod
    def wert(cls, v, laenge=300):
        """Ein Wert der Einstellungen als Text: Listen und kleine Wörterbücher ausgeschrieben, gekürzt auf `laenge` Zeichen."""
        if isinstance(v, dict):
            text = ' · '.join('%s %s' % (k, cls.wert(x, 80)) for k, x in v.items())
        elif isinstance(v, (list, tuple)):
            text = ', '.join(cls.wert(x, 80) for x in v) + (' (%d)' % len(v) if len(v) > 4 else '')
        else:
            text = cls.zahl(v)
        return text if len(text) <= laenge else text[:laenge - 1] + '…'
