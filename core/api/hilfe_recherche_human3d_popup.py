# -*- coding: utf-8 -*-
"""RechercheHuman3dPopup — die Popup-Daten EINES Projekts der Recherche-Tabelle (04.10.2026).

GET /hilfe/recherche/human-3d/popup/<projektkennung>/   → {name, repo, kategorie, kurz, beschreibung, details, todo_kurz, todo, bild, bilder, quellen, fork_von, fork_grund, urteil, urteil_*, todo_zeigen, …}

Vorher stand die Popup-Information ALLER Projekte als JSON in der Seite (bei 239 Projekten ein Drittel der Seite, bei 1.043 über 2,5 MB doppelt zur Tabelle); das Fenster holt sich jetzt beim Klick
nur das eine Projekt. Die Felder baut `Recherchetabelle.popup` — dieselbe Maskierungs- und Adressprüfung wie vorher; seit 09.10.2026 mit dem Urteil aus `Rechercheurteile`.
"""

from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.rechercheprojekte import Rechercheprojekte
from ..dienste.recherchetabelle import Recherchetabelle
from ..dienste.rechercheurteile import Rechercheurteile

__all__ = ['RechercheHuman3dPopup']


class RechercheHuman3dPopup:
    @staticmethod
    @require_GET
    def eintrag(request, projekt_id):
        projekte = [p for p in Rechercheprojekte.projekte() if p['id'] == projekt_id]
        if not projekte:
            raise Http404('Unbekanntes Projekt')
        return JsonResponse(Recherchetabelle.popup(projekte, Rechercheurteile.urteile())[projekt_id])
