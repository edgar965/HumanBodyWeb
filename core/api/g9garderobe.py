# -*- coding: utf-8 -*-
u"""Genesis-9-Garderobe (Daz) fuer Szene und Studio: Liste, Stuecknetz, Texturen.

    GET  /api/character/genesis9-figur/garderobe/
         {stuecke: [{id, name, art, varianten, stile, regler, vorschau,
                     zeigbar, hinweis}], anzahl}
    POST /api/character/genesis9-figur/garderobe/<kennung>/netz/
         {regler, pose, ausdruck, griffe, variante, stil, regler_stueck,
          getragen: [{kennung, stil, regler_stueck}], rang}
         {kennung, teile: [{name, vertices, faces, normals, uvs, gruppen,
                            hautgewichte, knochen}], boden, stufen,
          innen: [kennung], aussen: [kennung]}
    GET  /api/character/genesis9-figur/textur/<pfad>          Bilddatei

Bis 18.09.2026 in `g9figur.py` (das wuchs ueber 300 Zeilen). `pose` ist
die Kennung eines Daz-Posenpresets (`G9posen`): das Stueck muss auf
derselben Stellung sitzen wie der Koerper — Regler UND Knochendrehung.
`stil` (Pixie: Jaunty …; eine Kennung oder eine Liste — je Art eine:
Eirgrid `Pose 01 Back` und `Length 03 Long` drehen und skalieren die
eigenen Zopfknochen, `G9eigenknochen`) und `regler_stueck` (Viking-Shirt:
`Adj Inflate Collar`) sind die eigenen Kanaele des Stuecks. Ein PROP
(`G9requisit`) kommt an seinen Knochen (`knochen` je Teil, Haut ganz
darauf); seine Griffpose stellt die Figur ueber `griffe` (`G9figur`).
`getragen`/`rang` (19.09.2026): die anderen Stuecke in Anziehreihenfolge
und der eigene Platz — Kollision Stueck gegen Stueck (`G9lagenanfrage`).
`figurart: humanbody` mit `geschlecht, bauart, morphs, meta`: dasselbe Stueck
auf einer HumanBody-Figur (`G9kleidhumanbody`).
"""
import logging

import numpy as np
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .g9figur import G9figur, FEHLT
from .g9kleidhumanbody import G9kleidhumanbody
from ..dienste.g9antworten import G9antworten
from ..dienste.g9lagenanfrage import G9lagenanfrage
from Genesis9.garderobe import G9garderobe
from Genesis9.garderobekategorien import G9garderobekategorien
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.material import G9material
from Genesis9.netzstufe import G9netzstufe
from Genesis9.pfade import G9pfade
from Genesis9.posen import G9posen
from Genesis9.stueckfelder import G9stueckfelder

logger = logging.getLogger('core')

__all__ = ['G9garderobeapi']


