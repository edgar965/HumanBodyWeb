# -*- coding: utf-8 -*-
"""Gesichtsformendpunkte — Seite „Gesichtsform": „Kopf-Eigen" aus Schnitten und Konturen (27.09.2026).

GET  /gesichtsform/?auftrag=<kennung> | ?modell=<Name>     die Seite
POST /api/gesichtsform/profile/   {auftrag|modell, waagerecht?, senkrecht?, ziel_neu?}
                                  → Ist, Ergebnis, Ziel, Rahmen, Güte (`Gesichtsformantwort`)
POST /api/gesichtsform/rechnen/   {auftrag|modell, ziel: {schnitte, punkte} (mm)} → Morph ablegen
                                  (`G9schnittmorph`), beim Auftrag in `ergebnis.kopfeigen`; dann wie profile
POST /api/gesichtsform/speichern/ {auftrag|modell, wert} → Auftrag: Wert + sein Modell neu schreiben;
                                  Modell: Regler mit Wert in dieses Modell

Die Rechnung dauert Sekunden (Käfig, Ansichtsstufe, 14 Schnitte, zwei Runden) — synchron, ohne Lauf.
"""

import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger('core')

__all__ = ['Gesichtsformendpunkte']


class Gesichtsformendpunkte:
    @staticmethod
    @require_GET
    def seite(request):
        auftrag, modell = request.GET.get('auftrag') or '', request.GET.get('modell') or ''
        return render(request, 'gesichtsform.html', {'auftrag': auftrag, 'modell': modell})

    @staticmethod
    def _rumpf(request):
        try:
            return json.loads(request.body or b'{}')
        except ValueError:
            return {}

    @staticmethod
    def _antwort(quelle, rumpf, **zusatz):
        from ..dienste.gesichtsformantwort import Gesichtsformantwort

        aus = Gesichtsformantwort(quelle, rumpf.get('waagerecht'), rumpf.get('senkrecht'),
                                  rumpf.get('ziel_neu')).bauen()
        aus.update(zusatz)
        return JsonResponse(aus)

    @staticmethod
    def _fehler(fehler):
        logger.warning('Gesichtsform: %s', fehler)
        return JsonResponse({'error': str(fehler)}, status=400)

    @staticmethod
    @require_POST
    def profile(request):
        from ..dienste.gesichtsformquelle import Gesichtsformquelle

        rumpf = Gesichtsformendpunkte._rumpf(request)
        try:
            return Gesichtsformendpunkte._antwort(Gesichtsformquelle.aus(rumpf), rumpf)
        except (ValueError, OSError) as fehler:
            return Gesichtsformendpunkte._fehler(fehler)

    @staticmethod
    @require_POST
    def rechnen(request):
        from Genesis9.schnittmorph import G9schnittmorph

        from ..dienste.gesichtsformquelle import Gesichtsformquelle

        rumpf = Gesichtsformendpunkte._rumpf(request)
        try:
            quelle = Gesichtsformquelle.aus(rumpf)
            ziel = G9schnittmorph.ziel_aus_seite(rumpf.get('ziel'))
            if not ziel['schnitte'] and not ziel['punkte']:
                raise ValueError('Kein Ziel — erst Schnitte oder Konturpunkte setzen')
            morph = G9schnittmorph(quelle.stellung(), quelle.name())
            ergebnis = morph.rechnen(ziel, quelle=rumpf.get('zielquelle') or 'seite')
            quelle.uebernehmen(ergebnis['regler'], ergebnis)
            logger.info('Gesichtsform %s: %s, %d Punkte, max %.1f mm', quelle.titel(), ergebnis['regler'],
                        ergebnis['punkte'], ergebnis['max_mm'])
            return Gesichtsformendpunkte._antwort(Gesichtsformquelle.aus(rumpf), rumpf, rechnung=ergebnis)
        except (ValueError, OSError) as fehler:
            return Gesichtsformendpunkte._fehler(fehler)

    @staticmethod
    @require_POST
    def speichern(request):
        from Genesis9.schnittmorph import G9schnittmorph

        from ..dienste.gesichtsformquelle import Gesichtsformquelle

        rumpf = Gesichtsformendpunkte._rumpf(request)
        try:
            quelle = Gesichtsformquelle.aus(rumpf)
            wert = max(0.0, min(2.0, float(rumpf.get('wert', 1.0))))
            name = quelle.name()
            if not G9schnittmorph.steckbrief(name):
                raise ValueError('Noch kein Kopf-Eigen-Morph — erst „Morph rechnen"')
            regler = G9schnittmorph.regler_von(name)
            quelle.uebernehmen(regler, {'guete': G9schnittmorph.steckbrief(name).get('guete')}, wert)
            modell = quelle.speichern(regler, wert)
            return JsonResponse({'ok': True, 'modell': modell, 'regler': regler, 'wert': wert})
        except (ValueError, OSError) as fehler:
            return Gesichtsformendpunkte._fehler(fehler)
