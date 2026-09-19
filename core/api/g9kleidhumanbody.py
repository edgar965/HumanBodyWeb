# -*- coding: utf-8 -*-
u"""G9kleidhumanbody — die Antwort eines Daz-Stuecks fuer eine HumanBody-Figur.

Derselbe Endpunkt wie fuer Genesis 9 (`G9garderobeapi.kleidnetz`), mit
`figurart: humanbody` und der Figur im Rumpf (`geschlecht`, `bauart`,
`morphs`, `meta` — wie der GarmentCode-Reiter sie schickt). Die Uebertragung
selbst steht in `core/dienste/g9aufhumanbody.py`; hier nur, was die Antwort
in dieselbe Form bringt wie `_kleid`: je Teil Netz, Gruppen mit Bildern und
`hautgewichte` — mit DEF-Knochennamen, damit der Browser das Stueck an das
Rigify-Skelett bindet (`scene/genesis9/dazkleidung.js`).
"""
import logging

import numpy as np
from django.http import JsonResponse

from .g9figur import G9figur
from .g9netzantwort import G9netzantwort
from ..dienste.g9aufhumanbody import G9aufhumanbody
from ..dienste.g9hbfusspose import G9hbfusspose
from ..dienste.g9hbteilhaut import G9hbteilhaut
from Genesis9.formung import G9formung
from Genesis9.garderobe import G9garderobe
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.netzstufe import G9netzstufe
from Genesis9.teilbindung import G9teilbindung

logger = logging.getLogger('core')

__all__ = ['G9kleidhumanbody']


class G9kleidhumanbody:
    u"""`antwort(kennung, eintrag, rumpf)` -> Antwort-Dict oder Fehlerantwort."""

    FIGURART = 'humanbody'
    NICHT_TRAGBAR = 'Requisiten hängen an Daz-Knochen — auf HumanBody nicht tragbar'
    KEIN_NETZ = 'Stranghaar ohne Flächen — auf HumanBody nicht tragbar'
    #: Mindestabstand des Kaefigs zur HumanBody-Haut, Meter. Die Haut wird im
    #: Browser um bis zu 5 mm verschoben (`Hauttextur.VERSCHIEBUNG` 0,01 mit
    #: Mitte 0,5 — MB-Labs Displace-Modifier); mit dem 1 mm von `G9kollision`
    #: stand die Brust durch das Hemd (gemessen 19.09.2026: Apex 2,5 mm).
    HAUTABSTAND = 0.006

    @classmethod
    def antwort(cls, kennung, eintrag, rumpf):
        try:
            teile = G9garderobe.teile(kennung)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        except (OSError, KeyError) as fehler:
            logger.warning('Genesis 9: Stück %s nicht ladbar: %s', kennung, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        if any(lage is not None for _folger, lage in teile):
            return JsonResponse({'fehler': cls.NICHT_TRAGBAR}, status=400)
        teile = [(f, lage) for f, lage in teile if getattr(f, 'ART', None) != 'strang']
        if not teile:
            return JsonResponse({'fehler': cls.KEIN_NETZ}, status=400)
        try:
            traeger = G9aufhumanbody(rumpf.get('geschlecht'), rumpf.get('bauart'),
                                     cls._woerterbuch(rumpf.get('morphs')),
                                     cls._woerterbuch(rumpf.get('meta')))
            koerper = traeger.koerperflaeche()
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        formung = G9formung({})
        bilder = G9garderobe.bilder(kennung, G9figur._name(rumpf.get('variante')))
        werte, knochen = G9garderobe.stilwerte(kennung, G9figur._namen(rumpf.get('stil')))
        zusatz = dict(eintrag.get('vorgaben') or {})
        zusatz.update(werte)
        zusatz.update(G9garderobe.reglerwerte(kennung, rumpf.get('regler_stueck')))
        hoch = np.array([0.0, formung.boden(), 0.0])
        stufen = G9netzstufe.browser()
        kaefige = []
        for folger, _lage in teile:
            kaefig = traeger.uebertragen(
                folger.punkte_zu(formung, zusatz, drehung=knochen, lage=None) - hoch)
            if getattr(folger, 'koerperhaut', False):
                kaefig = traeger.hinaus(kaefig, cls.HAUTABSTAND)
            kaefige.append(kaefig)
        # Ein Schuh mit Fusspose: die Figur bekommt den Absatz, das Stueck geht
        # in die Ruhelage, damit der Fuss es beim Beugen mitnimmt (`G9hbfusspose`).
        absatz = G9hbfusspose.absatz(kennung, kaefige)
        antwort_teile = []
        for (folger, _lage), kaefig in zip(teile, kaefige):
            if absatz:
                kaefig = G9hbfusspose.ruhelage(kaefig, traeger.haut(kaefig), absatz, traeger.geschlecht)
            netz = G9koerpernetz.folgernetz(folger, kaefig, bilder, stufen, koerper=koerper)
            if getattr(folger, 'koerperhaut', False):
                # Auch die UNTERTEILTEN Punkte: Wo der Kaefig eine vorstehende Brust
                # umspannt, schneidet die Flaeche dazwischen bis 16 mm tief hinein.
                netz['punkte'] = traeger.hinaus(netz['punkte'], cls.HAUTABSTAND)
                netz['normalen'] = folger.netzstufe(stufen).normalen(kaefig, netz['punkte'])
            # Im Koerperteil der Daz-Bindung — die Hand neben dem Rock traegt ihn nicht.
            netz['haut'] = G9hbteilhaut.fuer(traeger.figur()).haut(
                netz['punkte'], G9teilbindung.stueck(folger, kaefig, netz['punkte']))
            teil = G9netzantwort.aus(netz)
            teil['name'] = folger.name
            teil['stufen'] = netz['stufen']
            teil['knochen'] = None
            antwort_teile.append(teil)
        logger.info('Daz auf HumanBody: %s — %d Teile, %d Punkte%s', kennung, len(antwort_teile),
                    sum(int(t.get('vertex_count') or 0) for t in antwort_teile),
                    ', Absatz %s' % absatz if absatz else '')
        return {'kennung': kennung, 'teile': antwort_teile, 'boden': 0.0, 'stufen': stufen,
                'figurart': cls.FIGURART, 'innen': [], 'aussen': [], 'absatz': absatz}

    @staticmethod
    def _woerterbuch(wert):
        return {str(k): v for k, v in wert.items()} if isinstance(wert, dict) else {}
