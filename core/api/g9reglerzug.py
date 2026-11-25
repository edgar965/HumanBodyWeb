# -*- coding: utf-8 -*-
u"""G9reglerzugapi — das Feld eines Reglerzugs auf den Browserpunkten einer stehenden Genesis-9-Figur (25.11.2026).

    POST /api/character/genesis9-figur/<name>/reglerzug/
         {rumpf: Rumpf wie bei `…/netz/` (die Stellung, in der die Figur STEHT), kanal, von, bis,
          teil: 'koerper' | 'rest' (Anhänge und Stücke) | '' (beides) | 'wecken' (nur die Stellung rechnen und merken), stuecke: [{kennung, stil, regler_stueck}]}
         -> {stufen, kanal, von, bis, koerper: Feld|null, anhaenge: {schluessel: Feld}, stuecke: {kennung: [Feld|null je Teil]}}

    alter_aussehen: das Aussehen am Ende des Zugs (Falten, graues Haar); ruhig: Knochen und Boden stehen wie vorher; genau: Körper und Anhänge brauchen keinen genauen Zug (`G9reglerzugfeld.genau`); wechsel: {morph: Wert nach − vor dem Zug}
    POST /api/character/genesis9-figur/garderobe/<kennung>/reglerzug/
         {rumpf: Rumpf wie bei `…/garderobe/<kennung>/netz/`, kanal, von, bis}   -> {teile: [Feld je Teil]}   (ein Regler des Stücks, `G9stueckzugfeld`)

    Feld = null (nicht berührt), {offen: true} (berührt, Lage erst im genauen Zug) oder {n: Punktnummern (uint32; null = alle Punkte der Reihe nach), d: Verschiebungen (float32, Meter), punkte: Punktzahl des Netzes}

Edgar, 25.11.2026: „alle regler unter 0,2 s“. Der Browser summiert das Feld mit dem Reglerwert auf das stehende Netz (`gemeinsam/genesis9reglerfeld.js`), der genaue Zug über
`…/netz/` folgt danach. Nichts wird abgelegt. `von`/`bis` sind die Werte des Kanals; gerechnet wird zwischen den zwei Stellungen (`G9reglerzugfeld`).

ASYNC MIT EIGENEM FADEN: Synchrone Ansichten teilen sich EINEN Faden (`thread_sensitive`), dahinter wartete der Reglerzug auf jede andere Anfrage der Seite.
"""
import json
import logging
from collections import OrderedDict
from urllib.parse import unquote

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.alter import G9alter
from Genesis9.formung import G9formung
from Genesis9.formungsfolge import G9formungsfolge
from Genesis9.formungswerte import G9formungswerte
from Genesis9.garderobe import G9garderobe
from Genesis9.netzstufe import G9netzstufe
from Genesis9.pfade import G9pfade
from Genesis9.reglerzugfeld import G9reglerzugfeld
from Genesis9.stueckzugfeld import G9stueckzugfeld

from ..daten.netzantwort import Netzantwort
from ..daten.netzausgabe import Netzausgabe
from ..dienste.g9lagenanfrage import G9lagenanfrage
from .g9figur import FEHLT, G9figur

logger = logging.getLogger('core')

__all__ = ['G9reglerzugapi']