class G9garderobeapi:
    u"""Lesende Endpunkte auf Kleidung, Haare und Bilder."""

    @staticmethod
    @require_GET
    def garderobe(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'stuecke': [], 'anzahl': 0, 'fehler': FEHLT})
        from .g9vorschau import G9vorschau
        # `kategorie`: die Vorgabe aus Daz' Metadaten (Oberteile, Hosen, …) —
        # Edgars eigene Zuordnung liegt darueber (`G9garderobekategorien`).
        stuecke = [dict(s, varianten=G9vorschau.varianten_mit_vorschau(s),
                        kategorie=G9garderobekategorien.vorgabe(s))
                   for s in G9garderobe.liste()]
        return JsonResponse({'stuecke': stuecke, 'anzahl': len(stuecke)})

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET', 'POST'])
    def kleidnetz(request, kennung):
        u"""Ein Stueck auf der GEFORMTEN (und posierten) Figur.

        Die Teile eines Stuecks (ein Outfit hat mehrere Netze) werden auf die
        Koerperpunkte dieser Stellung projiziert (`G9folger`); die Haut traegt
        die Knochennamen des Koerpers.
        """
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        rumpf = G9figur._rumpf(request)
        eintrag = G9garderobe.eintrag(kennung) or {}
        if rumpf.get('figurart') == G9kleidhumanbody.FIGURART:
            # Dasselbe Stueck auf einer HumanBody-Figur (19.09.2026).
            return G9antworten.liefern(
                'kleidhb', kennung, rumpf,
                lambda: G9kleidhumanbody.antwort(kennung, eintrag, rumpf), eintrag=eintrag)
        return G9antworten.liefern(
            'kleid', kennung, rumpf,
            lambda: G9garderobeapi._kleid(kennung, eintrag, rumpf), eintrag=eintrag)

    @staticmethod
    def _kleid(kennung, eintrag, rumpf):
        u"""Das Antwort-Dict eines Stuecks — oder eine Fehlerantwort."""
        formung = G9figur.formung(rumpf, {})
        # Ein Genesis-8-Schuh mit Fusspose: der Fuss der Figur stellt sich, der
        # Schuh bleibt in seiner (schon getragenen) Ruhelage (`G9autofit`).
        stueckformung = (G9figur.formung(rumpf, {}, ohne_griff=kennung)
                         if eintrag.get('fusspose') else formung)
        try:
            teile = G9garderobe.teile(kennung)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        except (OSError, KeyError) as fehler:
            logger.warning('Genesis 9: Stück %s nicht ladbar: %s', kennung, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        bilder = G9garderobe.bilder(kennung, G9figur._name(rumpf.get('variante')))
        werte, knochen = G9garderobe.stilwerte(kennung,
                                               G9figur._namen(rumpf.get('stil')))
        # Vorgaben des Presets (Angie: `HD Wrinkles` 1), darueber Stil und Regler.
        zusatz = dict(eintrag.get('vorgaben') or {})
        zusatz.update(werte)
        zusatz.update(G9garderobe.reglerwerte(kennung, rumpf.get('regler_stueck')))
        hoch = np.array([0.0, formung.boden(), 0.0])
        stufen = G9netzstufe.browser()
        koerper = G9koerpernetz(formung, stufen=stufen).koerperflaeche()
        kaefige = [folger.punkte_zu(stueckformung, zusatz, drehung=knochen, lage=lage) - hoch
                   for folger, lage in teile]
        # Stueck gegen Stueck (19.09.2026): Haut plus die getragenen Stuecke
        # DARUNTER als Kollisionsflaeche; was darueber liegt, holt der Browser neu.
        koerper, innen, aussen = G9lagenanfrage(rumpf, formung, koerper).vorbereiten(
            kennung, [(f, p) for (f, _lage), p in zip(teile, kaefige)])
        antwort_teile = []
        for (folger, lage), punkte in zip(teile, kaefige):
            hd_werte = dict(formung.morphwerte())
            hd_werte.update(zusatz)
            # Laenge/Weite verschieben den Kaefig am Koerper entlang — die Haut
            # muss von dort kommen, nicht aus der Ruhelage (20.09.2026).
            passform = (folger.passformhaut(zusatz)
                        if G9stueckfelder.folgt(folger, lage) else None)
            netz = G9koerpernetz.folgernetz(folger, punkte, bilder, stufen,
                                            koerper=koerper, werte=hd_werte,
                                            passform=passform)
            if lage is not None:
                # Ein Prop haengt ganz an seinem Knochen (`G9requisit.haut`).
                netz['haut'] = lage.haut(len(netz['punkte'])).fuer()
            teil = G9figur._netzantwort(netz)
            teil['name'] = folger.name
            teil['stufen'] = netz['stufen']
            teil['knochen'] = lage.knochen if lage is not None else None
            antwort_teile.append(teil)
        return {'kennung': kennung, 'teile': antwort_teile,
                'boden': round(hoch[1], 4), 'stufen': stufen,
                'innen': innen, 'aussen': aussen,
                # Die Art entscheidet im Browser, ob die Haut darunter
                # ausgeblendet wird (`Hautverdeckung`, nur `kleidung`).
                'art': eintrag.get('art')}

    # -------------------------------------------------------------- Texturen

    @staticmethod
    @require_GET
    def textur(request, pfad):
        u"""Ein Bild aus `Runtime/Textures` der Bibliothek oder der Schminke-
        Ablage (`schminke/<hash>_f.jpg`, `G9ebenen`) — sonst 404."""
        datei = G9material.datei(pfad)
        art = G9material.bildart(pfad)
        if datei is None or not art:
            return HttpResponseNotFound('Texture not found')
        return FileResponse(open(datei, 'rb'), content_type=art)

    # ---------------------------------------------------------------- Posen

    @staticmethod
    @require_GET
    def posen(request):
        u"""`{posen: [{gruppe, eintraege}], ausdruecke: [...], formen: [...]}`
        (`G9posen`; `formen` = Formpresets mit ihren Reglern, 18.09.2026)."""
        if not G9pfade.vorhanden():
            return JsonResponse({'posen': [], 'ausdruecke': [], 'formen': [],
                                 'fehler': FEHLT})
        return JsonResponse({'posen': G9posen.liste('pose'),
                             'ausdruecke': G9posen.liste('ausdruck'),
                             'formen': G9posen.liste('form')})
