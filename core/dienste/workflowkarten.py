# -*- coding: utf-8 -*-
"""Workflowkarten — die Klassenkarten des Workflow-Reiters: je Klasse ein Kasten wie im Klassenmodell, mit Datei, Zeilenzahl, Aufgabe
(erster Satz des Modul-Docstrings), öffentlichen Methoden und dem Platz im Ablauf (Hilfe → Architektur → 2D3D, 02.10.2026).

Der Platz im Ablauf ist nicht von Hand eingetragen, sondern aus den Daten der Seite gelesen: die Schritte des Laufs
(`Architektur2d3d.LAUF`), die Schritte der Runde (`Architektur2d3d.RUNDE`) und die Entscheidungsbäume (`Workflowbaum.klassen`).
So kann eine Karte nicht behaupten, eine Klasse gehöre zu einem Schritt, der sie nicht nennt.
"""

import re

__all__ = ['Workflowkarten']


class Workflowkarten:
    NAME = re.compile(r'[A-Za-z][A-Za-z0-9_]*')
    METHODEN_ZEIGEN = 6

    def __init__(self, gruppen, lauf, runde, baeume):
        """`gruppen`: `Architektur2d3dklassen.gruppen()`, `lauf`/`runde`: `Architektur2d3d.LAUF`/`RUNDE`, `baeume`: `[Workflowbaum]`."""
        self.gruppen_daten = gruppen
        self.namen = {z['klasse'] for g in gruppen for z in g['klassen']}
        self.verwendung = self._verwendung(lauf, runde, baeume)

    def _verwendung(self, lauf, runde, baeume):
        """`{Klasse: ([Schrittnamen], [Bäume])}` — nur Klassen, zu denen es eine Karte gibt."""
        schritte, trees = {}, {}
        for schritt, klassen, _was in lauf:
            for name in self.NAME.findall(klassen):
                if name in self.namen:
                    schritte.setdefault(name, []).append('Lauf: ' + schritt)
        for nr, _wann, _was, klassen, _takt in runde:
            for name in klassen.split(', '):
                if name in self.namen:
                    schritte.setdefault(name, []).append('Runde: Schritt %d' % nr)
        for baum in baeume:
            for name in baum.klassen():
                if name in self.namen:
                    trees.setdefault(name, []).append({'anker': baum.anker, 'titel': baum.titel})
        return {n: (schritte.get(n, []), trees.get(n, [])) for n in self.namen}

    def gruppen(self):
        aus = []
        for g in self.gruppen_daten:
            karten = []
            for z in g['klassen']:
                schritte, baeume = self.verwendung[z['klasse']]
                methoden = z['methoden']
                karten.append(
                    dict(
                        z,
                        anker='k-' + z['klasse'],
                        schritte=schritte,
                        baeume=baeume,
                        methoden_gezeigt=methoden[: self.METHODEN_ZEIGEN],
                        methoden_mehr=max(0, len(methoden) - self.METHODEN_ZEIGEN),
                    )
                )
            aus.append({'gruppe': g['gruppe'], 'hinweis': g['hinweis'], 'karten': karten})
        return aus
