# -*- coding: utf-8 -*-
"""Meshfiguroptionen — was der Reiter „Mesh to 3D" einstellen lässt, mit Vorgaben.

Dieselbe Bauart wie `Meshoptionen`: EINE Tabelle (`KATALOG`), aus der das Formular gebaut wird
(`mesh/meshoptionenformular.js`) und gegen die der Lauf prüft (`pruefen`: nur bekannte Schlüssel
und Werte, alles andere fällt auf die Vorgabe).

    basis        Grundfigur, an der die Regler abgeleitet werden (Feminine, Masculine, neutral)
    hoehe_cm     Körpergröße (Scheitel, ohne Haar) — 0: wie das Netz. Ein Netz aus dem Reiter
                 „Mesh" ist auf eine feste Höhe gebracht (170 cm samt Haar); wer die Größe der
                 Person kennt, gibt sie hier an
    runden       Körper-Runden: Regler stellen → Genesis echt nachrechnen (Formelketten,
                 Knochenskalierung, Gelenkkorrekturen der Haltung) → erneut stellen
    gesicht      eigene Kette für Kopf und Gesicht (296 Regler, 478 Gesichtspunkte)
    daempfung    wie stark Regler bei ihrem Grundwert bleiben, die wenig erklären
    eigenmorph   den Rest, den die Regler nicht erreichen, als Eigenmorph dazu
    symmetrie    den Eigenmorph links/rechts mitteln (Daz-Figuren sind symmetrisch)
    textur       Farbe des Netzes auf die Genesis-Haut backen, nur den Hautton, oder keine
    kopfhaut     unter dem Haar: die Haarfarbe des Netzes aufmalen oder Haut lassen
    referenz     Testfall: eine Figur der Genesis-Bibliothek, gegen die das Ergebnis gemessen wird
    blind        beim Testfall die Regler der Referenzfigur selbst NICHT benutzen (ehrliche Probe)
    modell       das Ergebnis als Modell speichern (`data/models/<Name>.json`, Szene/Studio)
"""

__all__ = ['Meshfiguroptionen']


class Meshfiguroptionen:
    DAEMPFUNG = {'weich': 0.01, 'mittel': 0.02, 'fest': 0.05}

    KATALOG = [
        {
            'schluessel': 'basis',
            'titel': 'Grundfigur',
            'art': 'wahl',
            'vorgabe': 'feminine',
            'werte': [
                ('feminine', 'Genesis 9 Feminine'),
                ('masculine', 'Genesis 9 Masculine'),
                ('neutral', 'Genesis 9 (neutral)'),
            ],
        },
        {
            'schluessel': 'hoehe_cm',
            'titel': 'Körpergröße (cm)',
            'art': 'zahl',
            'vorgabe': 0,
            'min': 0,
            'max': 250,
            'hinweis': '0 = Größe aus dem Netz. Sonst wird das Netz so skaliert, dass die Figur '
            '(Scheitel, ohne Haar) '
            'diese Größe hat.',
        },
        {
            'schluessel': 'runden',
            'titel': 'Körper-Runden',
            'art': 'wahl',
            'vorgabe': '2',
            'werte': [
                ('1', '1 — schnell'),
                ('2', '2 — Genesis dazwischen echt nachrechnen (Vorgabe)'),
                ('3', '3 — gründlich'),
            ],
        },
        {
            'schluessel': 'gesicht',
            'titel': 'Gesicht',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'Eigene Kette: 296 Kopf-/Gesichtsregler, 478 Gesichtspunkte'),
                ('aus', 'Nur Körperkette'),
            ],
        },
        {
            'schluessel': 'daempfung',
            'titel': 'Dämpfung',
            'art': 'wahl',
            'vorgabe': 'mittel',
            'werte': [
                ('weich', 'Weich — Regler folgen dem Netz eng'),
                ('mittel', 'Mittel (Vorgabe)'),
                ('fest', 'Fest — nur, was das Netz deutlich zeigt'),
            ],
        },
        {
            'schluessel': 'eigenmorph',
            'titel': 'Rest als Eigenmorph',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'Ja — was die Regler nicht erreichen, als eigener Morph'),
                ('aus', 'Nein — nur Daz-Regler'),
            ],
        },
        {
            'schluessel': 'symmetrie',
            'titel': 'Eigenmorph symmetrisch',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'Links und rechts mitteln'),
                ('aus', 'Wie das Netz'),
            ],
        },
        {
            'schluessel': 'textur',
            'titel': 'Textur',
            'art': 'wahl',
            'vorgabe': 'mesh',
            'werte': [
                ('mesh', 'Farbe des Netzes auf die Genesis-Haut'),
                ('hautton', 'Nur den Hautton übernehmen'),
                ('aus', 'Daz-Haut unverändert'),
            ],
        },
        {
            'schluessel': 'kopfhaut',
            'titel': 'Kopfhaut',
            'art': 'wahl',
            'vorgabe': 'haar',
            'werte': [
                ('haar', 'Haarfarbe des Netzes aufmalen'),
                ('haut', 'Haut lassen (für eigenes Haar)'),
            ],
        },
        {
            'schluessel': 'referenz',
            'titel': 'Testfall (Referenzfigur)',
            'art': 'wahl',
            'vorgabe': '',
            'werte': [],
        },
        {
            'schluessel': 'blind',
            'titel': 'Testfall blind',
            'art': 'wahl',
            'vorgabe': 'aus',
            'werte': [
                ('aus', 'Alle Regler benutzen'),
                ('an', 'Regler der Referenzfigur sperren'),
            ],
            'hinweis': 'Ehrliche Probe: Die Anpassung darf die Charakterregler der Referenz nicht benutzen.',
        },
        {
            'schluessel': 'modell',
            'titel': 'Als Modell speichern',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'Ja (Szene, Studio, Theatre)'),
                ('aus', 'Nein'),
            ],
        },
    ]

    @classmethod
    def eintrag(cls, schluessel):
        for e in cls.KATALOG:
            if e['schluessel'] == schluessel:
                return e
        raise KeyError(schluessel)

    @classmethod
    def _referenzen(cls):
        from .bildmodellpersonkatalog import Bildmodellpersonkatalog

        werte = [('', '— kein Testfall —')]
        for f in Bildmodellpersonkatalog.testfiguren():
            werte.append((f['name'], f['anzeige']))
        return werte

    @classmethod
    def katalog(cls):
        """`{optionen: [...]}` für das Formular — Werte als `{wert, text}`."""
        aus = []
        for e in cls.KATALOG:
            feld = {k: v for k, v in e.items() if k != 'werte'}
            werte = cls._referenzen() if e['schluessel'] == 'referenz' else e.get('werte') or []
            if e['art'] == 'wahl':
                feld['werte'] = [{'wert': w, 'text': t} for w, t in werte]
            aus.append(feld)
        return {'optionen': aus}

    @classmethod
    def pruefen(cls, roh):
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for e in cls.KATALOG:
            s = e['schluessel']
            wert = roh.get(s, e['vorgabe'])
            if e['art'] == 'zahl':
                try:
                    wert = min(e['max'], max(e['min'], float(wert)))
                except TypeError, ValueError:
                    wert = e['vorgabe']
            elif s == 'referenz':
                erlaubt = [w for w, _ in cls._referenzen()]
                wert = wert if wert in erlaubt else ''
            elif wert not in [w for w, _ in e['werte']]:
                wert = e['vorgabe']
            aus[s] = wert
        return aus

    @classmethod
    def daempfung(cls, optionen):
        return cls.DAEMPFUNG.get((optionen or {}).get('daempfung'), cls.DAEMPFUNG['mittel'])