class G9reglerzugapi:
    u"""`feld` — Endpunkt; `rechnen` — die Rechnung, ohne Anfrage prüfbar."""

    #: Mehr getragene Stücke rechnet die Sofortschau nicht (wie `G9lagenanfrage.HOECHSTENS`).
    HOECHSTENS = 24
    #: Die letzten Züge (Schlüssel → `G9reglerzugfeld`): der Browser fragt nach dem Körper gleich den Rest desselben Zugs.
    ZUEGE_MAX = 6
    _zuege = OrderedDict()

    @staticmethod
    @csrf_exempt
    @require_POST
    async def feld(request, name):
        return await sync_to_async(G9reglerzugapi._antwort, thread_sensitive=False)(request, name)

    @staticmethod
    @csrf_exempt
    @require_POST
    async def stueck(request, kennung):
        return await sync_to_async(G9reglerzugapi._stueckantwort, thread_sensitive=False)(request, kennung)

    @staticmethod
    def _stueckantwort(request, kennung):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        auftrag = G9figur._rumpf(request)
        rumpf, kanal = auftrag.get('rumpf'), str(auftrag.get('kanal') or '')
        stuecke = G9reglerzugapi._stuecke([dict(rumpf, kennung=kennung)]) if isinstance(rumpf, dict) else []
        try:
            von, bis = float(auftrag.get('von')), float(auftrag.get('bis'))
        except (TypeError, ValueError):
            return JsonResponse({'fehler': u'von und bis fehlen'}, status=400)
        if not stuecke or not kanal:
            return JsonResponse({'fehler': u'Stück oder Regler fehlt'}, status=404)
        kennung, eintrag, werte = stuecke[0]
        try:
            felder = G9stueckzugfeld.rechnen(G9figur.formung(rumpf, {}), kennung, eintrag, werte['stil'], *(dict(werte['regler_stueck'] or {}, **{kanal: w}) for w in (von, bis)),
                                             stufen=G9netzstufe.browser())
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Genesis 9: Stückregler %s %s nicht rechenbar: %s', kennung, kanal, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        return Netzausgabe.antwort({'kennung': kennung, 'kanal': kanal, 'teile': [G9reglerzugapi.paar(f) for f in felder]}, request)

    @staticmethod
    def _antwort(request, name):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        eintrag = G9figur._eintrag(name)
        if eintrag is None:
            return JsonResponse({'fehler': u'Unbekannte Genesis-9-Figur'}, status=404)
        auftrag = G9figur._rumpf(request)
        rumpf, kanal = auftrag.get('rumpf'), str(auftrag.get('kanal') or '')
        if auftrag.get('teil') == 'wecken' and isinstance(rumpf, dict):
            G9reglerzugfeld.wecken(G9figur.formung(rumpf, eintrag), G9figur._name(rumpf.get('brauenstil')) or eintrag.get('brauenstil') or None, eintrag.get('anhangsatz'),
                                   G9reglerzugapi._stuecke(auftrag.get('stuecke')))
            return JsonResponse({'ok': True})
        try:
            von, bis = float(auftrag.get('von')), float(auftrag.get('bis'))
        except (TypeError, ValueError):
            return JsonResponse({'fehler': u'von und bis fehlen'}, status=400)
        if not isinstance(rumpf, dict) or not kanal or von == bis:
            return JsonResponse({'fehler': u'rumpf, kanal oder Weg fehlt'}, status=400)
        try:
            aus = G9reglerzugapi.rechnen(rumpf, eintrag, kanal, von, bis, str(auftrag.get('teil') or ''), auftrag.get('stuecke'))
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Genesis 9: Reglerzug %s nicht rechenbar: %s', kanal, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        return Netzausgabe.antwort(aus, request)

    @classmethod
    def rechnen(cls, rumpf, eintrag, kanal, von, bis, teil='', stuecke=None):
        regler, drehung = G9figur.stellung(rumpf, eintrag)
        alt = G9formung.aus_abfrage(cls._mit(regler, kanal, von), drehung)
        werte = G9formungswerte.begrenzt(cls._mit(regler, kanal, bis))
        feld = cls._zug(alt, kanal, werte)
        genau = teil != 'rest' and feld.genau(lambda anteil: G9formungsfolge(G9formungswerte.begrenzt(cls._mit(regler, kanal, von + anteil * (werte.get(kanal, bis) - von))), alt))
        # Auf die Grenzen des Kanals zurückgenommen? Dann gilt der Weg bis dorthin (ein Alias-Kanal steht unter dem Namen seines Ziels: der verlangte).
        bis = werte.get(kanal, bis)
        aus = feld.rechnen(brauenstil=G9figur._name(rumpf.get('brauenstil')) or eintrag.get('brauenstil') or None, satz=eintrag.get('anhangsatz'),
                           stuecke=cls._stuecke(stuecke), koerper=teil != 'rest', rest=teil != 'koerper')
        return {'stufen': aus['stufen'], 'kanal': kanal, 'von': von, 'bis': bis, 'ruhig': feld.ruhig, 'genau': genau, 'alter_aussehen': round(float(feld.neu.alter_aussehen), 4),
                'wechsel': feld.neu.morphwechsel() if genau else {}, 'koerper': cls.paar(aus['koerper']),
                'anhaenge': {s: cls.paar(f) for s, f in aus['anhaenge'].items()},
                'stuecke': {s: [cls.paar(f) for f in felder] for s, felder in aus['stuecke'].items()}}

    @classmethod
    def aufwaermen(cls):
        u"""Nach dem Serverstart ein Zug an der zuletzt gezeigten Figur (`G9neustartnachlauf.auswahl`): ihre Stellung, die Nachbarn ihrer Anhänge und Stücke und die Formelverweise stehen
        dann — der erste Zug im frischen Prozess brauchte sonst 0,8 statt 0,1 s."""
        from ..dienste.g9neustartnachlauf import G9neustartnachlauf
        for e in G9neustartnachlauf.auswahl():
            teile = [t for t in e['pfad'].split('/') if t]
            if len(teile) < 2 or teile[-1] != 'netz' or 'garderobe' in teile:
                continue
            rumpf, eintrag = json.loads(e['rumpf'] or '{}'), G9figur._eintrag(unquote(teile[-2]))
            kanal = next((k for k, w in (rumpf.get('regler') or {}).items() if isinstance(w, (int, float)) and abs(w) > 0.01), None)
            if eintrag is not None and kanal is not None:
                G9reglerzugfeld.wecken(G9figur.formung(rumpf, eintrag), G9figur._name(rumpf.get('brauenstil')) or None, eintrag.get('anhangsatz'), cls._stuecke(rumpf.get('kleidung')))
                wert = float(rumpf['regler'][kanal])
                cls.rechnen(rumpf, eintrag, kanal, wert, 0.5 * wert, stuecke=rumpf.get('kleidung'))
                cls.rechnen(rumpf, eintrag, G9alter.NAME, 0.0, 0.3, stuecke=rumpf.get('kleidung'))
                return

    @classmethod
    def _zug(cls, alt, kanal, werte):
        schluessel = (alt.fingerabdruck(), kanal, werte.get(kanal), G9netzstufe.browser())
        feld = cls._zuege.get(schluessel)
        if feld is None or feld.alt is not alt:
            feld = cls._zuege[schluessel] = G9reglerzugfeld(alt, G9formungsfolge(werte, alt))
            while len(cls._zuege) > cls.ZUEGE_MAX:
                cls._zuege.popitem(last=False)
        return feld

    @staticmethod
    def _mit(regler, kanal, wert):
        aus = dict(regler)
        if abs(wert) < 1e-9:
            aus.pop(kanal, None)
        else:
            aus[kanal] = wert
        return aus

    @classmethod
    def _stuecke(cls, roh):
        u"""`[(kennung, eintrag, {stil, regler_stueck})]` der Stücke, die ein Garderobeneintrag trägt — die generischen Einträge (Haar, Kleidung) mischen und warten auf den genauen Zug."""
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.kleidgenerisch import G9kleidgenerisch
        aus = []
        for e in [e for e in (roh or []) if isinstance(e, dict)][:cls.HOECHSTENS]:
            kennung = G9figur._name(e.get('kennung'))
            if not kennung or G9haargenerisch.ist_generisch(kennung) or G9kleidgenerisch.ist_generisch(kennung):
                continue
            eintrag = G9garderobe.eintrag(kennung)
            if eintrag is None or not eintrag.get('zeigbar'):
                continue
            aus.append((kennung, eintrag, {'stil': G9lagenanfrage._namen(e.get('stil')), 'regler_stueck': e.get('regler_stueck')}))
        return aus

    @staticmethod
    def paar(feld):
        if feld is None:
            return None
        if feld == G9reglerzugfeld.OFFEN:
            return {'offen': True}
        nummern, deltas, punkte = feld
        return {'n': Netzantwort.feld(nummern, 'n', typ='uint32', genau=True) if len(nummern) < punkte else None, 'd': Netzantwort.feld(deltas, 'd'), 'punkte': punkte}
