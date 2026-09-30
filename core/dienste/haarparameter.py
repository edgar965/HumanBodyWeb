# -*- coding: utf-8 -*-
"""Haarparameter — das Haar als DATEN: jedes Maß, jede Farbe, jeder Teile-Schalter mit Startwert und
Grenzen (30.09.2026).

Eine Runde der Iterationen ändert nur Zahlen, keinen Code: der Optimierer (`Iterationsoptimierer`) und die
Prüf-KI (`Iterationskritik`) schlagen Wertesätze vor, die Genesis Haar Engine (`Genesishaarengine`) baut
daraus jedes Mal dasselbe. Diese Klasse ist der Mechanismus dafür (`schema`, `start`, `pruefen`,
`unterschiede`), gleich gebaut wie `Kostuemparameter` in BlenderModel.

**Ein „Teil" ist hier eine FRISUR.** Das Haar kommt aus der Daz-Garderobe (`G9garderobe`, Art `haar`), und
die Tabellen stehen nicht fest im Code, sondern kommen aus der Bibliothek — sonst müsste jede
nachinstallierte Frisur von Hand nachgetragen werden:

    <kennung>.an                 Schalter: trägt die Figur diese Frisur? Genau eine ist an.
    <kennung>.achse.<name>       die fünf gemeinsamen Formachsen (`G9haarachsen`), 0…1
    <kennung>.morph.<kanal>      die eigenen Morphs dieser Frisur, in IHREN Grenzen
    farbe.haar.r|g|b             die Umfärbung des Haars (0…1, sRGB — so misst der Kreislauf die Vorlage)

Der erste Schlüsselteil ist der Name des Teils: Genau daran erkennt `Iterationsoptimierer.veraenderlich`,
dass es die Maße einer AUSGESCHALTETEN Frisur nicht anfassen soll (`<teil>.an`). Von den rund 400 Maßen
sind also je Runde nur die der getragenen Frisur veränderlich — ohne eine Zeile Sonderbehandlung.

Welche Frisur getragen wird, entscheidet die Prüf-KI: Der Optimierer fasst Schalter nicht an (Kopf von
`Iterationsoptimierer`). Sind mehrere an, gewinnt die erste in der Reihenfolge der Garderobe
(`getragene`) — zwei Netze lassen sich nicht mischen.

Ändert sich das Haarmodell, steigt `VERSION`: Der Kreislauf beginnt dann mit den Startwerten statt mit den
Werten des alten Modells (`Iterationskreislauf`).
"""

import threading

__all__ = ['Haarparameter']


