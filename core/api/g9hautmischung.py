# -*- coding: utf-8 -*-
u"""Die Bilder eines Hautsatzes fuer die Texturmischung (`G9hautmischungapi`).

    GET /api/character/genesis9-figur/haut/<preset>/bilder/
        {gruppen: {Head: {albedo, normalen, rauheit, normalenachse?}, Body: …}}
        404 bei unbekanntem Hautsatz.

Edgar (21.09.2026): „kann ich denn eine HD Textur von einem Modell (z.B.
Ursula) auf Kin uebertragen? … mach eine Kategorie und Einstellung ganz unten
bei den Modell Eigenschaften, «Textur» mit allen Texturen die du hast, und
Regler dazu in %". Die Auswahl «Haut» tauscht den ganzen Satz; die Mischung
legt weitere Saetze mit Gewicht DARUEBER — im Browser, im Shader
(`gemeinsam/genesis9hautmischung.js`, `Genesis9haut.mischung`). Dafuer braucht
der Browser nur die Bildpfade je Koerpergruppe; der Koerper wird NICHT neu
gebaut (ein Reglerzug bleibt ein Uniform-Update, kein Serverlauf).

Nur Albedo, Normalen und Rauheit — die 8K-Detailnormalen bleiben draussen
(`G9browserbilder.fuer`: Grenze nach Stufe, `_NM_`-Nachbar ohne Normalen).
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from Genesis9.browserbilder import G9browserbilder
from Genesis9.hautpresets import G9hautpresets
from Genesis9.pfade import G9pfade

__all__ = ['G9hautmischungapi']


class G9hautmischungapi:
    u"""Bilder je Gruppe eines Hautsatzes."""

    ARTEN = ('albedo', 'normalen', 'rauheit', 'normalenachse')

    @staticmethod
    @require_GET
    def bilder(request, preset):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': u'Daz-Bibliothek nicht gefunden'}, status=404)
        gruppen = G9hautmischungapi.gruppen(preset)
        if not gruppen:
            return JsonResponse({'fehler': u'Unbekannter Hautsatz: %s' % preset}, status=404)
        return JsonResponse({'preset': preset, 'gruppen': gruppen})

    @classmethod
    def gruppen(cls, preset):
        u"""`{gruppe: {albedo, normalen, rauheit}}` — nur Gruppen mit Albedo."""
        aus = {}
        for gruppe, bilder in (G9hautpresets.haut(preset) or {}).items():
            tragbar = G9browserbilder.fuer(bilder)
            if not tragbar.get('albedo'):
                continue
            aus[gruppe] = {art: tragbar[art] for art in cls.ARTEN if tragbar.get(art)}
        return aus
