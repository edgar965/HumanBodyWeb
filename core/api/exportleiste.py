# -*- coding: utf-8 -*-
"""Endpunkte der Exportleiste (31.10.2026, `Exportleiste`, Vorlage `_exportleiste.html`).

    GET  /api/exportleiste/<bereich>/<kennung>/[?bvh=<Pfad oder Kategorie/Name>]   → Zustand: Name, Exportordner, Ton-Vorgabe, Regler (Katalog und Werte), Render, Pfade, BVH
    POST /api/exportleiste/<bereich>/<kennung>/export/          multipart: `modell` (GLB der Seite), `angaben` (JSON: format, animation, bvh, stellung, audio, audio_pfad, name, ordner)
    POST /api/exportleiste/<bereich>/<kennung>/obj/             multipart wie `/api/character/modellexport/` (`Modellexport`, Format obj) + `haut_deckt` (JSON-Liste der Stücknamen)
    POST /api/exportleiste/<bereich>/<kennung>/render/         multipart: `modell`, `angaben` (JSON: sekunden, kamera, groesse, spp, anmerkung, ton, bvh, stellung, name, ordner)
    POST /api/exportleiste/<bereich>/<kennung>/render/neu/     multipart: `modell`, `angaben` (JSON: nummern oder alle, ton, bvh, stellung, name, ordner) — „Neu rendern"
    POST /api/exportleiste/<bereich>/<kennung>/render/loeschen/ {nummern: [3, 5]} → Läufe samt Video und Bogen aus der Tabelle (nicht während eines Renders)
    (`modell` entfällt, wenn der Bereich sein eigenes Modell hat — `Exportleistequelle.EIGENES_MODELL`, 2D3D Kleider)
    POST /api/exportleiste/<bereich>/<kennung>/einstellungen/   {optionen: {renderqualitaet: {…}, …}} → {optionen}
    GET  /api/exportleiste/<bereich>/<kennung>/datei/<name>     Video oder Bogen eines Render-Laufs (nur aus `ergebnis/`, nur .mp4/.png)
"""

import json
import logging

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.exportleiste import Exportleiste
from ..dienste.exportleistebereiche import Exportleistebereiche
from ..dienste.exportleisteobjmaske import Exportleisteobjmaske
from ..dienste.exportleisterender import Exportleisterender
from ..dienste.modellexportlauf import Modellexportlauf
from ..dienste.modellexportziel import ZielAbgelehnt

logger = logging.getLogger('core')

__all__ = ['Exportleisteendpunkte']


