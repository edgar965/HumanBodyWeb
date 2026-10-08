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
    entlichten   das Licht der Netzfarbe herausrechnen (Prozent; die drei Texturoptionen: `Meshfigurtexturoptionen`)
    kleidung    was die Anpassung mit Shirt und Hose des Netzes tut: nur nicht nach außen drücken, oder
                 dazu schwach heranziehen (Rumpf hängt am Shirt) — oder wie Haut (alte Regel, Stoff = Haut)
    referenz     Testfall: eine Figur der Genesis-Bibliothek, gegen die das Ergebnis gemessen wird
    blind        beim Testfall die Regler der Referenzfigur selbst NICHT benutzen (ehrliche Probe)
    frisur       welche Frisur das Modell trägt (Schritt „frisur"): die mit der kleinsten Hülle,
                 nur Daz-Frisuren, nur „Haar Eigen", keine
    haarkarten   Haarkarten aus der Haarschale des Netzes als eigenes Objekt (Bühne, Weg C)
    modell       das Ergebnis als Modell speichern (`data/models/<Name>.json`, Szene/Studio)
"""

from .meshfigurkleidungsoptionen import Meshfigurkleidungsoptionen
from .meshfigurtexturoptionen import Meshfigurtexturoptionen

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
    ] + Meshfigurtexturoptionen.KATALOG + [
        {
            'schluessel': 'kleidung',
            'titel': 'Kleidung im Netz',
            'art': 'wahl',
            'vorgabe': 'weich',
            'werte': [
                ('weich', 'Der Stoff zieht schwach — die Haut liegt knapp darunter (Vorgabe)'),
                ('ignorieren', 'Der Stoff darf die Figur nur nicht nach außen drücken'),
                ('wie_haut', 'Wie Haut (bis 29.09.2026: Shirt und Shorts formen die Figur)'),
            ],
            'hinweis': 'Haut und Stoff trennt der Hautton der kahlen Stellen (Gesicht, Hände, Unterarme, '
            'Unterschenkel), nicht der von Rumpf und Oberschenkeln. Der Stoff färbt die Figur nie: '
            'Sie ist der Körper darunter.',
        },
        {
            'schluessel': 'kleidungszug',
            'titel': 'Zug des Stoffs (%)',
            'art': 'zahl',
            'vorgabe': 60,
            'min': 0,
            'max': 100,
            'fein': True,
            'hinweis': 'Nur bei „Der Stoff zieht schwach“: wie stark Shirt und Hose die Figur an sich ziehen '
            '(100 = so stark wie Haut, aber knapp darunter). Ohne Zug wird der Rumpf ein Standardkörper — bei '
            'Edgar ein Sixpack statt des Bauchs; zu viel bläht die Figur unter weiten Stellen auf.',
        },
        {
            'schluessel': 'kleidungsabstand_mm',
            'titel': 'Haut unter dem Stoff (mm)',
            'art': 'zahl',
            'vorgabe': 8,
            'min': 0,
            'max': 40,
            'fein': True,
            'hinweis': 'Wie weit die Haut unter der Stoffoberfläche liegen soll (Stoffdicke und Luft): ein '
            'anliegendes Shirt 3–8 mm, ein weites 15–25 mm.',
        },
    ] + Meshfigurkleidungsoptionen.KATALOG + [
        {
            'schluessel': 'genitalform',
            'titel': 'Genitalbereich (%)',
            'art': 'zahl',
            'vorgabe': 30,
            'min': 0,
            'max': 100,
            'fein': True,
            'hinweis': 'Nur bei der männlichen Grundfigur: wie stark der Schritt ausgeformt ist (Daz-Regler „Hip '
            'Genital Bulge“; 100 % = bis 2,9 cm nach vorn, 30 % = 9 mm). Der Wert steht fest, die Anpassung ändert '
            'ihn nicht und der Schritt zählt bei ihr kaum — bis 29.09.2026 stellte sie den Regler auf 100 %, um die '
            'Beule der Shorts nachzuformen: ein unförmiger Klumpen. Ein Anatomie-Paket für Genesis 9 ist nicht '
            'installiert (nur sein UV-Satz).',
        },
        {
            'schluessel': 'kandidaten',
            'titel': 'Normalensuche der Anpassung (Nachbarn)',
            'art': 'zahl',
            'vorgabe': 1,
            'min': 1,
            'max': 64,
            'fein': True,
            'hinweis': 'Ein Netz aus Bild-zu-3D hat oft eine Innenwand ~3 mm unter der Haut. Die Regleranpassung sucht '
            'unter dieser Zahl nächster Netzproben die nächste mit passender Normale (die Außenhaut); 1 = nur die '
            'nächste. Mit 16 zog die Anpassung Lippen und Kinn bei Edgar 6–12 mm vor das Netz (Mittelprofil RMS 6,8 '
            'gegen 4,0 mm) — darum 1; der Eigenmorph nutzt die Suche (nächste Option).',
        },
        {
            'schluessel': 'rest_kandidaten',
            'titel': 'Normalensuche des Eigenmorphs (Nachbarn)',
            'art': 'zahl',
            'vorgabe': 16,
            'min': 1,
            'max': 64,
            'fein': True,
            'hinweis': 'Wie die Option davor, für den Eigenmorph (Rest je Käfigpunkt nach den Reglern). Bei doppelwandigem '
            'Netz trafen sonst 49 % der Nasenpunkte und 51 % der Punkte an Mund und Wangen die Innenwand und bekamen '
            'kein Gewicht; mit 16 sind es 91 % und 78 % (Punkte mit Gewicht, Edgars Gesicht). 1 = nur die nächste Probe.',
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
            'schluessel': 'frisur',
            'titel': 'Frisur',
            'art': 'wahl',
            'vorgabe': 'beste',
            'werte': [
                ('beste', 'Die dem Netzhaar am nächsten kommt (Daz oder „Haar Eigen")'),
                ('daz', 'Nur Daz-Frisuren'),
                ('eigen', '„Haar Eigen" (Länge, Kurz, Dichte, Wellig, Dutt)'),
                ('aus', 'Keine'),
            ],
        },
        {
            'schluessel': 'haarkarten',
            'titel': 'Haarkarten aus dem Netz',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'Ja — Strähnen an der Haarschale entlang, als eigenes Objekt'),
                ('aus', 'Nein'),
            ],
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
