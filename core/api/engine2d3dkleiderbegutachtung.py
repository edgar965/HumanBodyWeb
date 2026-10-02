# -*- coding: utf-8 -*-
"""Engine2d3dKleiderbegutachtungsendpunkte — die Begutachtung der Iterationen von „2D3D Kleider" (30.09.2026).

    POST /api/engine2d3dkleider/<id>/begutachtung/     {aufrufe, kommentar} → das Rezept prüfen, ablegen und die nächste
                                                Runde rechnen (Arbeitsprozess, nur der Schritt „iterationen");
                                                {automatisch: true, runden: n} → `IterationModell` (Ordner
                                                `2d3DIterationen`) schreibt die Rezepte selbst, n Runden nacheinander
    GET  /api/engine2d3dkleider/<id>/rezept/           alle wirksamen Aufrufe der übernommenen Runden als Text —
                                                der wiederverwendbare Weg zu diesem Modell
    GET  /api/engine2d3dkleider/funktionen/            die Funktionen von `ModellMitKleidern` (Signatur, Kurztext)

Das Rezept wird hier nur GEPRÜFT (`G9rezept.pruefen`: erlaubte Aufrufe, lesbare Argumente); angewandt wird es im
Arbeitsprozess auf das Modell der letzten Runde. Ein Fehler beim Anwenden (unbekanntes Stück …) steht dann in der
Runde (`fehler`), das Modell bleibt.
"""

import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from ..dienste.begutachtungsrunde import Begutachtungsrunde
from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..dienste.engine2d3dkleidergpu import Engine2d3dKleidergpu
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderbegutachtungsendpunkte']


class Engine2d3dKleiderbegutachtungsendpunkte:
    @staticmethod
    @require_POST
    def runde(request, job_id):
        from Genesis9.modellrezept import G9rezept
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft schon'}, status=409)
        belegt = Engine2d3dKleidergpu.belegt_durch(job)
        if belegt:
            return JsonResponse({'error': belegt}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        aufrufe = str(rumpf.get('aufrufe') or '')[:20000]
        automatisch = bool(rumpf.get('automatisch'))
        try:
            runden = max(1, min(Begutachtungsrunde.RUNDEN_HOECHSTENS, int(rumpf.get('runden') or 1)))
            if not automatisch:
                G9rezept.pruefen(aufrufe)
        except ValueError as fehler:
            return JsonResponse({'error': 'Rezept: %s' % fehler}, status=400)
        ergebnis = dict(job.ergebnis or {})
        beg = dict(ergebnis.get('begutachtung') or {})
        beg['naechste'] = {'aufrufe': '' if automatisch else aufrufe, 'automatisch': automatisch, 'runden': runden,
                           'kommentar': str(rumpf.get('kommentar') or '')[:4000]}
        beg['zustand'] = 'rechnet'
        ergebnis['begutachtung'] = beg
        job.ergebnis = ergebnis
        job.save(update_fields=['ergebnis', 'updated_at'])
        pid = Engine2d3dKleiderarbeiter.starten(job, ab='iterationen', bis='iterationen')
        logger.info('2D3D Kleider %s: Begutachtung — %s, Runde startet (%s)', job.kennung,
                    '%d Runden automatisch' % runden if automatisch
                    else 'Rezept mit %d Zeilen' % len([z for z in aufrufe.splitlines() if z.strip()]), pid)
        return JsonResponse({'ok': True, 'pid': pid})

    @staticmethod
    @require_GET
    def rezept(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        zeilen = ['# Rezept „%s" (%s) — die wirksamen Aufrufe aller übernommenen Runden' % (job.name, job.kennung),
                  '# m = ModellMitKleidern()']
        for runde in ((job.ergebnis or {}).get('begutachtung') or {}).get('rezept') or []:
            zeilen.append('')
            kommentar = (' — ' + runde['kommentar']) if runde.get('kommentar') else ''
            zeilen.append('# Runde %s%s' % (runde.get('runde'), kommentar))
            zeilen.extend(runde.get('aufrufe') or [])
        antwort = HttpResponse('\n'.join(zeilen) + '\n', content_type='text/plain; charset=utf-8')
        if request.GET.get('laden') == '1':
            antwort['Content-Disposition'] = 'attachment; filename="rezept_%s.py"' % job.kennung
        return antwort

    @staticmethod
    @require_GET
    def funktionen(request):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        from Genesis9.modellrezept import G9rezept
        return JsonResponse({'objekt': G9rezept.OBJEKT,
                             'funktionen': [{'name': n, 'signatur': s, 'text': t}
                                            for n, s, t in ModellMitKleidern.hilfe()]})