class Exportleisteendpunkte:
    ENDUNGEN = ('.mp4', '.png')

    @staticmethod
    def _leiste(bereich, kennung):
        quelle = Exportleistebereiche.quelle(bereich, kennung)
        if quelle is None:
            raise Http404('Keine Exportleiste %s/%s' % (bereich, kennung))
        return Exportleiste(quelle)

    @staticmethod
    def _angaben(request):
        try:
            angaben = json.loads(request.POST.get('angaben') or '{}')
        except ValueError:
            return {}
        return angaben if isinstance(angaben, dict) else {}

    @staticmethod
    @require_GET
    def zustand(request, bereich, kennung):
        return JsonResponse(Exportleisteendpunkte._leiste(bereich, kennung).zustand(request.GET.get('bvh', '')))

    @staticmethod
    @require_POST
    def export(request, bereich, kennung):
        leiste = Exportleisteendpunkte._leiste(bereich, kennung)
        modell = request.FILES.get('modell')
        if modell is None and not leiste.quelle.EIGENES_MODELL:
            return JsonResponse({'error': 'Die Figur fehlt (GLB)'}, status=400)
        try:
            return JsonResponse(leiste.exportieren(modell, Exportleisteendpunkte._angaben(request)))
        except (ValueError, ZielAbgelehnt) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except RuntimeError as fehler:
            logger.error('Exportleiste %s/%s: %s', bereich, kennung, fehler)
            return JsonResponse({'error': str(fehler)[:600]}, status=500)

    @staticmethod
    def _json(roh, vorgabe):
        try:
            return json.loads(roh) if roh else vorgabe
        except ValueError:
            return vorgabe

    @staticmethod
    @require_POST
    def obj(request, bereich, kennung):
        """Die OBJ des Browsers ablegen wie `Modellexportanfrage.ablegen` (eigener Unterordner mit MTL und Bildern), die .obj vorher im Speicher ohne die Haut unter den Stücken
        (`Exportleisteobjmaske`) — es wird nur das Ergebnis geschrieben."""
        leiste = Exportleisteendpunkte._leiste(bereich, kennung)
        deckend, dateien, verdeckung = Exportleisteendpunkte._json(request.POST.get('haut_deckt'), None), [], None
        for datei in request.FILES.getlist('dateien'):
            if datei.name.lower().endswith('.obj'):
                text, verdeckung = Exportleisteobjmaske.text(b''.join(datei.chunks()).decode('utf-8'), deckend)
                datei = SimpleUploadedFile(datei.name, text.encode('utf-8'), content_type='text/plain')
            dateien.append(datei)
        if verdeckung is None:
            return JsonResponse({'error': 'Keine OBJ zum Ablegen'}, status=400)
        try:
            ergebnis = Modellexportlauf(ordner_roh=request.POST.get('ordner'), name_roh=request.POST.get('name'), dateien=dateien).ausfuehren()
        except ZielAbgelehnt as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        warnungen = Exportleisteendpunkte._json(request.POST.get('warnungen'), [])
        logger.info('Exportleiste %s/%s: obj nach %s, Haut %s', leiste.quelle.BEREICH, leiste.quelle.kennung, ergebnis['ordner'], verdeckung)
        return JsonResponse(dict(ergebnis, warnungen=warnungen if isinstance(warnungen, list) else [], hautverdeckung=verdeckung))

    @staticmethod
    @require_POST
    def render(request, bereich, kennung):
        """Rendern; `…/render/neu/` (`neu=True`): abgelegte Läufe noch einmal (`angaben.nummern` oder `angaben.alle`), nacheinander (`Exportleisterender.neu`)."""
        return Exportleisteendpunkte._rendern(request, bereich, kennung, False)

    @staticmethod
    @require_POST
    def render_neu(request, bereich, kennung):
        return Exportleisteendpunkte._rendern(request, bereich, kennung, True)

    @staticmethod
    def _rendern(request, bereich, kennung, neu):
        render = Exportleisterender(Exportleisteendpunkte._leiste(bereich, kennung))
        modell = request.FILES.get('modell')               # bei `EIGENES_MODELL` keine: der Render nimmt das Modell des Bereichs
        try:
            angaben = Exportleisteendpunkte._angaben(request)
            return JsonResponse({'ok': True, 'render': render.neu(modell, angaben) if neu else render.starten(modell, angaben)})
        except (ValueError, ZielAbgelehnt) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)

    @staticmethod
    @require_POST
    def render_loeschen(request, bereich, kennung):
        """`{nummern: [3, 5]}` → Läufe aus der Tabelle samt Video und Bogen (`Engine2d3dKleiderrenderlaeufe.loeschen`); nicht, solange ein Render läuft (er schreibt `laeufe.json`)."""
        from ..dienste.engine2d3dkleiderrenderlaeufe import Engine2d3dKleiderrenderlaeufe
        render = Exportleisterender(Exportleisteendpunkte._leiste(bereich, kennung))
        rumpf = Exportleisteendpunkte._json(request.body.decode('utf-8', 'replace'), {})
        nummern = rumpf.get('nummern') if isinstance(rumpf, dict) else None
        if not isinstance(nummern, list) or not nummern or not all(isinstance(n, int) for n in nummern):
            return JsonResponse({'error': 'nummern: Liste ganzer Zahlen'}, status=400)
        if render.laeuft():
            return JsonResponse({'error': 'Ein Render läuft — löschen geht, wenn er fertig ist'}, status=409)
        geloescht = Engine2d3dKleiderrenderlaeufe(render).loeschen(nummern)
        return JsonResponse({'ok': True, 'geloescht': geloescht, 'render': render.bericht()})

    @staticmethod
    @require_POST
    def einstellungen(request, bereich, kennung):
        leiste = Exportleisteendpunkte._leiste(bereich, kennung)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        return JsonResponse({'optionen': leiste.optionen_speichern((rumpf or {}).get('optionen') if isinstance(rumpf, dict) else {})})

    @staticmethod
    @require_GET
    def datei(request, bereich, kennung, name):
        leiste = Exportleisteendpunkte._leiste(bereich, kennung)
        ordner = leiste.ablage.ergebnis().resolve()
        pfad = (ordner / name).resolve()
        if pfad.parent != ordner or pfad.suffix.lower() not in Exportleisteendpunkte.ENDUNGEN or not pfad.is_file():
            raise Http404('Keine Datei %s' % name)
        return FileResponse(open(pfad, 'rb'))
