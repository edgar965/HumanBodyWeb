# -*- coding: utf-8 -*-
"""Kostuemoptionen — die Gruppe `kostuem` der Optionen von BlenderModel: wie lange und womit iteriert wird.

Dieselbe Katalogform wie `Blendermodellblenderoptionen` (`schluessel`, `titel`, `art`, `vorgabe`, `werte`,
`hinweis`). Die Prüf-KI ist wählbar (Edgar, 29.09.2026: „mach die Wahl der Prüf-KI einstellbar beim Job"): die
Liste kommt beim Aufbau der Seite aus Ollama (`Ollamamodelle.mit_bildern`) — nur Modelle, die Bilder lesen
können. Ein gespeichertes Modell bleibt gültig, auch wenn Ollama gerade nicht antwortet (sonst fiele die Wahl
still auf die Vorgabe zurück); geprüft wird nur, dass der Name wie ein Ollama-Name aussieht.
"""

import re

from .ollamamodelle import Ollamamodelle

__all__ = ['Kostuemoptionen']


class Kostuemoptionen:
    AUS = 'aus'
    VORGABE_KI = 'qwen3.8:27b'
    OLLAMANAME = re.compile(r'^[\w.\-:/]{1,120}$')
    KATALOG = [
        {
            'schluessel': 'runden',
            'titel': 'Runden je Lauf',
            'art': 'zahl',
            'vorgabe': 20,
            'min': 1,
            'max': 1000,
            'hinweis': 'So viele Runden rechnet ein Druck auf „Weiter iterieren" (oder der Schritt im '
            'ganzen Lauf). Jeder Lauf setzt beim besten bisherigen Kostüm an.',
        },
        {
            'schluessel': 'kandidaten',
            'titel': 'Kandidaten je Runde',
            'art': 'zahl',
            'vorgabe': 4,
            'min': 1,
            'max': 16,
            'hinweis': 'So viele Abwandlungen baut und rendert Blender je Runde in einem Prozess.',
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
            'hinweis': 'Sieht Vorlage und Render und schlägt Werte vor (Teile an/aus, Längen, Farben). '
            'Nur Modelle, die Bilder lesen können. „Aus" = nur der Optimierer.',
        },
        {
            'schluessel': 'pruefki_alle',
            'titel': 'Prüf-KI alle … Runden',
            'art': 'zahl',
            'vorgabe': 5,
            'min': 1,
            'max': 100,
            'hinweis': 'Dazu jedes Mal, wenn drei Runden hintereinander nichts besser wurde.',
        },
        {
            'schluessel': 'toleranz',
            'titel': 'Toleranz der Prüf-KI (%)',
            'art': 'zahl',
            'vorgabe': 2,
            'min': 0,
            'max': 20,
            'hinweis': 'Ein Vorschlag der Prüf-KI wird übernommen, solange die Abweichung um höchstens so '
            'viel Prozent schlechter wird — ein Bart ändert den Umriss kaum, gehört aber dazu.',
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
                # Die Vorgabe bleibt wählbar, auch wenn Ollama gerade schweigt — sonst zeigte das Feld „Aus",
                # und das nächste Speichern schriebe es.
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
            elif e['art'] == 'zahl':
                try:
                    zahl = float(wert)
                except TypeError, ValueError:
                    continue
                if e['min'] <= zahl <= e['max']:
                    aus[e['schluessel']] = int(zahl) if zahl.is_integer() else zahl
        return aus
