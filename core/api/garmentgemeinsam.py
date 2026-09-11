# -*- coding: utf-8 -*-
"""Mehrere GarmentCode-Stuecke in EINEM Lauf anziehen.

Eigenes Modul, nicht am Ende von `garmentcode.py`: Die Datei steht bei 211
Zeilen, und eine Datei waechst beim Anfassen nicht ueber ihre Grenze
(`~/.claude/rules/struktur.md`).

WARUM EIN EIGENER ENDPUNKT UND NICHT MEHRFACH `/drapieren/`
===========================================================
Weil genau das der Befund war: Zwei getrennte Laeufe kennen einander nicht.
Der Stoff-gegen-Stoff-Kontakt des Upstream gilt innerhalb EINES simulierten
Netzes; also muessen beide Stuecke in einem Netz stehen. Der Dienst
(`GarmentCode/gemeinsamdienst.py`) baut deshalb die Schnitte SELBST — sie
muessen aus denselben Koerpermassen kommen und in eine Spezifikation
vereint werden, bevor simuliert wird. Ein Aufruf, ein Ergebnis je Stueck.
"""

import json
import logging
import os

from django.http import JsonResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


class Garmentgemeinsamendpunkte:
    """Der Endpunkt hinter dem Knopf „Gemeinsam anziehen"."""

    @staticmethod
    @require_POST
    def gemeinsam(request):
        """Mehrere Stuecke bauen, zusammen drapieren, je Stueck anziehen."""
        from GarmentCode.gemeinsamdienst import (Garmentgemeinsam,
                                                 GemeinsamFehler)
        from GarmentCode.gemeinsamablage import AblageFehler
        from GarmentCode.drapierung import DrapierFehler
        from .garmentcode import Garmentcode
        anfrage = Garmentcode.aus_anfrage(request)
        # Ein SMPL-Referenzkoerper hat keine Skinning-Gewichte und keine
        # Stoffkorrektur; der gemeinsame Weg braucht beides. Das zu
        # uebergehen hiesse, auf einem anderen Koerper zu drapieren als
        # angezeigt — der Fehler vom 06.09.2026.
        if anfrage['koerper']:
            return JsonResponse(
                {'fehler': 'Gemeinsam anziehen gilt für die HumanBody-Figur, '
                           'nicht für einen Referenzkörper.'}, status=400)
        stuecke = Garmentgemeinsamendpunkte._stuecke(request)
        if not stuecke:
            return JsonResponse(
                {'fehler': 'Keine Stücke angegeben'}, status=400)
        try:
            ergebnis = Garmentgemeinsam.lauf(
                stuecke, geschlecht=anfrage['geschlecht'],
                morphs=anfrage['morphs'], bauart=anfrage['bauart'],
                meta=anfrage['meta'])
        except (GemeinsamFehler, AblageFehler,
                DrapierFehler) as fehler:
            logger.warning('Gemeinsamer Lauf gescheitert: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:                       # noqa: BLE001
            logger.exception('Gemeinsamer Lauf: unerwarteter Fehler')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        return JsonResponse(Garmentgemeinsamendpunkte._antwort(ergebnis))

    #: Was ein Stueck an Bauwerten mitbringen darf — dieselben Felder wie
    #: beim Einzelbau (`Baufeineinstellung.aus_anfrage`), hier je Stueck.
    BAUFELDER = ('hautabstand_mm', 'aufloesung', 'anliegen_mm')

    @staticmethod
    def _stuecke(request):
        """Die Wunschliste aus dem Formular: [{vorlage, regler, fein}, …].

        `bau` je Stueck (11.09.2026): Die Kombiliste kopiert beim
        Uebernehmen auch die Bauregler — ohne sie baute die Leggings im
        gemeinsamen Lauf weit, weil `anliegen_mm` nie ankam.
        """
        from GarmentCode.baufeineinstellung import Baufeineinstellung
        try:
            roh = json.loads(request.POST.get('stuecke') or '[]')
        except ValueError:
            logger.warning('Gemeinsam: Stueckliste unlesbar')
            return []
        if not isinstance(roh, list):
            return []
        gewaehlt = []
        for eintrag in roh:
            if not isinstance(eintrag, dict) or not eintrag.get('vorlage'):
                continue
            regler = eintrag.get('regler')
            bau = eintrag.get('bau')
            bau = bau if isinstance(bau, dict) else {}
            gewaehlt.append({'vorlage': eintrag['vorlage'],
                             'regler': regler if isinstance(regler, dict)
                             else {},
                             'fein': Baufeineinstellung(**{
                                 f: bau.get(f) for f in
                                 Garmentgemeinsamendpunkte.BAUFELDER})})
        return gewaehlt

    @staticmethod
    def _antwort(ergebnis):
        """Das Ergebnis so, wie es der Browser je Stueck weiterverarbeitet.

        Jeder Eintrag hat die Form, die `GarmentcodeDrapierung.anziehen`
        schon kennt (`rig_url`, `ordner`, `punkte`, `hautabstand_mm`) —
        damit braucht der gemeinsame Weg im Browser keinen zweiten
        Einhaeng-Code, und ein Stueck aus einem gemeinsamen Lauf ist in
        der Szene von einem einzeln gebauten nicht zu unterscheiden.
        """
        stuecke = []
        for eintrag in ergebnis.get('stuecke') or []:
            kopie = dict(eintrag)
            ordner = os.path.basename(kopie.get('ordner') or '')
            datei = kopie.get('rig_datei')
            if ordner and datei:
                kopie['rig_url'] = ('/api/garmentcode/datei/%s/%s/'
                                    % (ordner, datei))
            # `ordner` bleibt der VOLLE Pfad — genau wie beim Einzelbau.
            # Die Ablage merkt ihn, und `Stoffnachfuehrung.netzpfad`
            # bekommt ihn zurueck und prueft ihn gegen den Ausgabeordner.
            # Die beiden Dateipfade daneben braucht der Browser nicht.
            kopie['ordner'] = kopie.get('ordner') or ''
            kopie.pop('netz', None)
            kopie.pop('rig', None)
            stuecke.append(kopie)
        return {
            'stuecke': stuecke,
            'punkte': ergebnis.get('punkte'),
            'dreiecke': ergebnis.get('dreiecke'),
            'dauer_s': ergebnis.get('dauer_s'),
            'dauer_gesamt_s': ergebnis.get('dauer_gesamt_s'),
            'geraet': ergebnis.get('geraet'),
            'aus_der_haut': ergebnis.get('aus_der_haut', 0),
            'auf_figur': ergebnis.get('auf_figur'),
            'drapierkoerper': ergebnis.get('drapierkoerper'),
            'gemeinsam': os.path.basename(ergebnis.get('ordner') or ''),
        }
