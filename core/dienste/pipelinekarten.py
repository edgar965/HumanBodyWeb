# -*- coding: utf-8 -*-
u"""Pipelinekarten — die Karten der 3D-Uploadseite in der Folge des Rangs.

Auftrag Edgar (12.09.2026): „ordne die pipelines nach der Ranking, alle
sollen per default eingeklappt sein". Der Rang steht in `Pipelinevergleich`
(Hilfe -> Video to BVH), gemessen an EINEM Video; `/process/VideoToBVH/`
zeigt die Karten in derselben Folge, damit nicht zwei Seiten zwei
Reihenfolgen behaupten. Wer keinen Rang hat (kein Ergebnis), steht am Ende,
in der Folge des Vergleichs. Das Zuklappen selbst ist Sache der Vorlage
und von `kartenklappe.js`; hier steht nur, welche Karte wo steht.

Je Karte eine Vorlage `_pipeline_<karte>.html`: `upload_v4.html` war mit 761
Zeilen laengst ueber der Grenze, DuoMo und GEM-X lagen schon draussen. Die
Hybrid-Karte deckt zwei Pipelines (`hybrid_gvhmr`, `hybrid_prompthmr`, das
Auswahlfeld „Body-Backend" setzt den Wert) — sie steht dort, wo die bessere
der beiden steht.
"""
from .pipelinevergleich import Pipelinevergleich
from .pipelinevergleich_3d import Pipelines3d


class Pipelinekarten:
    u"""Kartennamen und Vorlagen der 3D-Seite, nach Rang."""

    #: Pipeline -> Karte, wo es nicht dieselbe ist.
    KARTE = {'hybrid_gvhmr': 'hybrid', 'hybrid_prompthmr': 'hybrid',
             'hybrid_gem': 'hybrid'}

    VORLAGE = '_pipeline_%s.html'

    @classmethod
    def karte(cls, pipeline):
        return cls.KARTE.get(pipeline, pipeline)

    @classmethod
    def dreid(cls):
        u"""Die Pipelines der 3D-Seite — die Eintraege des 3D-Vergleichs,
        jede einmal (Varianten nicht doppelt)."""
        return list(dict.fromkeys(e['schluessel'] for e in Pipelines3d.EINTRAEGE))

    @classmethod
    def reihenfolge(cls):
        u"""Kartennamen nach Rang; jede Karte einmal, ohne Rang am Ende."""
        dreid = set(cls.dreid())
        karten = []
        for eintrag in Pipelinevergleich.rangfolge():
            karte = cls.karte(eintrag['schluessel'])
            if eintrag['schluessel'] in dreid and karte not in karten:
                karten.append(karte)
        return karten

    @classmethod
    def rang(cls, karte):
        u"""Der beste Rang der Pipelines auf dieser Karte; None ohne Rang."""
        raenge = [e['rang'] for e in Pipelinevergleich.mit_rang()
                  if cls.karte(e['schluessel']) == karte]
        return min(raenge) if raenge else None

    @classmethod
    def vorlagen(cls):
        u"""Die Vorlagennamen in Kartenfolge."""
        return [cls.VORLAGE % karte for karte in cls.reihenfolge()]

    @classmethod
    def rang_von(cls):
        u"""Wie viele Pipelines im Vergleich einen Rang haben — der Nenner
        im Abzeichen („Rang 2 von 10")."""
        return len(Pipelinevergleich.mit_rang())

    @classmethod
    def eintraege(cls):
        u"""Karte, Vorlage und Rang je Karte in Kartenfolge — so geht es in
        die Seite; `_pipeline_rang.html` zeigt den Rang im Kartenkopf
        (Edgar, 12.09.2026: „mach das Rang abzeichen")."""
        # Dictionary gewollt: geht so in die Vorlage.
        return [{'karte': karte, 'vorlage': cls.VORLAGE % karte,
                 'rang': cls.rang(karte)}
                for karte in cls.reihenfolge()]
