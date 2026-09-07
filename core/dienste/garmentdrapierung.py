# -*- coding: utf-8 -*-
"""Garmentdrapierung — Schnittmuster -> 3D-Netz auf DER FIGUR -> Rig.

Der zweite und dritte Schritt nach dem Schnitt. Frueher stand das in
`GarmentcodeDienst`; die Datei waere mit dem Koerperteil ueber 300 Zeilen
gewachsen.

WAS SICH AM 06.09.2026 GEAENDERT HAT
====================================
Der Stoff faellt jetzt auf den Koerper der GEWAEHLTEN Figur, nicht auf
`mean_all`. Vorher stand im Aufruf `koerper=None`, und das heisst in
`Drapierung` der Durchschnittskoerper des Upstream-Projekts. Das Ergebnis war
ein tadellos sitzendes Kleidungsstueck — auf einem Koerper, den niemand sieht.
Auf der Figur gemessen: Median 27,4 mm Abstand zur Haut, 31 % der 5.658
Punkte weiter als 5 cm weg (Edgar: „er liegt aber nicht an").

UND DANN WIRD NACHGERAEUMT
=========================
Auch auf dem richtigen Koerper steckt Stoff in der Haut: Die Simulation haelt
2,5 mm Abstand (`body_collision_thickness`), und alles, was spitzer aus dem
MB-Lab-Netz ragt — Brustwarzen, Nabel —, steht hindurch. Gemessen 19,3 % der
Kontaktpunkte. `GarmentCode.stoffkorrektur` holt sie heraus (danach 0,5 %);
warum weder Body-Smoothing noch ein groesserer Kollisionsabstand das loesen,
steht dort.

DAS FIGURNETZ WIRD EINMAL GERECHNET
===================================
Es wird an drei Stellen gebraucht — fuer die Masse, fuer den Drapierkoerper
und fuer die Verankerung beim Anziehen. `CharacterState.compute()` laeuft
ueber 18.210 Vertices mit allen gesetzten Morphs; dreimal dasselbe zu rechnen
ist Zeit, die der Nutzer wartet.
"""

import logging
import os

from GarmentCode.stoffkorrektur import Stoffkorrektur

from .charakterdaten import Charakterdaten
from .garmentkoerper import Garmentkoerper

logger = logging.getLogger('core')


