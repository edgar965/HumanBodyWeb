# -*- coding: utf-8 -*-
"""Mesh3daiformvarianteendpunkte — die Seite einer Formvariante: Start · Ziel · Ergebnis des Formkopfs (18.10.2026 abends, Edgar: „mach das: Formvariante als Jobseite“).

GET /mesh-3D-AI/formvariante/<figur>/[?lauf=<lauf>]                 die Seite (Vorgabe: jüngster Formlauf, der die Figur trägt)
GET /api/mesh3dai/formvariante/<figur>/[?lauf=]                     Lauf, Läufe, Proben mit ihrer Zeile, Werte des Laufs, Regler mit der größten Abweichung (`Mesh3daiformvariante.lesen`)
GET /api/mesh3dai/formvariante/<figur>/wolke/<nr>/<k>/[?lauf=]      die A-Pose-Wolke, die der Lauf gelesen hat (`<eingang>_<k>.npz`: 16.384 Punkte, Farbe 0–255, Teil)
GET /api/mesh3dai/formvariante/<figur>/figur/<was>/[?lauf=]         Lage der Körperpunkte (Binärpaket, `Mesh3daiformvariantefigur.paket`); was = ziel | mittel | Probennummer
GET /api/mesh3dai/formvariante/<figur>/linien/<nr>/[?lauf=]        Messlinien der Regler-KI an Probe nr (Binärpaket `Mesh3dailinien`, gerechnet von `mesh3dai_reglerki_linien.py`)
GET /api/mesh3dai/formvariante/<figur>/koerper/                     Dreiecke, UV, Material des Körpers (Haut der Grundlage, einmal je Seite)
GET /api/mesh3dai/formvariante/<figur>/bild/<name>                  ein Bild der Haut (`m<Zahl>.jpg` aus dem Anzeigenetz der Grundlage, ETag/304)

Figur und Lauf kommen nie als Pfad aus der Adresse: die Figur ist ein direkter Unterordner von `3DObjects/mesh3dai`, der Lauf einer aus der Liste der Läufe, die sie tragen.
`staticmethod`, nicht `classmethod`: `require_GET` liest `request.method` am ERSTEN Argument (`mesh3dai-kleider.md`).
"""

import re

import numpy as np
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.mesh3daiflaechennetz import Mesh3daiflaechennetz
from ..dienste.mesh3daiformvariante import Mesh3daiformvariante
from ..dienste.mesh3daiformvariantefigur import Mesh3daiformvariantefigur
from ..dienste.mesh3dailinien import Mesh3dailinien

__all__ = ['Mesh3daiformvarianteendpunkte']

WAS = re.compile(r'^(ziel|mittel|\d{1,4})$')


def _lesen(request, figur):
    daten = Mesh3daiformvariante.lesen(figur, request.GET.get('lauf'))
    if daten is None:
        raise Http404('Keine Figur %s' % figur)
    return daten


def _lauf(daten):
    """Der Ordner des gewählten Laufs — sein Name stammt aus der Liste der Läufe (`Mesh3daiformvariante.laeufe`), nie aus der Adresse."""
    if not daten.get('lauf'):
        raise Http404('Kein Formlauf trägt %s' % daten['figur'])
    ordner = Mesh3daiformvariante.ordner_von(daten['lauf']['name'])
    if ordner is None:
        raise Http404('Lauf %s nicht gefunden' % daten['lauf']['name'])
    return ordner


class Mesh3daiformvarianteendpunkte:
    @staticmethod
    @require_GET
    def seite(request, figur):
        daten = _lesen(request, figur)
        lauf = daten.get('lauf') or {}
        return render(request, 'mesh3dai_formvariante.html', {'figur': daten['figur'], 'lauf': lauf.get('name') or '', 'modell': daten['modell'], 'laeufe': daten['laeufe'],
                                                              'ki_der': 'die Regler-KI' if lauf.get('ki') == 'Regler-KI' else 'der Formkopf'})

    @staticmethod
    @require_GET
    def daten(request, figur):
        return JsonResponse(_lesen(request, figur))

    @staticmethod
    @require_GET
    def wolke(request, figur, nr, k):
        daten = _lesen(request, figur)
        _lauf(daten)
        probe = next((p for p in daten['proben'] if p['nr'] == int(nr)), None)
        if probe is None or int(k) not in probe['wolken']:
            raise Http404('Keine Wolke %s/%s für %s im Lauf' % (nr, k, figur))
        datei = Mesh3daiformvariante.finden(figur) / 'proben' / ('%04d' % int(nr)) / ('%s_%d.npz' % (daten['lauf']['eingang'], int(k)))
        try:
            with np.load(datei) as z:
                punkte, farbe = z['punkte'], z['farbe']
                etikett = z['etikett'].astype(int).tolist() if 'etikett' in z.files else None
        except (OSError, ValueError, KeyError) as fehler:
            raise Http404('Wolke %s nicht lesbar (%s)' % (datei.name, fehler)) from fehler
        # float64 vor dem Runden (float32 gerundet gibt in JSON lange Ziffernfolgen, `Mesh3daidaten.eingabe`).
        return JsonResponse({'nr': int(nr), 'k': int(k), 'datei': datei.name, 'punkte': np.round(punkte.astype(float), 3).tolist(),
                             'farbe': np.clip(np.round(farbe.astype(float) * 255), 0, 255).astype(int).tolist(), 'etikett': etikett})

    @staticmethod
    @require_GET
    def figur(request, figur, was):
        if not WAS.match(str(was)):
            raise Http404('Unbekannte Figur %s' % was)
        daten = _lesen(request, figur)
        lauf = _lauf(daten)
        liste = Mesh3daiformvariante.liste(lauf)
        paket = Mesh3daiformvariantefigur.paket(lauf, figur, was, liste, daten['proben']) if liste else None
        if paket is None:
            raise Http404('Keine Figur „%s“ für %s im Lauf %s' % (was, figur, lauf.name))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def linien(request, figur, nr):
        daten = _lesen(request, figur)
        lauf = _lauf(daten)
        paket = Mesh3dailinien.paket(lauf, daten['figur'], int(nr))
        if paket is None:
            raise Http404('Keine Messlinien für Probe %s von %s im Lauf %s — für diesen Lauf nicht gerechnet' % (nr, figur, lauf.name))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def koerper(request, figur):
        daten = _lesen(request, figur)
        paket = Mesh3daiformvariantefigur.koerper(daten['grundlage']) if Mesh3daiformvariante.finden(daten['grundlage']) else None
        if paket is None:
            raise Http404('Kein Anzeigenetz der Grundlage %s' % daten['grundlage'])
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def bild(request, figur, name):
        ordner = Mesh3daiformvariante.finden(figur)
        if ordner is None:
            raise Http404('Keine Figur %s' % figur)
        grundlage = (Mesh3daiformvariante._json(ordner / 'modell.json') or {}).get('grundlage') or figur
        pfad = Mesh3daiflaechennetz.bild(grundlage, name) if Mesh3daiformvariante.finden(grundlage) else None
        if pfad is None:
            raise Http404('Kein Bild %s für %s' % (name, figur))
        return Auftragsdatei.antwort(request, pfad)
