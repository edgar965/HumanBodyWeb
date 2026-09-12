# -*- coding: utf-8 -*-
u"""Vorschau 3D — ein Schnitt am Körper, ohne Simulation.

    POST /api/garmentcode/vorschau3d/
         {ordner, geschlecht, morphs, bauart, koerper, smpl, meta}
      -> {punkte, dreiecke, hautabstand_mm, gebunden, ungebunden, naeherung}

WARUM (08.09.2026, Edgar: „die aktuellen Buttons machen noch die «lange»
Berechnung. Mach evtl. 5 Buttons insgesamt: Vorschau: 2D und 3D — Bauen: 2D,
3D, 2D+3D")

Der Körper ist DERSELBE, auf dem auch drapiert würde: `Garmentkoerper.
bereitstellen` legt ihn ab und nennt seinen Fassungsnamen. Ihn hier anders
zu beschaffen hiesse, dass Vorschau und Ergebnis auf verschiedenen Körpern
sitzen — der Fehler vom 06.09.2026, als der Stoff auf `mean_all` fiel,
während die Figur daneben stand.
"""
import json
import logging
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger('core')

__all__ = ['Garmentvorschauendpunkte']


class Garmentvorschauendpunkte:
    u"""Der schnelle 3D-Blick auf einen fertigen Schnitt."""

    @staticmethod
    @csrf_exempt
    @require_POST
    def vorschau3d(request):
        from GarmentCode.vorschau3d import Garmentvorschau3d
        wunsch = Garmentvorschauendpunkte._wunsch(request)
        ordner = str(wunsch.get('ordner') or '').strip()
        if not ordner:
            return JsonResponse({'fehler': 'Kein Schnittordner angegeben'},
                                status=400)
        try:
            koerper, dreiecke = Garmentvorschauendpunkte._koerper(wunsch)
        except (OSError, ValueError) as fehler:
            logger.warning('Vorschau 3D: kein Körper (%s)', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)

        try:
            antwort = Garmentvorschau3d.legen(ordner, koerper, dreiecke)
        except Exception as fehler:
            logger.exception('Vorschau 3D: unerwarteter Fehler')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        if antwort.get('fehler'):
            return JsonResponse(antwort, status=400)
        return JsonResponse(antwort)

    @staticmethod
    def _wunsch(request):
        u"""Formular ODER JSON — der GarmentCode-Reiter schickt Formulare,
        Messskripte lieber JSON."""
        if request.content_type and 'json' in request.content_type:
            try:
                return json.loads(request.body or b'{}')
            # stumm gewollt: kaputtes JSON aus dem Browser heisst 'keine Angaben'
            except ValueError:
                return {}
        roh = request.POST.dict()
        for feld in ('morphs', 'meta'):
            if roh.get(feld):
                try:
                    roh[feld] = json.loads(roh[feld])
                # stumm gewollt: ein unlesbares Feld aus dem Formular gilt als leer
                except ValueError:
                    roh[feld] = {}
        return roh

    @staticmethod
    def _koerper(wunsch):
        u"""Punkte (m, Y oben) und Dreiecke des Körpers, auf dem gerechnet wird.

        Zwei Wege, dieselben wie beim Drapieren: ein Referenzkörper von
        GarmentCode (`koerper` gesetzt) oder die Figur der Szene.
        """
        from UMA_Python.paare import Umapythonpaare

        name = str(wunsch.get('koerper') or '').strip()
        if name:
            pfad = Garmentvorschauendpunkte._referenz(name)
            if pfad is None:
                raise ValueError('Referenzkörper %r nicht gefunden' % name)
            return Umapythonpaare.obj_lesen(pfad)
        return Umapythonpaare.obj_lesen(
            Garmentvorschauendpunkte._figurkoerper(wunsch))

    @staticmethod
    def _figurkoerper(wunsch):
        u"""Die OBJ der Szenenfigur: Netz aus Morphs, vermessen, abgelegt."""
        from GarmentCode.dienst import GarmentcodeDienst
        from GarmentCode.koerperdienst import Garmentkoerper

        geschlecht = str(wunsch.get('geschlecht') or 'female')
        bauart = wunsch.get('bauart') or None
        morphs = wunsch.get('morphs') or {}
        netz = GarmentcodeDienst.figurnetz(geschlecht, morphs, bauart,
                                           wunsch.get('meta') or {})
        masse, _ = GarmentcodeDienst.masse(geschlecht, morphs=morphs,
                                           bauart=bauart, netz=netz)
        ablage = Garmentkoerper.bereitstellen(geschlecht, netz, masse)
        if not ablage or not ablage.get('ordner'):
            raise ValueError('Der Figurkörper liess sich nicht ablegen')
        return os.path.join(ablage['ordner'], '%s.obj' % ablage['name'])

    @staticmethod
    def _referenz(name):
        u"""Die OBJ eines Referenzkörpers — im Upstream oder als geformte
        Variante unter `koerper/smpl/`."""
        from django.conf import settings
        wurzel = settings.ASSETS_ROOT / 'GarmentCode'
        for kandidat in (wurzel / 'upstream' / 'assets' / 'bodies' / ('%s.obj' % name),
                         wurzel / 'koerper' / 'smpl' / ('%s.obj' % name)):
            if kandidat.is_file():
                return str(kandidat)
        return None
