# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Human 3D: GitHub-Projekte der letzten zwei Jahre zu Menschenerkennung und -erzeugung in 3D.

Edgar (04.10.2026): „lege ein Menü an: Hilfe - Recherche, darunter Menü und Seite Human 3D, darin eine Tabelle nach djangoBase-Muster mit allen Projekten". Die Projekte stehen in
`core/daten/recherche_human3d.json` (`Rechercheprojekte`), die Tabelle baut `Recherchetabelle`; hier wird beides nur an die Vorlage gereicht.

Seit 09.10.2026 drei Tabellen (Edgar: „die Teile, die wir eingebaut haben oder die sich nicht lohnen, bitte in getrennte Tabellen unten"): offen, eingebaut, veraltet/lohnt sich nicht.
Welches Projekt wohin gehört, sagt `Rechercheurteile` (eigene Datei, nicht die Projektdatei).
"""

from ..dienste.rechercheprio import Rechercheprio
from ..dienste.rechercheprojekte import Rechercheprojekte
from ..dienste.recherchetabelle import Recherchetabelle
from ..dienste.rechercheurteile import Rechercheurteile
from .hilfeseite import Hilfeseite


class RechercheHuman3d(Hilfeseite):
    """Die Tabellen aller Projekte; ein Klick auf Einschätzung, Grund oder ToDo öffnet das Fenster mit mehr Infos und Bildern."""

    template_name = 'hilfe/recherche_human3d.html'
    AKTIV = 'hilfe_recherche_human3d'
    #: Reihenfolge der Tabellen auf der Seite.
    ABSCHNITTE = (Rechercheurteile.OFFEN, Rechercheurteile.EINGEBAUT, Rechercheurteile.ABGELEGT)

    @staticmethod
    def _kategorien(projekte, urteile):
        """`[(Name, Anzahl, Hinweis)]` — die Zahl zählt ALLE drei Tabellen; der Hinweis schlüsselt sie auf."""
        je_kategorie = {}
        for p in projekte:
            abschnitt = Rechercheurteile.abschnitt((urteile.get(p['id']) or {}).get('urteil'))
            zeile = je_kategorie.setdefault(p['kategorie'], dict.fromkeys(RechercheHuman3d.ABSCHNITTE, 0))
            zeile[abschnitt] += 1
        ergebnis = []
        for name, z in je_kategorie.items():
            hinweis = (f'{name}: {z[Rechercheurteile.OFFEN]} offen · {z[Rechercheurteile.EINGEBAUT]} eingebaut · '
                       f'{z[Rechercheurteile.ABGELEGT]} veraltet oder lohnt sich nicht — Klick schaltet die Kategorie in allen Tabellen ein oder aus')
            ergebnis.append((name, sum(z.values()), hinweis))
        return sorted(ergebnis, key=lambda k: (-k[1], k[0]))

    @staticmethod
    def _uebersicht(urteile):
        """`[(Beschriftung, Urteil, Anzahl)]` in der Reihenfolge der Tabellen — die Zahlen stammen aus den Urteilen, nicht aus dem HTML."""
        zaehler = {}
        for u in urteile.values():
            zaehler[u['urteil']] = zaehler.get(u['urteil'], 0) + 1
        folge = ('verbesserung', 'beobachten', 'neues_feature', 'eingebaut', 'veraltet', 'lohnt_nicht')
        return [(Rechercheurteile.beschriftung(w), w, zaehler.get(w, 0)) for w in folge]

    def kontext(self):
        projekte = Rechercheprojekte.projekte()
        urteile = Rechercheurteile.urteile()
        gruppen = Rechercheurteile.verteilen(projekte, urteile)
        # Erste Tabelle: Verbesserung vor Beobachten vor Neuem vor „nicht eingeschätzt"; `sorted` ist stabil, innerhalb eines Rangs bleibt die Sternenfolge.
        gruppen[Rechercheurteile.OFFEN] = sorted(gruppen[Rechercheurteile.OFFEN], key=lambda p: Rechercheurteile.rang((urteile.get(p['id']) or {}).get('urteil')))
        prios = Rechercheprio.laden()
        abschnitte = [{'id': a, 'anzahl': len(gruppen[a]),
                       'tabelle': Recherchetabelle.bauen(gruppen[a], prios if a == Rechercheurteile.OFFEN else None, urteile, a)} for a in self.ABSCHNITTE]
        return {
            'meta': Rechercheprojekte.meta(),
            'urteil_meta': Rechercheurteile.meta(),
            'anzahl': len(projekte),
            'kategorien': self._kategorien(projekte, urteile),
            'uebersicht': self._uebersicht(urteile),
            'abschnitte': abschnitte,
        }
