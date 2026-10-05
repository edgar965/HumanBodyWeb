# -*- coding: utf-8 -*-
u"""G9kleidhumanbody — die Antwort eines Daz-Stuecks fuer eine HumanBody-Figur.

Derselbe Endpunkt wie fuer Genesis 9 (`G9garderobeapi.kleidnetz`), mit
`figurart: humanbody` und der Figur im Rumpf (`geschlecht`, `bauart`,
`morphs`, `meta` — wie der GarmentCode-Reiter sie schickt). Die Uebertragung
selbst steht in `core/dienste/g9aufhumanbody.py`; hier nur, was die Antwort
in dieselbe Form bringt wie `_kleid`: je Teil Netz, Gruppen mit Bildern und
`hautgewichte` — mit DEF-Knochennamen, damit der Browser das Stueck an das
Rigify-Skelett bindet (`scene/genesis9/dazkleidung.js`).

Seit 30.09.2026 (Edgar: „auf einer HumanBody soll das haar genau so gemischt werden")
wie `_kleid` mit `vor_antwort` — die Haarmischung (`G9haarmischbau`) duennt damit jedes
Teil auf seinen Anteil aus —, mit den fuenf Formachsen einer Frisur (`G9haarachsen`, auf
dem Genesis-Grundkoerper VOR der Uebertragung) und mit Stranghaar (`G9hbstrang`), das hier
bis dahin ganz wegfiel: Pixie kam als kahle Kappe, Hime Cut und Viola gar nicht.
"""
import logging
import time

import numpy as np
from django.http import JsonResponse
from Genesis9.formung import G9formung
from Genesis9.garderobe import G9garderobe
from Genesis9.haarachsen import G9haarachsen
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.netzstufe import G9netzstufe
from Genesis9.oberflaechenbindung import G9oberflaechenbindung
from Genesis9.teilbindung import G9teilbindung

from ..daten.netzantwort import Netzantwort
from ..dienste.g9aufhumanbody import G9aufhumanbody
from ..dienste.g9hbfusspose import G9hbfusspose
from ..dienste.g9hbschuhpassung import G9hbschuhpassung
from ..dienste.g9hbstoffbruecke import G9hbstoffbruecke
from ..dienste.g9hbstoffkorrektur import G9hbstoffkorrektur
from ..dienste.g9hbstrang import G9hbstrang
from ..dienste.g9hbteilhaut import G9hbteilhaut
from .g9figur import G9figur
from .g9netzantwort import G9netzantwort

logger = logging.getLogger('core')

__all__ = ['G9kleidhumanbody']


