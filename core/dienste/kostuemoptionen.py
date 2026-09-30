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
            'max': 5000,
            'hinweis': 'So viele Runden rechnet ein Druck auf „Weiter iterieren" (oder der Schritt im '
            'ganzen Lauf). Jeder Lauf setzt beim besten bisherigen Modell an. Bei rund 25 s je Runde '
            '(8 Kandidaten) sind 1.000 Runden etwa 7 Stunden.',
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
            'schluessel': 'textur',
            'titel': 'Fototextur im Modell',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — Farben und Stoff der Vorlage im Modell (Vertexfarben)'),
                ('aus', 'Aus — flache Materialfarben'),
            ],
            'hinweis': 'Das Modell einer Runde (GLB für die Bühne) bekommt die Farben und die Stoffstruktur '
            'der Vorlagenbilder, auf die Oberfläche projiziert. Kostet ~12 s je Modell (GLB ~16 MB); ein '
            'Modell je 45 s genügt. Die Suche rechnet weiter mit flachen Farben.',
        },
        {
            'schluessel': 'huelle',
            'titel': 'Mantel folgt dem Umriss der Vorlage',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — Mantelringe an die Silhouetten der Vorlage angepasst'),
                ('aus', 'Aus — nur die Maße des Optimierers'),
            ],
            'hinweis': 'Aus den Silhouetten aller Vorlagenbilder entsteht ein Sichtkörper; die Ringe des '
            'Mantels werden an dessen Rand gezogen (begrenzt auf ein Vielfaches der Optimierer-Weite). Kostet '
            'gemessen ein Ausgangs-Render je Blender-Prozess und Ausgangsmodell (~1 s) und wenige '
            'Millisekunden je Kandidat.',
        },
        {
            'schluessel': 'sichtmodell',
            'titel': 'Sichtmodell (Umriss der Fotos) mitbauen',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — zweites Modell aus den Silhouetten, mit Fototextur'),
                ('aus', 'Aus — nur das Modell aus Teilen'),
            ],
            'hinweis': 'Aus den Silhouetten aller Vorlagenbilder entsteht ein Netz (Schichten von 1,5 cm, 72 Strahlen), '
            'darauf die Fototextur — es sieht aus den Blickwinkeln der Fotos aus wie die Fotos, hängt am selben Rig, '
            'ist aber kein Kostüm aus Teilen. Kostet ~10 s je Modell, deshalb nur alle fünf Minuten; Voraussetzung '
            'sind Fototextur und Mantel-Umriss. Bühne: Knopf „Sichtmodell“.',
        },
        {
            'schluessel': 'parallel',
            'titel': 'Blender-Prozesse parallel',
            'art': 'zahl',
            'vorgabe': 4,
            'min': 1,
            'max': 8,
            'hinweis': 'So viele Blender-Prozesse rechnen die Kandidaten einer Runde gleichzeitig — jeder lädt '
            'die Figur einmal je Lauf und bleibt dann bereit. Ein Kandidat kostet gemessen 0,6–0,8 s; mehr '
            'Prozesse belasten den Rechner stärker, bringen ab etwa einem Prozess je zwei Kandidaten kaum '
            'etwas.',
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
            'max': 1000,
            'hinweis': 'Die Prüf-KI sieht sich alle so viele Runden die Tafel an (dazu bei einer Flaute, siehe '
            'nächste Option). Ein Aufruf kostet 1–3 Minuten — in einer langen Suche alle 250 Runden.',
        },
        {
            'schluessel': 'pruefki_stillstand',
            'titel': 'Prüf-KI nach … Runden ohne Besserung',
            'art': 'zahl',
            'vorgabe': 3,
            'min': 1,
            'max': 1000,
            'hinweis': 'Eine Runde der Prüf-KI dauert je nach Modell 20–60 s; bei 3 Runden Flaute würde sie in '
            'einer langen Flaute fast jede dritte Runde des Optimierers (2–3 s) verdrängen.',
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
