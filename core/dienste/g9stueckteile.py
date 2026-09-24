# -*- coding: utf-8 -*-
u"""G9stueckteile — ein Daz-Stueck auf der geformten Figur: Kaefige, Lagen, Browsernetze.

HERAUSGELOEST AM 24.09.2026 aus `G9garderobeapi._kleid`, als der zweite Nutzer
dazukam: GarmentCode auf Genesis 9 (Edgar: „GarmentCode Pants Harem zieht die
Kleider bei Genesis nicht ueber existierende Genesis-Kleider hoch"). Der Bau
eines GarmentCode-Stuecks kannte die getragenen Daz-Stuecke nicht — die
Nacharbeit legte die Harem Pants auf 2 mm an die HAUT (Bau 24.09. 15:05:
Median 2,0 mm), die Jeans steht dort 7 mm ueber der Haut. Jetzt bekommt die
Nacharbeit die fertigen Netze der getragenen Stuecke (`getragene`), gerechnet
auf genau demselben Weg wie die Antwort an den Browser (`netze`).

    netze(kennung, eintrag, rumpf, formung, …)  -> (Teile, innen, aussen, hoch)
    getragene(formung, eintraege)               -> [(kennung, Punkte (N, 3))]

Die Punkte liegen wie im Browser: Meter, Y oben, Fuesse auf dem Boden.
"""
import logging

import numpy as np
from Genesis9.garderobe import G9garderobe
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.netzstufe import G9netzstufe
from Genesis9.stoffhuelle import G9stoffhuelle
from Genesis9.stueckfelder import G9stueckfelder

from .g9lagenanfrage import G9lagenanfrage

logger = logging.getLogger('core')

__all__ = ['G9stueckteile']


class G9stueckteile:
    u"""Die Rechnung hinter einer Stueckantwort, fuer Browser und GarmentCode."""

    #: Nur diese Art zaehlt als Stoff, ueber den ein GarmentCode-Stueck gebaut
    #: wird — kein Haar, kein Requisit (wie `Hautverdeckung.stoffe`).
    ART = 'kleidung'

    @staticmethod
    def zusatz(kennung, eintrag, stile, regler_stueck):
        u"""(Werte, Knochendrehung): Vorgaben des Presets, darueber Stil und Regler."""
        werte, knochen = G9garderobe.stilwerte(kennung, stile)
        zusatz = dict(eintrag.get('vorgaben') or {})
        zusatz.update(werte)
        zusatz.update(G9garderobe.reglerwerte(kennung, regler_stueck))
        return zusatz, knochen

    @classmethod
    def netze(cls, kennung, eintrag, rumpf, formung, koerper, stufen, bilder=None,
              stueckformung=None, bindung=None, gc_vorrat=None, teile=None):
        u"""`([(folger, lage, netz)], innen, aussen, hoch)` — ein Stueck ueber
        den getragenen darunter gehoben (`G9lagenanfrage`), je Teil das Netz
        aus `G9koerpernetz.folgernetz`. `teile`: schon gelesen (sonst hier);
        ValueError/OSError/KeyError von `G9garderobe.teile` gehen an den
        Aufrufer. `gc_vorrat`: getragene GarmentCode-Stuecke (`gc_getragen`)."""
        stueckformung = stueckformung or formung
        teile = teile if teile is not None else G9garderobe.teile(kennung)
        zusatz, knochen = cls.zusatz(kennung, eintrag,
                                     G9lagenanfrage._namen(rumpf.get('stil')),
                                     rumpf.get('regler_stueck'))
        hoch = np.array([0.0, formung.boden(), 0.0])
        kaefige = [folger.punkte_zu(stueckformung, zusatz, drehung=knochen, lage=lage) - hoch
                   for folger, lage in teile]
        # Stueck gegen Stueck (19.09.2026): Haut plus die getragenen Stuecke
        # DARUNTER als Kollisionsflaeche; was darueber liegt, holt der Browser neu.
        anfrage = G9lagenanfrage(rumpf, formung, koerper, gc=gc_vorrat)
        flaeche, innen, aussen = anfrage.vorbereiten(
            kennung, [(f, p) for (f, _lage), p in zip(teile, kaefige, strict=True)])
        # GarmentCode-Stuecke darunter zuletzt als echte Flaeche (`G9stoffhuelle`, 24.09.2026):
        # gegen die Punktwolke allein lag Damiras Haar bis 29 mm im Kleid.
        huellen = anfrage.huellen(innen) if gc_vorrat else []
        netze = []
        for (folger, lage), punkte in zip(teile, kaefige, strict=True):
            hd_werte = dict(formung.morphwerte())
            hd_werte.update(zusatz)
            # Laenge/Weite verschieben den Kaefig am Koerper entlang — die Haut
            # muss von dort kommen, nicht aus der Ruhelage (20.09.2026).
            passform = (folger.passformhaut(zusatz)
                        if G9stueckfelder.folgt(folger, lage) else None)
            netz = G9koerpernetz.folgernetz(folger, punkte, bilder or {}, stufen,
                                            koerper=flaeche, werte=hd_werte,
                                            passform=passform,
                                            bindung=bindung if lage is None else None)
            if huellen and (getattr(folger, 'koerperhaut', False)
                            or getattr(folger, 'ART', None) == 'strang'):
                netz['punkte'] = G9stoffhuelle.alle_hinaus(huellen, netz['punkte'])
                if netz.get('bindung') is not None:
                    netz['bindung'] = bindung.fuer(netz['punkte'])
            netze.append((folger, lage, netz))
        return netze, innen, aussen, hoch

    @classmethod
    def getragene(cls, formung, eintraege, stufen=None):
        u"""Die fertigen Browserpunkte der getragenen Daz-Stuecke der Art
        `kleidung`, jedes ueber die anderen gehoben wie im Browser —
        `[(kennung, (N, 3))]` in Anziehreihenfolge. Ein Stueck, das nicht
        rechenbar ist, faellt mit Log heraus."""
        eintraege = [e for e in (eintraege or []) if isinstance(e, dict)][:G9lagenanfrage.HOECHSTENS]
        if not eintraege:
            return []
        stufen = G9netzstufe.browser() if stufen is None else stufen
        koerper = G9koerpernetz(formung, stufen=stufen).koerperflaeche()
        ergebnis = []
        for rang, e in enumerate(eintraege):
            kennung = G9lagenanfrage._kennung(e.get('kennung'))
            eintrag = (G9garderobe.eintrag(kennung) or {}) if kennung else {}
            if eintrag.get('art') != cls.ART:
                continue
            rumpf = {'getragen': eintraege, 'rang': rang, 'stil': e.get('stil'),
                     'regler_stueck': e.get('regler_stueck')}
            try:
                netze, _i, _a, _h = cls.netze(kennung, eintrag, rumpf, formung, koerper, stufen)
            except (ValueError, OSError, KeyError) as fehler:
                logger.warning('GarmentCode: getragenes Daz-Stück %s nicht rechenbar: %s',
                               kennung, fehler)
                continue
            punkte = [np.asarray(netz['punkte'], dtype=np.float64) for _f, lage, netz in netze
                      if lage is None and len(netz['punkte'])]
            if punkte:
                ergebnis.append((kennung, np.vstack(punkte)))
        return ergebnis
