# -*- coding: utf-8 -*-
"""Architektur2d3dworkflow — die Daten des Reiters „Workflow" der Seite Hilfe → Architektur → 2D3D (02.10.2026).

Edgar: „mache einen neuen Tab, wo du den Workflow der 2D3D-Erkennung machst, mit allen Klassen und allen Optionen (z. B. Blender) —
ich brauche grafische Klassen mit Entscheidungsbäumen und Infos, was jeder Schritt kostet an Zeit". Hier werden die Teile
zusammengesteckt: die Kette der elf Schritte (`Workflowstrecke`), die Entscheidungsbäume des Laufs und der Runde
(`Workflowlauf`, `Workflowrunde`, `Workflowrundebau`, darin `Workflowkleidung` und `Workflowdrapieren`), der Fluss einer Runde (`Workflowfluss`), die Klassenkarten
(`Workflowkarten`) und seit 06.10.2026 die technischen Details (`Architektur2d3dtechnik`). Die Quellen der Zeiten werden in der Reihenfolge nummeriert, in der sie auf der Seite zuerst stehen.
"""

from .architektur2d3dtechnik import Architektur2d3dtechnik
from .stoffsolverumfang import Stoffsolverumfang
from .workflowfluss import Workflowfluss
from .workflowkarten import Workflowkarten
from .workflowlauf import Workflowlauf
from .workflowquellen import Workflowquellen
from .workflowrunde import Workflowrunde
from .workflowrundebau import Workflowrundebau
from .workflowstrecke import Workflowstrecke
from .workflowzeichner import Workflowzeichner

__all__ = ['Architektur2d3dworkflow']


class Architektur2d3dworkflow:
    #: Beschriftung der Zeitstufen (`Workflowzeit.STUFEN`) für die Legende.
    LEGENDE = [
        ('z0', 'unter 1 s'),
        ('z1', '1–10 s'),
        ('z2', '10–60 s'),
        ('z3', '1–5 min'),
        ('z4', 'über 5 min'),
        ('zx', 'nicht gemessen'),
    ]

    @classmethod
    def baeume(cls):
        """Alle Entscheidungsbäume: zuerst die des Laufs, dann die der Runde."""
        return Workflowlauf.baeume() + Workflowrunde.baeume() + Workflowrundebau.baeume()

    @classmethod
    def kontext(cls, gruppen, lauf, runde):
        """`gruppen`: `Architektur2d3dklassen.gruppen()`, `lauf`/`runde`: `Architektur2d3d.LAUF`/`RUNDE`."""
        baeume = cls.baeume()
        quellen = Workflowquellen()
        zeichner = Workflowzeichner(quellen, {z['klasse'] for g in gruppen for z in g['klassen']})
        titel = {b.kennung: b.titel for b in baeume}
        strecke = Workflowstrecke(zeichner, titel)
        # In der Reihenfolge der Seite aufrufen: Die Quellen werden nach ihrem ersten Auftreten nummeriert.
        schritte, zeitleiste = strecke.schritte(), strecke.zeitleiste()
        gezeichnet = [
            {'kennung': b.kennung, 'anker': b.anker, 'titel': b.titel, 'html': zeichner.baum(b)}
            for b in baeume
        ]
        fluss = Workflowfluss(zeichner, titel, runde).abschnitte()
        anzahl_lauf = len(Workflowlauf.baeume())
        return {
            'legende': [{'klasse': k, 'text': t} for k, t in cls.LEGENDE],
            'schritte': schritte,
            'zeitleiste': zeitleiste,
            'baeume_lauf': gezeichnet[:anzahl_lauf],
            'baeume_runde': gezeichnet[anzahl_lauf:],
            'fluss': fluss,
            'karten': Workflowkarten(gruppen, lauf, runde, baeume).gruppen(),
            'stoffsolver': {'zeilen': Stoffsolverumfang.zeilen(), 'zaehlung': Stoffsolverumfang.zaehlung(),
                            'quelle': Stoffsolverumfang.QUELLE},
            'quellen': [{'nr': n, 'text': q} for n, q in quellen.liste()],
            'technik': Architektur2d3dtechnik.kontext(),
        }