class Haarparameter:
    VERSION = 2
    #: Vor dem Kanal einer Frisur: `<kennung>.morph.<kanal>` bzw. `<kennung>.achse.<name>`.
    MORPH = 'morph.'
    ACHSE = 'achse.'
    #: Der Schalter je Frisur — dieselbe Form, die `Iterationsoptimierer.veraenderlich` erwartet.
    AN = '.an'
    #: Die Frisur, die ein neuer Auftrag trägt, wenn es sie gibt.
    VORGABE = 'kin_hair'
    #: Stoffe und ihre Startfarbe (sRGB 0…1): {stoff: (titel, (r, g, b))}. Mittelbraun.
    FARBEN = {'haar': ('Haar', (0.28, 0.20, 0.15))}

    _gemerkt = None
    _schloss = threading.Lock()

    # ----------------------------------------------------- aus der Bibliothek

    @classmethod
    def frisuren(cls):
        """`[(kennung, name, [(kanal, anzeige, min, max)])]` — die Frisuren der Garderobe mit ihren
        eigenen Morphs. Leer, wenn keine Daz-Bibliothek da ist (Tests, fremder Rechner)."""
        try:
            from Genesis9.garderobe import G9garderobe
            from Genesis9.pfade import G9pfade
        except ImportError:
            return []
        if not G9pfade.vorhanden():
            return []
        aus = []
        for e in G9garderobe.liste():
            if e.get('art') != 'haar' or not e.get('zeigbar'):
                continue
            kanaele = [(r['name'], r.get('anzeige') or r['name'], float(r['min']), float(r['max']))
                       for r in e.get('regler') or []]
            aus.append((e['id'], e.get('name') or e['id'], kanaele))
        return aus

    @classmethod
    def vergessen(cls):
        """Nach einer Änderung an der Bibliothek (eigenes Stück geschrieben)."""
        with cls._schloss:
            cls._gemerkt = None

    @classmethod
    def getragene(cls, werte):
        """Die Kennung der Frisur, die dieser Wertesatz trägt — oder None."""
        an = [k[: -len(cls.AN)] for k, v in (werte or {}).items()
              if k.endswith(cls.AN) and float(v or 0) >= 0.5]
        if not an:
            return None
        for kennung, _name, _kanaele in cls.frisuren():
            if kennung in an:
                return kennung
        return an[0]

    @classmethod
    def tabellen(cls):
        """(MASSE, SCHALTER) aus der Bibliothek — die Form, die `Kostuemparameter` fest im Code hat."""
        from Genesis9.haarachsen import G9haarachsen
        frisuren = cls.frisuren()
        vorgabe = cls.VORGABE if any(k == cls.VORGABE for k, _n, _c in frisuren) else (
            frisuren[0][0] if frisuren else None)
        masse, schalter = [], []
        for kennung, name, kanaele in frisuren:
            schalter.append(('%s%s' % (kennung, cls.AN), 'Frisur „%s"' % name,
                             1 if kennung == vorgabe else 0))
            for k, anzeige, lo, hi in kanaele:
                masse.append(('%s.%s%s' % (kennung, cls.MORPH, k),
                              '%s: %s' % (name, anzeige), 0.0, lo, hi))
            if G9haarachsen.vorhanden(kennung):
                for r in G9haarachsen.regler():
                    masse.append(('%s.%s%s' % (kennung, cls.ACHSE, r['name'][len(G9haarachsen.PRAEFIX):]),
                                  '%s: Form %s' % (name, r['anzeige']), 0.0, 0.0, 1.0))
        return masse, schalter

    @classmethod
    def _tabellen_gemerkt(cls):
        with cls._schloss:
            if cls._gemerkt is None:
                cls._gemerkt = cls.tabellen()
            return cls._gemerkt

    @classmethod
    def masse(cls):
        """(schluessel, titel, start, min, max) — Titel gehen wörtlich an die Prüf-KI."""
        return cls._tabellen_gemerkt()[0]

    @classmethod
    def schalter(cls):
        """(schluessel, titel, start) — je Frisur einer."""
        return cls._tabellen_gemerkt()[1]

    @classmethod
    def schema(cls):
        """`{schluessel: {titel, art, start, min, max}}` — alle Werte, die eine Runde ändern darf."""
        aus = {}
        for k, titel, start, lo, hi in cls.masse():
            aus[k] = {'titel': titel, 'art': 'mass', 'start': start, 'min': lo, 'max': hi}
        for k, titel, start in cls.schalter():
            aus[k] = {
                'titel': '%s an (1) oder aus (0)' % titel,
                'art': 'schalter',
                'start': start,
                'min': 0,
                'max': 1,
            }
        for stoff, (titel, rgb) in cls.FARBEN.items():
            for kanal, wert in zip('rgb', rgb, strict=True):
                aus['farbe.%s.%s' % (stoff, kanal)] = {
                    'titel': 'Farbe %s: %s-Anteil (0…1)' % (titel, kanal.upper()),
                    'art': 'mass',
                    'start': wert,
                    'min': 0.0,
                    'max': 1.0,
                }
        return aus

    @classmethod
    def start(cls):
        return {k: e['start'] for k, e in cls.schema().items()}

    @classmethod
    def pruefen(cls, roh):
        """Vollständiger Wertesatz: bekannte Schlüssel auf ihre Grenzen gezogen, Schalter 0/1, der Rest
        Startwert."""
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for k, e in cls.schema().items():
            try:
                wert = float(roh.get(k, e['start']))
            except TypeError, ValueError:
                wert = float(e['start'])
            if wert != wert:  # NaN
                wert = float(e['start'])
            wert = min(e['max'], max(e['min'], wert))
            aus[k] = int(wert >= 0.5) if e['art'] == 'schalter' else round(wert, 5)
        return aus

    @classmethod
    def unterschiede(cls, alt, neu, genauigkeit=1e-4):
        """`{schluessel: [alt, neu]}` — nur, was sich merklich geändert hat (für die Anzeige einer Runde)."""
        schema = cls.schema()
        aus = {}
        for k in schema:
            a, b = alt.get(k), neu.get(k)
            if a is None or b is None:
                continue
            spanne = schema[k]['max'] - schema[k]['min'] or 1.0
            if abs(float(a) - float(b)) > genauigkeit * spanne:
                aus[k] = [a, b]
        return aus
