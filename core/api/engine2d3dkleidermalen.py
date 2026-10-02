# -*- coding: utf-8 -*-
"""Engine2d3dKleidermalendpunkte — von Hand auf das Modell der Runde malen (01.10.2026; Blenders „Texture Paint").

    POST /api/engine2d3dkleider/<id>/malen/   {kennung, art: kleidung|haar, name, farbe, radius, deckung,
                                        striche: [{gruppe: slug, u, v}]}
                                       → {brief, regler: '<kennung>.bild.decal_<name>', rezept: zeile}

Die Bühne nimmt die Striche auf (Raycast auf die GLB der Runde: Knoten `…_g<k>__<slug>` nennt die Gruppe, `uv` in
glTF-Konvention), `G9kleidpinsel` malt sie in die Decal-Schicht des Stücks. Der Regler `bild.decal_<name>` wird im
Modell des Kreislaufs auf 1 gestellt, damit der nächste Bau die Schicht zeigt, und die Rezeptliste bekommt die Zeile
(`m.bild_wert(...)`), damit `GET …/rezept/` den Weg vollständig nennt. Während der Auftrag rechnet: 409.
"""

import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from Genesis9.kleidpinsel import G9kleidpinsel
from Genesis9.kleidtexturen import G9kleidtexturen

from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidermalendpunkte']


class Engine2d3dKleidermalendpunkte:
    @staticmethod
    @require_POST
    def malen(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft — malen, wenn die Runde fertig ist'}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        kennung = str(rumpf.get('kennung') or '').strip()
        art = 'haar' if rumpf.get('art') == 'haar' else 'kleidung'
        name = str(rumpf.get('name') or 'pinsel').strip().lower()
        striche = rumpf.get('striche') if isinstance(rumpf.get('striche'), list) else []
        if not kennung or not striche:
            return JsonResponse({'error': 'kennung und striche fehlen'}, status=400)
        try:
            radius = float(rumpf.get('radius') or 12.0)
            deckung = float(rumpf.get('deckung') or 1.0)
            brief = G9kleidpinsel.malen(kennung, name, striche, str(rumpf.get('farbe') or '#ffffff'),
                                        min(max(radius, 1.0), 200.0), min(max(deckung, 0.0), 1.0))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except OSError as fehler:
            logger.warning('Malen %s/%s: %s', kennung, name, fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        regler = '%s.%sdecal_%s' % (kennung, G9kleidtexturen.PRAEFIX, name)
        zeile = "m.bild_wert(%r, %r, %r, 1.0)" % (art, kennung, 'decal_' + name)
        ergebnis = dict(job.ergebnis or {})
        z = dict(ergebnis.get('kreislauf') or {})
        modell = dict(z.get('modell') or {})
        if modell:
            ziel = dict(modell.get(art) or {})
            ziel[regler] = 1.0
            modell[art] = ziel
            z['modell'] = modell
            ergebnis['kreislauf'] = z
        beg = dict(ergebnis.get('begutachtung') or {})
        rezept = list(beg.get('rezept') or [])
        if not any(r.get('kommentar') == 'gemalt' and zeile in (r.get('aufrufe') or []) for r in rezept):
            rezept.append({'runde': z.get('letzte_runde'), 'aufrufe': [zeile], 'kommentar': 'gemalt'})
        beg['rezept'] = rezept
        ergebnis['begutachtung'] = beg
        job.ergebnis = ergebnis
        job.save(update_fields=['ergebnis', 'updated_at'])
        logger.info('2D3D Kleider %s: gemalt auf %s/%s — %d Striche', job.kennung, kennung, name, brief.get('striche', 0))
        return JsonResponse({'ok': True, 'brief': brief, 'regler': regler, 'rezept': zeile})
