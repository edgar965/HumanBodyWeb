# -*- coding: utf-8 -*-
"""Engine2d3dKleiderformendpunkte — von Hand auf der Form des Modells der Runde modellieren (01.10.2026; Blenders Sculpt).

    POST /api/engine2d3dkleider/<id>/formen/   {kennung, art: kleidung|haar|koerper, name, modus, radius_cm, staerke,
                                         striche: [{p: [x,y,z], n: [x,y,z], d?: [x,y,z]}]}
                                        → {brief, regler, rezept: zeile}

Die Bühne nimmt die Striche auf (Raycast auf die GLB der letzten Runde: Punkt und Normale je Bildpunkt des Zugs,
`d` = Zug beim Greifen), `G9formpinsel` rechnet daraus einen EIGENEN MORPH — Stück/Frisur `<kennung>.eigen.<name>`,
Körper `eigen:form_<name>` — und überträgt die Striche über den Körperkäfig der Runde (`runde_NNN_formbezug.npz`)
in die Lage der Grundfigur. Der Regler wird im Modell des Kreislaufs auf 1 gestellt, die Rezeptliste bekommt die Zeile
(`m.morph_wert(...)` bzw. `m.koerper_regler(...)`). Weil es ein Morph ist, bleiben UV und Gruppen — die Fotoprojektion
der nächsten Runde läuft auf der geformten Fläche. Während der Auftrag rechnet: 409.
"""

import logging

import numpy as np
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from Genesis9.formpinsel import G9formpinsel
from Genesis9.kleidmorphe import G9kleidmorphe

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderformendpunkte']


class Engine2d3dKleiderformendpunkte:
    @staticmethod
    def _zahl(wert, lo, hi, vorgabe):
        try:
            z = float(wert)
        except (TypeError, ValueError):
            return vorgabe
        return min(max(z, lo), hi) if np.isfinite(z) else vorgabe

    @staticmethod
    def _rundenkoerper(job):
        """Der Körperkäfig der letzten Runde (Anker der Übertragung) — None, wenn die Runde ihn nicht abgelegt hat."""
        runde = int(((job.ergebnis or {}).get('kreislauf') or {}).get('letzte_runde') or 0)
        if not runde:
            return None
        pfad = Engine2d3dKleiderablage(job.kennung).iterationen('runde_%03d_formbezug.npz' % runde)
        if not pfad.is_file():
            return None
        with np.load(pfad) as d:
            return np.asarray(d['koerper'], dtype=np.float64)

    @staticmethod
    @require_POST
    def formen(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft — formen, wenn die Runde fertig ist'}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        art = rumpf.get('art') if rumpf.get('art') in ('kleidung', 'haar', 'koerper') else 'kleidung'
        kennung = str(rumpf.get('kennung') or '').strip()
        name = str(rumpf.get('name') or 'form').strip().lower()
        modus = str(rumpf.get('modus') or 'ziehen')
        striche = rumpf.get('striche') if isinstance(rumpf.get('striche'), list) else []
        if (art != 'koerper' and not kennung) or not striche:
            return JsonResponse({'error': 'kennung und striche fehlen'}, status=400)
        if not G9kleidmorphe.NAME.match(name):
            return JsonResponse({'error': 'name: Kleinbuchstaben, Ziffern, Unterstrich (a-z, 0-9, _)'}, status=400)
        radius = Engine2d3dKleiderformendpunkte._zahl(rumpf.get('radius_cm'), 0.3, 40.0, 4.0) / 100.0
        staerke = Engine2d3dKleiderformendpunkte._zahl(rumpf.get('staerke'), 0.05, 10.0, 1.0)
        anker = Engine2d3dKleiderformendpunkte._rundenkoerper(job)
        try:
            if art == 'koerper':
                regler = G9formpinsel.koerper(name, striche, modus, radius, staerke, anker)
                brief = {'regler': regler}
                zeile = 'm.koerper_regler(%r, 1.0)' % regler
            else:
                brief = G9formpinsel.stueck(kennung, name, striche, modus, radius, staerke, anker)
                regler = '%s.%s%s' % (kennung, G9kleidmorphe.PRAEFIX, name)
                zeile = 'm.morph_wert(%r, %r, %r, 1.0)' % (art, kennung, name)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except (OSError, KeyError) as fehler:
            logger.warning('Formen %s/%s: %s', kennung or 'koerper', name, fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        Engine2d3dKleiderformendpunkte._eintragen(job, art, regler, zeile)
        logger.info('2D3D Kleider %s: geformt %s/%s (%s, %d Striche, Anker %s)', job.kennung, kennung or 'koerper',
                    name, modus, len(striche), 'Runde' if anker is not None else 'keiner')
        return JsonResponse({'ok': True, 'brief': brief, 'regler': regler, 'rezept': zeile,
                             'anker': anker is not None})

    @staticmethod
    def _eintragen(job, art, regler, zeile):
        """Regler im Modell des Kreislaufs auf 1, Rezeptzeile „geformt" (einmal je Zeile)."""
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
        if not any(r.get('kommentar') == 'geformt' and zeile in (r.get('aufrufe') or []) for r in rezept):
            rezept.append({'runde': z.get('letzte_runde'), 'aufrufe': [zeile], 'kommentar': 'geformt'})
        beg['rezept'] = rezept
        ergebnis['begutachtung'] = beg
        job.ergebnis = ergebnis
        job.save(update_fields=['ergebnis', 'updated_at'])
