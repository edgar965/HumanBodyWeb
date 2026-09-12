# -*- coding: utf-8 -*-
"""Absatzvorschau — die Fussbeugung zu Reglerwerten, ohne einen Bau.

    POST /api/garmentcode/absatz/vorschau/
         geschlecht, morphs, bauart, meta, koerper   (wie /erzeugen/)
         heel, platform, toe_spring                  (cm, cm, Grad)
      -> {absatz_cm, plateau_cm, winkel_grad, hebung_cm, sprengung_grad,
          hinweise}

WARUM (11.09.2026, Edgar: „kannst du bei denen einen Regler machen, der
auch gleich die Pose ändert - den Fuss anhebt?"): Der Regler `shoe.heel`
soll die Figur sofort auf den Absatz stellen, nicht erst nach Schnitt und
Simulation. Die Zahlen dafür sind dieselben wie beim Bau —
`Fussbeugung.aus_fuss` über die Fussmasse der gewählten Figur
(`GarmentcodeDienst.masse`, gemessen 0,2 s) — damit der gebaute Schuh
später genau auf dem steht, was die Vorschau gezeigt hat.
"""
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger('core')

__all__ = ['Garmentabsatzvorschau']


class Garmentabsatzvorschau:
    """Der Endpunkt, der die Beugung zu Absatz, Plateau und Sprengung liefert."""

    #: Die Regler, die hier zählen, mit ihrer Vorgabe.
    REGLER = (('heel', 0.0), ('platform', 0.0), ('toe_spring', 0.0))

    @classmethod
    def rechnen(cls, masse, heel, platform, toe_spring):
        """`Fussbeugung.beschreibung()` plus Hinweise der Fussvorgabe."""
        from GarmentCode.schuh.fussbeugung import Fussbeugung
        from GarmentCode.schuh.fussvorgabe import Fussvorgabe
        fuss = Fussvorgabe(masse)
        beugung = Fussbeugung.aus_fuss(fuss, heel, platform, toe_spring)
        return {**beugung.beschreibung(), 'hinweise': list(fuss.hinweise)}

    @staticmethod
    def _zahl(request, name, vorgabe):
        try:
            return float(request.POST.get(name) or vorgabe)
        # stumm gewollt: ein unlesbarer Reglerwert aus dem Browser faellt auf
        # die Vorgabe
        except ValueError:
            return vorgabe

    @staticmethod
    @require_POST
    def vorschau(request):
        from .garmentcode import Garmentcode
        from GarmentCode.dienst import GarmentcodeDienst
        werte = [Garmentabsatzvorschau._zahl(request, name, vorgabe)
                 for name, vorgabe in Garmentabsatzvorschau.REGLER]
        anfrage = Garmentcode.aus_anfrage(request)
        try:
            masse, _ = GarmentcodeDienst.masse(
                anfrage['geschlecht'], morphs=anfrage['morphs'],
                bauart=anfrage['bauart'], koerper=anfrage['koerper'],
                meta=anfrage['meta'])
            return JsonResponse(Garmentabsatzvorschau.rechnen(masse, *werte))
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Absatzvorschau nicht berechenbar')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
