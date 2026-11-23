# -*- coding: utf-8 -*-
"""Meshgenesistestkleidmethoden — welche Stücke mit welchen Methoden ins gespeicherte Modell gehen (23.11.2026).

Edgar, 23.11.2026: „beim Speichern sollen zumindest Haare, Bart, Haut mitgehen, Toggles welche Kleider (Bibliothek usw)“. Bis dahin nahm „Als Modell speichern“ je Zeile nur
den wirksamen Weg (`Meshgenesistestkleider.wirksam`, also die Kleiderbibliothek), egal welche Methode die Ergebniskarte zeigte, und Eigen (e) und Passend (p) fielen still weg.

Dieselbe Regel wie die Ergebniskarte (`Fotogenesistestfigur.wegWahl`):
  * Kleidung (`KLEIDUNG`, wie `Fotogenesistestfigur.KLEIDUNG`): je angehakter Methode ihr Weg, wo die Zeile ein Stück dafür hat; Kleiderbibliothek = der wirksame Weg der Zeile.
    Zwei Methoden heißt zwei Stücke derselben Zeile — angehakt ist angehakt.
  * alles andere (Haar, Bart, Schuhe, Hut, Requisiten): IMMER der wirksame Weg, wie die Karte sie bei jeder Methode zeigt.

    Meshgenesistestkleidmethoden.pruefen(['eigen', 'bibliothek']) -> ('bibliothek', 'eigen')     # ValueError bei unbekannter Methode
    Meshgenesistestkleidmethoden.wege(zeile, methoden)            -> ['z', 'e']
    Meshgenesistestkleidmethoden.angebot(liste)                   -> [{wert, text, anzahl}]
"""

__all__ = ['Meshgenesistestkleidmethoden']


class Meshgenesistestkleidmethoden:
    #: Methode → Weg (`Fotogenesistestfigur.WEG`); None = der wirksame Weg der Zeile. Reihenfolge = Reihenfolge der Häkchen.
    WEG = {'bibliothek': None, 'drapieren': 'f', 'eigen': 'e', 'passend': 'p'}
    TEXTE = {'bibliothek': 'Kleiderbibliothek', 'drapieren': 'Drapieren', 'eigen': 'Eigen', 'passend': 'Passend'}
    KLEIDUNG = frozenset(('oberteil', 'kleid', 'anzug', 'hose', 'rock', 'unterwaesche'))
    VORGABE = ('bibliothek',)
    #: Kein Haken gesetzt: keine Kleidung (Haar, Bart, Schuhe, Hut, Requisiten bleiben) — so heißt es auf der Befehlszeile, wo eine leere Liste die Vorgabe wäre.
    KEINE = 'keine'

    @staticmethod
    def da(st, weg):
        """Hat die Zeile ein Stück auf diesem Weg (Anzeigenetz oder Stück der Garderobe, ohne Fehler)?"""
        d = st.get(weg)
        return isinstance(d, dict) and not d.get('fehler') and bool(d.get('netz') or d.get('kennung'))

    @classmethod
    def pruefen(cls, methoden):
        """None oder '' → Vorgabe (Kleiderbibliothek); eine leere Liste oder 'keine' → keine Kleidung; sonst die Methoden in fester Reihenfolge."""
        if methoden is None or methoden == '':
            return cls.VORGABE
        if isinstance(methoden, str):
            methoden = [m for m in methoden.split(',') if m]
        methoden = [m for m in methoden if m != cls.KEINE]
        falsch = [str(m) for m in methoden if m not in cls.WEG]
        if falsch:
            raise ValueError('Unbekannte Methode: %s' % ', '.join(falsch))
        return tuple(m for m in cls.WEG if m in methoden)

    @classmethod
    def befehl(cls, methoden):
        """Die geprüften Methoden für `--methoden` des Arbeitsprozesses."""
        return ','.join(methoden) or cls.KEINE

    @classmethod
    def wege(cls, st, methoden):
        wirksam = st.get('wahl') if st.get('wahl') not in (None, 'aus') else None
        if st.get('art') not in cls.KLEIDUNG:
            return [wirksam] if wirksam else []
        aus = []
        for m in methoden:
            weg = cls.WEG[m]
            if weg is None:
                weg = wirksam
            elif not cls.da(st, weg):
                continue
            if weg and weg not in aus:
                aus.append(weg)
        return aus

    @classmethod
    def angebot(cls, liste):
        """Die Methoden mit der Zahl der Kleidungsstücke, die sie hätten — Kleiderbibliothek immer, die anderen nur, wenn sie für dieses Modell gerechnet sind."""
        kleidung = [st for st in ((liste or {}).get('stuecke') or []) if st.get('art') in cls.KLEIDUNG]
        aus = []
        for m, weg in cls.WEG.items():
            anzahl = sum(1 for st in kleidung if (st.get('wahl') not in (None, 'aus') if weg is None else cls.da(st, weg)))
            if weg is None or anzahl:
                aus.append({'wert': m, 'text': cls.TEXTE[m], 'anzahl': anzahl})
        return aus