class G9kleidhumanbody:
    u"""`antwort(kennung, eintrag, rumpf, vor_antwort)` -> Antwort-Dict oder Fehlerantwort."""

    FIGURART = 'humanbody'
    NICHT_TRAGBAR = 'Requisiten hängen an Daz-Knochen — auf HumanBody nicht tragbar'
    KEIN_NETZ = 'Das Stück hat kein Netz'
    #: Mindestabstand des Kaefigs zur HumanBody-Haut, Meter. Die Haut wird im
    #: Browser um bis zu 5 mm verschoben (`Hauttextur.VERSCHIEBUNG` 0,01 mit
    #: Mitte 0,5 — MB-Labs Displace-Modifier); mit dem 1 mm von `G9kollision`
    #: stand die Brust durch das Hemd (gemessen 19.09.2026: Apex 2,5 mm).
    HAUTABSTAND = 0.006
    #: Schuhe (05.10.2026, Edgar: „Angie_Sneakers passt nicht auf Modell F2_ShirtLeggins, große Zehe geht durch den Schuh"): Mit 6 mm
    #: stand die Haut der grossen Zehe an der Kappe durch — am Browser gemessen (Strahl +z von 960 Hautpunkten der Zehenfront bis zur
    #: ersten Schuhflaeche) ragten 17 heraus, die Kappe lag 0–2 mm vor der Haut; die Haut im Browser ist die des Servers (Zehenspitze
    #: 231 mm), aber um bis zu 5 mm verschoben (siehe oben), und die Kappe hat Flaechen mit Kanten bis 29 mm. Mit 8, 10 und 12 mm ragte keiner mehr heraus.
    HAUTABSTAND_SCHUH = 0.010

    @classmethod
    def antwort(cls, kennung, eintrag, rumpf, vor_antwort=None):
        u"""`vor_antwort(nummer, netz) -> netz | None` greift je Teil ein wie bei
        `G9garderobeapi._kleid`: `None` laesst das Teil weg. Bei Flaechen VOR der
        Hautsuche — die kostet je Punkt, und eine ausgeduennte Beimischung soll nur ihre
        behaltenen Punkte bezahlen."""
        try:
            teile = G9garderobe.teile(kennung)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        except (OSError, KeyError) as fehler:
            logger.warning('Genesis 9: Stück %s nicht ladbar: %s', kennung, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        if any(lage is not None for _folger, lage in teile):
            return JsonResponse({'fehler': cls.NICHT_TRAGBAR}, status=400)
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
        schuh = cls.ist_schuh(eintrag)
        abstand = cls.HAUTABSTAND_SCHUH if schuh else cls.HAUTABSTAND
        stufen = G9netzstufe.browser()
        # Dauer je Schritt ins Log: Kin Hair brauchte hier kalt 88 s (30.09.2026), und
        # ohne Aufteilung laesst sich nicht sagen, wo sie steckt.
        dauer = {'uebertragen': 0.0, 'netz': 0.0, 'haut': 0.0}
        uhr = time.perf_counter()
        roh = [folger.punkte_zu(formung, zusatz, drehung=knochen, lage=None) - hoch
               for folger, _lage in teile]
        if eintrag.get('art') == 'haar':
            # Die fuenf Formachsen wie im Genesis-Weg (`G9stueckteile.netze`): keine
            # Daz-Kanaele, deshalb nicht in `reglerwerte`. Ihre Deltas liegen auf dem
            # Genesis-Grundkoerper — also VOR der Uebertragung dazu.
            roh = G9haarachsen.anwenden(kennung, teile, roh,
                                        G9haarachsen.werte(rumpf.get('regler_stueck')))
        # Eigene Morphe (`eigen.`), Zusatzstraehnen (`str.`) und Texturschichten (`bild.`) der Iterationen wirkten
        # bis 01.10.2026 nur auf Genesis („`G9kleidhumanbody` kennt die Schichten nicht") — jetzt derselbe Weg wie in
        # `G9stueckteile.netze`, auf dem Genesis-Grundkoerper VOR der Uebertragung; die Schichten ersetzen die Albedo.
        from Genesis9.kleidmorphe import G9kleidmorphe
        from Genesis9.kleidtexturen import G9kleidtexturen
        roh = G9kleidmorphe.anwenden(kennung, teile, roh, G9kleidmorphe.werte(rumpf.get('regler_stueck')))
        if eintrag.get('art') == 'haar':
            from Genesis9.haarzusatz import G9haarzusatz
            teile, roh = G9haarzusatz.anwenden(kennung, teile, roh, G9haarzusatz.werte(rumpf.get('regler_stueck')))
        bilder = G9kleidtexturen.anwenden(kennung, bilder or {}, rumpf.get('regler_stueck'))
        kaefige = []
        for (folger, _lage), punkte in zip(teile, roh, strict=True):
            if cls._strang(folger):
                kaefige.append(G9hbstrang.uebertragen(traeger, punkte))
                continue
            # Kleidung nur im Koerperteil ihrer Daz-Bindung (30.09.2026: unter der Achsel zog
            # der Oberarm am Seitenteil des GC T-Shirts). Haar nicht: Langes Haar liegt auf
            # dem Ruecken, gebunden ist es an den Kopf.
            bindung = (G9teilbindung.aus_haut(getattr(folger, 'dazhaut', None), len(punkte))
                       if eintrag.get('art') == 'kleidung' else None)
            # Ein Schuh als Ganzes an den HumanBody-Fuss (05.10.2026, `G9hbschuhpassung`), Stoff Punkt fuer Punkt.
            kaefig = (G9hbschuhpassung.passen(traeger, punkte, bindung=bindung) if schuh
                      else traeger.uebertragen(punkte, bindung=bindung))
            if getattr(folger, 'koerperhaut', False):
                gehoben = traeger.hinaus(kaefig, abstand)
                if eintrag.get('art') == 'kleidung':
                    # Mit seiner Stofflaenge spannen (30.09.2026, GC T-Shirt: „Drapierung bei
                    # den Bruesten fehlerhaft") — punktweise Heben kennt keine Laenge.
                    gehoben = G9hbstoffbruecke.spannen(
                        traeger, gehoben, kaefig, G9hbstoffbruecke.kanten(folger.polys, len(kaefig)),
                        abstand)
                kaefig = gehoben
            kaefige.append(kaefig)
        dauer['uebertragen'] = time.perf_counter() - uhr
        # Ein Schuh mit Fusspose: die Figur bekommt den Absatz, das Stueck geht
        # in die Ruhelage, damit der Fuss es beim Beugen mitnimmt (`G9hbfusspose`).
        absatz = G9hbfusspose.absatz(kennung, kaefige)
        antwort_teile = []
        for nummer, ((folger, _lage), kaefig) in enumerate(zip(teile, kaefige, strict=True)):
            uhr = time.perf_counter()
            if absatz:
                kaefig = G9hbfusspose.ruhelage(kaefig, traeger.haut(kaefig), absatz, traeger.geschlecht)
            netz = G9koerpernetz.folgernetz(folger, kaefig, bilder, stufen, koerper=koerper)
            if getattr(folger, 'koerperhaut', False):
                # Auch die UNTERTEILTEN Punkte: Wo der Kaefig eine vorstehende Brust
                # umspannt, schneidet die Flaeche dazwischen bis 16 mm tief hinein.
                netz['punkte'] = (G9hbschuhpassung.heben(traeger, netz['punkte'], abstand) if schuh
                                  else traeger.hinaus(netz['punkte'], abstand))
                if eintrag.get('art') == 'kleidung' and not netz.get('stufen'):
                    # Und gegen die FLAECHE: Zwischen drei Stoffpunkten stand die Brustwarze
                    # durch (30.09.2026, GC T-Shirt) — `G9hbstoffkorrektur`. Nur ohne
                    # Unterteilung: Dort liegen die Punkte 1–2 cm auseinander; unterteilt sind
                    # es Millimeter, und das G9 Base Shirt (33.078 Punkte) kostete 11 s mehr.
                    netz['punkte'], _bilanz = G9hbstoffkorrektur.anwenden(
                        traeger, netz['punkte'], netz['dreiecke'], abstand)
                netz['normalen'] = folger.netzstufe(stufen).normalen(kaefig, netz['punkte'])
            dauer['netz'] += time.perf_counter() - uhr
            uhr = time.perf_counter()
            strang = cls._strang(folger)
            if strang:
                # Strähnen: Haut aus der Stichprobe (`G9hbstrang`) — VOR dem Ausduennen,
                # die Karte der Bindung gilt je Strangpunkt des ganzen Netzes.
                netz['haut'] = G9hbstrang.haut(traeger, folger, netz['punkte'])
            if vor_antwort is not None:
                netz = vor_antwort(nummer, netz)
                if netz is None:
                    continue
            if not strang:
                # Im Koerperteil der Daz-Bindung — die Hand neben dem Rock traegt ihn nicht.
                netz['haut'] = G9hbteilhaut.fuer(traeger.figur()).haut(
                    netz['punkte'], G9teilbindung.stueck(folger, kaefig, netz['punkte']))
            dauer['haut'] += time.perf_counter() - uhr
            teil = G9netzantwort.aus(netz)
            teil['name'] = folger.name
            teil['stufen'] = netz['stufen']
            teil['knochen'] = None
            teil['zweiseitig'] = bool(eintrag.get('eigen'))   # wie `g9garderobe._kleid`
            # Stoffschwung auch auf HumanBody (20.09.2026, Edgar: „das kleid muss nach
            # unten animieren"): `netz['stoff']` traegt bereits den HumanBody-Kaefig und
            # die Freiheit gegen die HumanBody-Haut (`folgernetz` mit `koerper`). Was
            # fehlte, war die HAUT des Kaefigs: der Bauplan (`G9stoffapi`) nennt dafuer
            # Daz-Knochen, die das Rigify-Skelett nicht hat - der Worker startete nie.
            # Deshalb kommt die Kaefighaut mit DEF-Namen hier mit; `genesis9stoffschwung.js`
            # nimmt sie dem Bauplan vor. Gemessen vorher: 33 von 40 Armproben im Kleid,
            # 42,8 cm tief (`test_kleid_arme_frei`).
            if teil.get('stoff') and netz.get('stoff') is not None:
                kaefig_stoff = netz['stoff']['kaefig']
                haut_kaefig = G9hbteilhaut.fuer(traeger.figur()).haut(
                    kaefig_stoff, G9teilbindung.stueck(folger, kaefig, kaefig_stoff))
                teil['stoff']['hautgewichte'] = Netzantwort.hautgewichte(haut_kaefig, kompakt=True)
            antwort_teile.append(teil)
        logger.info('Daz auf HumanBody: %s — %d Teile, %d Punkte%s (Übertragung %.1f s, '
                    'Netz %.1f s, Haut und Auswahl %.1f s)', kennung, len(antwort_teile),
                    sum(int(t.get('vertex_count') or 0) for t in antwort_teile),
                    ', Absatz %s' % absatz if absatz else '',
                    dauer['uebertragen'], dauer['netz'], dauer['haut'])
        # `art` wie bei `_kleid`: der Browser blendet nur unter `kleidung` die Haut aus
        # (`Hautverdeckung.zaehlt`) — unter Haar bliebe sonst die Kopfhaut weg.
        return {'kennung': kennung, 'teile': antwort_teile, 'boden': 0.0, 'stufen': stufen,
                'figurart': cls.FIGURART, 'innen': [], 'aussen': [], 'absatz': absatz,
                'art': eintrag.get('art')}

    @staticmethod
    def ist_schuh(eintrag):
        u"""Gehoert das Stueck in die Kategorie „Schuhe"? Die WIRKSAME Kategorie zaehlt (Edgars Einteilung vor der Vorgabe aus Daz' Metadaten);
        ist die Einteilung nicht lesbar, gilt es als Kleidung."""
        from Genesis9.garderobekategorien import G9garderobekategorien
        try:
            return G9garderobekategorien.kategorie(eintrag) == u'Schuhe'
        except (OSError, ValueError, KeyError):
            return False

    @classmethod
    def hautabstand(cls, eintrag):
        u"""Der Mindestabstand zur Haut fuer dieses Stueck: `HAUTABSTAND_SCHUH` in der Kategorie „Schuhe", sonst `HAUTABSTAND`."""
        return cls.HAUTABSTAND_SCHUH if cls.ist_schuh(eintrag) else cls.HAUTABSTAND

    @classmethod
    def bindungsflaeche(cls, rumpf):
        u"""Die sichtbare HumanBody-Haut dieser Figur als `G9oberflaechenbindung` — der Körper, über dem
        „Kleidung – Generisch" mischt (`G9kleidmischbau`, 30.09.2026: auf einer HumanBody-Figur genauso wie auf
        Genesis). Die Dreiecksumgebung entsteht beim ersten Aufruf; danach liegt die Fläche an der Figur
        (`Hbtraeger.laden` merkt die jüngsten Stellungen)."""
        traeger = G9aufhumanbody(rumpf.get('geschlecht'), rumpf.get('bauart'),
                                 cls._woerterbuch(rumpf.get('morphs')), cls._woerterbuch(rumpf.get('meta')))
        figur = traeger.figur()
        if 'bindung' not in figur:
            haut, normalen, baum = traeger.koerperflaeche()
            figur['bindung'] = G9oberflaechenbindung(haut, normalen, figur['fein_dreiecke'], baum)
        return figur['bindung']

    @staticmethod
    def _strang(folger):
        return getattr(folger, 'ART', None) == 'strang'

    @staticmethod
    def _woerterbuch(wert):
        return {str(k): v for k, v in wert.items()} if isinstance(wert, dict) else {}
