# -*- coding: utf-8 -*-
"""Absatz — was der Betrachter über einen gebauten Schuh wissen muss.

    GET /api/garmentcode/absatz/?stueck=pumps
      -> {stueck, name, absatz_cm, plateau_cm, winkel_grad, hebung_cm}

WARUM EIN EIGENER ENDPUNKT (11.09.2026, Edgar: „mach das: Absatz/Plateau
braucht einen gebeugten Fuss"): Ein Schuh mit Absatz wird auf dem
gebeugten Fuss simuliert und in der Ruhelage an die Figur gebunden
(`schuh/absatzdrapierung.py`). Damit er im Betrachter richtig sitzt, muss
die Figur auf den Absatz gestellt werden — Fuss und Zehen um den
Beugewinkel gedreht, die Figur um die Hebung angehoben. Diese Zahlen
stehen im `schuh`-Block der Spezifikation (`Schuhentwurf.vermerken`);
`garmentcode_absatz.js` holt sie hier, sobald ein Stück angezogen ist.
Die Rig-Datei des Stücks schreibt eine Datei der parallelen Sitzung
(`anziehen.py`) — sie bleibt unangetastet.

Gesucht wird der JÜNGSTE Ergebnisordner des Stücks: `erzeugen` nennt ihn
`<vorlage>_<geschlecht>` (`GarmentcodeDienst.erzeugen`), ein Probelauf
`probe_<vorlage>`; der Betrachter kennt nur die Vorlage.
"""
import logging
import os
import re

from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger('core')

__all__ = ['Garmentabsatz']


class Garmentabsatz:
    """Der Endpunkt, der die Fussbeugung eines gebauten Schuhs liefert."""

    #: Der Ergebnisordner der Schnitte — änderbar für Tests.
    AUSGABE = None
    #: Was der Betrachter braucht, mit Vorgabe für einen flachen Schuh.
    FELDER = (('absatz_cm', 0.0), ('plateau_cm', 0.0), ('winkel_grad', 0.0),
              ('hebung_cm', 0.0))

    @classmethod
    def ausgabe(cls):
        if cls.AUSGABE:
            return cls.AUSGABE
        from GarmentCode.entwurf import Entwurf
        return os.path.join(os.path.dirname(Entwurf.REPO), 'ausgabe')

    @classmethod
    def ordner(cls, stueck):
        """Der jüngste Ergebnisordner zu diesem Stück, oder None."""
        wurzel = cls.ausgabe()
        if not os.path.isdir(wurzel):
            return None
        muster = re.compile(r'^(probe_)?%s(_[a-z]+)?$' % re.escape(stueck))
        treffer = [os.path.join(wurzel, d) for d in os.listdir(wurzel)
                   if muster.match(d)
                   and os.path.isdir(os.path.join(wurzel, d))]
        if not treffer:
            return None
        return max(treffer, key=os.path.getmtime)

    @classmethod
    def lesen(cls, stueck):
        """{stueck, name, absatz_cm, ...} — flach, wenn nichts gebaut ist."""
        from GarmentCode.schuh.schuhentwurf import Schuhentwurf
        antwort = {'stueck': stueck, 'name': ''}
        antwort.update(dict(cls.FELDER))
        ordner = cls.ordner(stueck)
        if not ordner:
            return antwort
        name = os.path.basename(ordner)
        vermerk = Schuhentwurf.vermerk(
            os.path.join(ordner, '%s_specification.json' % name))
        antwort['name'] = name
        for feld, vorgabe in cls.FELDER:
            antwort[feld] = float(vermerk.get(feld) or vorgabe)
        return antwort

    @staticmethod
    @require_GET
    def absatz(request):
        stueck = (request.GET.get('stueck') or '').strip()
        if not re.match(r'^[a-z0-9_-]+$', stueck):
            return JsonResponse({'fehler': 'Kein Kleidungsstück angegeben'},
                                status=400)
        try:
            return JsonResponse(Garmentabsatz.lesen(stueck))
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Absatz für %s nicht lesbar', stueck)
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
