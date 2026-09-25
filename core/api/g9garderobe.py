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

from asgiref.sync import sync_to_async
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .g9figur import G9figur, FEHLT
from .g9kleidhumanbody import G9kleidhumanbody
from ..dienste.g9antworten import G9antworten
from ..dienste.g9stueckteile import G9stueckteile
from Genesis9.garderobe import G9garderobe
from Genesis9.garderobekategorien import G9garderobekategorien
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.material import G9material
from Genesis9.netzstufe import G9netzstufe
from Genesis9.pfade import G9pfade
from Genesis9.posen import G9posen

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
    async def kleidnetz(request, kennung):
        u"""Ein Stueck auf der GEFORMTEN (und posierten) Figur.

        Die Teile eines Stuecks (ein Outfit hat mehrere Netze) werden auf die
        Koerperpunkte dieser Stellung projiziert (`G9folger`); die Haut traegt
        die Knochennamen des Koerpers.

        ASYNC (23.09.2026, Edgar: „ladezeit ... mehr als 30 s"): eine Figur mit
        Outfit fragt mehrere Stuecke GLEICHZEITIG ab (hier: Haar, Jeans, Schuhe,
        Shirt). Als plain-sync View liefen alle vier nacheinander auf Daphnes
        einem geteilten `thread_sensitive`-Faden — Log zeigte 25,7/27,0/27,2/
        28,7 s je Anfrage fuer dieselbe Seite, die vorher (vor der Umstellung von
        `retarget.py`/`bildmodell.zustand` auf async) schon einmal als dieselbe
        Fehlerklasse gefunden wurde. Nur die schwere Rechnung (`G9antworten.
        liefern`, mit ihrem `threading.Event().wait`) geht auf einen eigenen
        Thread — `request` bleibt synchron, VOR dem `await` gelesen.
        """
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        rumpf = G9figur._rumpf(request)
        eintrag = G9garderobe.eintrag(kennung) or {}
        if rumpf.get('figurart') == G9kleidhumanbody.FIGURART:
            # Dasselbe Stueck auf einer HumanBody-Figur (19.09.2026).
            bauen = lambda: G9kleidhumanbody.antwort(kennung, eintrag, rumpf)
            art = 'kleidhb'
        else:
            bauen = lambda: G9garderobeapi._kleid(kennung, eintrag, rumpf)
            art = 'kleid'
        return await sync_to_async(G9antworten.liefern, thread_sensitive=False)(
            art, kennung, rumpf, bauen, eintrag=eintrag)

    @staticmethod
    def _kleid(kennung, eintrag, rumpf):
        u"""Das Antwort-Dict eines Stuecks — oder eine Fehlerantwort."""
        formung = G9figur.formung(rumpf, {})
        # Ein Genesis-8-Schuh mit Fusspose: der Fuss der Figur stellt sich, der
        # Schuh bleibt in seiner (schon getragenen) Ruhelage (`G9autofit`).
        stueckformung = (G9figur.formung(rumpf, {}, ohne_griff=kennung)
                         if eintrag.get('fusspose') else formung)
        stufen = G9netzstufe.browser()
        koerpernetz = G9koerpernetz(formung, stufen=stufen)
        # Oberflaechenbindung (21.09.2026, Konzept Fitting): nur Kleidung, gegen
        # den REINEN Koerper — die Lagenflaeche traegt die Stuecke darunter,
        # deren Indizes gibt es im Browser nicht.
        bindung = koerpernetz.bindungsflaeche() if eintrag.get('art') == 'kleidung' else None
        # Die Rechnung selbst teilt sich die Antwort seit 24.09.2026 mit dem
        # GarmentCode-Bau auf Genesis 9 (`G9stueckteile`); GarmentCode-Stuecke
        # der Figur liegen mit in der Lagenrechnung (`gc_getragen`).
        try:
            # Die Bilder erst hier: wie vorher erst nach `teile` — eine
            # unbekannte Kennung bleibt eine 404, keine 500.
            teile = G9garderobe.teile(kennung)
            bilder = G9garderobe.bilder(kennung, G9figur._name(rumpf.get('variante')))
            netze, innen, aussen, hoch = G9stueckteile.netze(
                kennung, eintrag, rumpf, formung, koerpernetz.koerperflaeche(), stufen,
                bilder=bilder, stueckformung=stueckformung, bindung=bindung,
                gc_vorrat=rumpf.get('gc_getragen'), teile=teile)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        except (OSError, KeyError) as fehler:
            logger.warning('Genesis 9: Stück %s nicht ladbar: %s', kennung, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        antwort_teile = []
        for folger, lage, netz in netze:
            if lage is not None:
                # Ein Prop haengt ganz an seinem Knochen (`G9requisit.haut`).
                netz['haut'] = lage.haut(len(netz['punkte'])).fuer()
            teil = G9figur._netzantwort(netz)
            teil['name'] = folger.name
            teil['stufen'] = netz['stufen']
            teil['knochen'] = lage.knochen if lage is not None else None
            # Eigene Stücke (GC, MakeHuman, OBJ) sind EINE Stofffläche wie die live
            # gebauten (`stoffabruf.js`: DoubleSide) — an Aufschlag, Falte und offenem
            # Schaft sieht man die Innenseite; nur von vorn gezeichnet stand dort ein
            # Loch (25.09.2026, `ProjektTemp/gcstuecke/durchsicht.py`: Socken, Stiefel,
            # Achseln; 2–14 % der hautnahen Flächen zeigen zur Haut).
            teil['zweiseitig'] = bool(eintrag.get('eigen'))
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
