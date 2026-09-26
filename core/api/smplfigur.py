# -*- coding: utf-8 -*-
"""SMPL-Referenzkoerper fuer die Szene: Liste und Netz.

    GET /api/character/smpl-figur/               {figuren: [{name, anzeige,
                                                  geschlecht, bytes, masse_vorhanden}]}
    GET /api/character/smpl-figur/<name>/netz/   {name, geschlecht, punkte,
                                                  dreiecke, hoehe, masse,
                                                  uv, uv_dreiecke, uv_ursprung}
                                                  (die drei UV-Felder nur bei
                                                  `smpl: true` und vorhandener
                                                  `smplx_uv.npz`)

Warum es diese Figur gibt: `core/dienste/smplfigur.py`.
"""

import logging

from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET

from ..daten.netzantwort import Netzantwort
from ..dienste.smplfigur import Smplfiguren

logger = logging.getLogger('core')

__all__ = ['Smplfigur']


class Smplfigur:
    """Lesende Endpunkte auf die SMPL-Koerper des GarmentCode-Klons."""

    @staticmethod
    @require_GET
    def liste(request):
        return JsonResponse({'figuren': Smplfiguren.liste()})

    @staticmethod
    @require_GET
    def netz(request, name):
        if not Smplfiguren.kennt(name):
            return JsonResponse({'fehler': 'Unbekannter SMPL-Körper'}, status=404)
        try:
            punkte, dreiecke = Smplfiguren.netz(name)
            masse = Smplfiguren.masse(name)
        except (OSError, ValueError) as fehler:
            logger.warning('SMPL-Koerper %s nicht lesbar: %s', name, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        smpl = Smplfiguren.ist_smpl(name)
        antwort = {
            'name': name,
            'geschlecht': Smplfiguren.geschlecht(name),
            'smpl': smpl,
            'punkte': punkte.tolist(),
            'dreiecke': dreiecke.tolist(),
            'hoehe': (float(punkte[:, 1].max() - punkte[:, 1].min()) if len(punkte) else 0.0),
            'masse': {k: (float(v) if isinstance(v, (int, float)) else v) for k, v in masse.items()},
            # Das Skelett kommt MIT dem Netz, nicht ueber einen zweiten
            # Endpunkt: Die Gelenke werden aus genau diesen Punkten
            # gerechnet, und ein zweiter Aufruf koennte ein anderes Netz
            # treffen (Formregler, Geschlechtswechsel). `null` heisst
            # „dieser Koerper hat keine SMPL-Topologie".
            'skelett': Smplfiguren.skelett(name, punkte),
            # Ohne Hautgewichte bleibt die Figur beim Abspielen starr —
            # das Skelett bewegt sich, das Netz nicht.
            'hautgewichte': Netzantwort.hautgewichte(Smplfiguren.haut(name, punkte)),
        }
        # UV nur fuer echte SMPL-X-Koerper — GarmentCodes eigene Referenz-
        # koerper (mean_all & Co., 23.752 Punkte) haben eine andere Topologie
        # und keine UV-Datei (25.09.2026, „SMPL-X-Texturen").
        if smpl:
            uv_felder = Smplfiguren.uv_felder(dreiecke)
            if uv_felder:
                antwort.update(uv_felder)
        return JsonResponse(antwort)

    @staticmethod
    @require_GET
    def textur(request, geschlecht):
        """Die Hautfoto-Textur eines Geschlechts — `weiblich_haut.jpg`/
        `maennlich_haut.jpg`, unabhängig vom Körper (jede SMPL-X-Figur
        dieses Geschlechts teilt sich dieselbe UV-Fläche, siehe `Smplxuv`).
        `geschlecht` ist eine feste Aufzählung (`female`/`male`), kein
        Dateiname aus der Anfrage — `SafePath` ist hier nicht nötig.
        """
        pfad = Smplfiguren.textur_pfad(geschlecht)
        if not pfad:
            return HttpResponseNotFound('Keine Textur für dieses Geschlecht')
        # Cache-Header setzt `CacheHeaderMiddleware` (Last-Modified der Datei) —
        # keine eigene Regel, damit ein Tausch der Datei sofort ankommt.
        return FileResponse(open(pfad, 'rb'), content_type='image/jpeg')

    @staticmethod
    @require_GET
    def details_maske(request, geschlecht):
        """RGBA-Maske der Details (R Lippen, G Fingernägel, B Fußnägel,
        A Augen) — `Smplxdetaildienst`, beim ersten Abruf gerechnet (~3 s)."""
        from ..dienste.smplxdetaildienst import Smplxdetaildienst

        pfad = Smplxdetaildienst.maske_pfad(geschlecht)
        if not pfad:
            return HttpResponseNotFound('Keine Detailmaske')
        return FileResponse(open(pfad, 'rb'), content_type='image/png')

    @staticmethod
    @require_GET
    def bedlam_liste(request, geschlecht):
        """`{texturen: [{schluessel, name}]}` — die BEDLAM-Hauttexturen dieses
        Geschlechts (26.09.2026, „du hast doch eine Textur heruntergeladen,
        wende sie an"), leer ohne heruntergeladenen Ordner."""
        from ..dienste.smplxbedlamdienst import Smplxbedlamdienst

        return JsonResponse({'texturen': Smplxbedlamdienst.verfuegbar(geschlecht)})

    @staticmethod
    @require_GET
    def bedlam_textur(request, geschlecht, schluessel):
        """Eine einzelne BEDLAM-Textur, aufbereitet für SMPL-X (Braue weg,
        eigenes Auge hinein) — `schluessel` nur aus `bedlam_liste`, sonst 404
        (kein Dateiname aus der Anfrage)."""
        from ..dienste.smplxbedlamdienst import Smplxbedlamdienst

        pfad = Smplxbedlamdienst.textur_pfad(geschlecht, schluessel)
        if not pfad:
            return HttpResponseNotFound('Unbekannte BEDLAM-Textur')
        return FileResponse(open(pfad, 'rb'), content_type='image/jpeg')
