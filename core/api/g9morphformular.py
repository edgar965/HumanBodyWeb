# -*- coding: utf-8 -*-
u"""G9morphformularapi — das freie Morph-Formular im UI (01.10.2026; bis dahin „nicht gebaut: die festen Regler decken
die Operationen"). Ein Ortsmorph mit eigenem Namen an einem Stück der Garderobe oder am Körper, aus der Szene heraus:

    POST /api/character/genesis9-figur/garderobe/<kennung>/morph/
         {name, ort: {band: [von, bis], sektor: [a, b], landmarke, radius_cm, kugel: [x, y, z]},
          richtung: haut|aussen|innen|oben|unten|vorn|hinten|[x, y, z], weg_cm, seite, weich, welle: {laenge_cm, richtung}}
         → {regler: {name: 'eigen.<name>', anzeige, min, max, vorgabe, gruppe}, brief}
    POST /api/character/genesis9-figur/morph/          (Körper, `G9koerpermorph`)
         {name, ort, richtung, weg_cm, spiegeln}
         → {regler: {name: 'eigen:ort_<name>', …}, brief}

Dieselbe Rechnung wie das Rezept (`morph_ort`, `koerper_ort`): `G9kleidmorphe.bauen` / `G9koerpermorph.bauen`. Der
Regler steht danach in der Garderobenliste (Gruppe „Eigene Morphe") bzw. im Bereich „Nachformung (Ort)" — der Browser
hängt ihn sofort an und stellt ihn auf 1 (`genesis9morphformular.js`, `genesis9koerpermorphformular.js`).
"""
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.eigenmorphe import G9eigenmorphe
from Genesis9.kleidmorphe import G9kleidmorphe
from Genesis9.koerpermorph import G9koerpermorph
from Genesis9.ortsmorph import G9ortsmorph
from Genesis9.pfade import G9pfade

from .g9figur import FEHLT, G9figur

logger = logging.getLogger('core')

__all__ = ['G9morphformularapi']


class G9morphformularapi:
    RICHTUNGEN = ('haut', 'aussen', 'innen', 'oben', 'unten', 'vorn', 'hinten')

    @staticmethod
    def _zahl(wert, lo, hi, vorgabe):
        try:
            z = float(wert)
        except (TypeError, ValueError):
            return vorgabe
        return min(max(z, lo), hi) if z == z else vorgabe

    @classmethod
    def _ort(cls, roh):
        u"""Den Ort aus dem Rumpf säubern — nur, was `G9ortsmorph` kennt."""
        ort = {}
        roh = roh if isinstance(roh, dict) else {}
        for schluessel in ('band', 'sektor'):
            paar = roh.get(schluessel)
            if isinstance(paar, (list, tuple)) and len(paar) == 2:
                try:
                    ort[schluessel] = (float(paar[0]), float(paar[1]))
                except (TypeError, ValueError):
                    pass
        if roh.get('landmarke') in G9ortsmorph.landmarken():
            ort['landmarke'] = str(roh['landmarke'])
            ort['radius_cm'] = cls._zahl(roh.get('radius_cm'), 0.5, 60.0, 8.0)
        kugel = roh.get('kugel')
        if isinstance(kugel, (list, tuple)) and len(kugel) == 3:
            try:
                ort['kugel'] = [float(v) for v in kugel]
                ort['radius_cm'] = cls._zahl(roh.get('radius_cm'), 0.5, 60.0, 8.0)
            except (TypeError, ValueError):
                pass
        welle = roh.get('welle')
        if isinstance(welle, dict) and welle.get('laenge_cm'):
            ort['welle'] = {'laenge_cm': cls._zahl(welle.get('laenge_cm'), 1.0, 60.0, 5.0),
                            'richtung': 'quer' if welle.get('richtung') == 'quer' else 'laengs'}
        return ort

    @classmethod
    def _richtung(cls, roh):
        if isinstance(roh, (list, tuple)) and len(roh) == 3:
            try:
                return [float(v) for v in roh]
            except (TypeError, ValueError):
                return 'haut'
        return str(roh) if roh in cls.RICHTUNGEN else 'haut'

    @classmethod
    def _form(cls, rumpf):
        form = {'ort': cls._ort(rumpf.get('ort')), 'richtung': cls._richtung(rumpf.get('richtung')),
                'weg_cm': cls._zahl(rumpf.get('weg_cm'), -20.0, 20.0, 2.0),
                'weich': cls._zahl(rumpf.get('weich'), 0.01, 0.5, 0.15)}
        if rumpf.get('seite') in ('links', 'rechts'):
            form['seite'] = rumpf['seite']
        if not form['ort'] and form['richtung'] != 'haut':
            form['ort'] = {'band': (0.0, 1.0)}
        return form

    @staticmethod
    @csrf_exempt
    @require_POST
    def stueck(request, kennung):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        rumpf = G9figur._rumpf(request)
        name = str(rumpf.get('name') or '').strip().lower()
        if not G9kleidmorphe.NAME.match(name):
            return JsonResponse({'fehler': 'name: Kleinbuchstaben, Ziffern, Unterstrich (a-z, 0-9, _)'}, status=400)
        form = G9morphformularapi._form(rumpf)
        try:
            brief = G9kleidmorphe.bauen(kennung, name, form)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except (OSError, KeyError) as fehler:
            logger.warning('Morph-Formular %s/%s: %s', kennung, name, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        regler = {'name': G9kleidmorphe.PRAEFIX + name, 'anzeige': u'Eigen: %s' % name, 'min': -2.0, 'max': 2.0,
                  'vorgabe': 0.0, 'gruppe': G9kleidmorphe.GRUPPE}
        return JsonResponse({'regler': regler, 'brief': brief, 'form': form})

    @staticmethod
    @csrf_exempt
    @require_POST
    def koerper(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        rumpf = G9figur._rumpf(request)
        name = G9eigenmorphe.kennung(rumpf.get('name') or '')
        if not name or name == 'morph':
            return JsonResponse({'fehler': 'name fehlt'}, status=400)
        form = G9morphformularapi._form(rumpf)
        if not form['ort']:
            return JsonResponse({'fehler': 'ort fehlt (Landmarke, Band, Sektor oder Kugel)'}, status=400)
        try:
            reglername = G9koerpermorph.bauen(name, form, bool(rumpf.get('spiegeln', True)))
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except (OSError, KeyError) as fehler:
            logger.warning('Morph-Formular Körper %s: %s', name, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        brief = G9eigenmorphe.steckbrief(reglername[len(G9eigenmorphe.PRAEFIX):])
        regler = {'name': reglername, 'anzeige': u'Ort: %s' % name, 'min': -2.0, 'max': 2.0, 'vorgabe': 0.0,
                  'bereich': 'ort', 'art': 'form'}
        return JsonResponse({'regler': regler, 'brief': brief, 'form': form})

    @staticmethod
    def landmarken(request):
        u"""GET: die Landmarken der Grundfigur für die Auswahl im Formular."""
        if not G9pfade.vorhanden():
            return JsonResponse({'landmarken': {}, 'fehler': FEHLT}, status=404)
        return JsonResponse({'landmarken': G9ortsmorph.landmarken()})
