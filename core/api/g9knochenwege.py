# -*- coding: utf-8 -*-
u"""Knochenwege — wie sich jeder Genesis-9-Knochen von einer Stellung zur nächsten bewegt.

    POST /api/character/genesis9-figur/<name>/knochenwege/
         {alt: Rumpf, neu: Rumpf}   (Rumpf wie bei `…/netz/`: regler, pose, ausdruck, griffe, drehung …)
         -> {wege: {knochen: [16 Zahlen]}}   4×4 spaltenweise (wie Three.js), Browser-Meter

WARUM (Edgar, 17.10.2026: „posen dauern irrsinnig lange, das sollte doch in 1 s gehen" — dann
„mach erst … Sofortschau"): Eine Daz-Pose baut Körper und jedes Stück neu. Mit fünf Stücken stand
die genaue Figur nach rund 10 s, der neue Körper nach 1,4–4,4 s — sein Neubau im Browser (Netz,
Materialien) kostet allein Sekunden. Für eine Vorschau braucht der Browser nur, wie sich jeder
Knochen bewegt: Er dreht damit das VORHANDENE Skelett (`Genesis9posenvorschau`), Körper, Kleidung und
Haar folgen über ihre Haut, ohne Neubau. Die Bewegung ist `neu · alt⁻¹` der Daz-Knochenmatrizen
(`G9knochenmatrizen`, mit Verdrehung) — genauer als die Knochenachsen des Browsers, die aus den
Gelenken hergeleitet sind (`Gelenkskelett.bauplan`).

Beide Stellungen kommen über `G9figur.formung`, also über `G9formung.gemerkt`: Der Neubau, der gleich
danach dieselbe neue Stellung anfragt, findet sie fertig vor — der Server rechnet nichts doppelt.

Einheiten: Daz rechnet in Zentimetern, das Netz im Browser in Metern und um `boden` gesenkt
(`G9koerpernetz`: Punkte minus `[0, boden, 0]`). Je Stellung also `T(−boden) · M_m`; die Bewegung
dazwischen bildet einen alten Browserpunkt auf den neuen ab.
"""
import logging

import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.pfade import G9pfade

from .g9figur import FEHLT, G9figur

logger = logging.getLogger('core')

__all__ = ['G9knochenwegeapi']


class G9knochenwegeapi:
    u"""`wege` — Endpunkt; `lagen`/`wege_zwischen` — die Rechnung, ohne Anfrage prüfbar."""

    CM = 0.01

    @staticmethod
    @csrf_exempt
    @require_POST
    def wege(request, name):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        eintrag = G9figur._eintrag(name)
        if eintrag is None:
            return JsonResponse({'fehler': u'Unbekannte Genesis-9-Figur'}, status=404)
        rumpf = G9figur._rumpf(request)
        alt, neu = rumpf.get('alt'), rumpf.get('neu')
        if not isinstance(alt, dict) or not isinstance(neu, dict):
            return JsonResponse({'fehler': u'alt und neu fehlen'}, status=400)
        try:
            wege = G9knochenwegeapi.wege_zwischen(G9figur.formung(alt, eintrag),
                                                  G9figur.formung(neu, eintrag))
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Genesis 9: Knochenwege nicht rechenbar: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        return JsonResponse({'wege': {k: G9knochenwegeapi._spaltenweise(m) for k, m in wege.items()}})

    @classmethod
    def lagen(cls, formung):
        u"""`{knoten: 4×4}` einer Stellung in Browser-Metern: Daz-Matrix (cm) in Meter, Boden abgezogen."""
        boden = formung.boden()
        aus = {}
        for name, matrix in formung.matrizen().matrizen().items():
            lage = np.array(matrix, dtype=np.float64)
            lage[:3, 3] *= cls.CM
            lage[1, 3] -= boden
            aus[name] = lage
        return aus

    @classmethod
    def wege_zwischen(cls, alt, neu):
        u"""`{knoten: 4×4}` mit `neu · alt⁻¹` — bildet einen Punkt der alten Stellung auf die neue ab."""
        lagen_alt, lagen_neu = cls.lagen(alt), cls.lagen(neu)
        return {name: lage @ np.linalg.inv(lagen_alt[name])
                for name, lage in lagen_neu.items() if name in lagen_alt}

    @staticmethod
    def _spaltenweise(matrix):
        return [round(float(v), 7) for v in np.asarray(matrix).T.ravel()]
