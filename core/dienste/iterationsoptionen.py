# -*- coding: utf-8 -*-
"""Iterationsoptionen — die Gruppe `iterationen` der Optionen von „Haar Engine": wie lange und womit iteriert
wird (30.09.2026).

Dieselbe Katalogform wie `Haarenginefilmoptionen` (`schluessel`, `titel`, `art`, `vorgabe`, `werte`,
`hinweis`). Die Prüf-KI ist wählbar: die Liste kommt beim Aufbau der Seite aus Ollama
(`Ollamamodelle.mit_bildern`) — nur Modelle, die Bilder lesen können. Ein gespeichertes Modell bleibt
gültig, auch wenn Ollama gerade nicht antwortet (sonst fiele die Wahl still auf die Vorgabe zurück); geprüft
wird nur, dass der Name wie ein Ollama-Name aussieht.

Gegenüber BlenderModel fehlen die Optionen, die zum Bau in Blender gehörten (Fototextur, Umriss-Hülle,
Sichtmodell): Was die Engine an Einstellungen bekommt, steht mit ihren Einzelheiten hier.
"""

import re

from .ollamamodelle import Ollamamodelle

__all__ = ['Iterationsoptionen']


class Iterationsoptionen:
    AUS = 'aus'
    VORGABE_KI = 'qwen3.8:27b'
    OLLAMANAME = re.compile(r'^[\w.\-:/]{1,120}$')
    BEGUTACHTUNG, AUTOMATISCH = 'begutachtung', 'automatisch'
    KATALOG = [
        {
            'schluessel': 'modus',
            'titel': 'Iterationen',
            'art': 'wahl',
            'vorgabe': BEGUTACHTUNG,
            'werte': [
                (BEGUTACHTUNG, 'Begutachtung — je Runde ein Rezept (Aufrufe an ModellMitKleidern), danach wartet der Auftrag'),
                (AUTOMATISCH, 'Automatisch — Optimierer und Prüf-KI über die Haarparameter (die frühere Schleife)'),
            ],
            'hinweis': 'Begutachtung (Edgar, 30.09.2026): jede Runde wird angesehen, dann kommt neuer Code; der Auftrag steht '
            'mit „Wartet auf Begutachtung", bis das nächste Rezept kommt (Reiter „Iterationen").',
        },
        {
            'schluessel': 'bildbreite',
            'titel': 'Renderbreite (px)',
            'art': 'zahl',
            'vorgabe': 256,
            'min': 96,
            'max': 1024,
            'hinweis': 'Breite der Renders je Blickwinkel (Höhe = 1,5 × Breite). Die Note rechnet auf 128 × 192, mehr ist nur '
            'für das Auge. Klein für einen schnellen Durchlauf.',
        },
        {
            'schluessel': 'runden',
            'titel': 'Runden je Lauf',
            'art': 'zahl',
            'vorgabe': 20,
            'min': 1,
            'max': 5000,
            'hinweis': 'So viele Runden rechnet ein Druck auf „Weiter iterieren" (oder der Schritt im ganzen Lauf). Jeder Lauf '
            'setzt beim besten bisherigen Modell an.',
        },
        {
            'schluessel': 'kandidaten',
            'titel': 'Kandidaten je Runde',
            'art': 'zahl',
            'vorgabe': 4,
            'min': 1,
            'max': 16,
            'hinweis': 'So viele Abwandlungen des besten Modells baut und rendert die Engine je Runde.',
        },
        {
            'schluessel': 'parallel',
            'titel': 'Engine-Prozesse parallel',
            'art': 'zahl',
            'vorgabe': 1,
            'min': 1,
            'max': 8,
            'hinweis': 'So viele Prozesse der Engine rechnen die Kandidaten einer Runde gleichzeitig. Mehr Prozesse belasten '
            'den Rechner stärker.',
        },
        {
            'schluessel': 'stillstand',
            'titel': 'Halt nach Runden ohne Besserung',
            'art': 'zahl',
            'vorgabe': 15,
            'min': 0,
            'max': 1000,
            'hinweis': '0 = nie vorzeitig anhalten.',
        },
        {
            'schluessel': 'pruefki',
            'titel': 'Prüf-KI (lokal, Ollama)',
            'art': 'wahl',
            'vorgabe': VORGABE_KI,
            'werte': [],
            'hinweis': 'Sieht Vorlage und Render und schlägt Werte vor (Teile an/aus, Längen, Farben). Nur Modelle, die Bilder '
            'lesen können. „Aus" = nur der Optimierer.',
        },
        {
            'schluessel': 'pruefki_alle',
            'titel': 'Prüf-KI alle … Runden',
            'art': 'zahl',
            'vorgabe': 5,
            'min': 1,
            'max': 1000,
            'hinweis': 'Die Prüf-KI sieht sich alle so viele Runden die Tafel an (dazu bei einer Flaute, siehe nächste Option). '
            'Ein Aufruf kostet 1–3 Minuten — in einer langen Suche alle 250 Runden.',
        },
        {
            'schluessel': 'pruefki_stillstand',
            'titel': 'Prüf-KI nach … Runden ohne Besserung',
            'art': 'zahl',
            'vorgabe': 3,
            'min': 1,
            'max': 1000,
            'hinweis': 'Eine Runde der Prüf-KI dauert je nach Modell 20–60 s; bei 3 Runden Flaute würde sie in einer langen '
            'Flaute fast jede dritte Runde des Optimierers verdrängen.',
        },
        {
            'schluessel': 'toleranz',
            'titel': 'Toleranz der Prüf-KI (%)',
            'art': 'zahl',
            'vorgabe': 2,
            'min': 0,
            'max': 20,
            'hinweis': 'Ein Vorschlag der Prüf-KI wird übernommen, solange die Abweichung um höchstens so viel Prozent '
            'schlechter wird — ein Detail, das den Umriss kaum ändert, gehört trotzdem dazu.',
        },
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def katalog(cls):
        modelle = Ollamamodelle.mit_bildern()
        aus = []
        for e in cls.KATALOG:
            werte = e.get('werte', [])
            if e['schluessel'] == 'pruefki':
                # Die Vorgabe bleibt wählbar, auch wenn Ollama gerade schweigt — sonst zeigte das Feld „Aus", und das
                # nächste Speichern schriebe es.
                if cls.VORGABE_KI not in [n for n, _ in modelle]:
                    modelle = [
                        (cls.VORGABE_KI, '%s (Ollama antwortet gerade nicht)' % cls.VORGABE_KI)
                    ] + modelle
                werte = [(cls.AUS, 'Aus — nur der Optimierer')] + modelle
            aus.append(dict(e, werte=[{'wert': w, 'text': t} for w, t in werte], fein=False))
        return {'optionen': aus}

    @classmethod
    def pruefen(cls, roh):
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            if e['schluessel'] == 'pruefki':
                if str(wert) == cls.AUS or cls.OLLAMANAME.match(str(wert)):
                    aus['pruefki'] = str(wert)
            elif e['art'] == 'wahl':
                if str(wert) in [w for w, _ in e.get('werte', [])]:
                    aus[e['schluessel']] = str(wert)
            elif e['art'] == 'zahl':
                try:
                    zahl = float(wert)
                except TypeError, ValueError:
                    continue
                if e['min'] <= zahl <= e['max']:
                    aus[e['schluessel']] = int(zahl) if zahl.is_integer() else zahl
        return aus
