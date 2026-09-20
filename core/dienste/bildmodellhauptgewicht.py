# -*- coding: utf-8 -*-
"""Bildmodellhauptgewicht — nur die markierten Hauptbilder bauen den Körper.

Edgar (20.09.2026): „Nimm die Proportionen / Schätzungen aus den ersten 2
Hauptbildern. Mach eine Kategorie: Hauptbild Vorne, Hauptbild Hinten,
Hauptbild Seitlich. Dann für Kopf die 3 Hauptbild-Kategorien (vorne, hinten,
seitlich). Diese sollen mehrheitlich gewichtet werden." — und danach: „ab
sofort den Gesamtkörper nur anhand der Hauptbilder aus der Combo bauen."

Hauptbilder sind die Einträge, die in der zweiten Box als „Hauptbild: vorn /
hinten / seitlich" bzw. „Kopf-Hauptbild: …" markiert sind (`hauptbild: True`,
`Bildmodellbildtypen.HAUPTBILD`). Sie bauen den Körper allein: die markierten
Körper-Hauptbilder teilen sich das ganze Gewicht (`MEHRHEIT` = 1), alle übrigen
Körperbilder bekommen 0 — ein posiertes Bild oder ein Ausschnitt ändert die
Form nicht mehr. Ist in einer Kategorie nichts markiert, gelten die Kandidaten
(Ansicht vorn, hinten oder Seite, nicht dreiviertel, kein Video) in der
Zeilenreihenfolge der Proportionentabelle (`Bildmodellfotolinien.hauptbilder`:
Spalte „Nr.", sonst Typ) — beim Körper die ersten `ANZAHL` (2); gibt es auch
die nicht, zählen alle gleich. Dieselben Zahlen nimmt die Mischung der Betas (`Bildmodellmischung`),
das Maßband (`Bildmodellmassband.smplx`) und die Kopfwahl (`kopf`: erst das
Kopf-Hauptbild von vorn, dann Seite, dann hinten, dann das größte Gesicht).
"""

import numpy as np

from .bildmodellbildtypen import Bildmodellbildtypen

__all__ = ['Bildmodellhauptgewicht']


class Bildmodellhauptgewicht:
    ANZAHL = 2
    MEHRHEIT = 1.0   # 20.09.2026: nur die Hauptbilder; davor 2/3
    ANSICHTEN = ('vorne', 'hinten', 'seite')
    KOPFREIHE = ('vorne', 'seite', 'hinten')

    def __init__(self, job):
        self.job = job

    @classmethod
    def ist_hauptbild(cls, b, kategorie='koerper'):
        return (b.get('kategorie') == kategorie and b.get('ansicht') in cls.ANSICHTEN
                and not b.get('video') and Bildmodellbildtypen.fuer_form(b))

    def hauptbilder(self, kategorie='koerper'):
        """Die Hauptbilder der Kategorie in Zeilenreihenfolge: die markierten (`hauptbild`) —
        sonst die Kandidaten, beim Körper die ersten `ANZAHL`."""
        from .bildmodellfotolinien import Bildmodellfotolinien

        reihe = Bildmodellfotolinien(self.job).hauptbilder()
        kandidaten = [b for b in reihe if self.ist_hauptbild(b, kategorie)]
        markiert = [b for b in kandidaten if b.get('hauptbild')]
        if markiert:
            return markiert
        return kandidaten[:self.ANZAHL] if kategorie == 'koerper' else kandidaten

    def gewichte(self, bilder):
        """`{datei: gewicht}` für `bilder` (Körperbilder mit Ergebnis), Summe 1.

        Die Hauptbilder (`hauptbilder`), die in `bilder` vorkommen, teilen sich `MEHRHEIT`
        (= 1: die übrigen bekommen 0). Gibt es kein Hauptbild, zählen alle gleich.
        """
        dateien = [b.get('datei') for b in bilder]
        haupt = [b.get('datei') for b in self.hauptbilder()]
        haupt = [d for d in haupt if d in dateien]
        rest = [d for d in dateien if d not in haupt]
        aus = {}
        if haupt and rest:
            for d in haupt:
                aus[d] = self.MEHRHEIT / len(haupt)
            for d in rest:
                aus[d] = (1.0 - self.MEHRHEIT) / len(rest)
        else:
            alle = haupt or rest
            for d in alle:
                aus[d] = 1.0 / len(alle)
        return aus

    def mittel(self, bilder, werte):
        """Gewichtetes Mittel der Zeilen `werte` (eine je Bild, gleiche Länge) — oder None."""
        if not bilder or len(werte) == 0:  # `werte` kann ein numpy-Array sein — kein `not`
            return None
        g = self.gewichte(bilder)
        w = np.array([g.get(b.get('datei'), 0.0) for b in bilder], dtype=float)
        m = np.array(werte, dtype=float)
        if w.sum() <= 0:
            return m.mean(axis=0)
        return (m * w[:, None]).sum(axis=0) / w.sum()

    def kopf(self, bilder):
        """Das Bild für den Kopf: Kopf-Hauptbild von vorn, dann Seite, dann hinten — sonst None
        (der Aufrufer nimmt dann das größte Gesicht)."""
        koepfe = self.hauptbilder('kopf')
        for ansicht in self.KOPFREIHE:
            for b in koepfe:
                if b.get('ansicht') == ansicht and b in bilder:
                    return b
        return None
