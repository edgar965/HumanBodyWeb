# -*- coding: utf-8 -*-
"""Bildmodellproportionenendpunkte — die Eingaben des Proportionen-Popups ablegen.

Edgar (19.09.2026): „Mit einem Popup kommt ein Fenster, wo ich diese anpassen
kann. Diese Proportionen nutzt du dann für deine Berechnung."

POST `api/bildmodell/<id>/proportionen/` mit `{proportionen: {schluessel: cm},
linien: {datei: {linien}}}` schreibt die geprüften Werte
(`Bildmodelloptionen.proportionen_pruefen`) nach `job.optionen.proportionen` —
leer heißt „keine Vorgabe", das rohe Zielnetz gilt — und die im Popup gezogenen
Linien (`Bildmodellfotolinien.linien_pruefen`, Pixel des Fotos je Bild) nach
`job.optionen.proportionen_linien`. Wirksam werden sie mit dem nächsten Lauf ab „Anpassung"
(`Bildmodellzielproportionen` formt das Zielnetz); der Start-Endpunkt behält
sie, wenn der Aufruf keine eigenen mitbringt.

POST `api/bildmodell/<id>/zeilenbild/<ansicht>/` mit `{proportionen}` (optional, die aktuellen
Popup-Werte) rendert NUR die Vorher-/Nachher-Bilder dieser Ansicht neu — Zielnetz mit Umriss und
Proportionen geformt, Modell aus dem gespeicherten Ergebnis, kein Lauf (`Bildmodellzeilenbild`;
Edgar, 20.09.2026: „nicht das gesamte 3D-Modell, sondern eine schnelle Bildberechnung der Zeile").

POST `api/bildmodell/<id>/zielnetz3d/` mit `{proportionen, netz}` formt das Zielnetz (Umriss aus der
Ablage, Proportionen je Aufruf, 64 ms) für das 3D-Popup (`Bildmodellzielnetz3d`; Edgar, 20.09.2026:
„das 3D Modell interaktiv anpassen, wenn ich die Pfeile ändere … wie die Morph-Slider bei Genesis").

POST `api/bildmodell/<id>/reihenfolge/` mit `{reihenfolge: [datei, …]}` nummeriert die
Zeilen der Bildtabelle (Spalte „Nr.", editierbar — Edgar, 20.09.2026); die Nummer steht
als `reihe` am Bild, `Bildmodellfotolinien.hauptbilder` sortiert danach.
"""

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.bildmodellablage import Bildmodellablage
from ..dienste.bildmodellarbeiter import Bildmodellarbeiter
from ..dienste.bildmodellfotolinien import Bildmodellfotolinien
from ..dienste.bildmodelloptionen import Bildmodelloptionen
from ..dienste.bildmodellzeilenbild import Bildmodellzeilenbild
from ..dienste.bildmodellzielnetz3d import Bildmodellzielnetz3d
from ..models import Bildmodellauftrag

__all__ = ['Bildmodellproportionenendpunkte']


class Bildmodellproportionenendpunkte:
    """Vier Endpunkte: Proportionen stellen, Reihenfolge der Bildtabelle, Zeilenbild neu, Zielnetz 3D."""

    @staticmethod
    @require_POST
    def zielnetz3d(request, job_id):
        """Das Zielnetz mit den Popup-Werten geformt — Punkte (base64), mit `netz` auch die Dreiecke."""
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        proportionen = rumpf.get('proportionen') if isinstance(rumpf.get('proportionen'), dict) else {}
        try:
            netz = Bildmodellzielnetz3d(job, Bildmodellablage(job.kennung))
            return JsonResponse(netz.antwort(proportionen, mit_netz=bool(rumpf.get('netz'))))
        except RuntimeError as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)

    @staticmethod
    @require_POST
    def zeilenbild(request, job_id, ansicht):
        """Nur die Bilder dieser Ansicht neu (Sekunden, kein Lauf) — `{ok, ansicht, eintrag, formung}`."""
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        if job.laeuft and Bildmodellarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft gerade'}, status=409)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        if ansicht not in Bildmodellzeilenbild.ANSICHTEN:
            return JsonResponse({'error': 'Unbekannte Ansicht: %s' % ansicht}, status=400)
        proportionen = rumpf.get('proportionen') if isinstance(rumpf.get('proportionen'), dict) else None
        try:
            zeile = Bildmodellzeilenbild(job, Bildmodellablage(job.kennung))
            eintrag, formung = zeile.rechnen(ansicht, proportionen)
        except RuntimeError as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        return JsonResponse({'ok': True, 'ansicht': ansicht, 'eintrag': eintrag, 'formung': formung})

    @staticmethod
    @require_POST
    def reihenfolge(request, job_id):
        """`{reihenfolge: [datei, …]}` — die Zeilen der Bildtabelle in dieser Reihe
        (Spalte „Nr.", `bilder[].reihe`); Antwort mit den neuen `fotolinien`."""
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        linien = Bildmodellfotolinien(job)
        nummern = linien.reihenfolge(rumpf.get('reihenfolge'))
        if not nummern:
            return JsonResponse({'error': 'Keine bekannten Dateien in der Reihenfolge'}, status=400)
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'reihe': nummern, 'fotolinien': linien.alle()})

    @staticmethod
    @require_POST
    def stellen(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        werte = Bildmodelloptionen.proportionen_pruefen(rumpf.get('proportionen'))
        optionen = dict(job.optionen or {})
        optionen['proportionen'] = werte
        if 'linien' in rumpf:
            optionen[Bildmodellfotolinien.OPTION] = Bildmodellfotolinien.linien_pruefen(rumpf.get('linien'))
        job.optionen = optionen
        job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'proportionen': werte,
                             'linien': optionen.get(Bildmodellfotolinien.OPTION) or {}})