class Garmentdrapierung:
    """Legt ein Schnittmuster auf die Figur und macht es animierbar."""

    @classmethod
    def lauf(cls, spezifikation, geschlecht='female', morphs=None, bauart=None,
             koerper=None, smpl=False, meta=None):
        """Drapieren und anziehen, in einem Zug.

        `koerper` benennt einen Koerper des Upstream-Projekts statt der Figur
        — seit dem 06.09.2026 die SMPL-Referenzkoerper (`smpl=True`, dann
        nimmt GarmentCode `smpl_vert_segmentation.json`). Auf ihnen laeuft
        der Weg exakt wie das Online-Tool: keine Messung, keine
        Stoffkorrektur, kein Rig — nur das Netz, so wie die Simulation es
        abgelegt hat.
        """
        from GarmentCode.drapierung import Drapierung
        from .garmentcode import GarmentcodeDienst

        if koerper:
            logger.info('GarmentCode: drapiere %s auf %s (Referenzkoerper%s)',
                        spezifikation, koerper, ', SMPL' if smpl else '')
            # Eine geformte Variante (Regler Groesse/Fuelle) liegt in ihrem
            # eigenen Ordner neben der SMPL-Segmentierung. Ohne diesen Weg
            # sucht `_koerperordner` im Upstream und drapiert stumm auf dem
            # Durchschnittskoerper — genau der Fehler, der die Figur schon
            # einmal auf `mean_all` gekleidet hat.
            ergebnis = Drapierung(spezifikation, koerper=koerper,
                                  koerperordner=cls._variantenordner(koerper),
                                  smpl_body=smpl).drapieren()
            ergebnis['drapierkoerper'] = koerper
            ergebnis['auf_figur'] = False
            try:
                ergebnis.update(cls._netz_ablegen(ergebnis))
            except Exception:
                logger.exception('GarmentCode: Netz nicht ablegbar')
                ergebnis['rig'] = ''
            return ergebnis

        figurnetz = GarmentcodeDienst.figurnetz(geschlecht, morphs, bauart, meta)
        masse, _ = GarmentcodeDienst.masse(geschlecht, morphs=morphs,
                                           bauart=bauart, netz=figurnetz)
        ablage = Garmentkoerper.bereitstellen(geschlecht, figurnetz, masse)

        logger.info('GarmentCode: drapiere %s auf %s', spezifikation,
                    (ablage or {}).get('name') or 'Vorgabekoerper')
        ergebnis = Drapierung(
            spezifikation,
            koerper=(ablage or {}).get('name'),
            koerperordner=(ablage or {}).get('ordner')).drapieren()
        ergebnis['drapierkoerper'] = (ablage or {}).get('name') or Drapierung.KOERPER
        ergebnis['auf_figur'] = bool(ablage)
        try:
            ergebnis.update(cls._anziehen(ergebnis, geschlecht, figurnetz))
        except Exception:
            # Ein fehlendes Rig macht das Netz nicht wertlos — es ist dann
            # nur nicht animierbar. Deshalb hier kein Abbruch.
            logger.exception('GarmentCode: Anziehen gescheitert')
            ergebnis['rig'] = ''
        return ergebnis

    @staticmethod
    def _variantenordner(koerper):
        u"""Der eigene Ordner einer geformten SMPL-Variante, sonst None
        (dann sucht GarmentCode selbst im Upstream)."""
        from .smplvarianten import Smplvarianten
        return Smplvarianten.ordner() if Smplvarianten.vorhanden(koerper) else None

    # ------------------------------------------------- Referenzkoerper: nur Netz

    @staticmethod
    def _netz_ablegen(ergebnis):
        """Das drapierte Netz ohne Rig ablegen — fuer den Referenzkoerper.

        Dieselbe Datei wie beim Anziehen (`*_sim_rig.json`), nur ohne
        Gewichte und Anker: Der Browser haengt es dann als starres Netz ein.
        Bewusst KEINE Stoffkorrektur — das hier ist die Messlatte, und die
        darf nichts enthalten, was das Tool nicht auch tut.
        """
        from GarmentCode.anziehen import Anziehen
        netzdatei = ergebnis.get('netz') or ''
        if not os.path.isfile(netzdatei):
            return {'rig': ''}
        punkte, dreiecke = Anziehen.netz_lesen(netzdatei, aus_garmentcode=True)
        ziel = os.path.splitext(netzdatei)[0] + '_rig.json'
        Anziehen.ablegen(ziel, punkte, dreiecke, None, [])
        return {'rig': ziel, 'rig_datei': os.path.basename(ziel),
                'rig_punkte': len(punkte), 'rig_ohne_gewicht': len(punkte)}

    # ------------------------------------------------------------- anziehen

    @classmethod
    def _anziehen(cls, ergebnis, geschlecht, figurnetz):
        """Dem drapierten Netz Gewichte und Verankerung geben."""
        import numpy as np
        from GarmentCode.anziehen import Anziehen

        netzdatei = ergebnis.get('netz') or ''
        if not os.path.isfile(netzdatei):
            return {'rig': ''}

        punkte, dreiecke = Anziehen.netz_lesen(netzdatei, aus_garmentcode=True)
        netz = Charakterdaten.netzdaten(geschlecht)
        gewichte = (getattr(netz, 'skin_weights', None)
                    or getattr(netz, 'skin_weights_base', None))

        # Eingesunkene Punkte herausholen, BEVOR verankert wird — sonst
        # haengt die Kleidung an Ankern, die im Koerper liegen, und jeder
        # Morph-Regler zieht den Fehler mit.
        korrektur = {}
        if figurnetz is not None and getattr(netz, 'faces', None) is not None:
            punkte, korrektur = Stoffkorrektur.aus_netz(
                figurnetz, netz.faces, dreiecke).anwenden(punkte)
        # Ohne Koerpernetz oder Gewichte gibt es kein Rig — dann bleibt das
        # Netz erhalten und nur `rig` leer, statt hier abzustuerzen.
        if figurnetz is None or not gewichte:
            logger.warning('GarmentCode: kein Rig — Koerpernetz oder '
                           'Gewichte fehlen')
            return {'rig': ''}

        anzieher = Anziehen(np.asarray(figurnetz), netz.faces,
                            gewichte['weights'], gewichte['bone_names'])
        rig = anzieher.anziehen(punkte)
        ziel = os.path.splitext(netzdatei)[0] + '_rig.json'
        Anziehen.ablegen(ziel, punkte, dreiecke, rig, gewichte['bone_names'])
        logger.info('GarmentCode: angezogen — %d Punkte, %d ohne Gewicht, '
                    'Abstand zur Haut median %.1f mm', rig['punkte'],
                    rig['ohne_gewicht'], cls._hautabstand(rig))
        return {
            'rig': ziel,
            'korrektur': korrektur,
            'rig_datei': os.path.basename(ziel),
            'rig_punkte': rig['punkte'],
            'rig_ohne_gewicht': rig['ohne_gewicht'],
            'hautabstand_mm': round(cls._hautabstand(rig), 1),
        }

    @staticmethod
    def _hautabstand(rig):
        """Median-Abstand des Netzes zur Haut, in Millimetern.

        Der Versatz der Verankerung IST dieser Abstand — er steht ohnehin
        in der Rig-Datei. Als Zahl in der Antwort ist er die Probe aufs
        Exempel: Ein T-Shirt liegt bei wenigen Millimetern an; wird daraus
        wieder eine zweistellige Zahl, drapiert etwas auf dem falschen
        Koerper, ohne dass jemand einen Fehler sieht.
        """
        import numpy as np
        versatz = np.asarray(rig['anker']['versatz'], dtype=np.float64)
        if not len(versatz):
            return 0.0
        return float(np.median(np.linalg.norm(versatz, axis=1)) * 1000.0)
