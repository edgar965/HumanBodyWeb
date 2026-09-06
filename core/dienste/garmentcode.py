# -*- coding: utf-8 -*-
"""GarmentcodeDienst — Schnitte aus GarmentCode, fuer die Szene-Seite.

GarmentCode konstruiert Kleidung aus KOERPERMASSEN, statt ein fremdes Netz
anzupassen. Das ist der Unterschied zum `.mhclo`-Bestand, der auf dem
MB-Lab-Koerper nicht sitzt (gemessen am 06.09.2026: 14,3 % der Anker fallen
ueber `mh_to_body_map` auf EINEN Koerpervertex, Shrinkwrap liefert bis 36 %
Vertices im Koerper). Wo nichts angepasst wird, kann nichts verrutschen.

Der eigentliche Lauf liegt in `GarmentCode.entwurf` und laeuft als eigener
Prozess — Begruendung dort. Dieser Dienst haelt nur die Bruecke: Masse
besorgen, Lauf anstossen, Ergebnis fuer die Seite aufbereiten.
"""

import logging
import os

from django.conf import settings

from .charakterdaten import Charakterdaten

logger = logging.getLogger('core')


class GarmentcodeDienst:
    """Zugang zu GarmentCode fuer die Endpunkte."""

    #: Referenzkoerper, dessen Masse als Grundlage dienen. Die formgebenden
    #: Werte werden am eigenen Netz nachgemessen, der Rest bleibt von hier.
    VORLAGEN = {'female': 'mean_female.yaml', 'male': 'mean_male.yaml'}

    #: Bauart, wenn die Figur keine mitgibt — Schreibweise wie in
    #: `character.js` (`presetData.body_type`), nicht die Kurzform.
    BAUART = {'female': 'Female_Caucasian', 'male': 'Male_Caucasian'}

    # ------------------------------------------------------------------ Status

    @staticmethod
    def zustand():
        """Was die Seite ueber GarmentCode wissen muss."""
        from GarmentCode.entwurf import Entwurf
        da = Entwurf.vorhanden()
        return {
            'vorhanden': da,
            'pfad': Entwurf.REPO,
            'vorlagen': Entwurf.katalog() if da else [],
            'entwuerfe': Entwurf.entwurfsvorlagen() if da else [],
            'hinweis': '' if da else
                       'GarmentCode-Klon fehlt unter %s' % Entwurf.REPO,
        }

    # ------------------------------------------------------------------- Masse

    @classmethod
    def masse(cls, geschlecht='female', morphs=None, bauart=None):
        """Koerpermasse der GEWAEHLTEN Figur, am Netz gemessen.

        `morphs` sind die Reglerwerte der Figur aus der Szene. Ohne sie wird
        der Grundkoerper gemessen — dann bekommt man die Masse der
        Voreinstellung, nicht die der Figur auf dem Bildschirm.
        """
        import numpy as np
        from GarmentCode.koerpermasse import Koerpermasse
        vorlage = cls._vorlage(geschlecht)
        netz = cls._figurnetz(geschlecht, morphs, bauart)
        if netz is None:
            return vorlage, {name: 'vorlage' for name in vorlage}
        rechner = Koerpermasse(np.asarray(netz), vorlage)
        return rechner.masse(), rechner.herkunft()

    @classmethod
    def _figurnetz(cls, geschlecht, morphs, bauart):
        """Die Vertices der Figur MIT ihren Morphs, oder das Grundnetz.

        Derselbe Weg wie `/api/character/mesh/`: ein `CharacterState` bekommt
        Bauart und Regler und rechnet die Punkte. Ohne das misst man den
        Grundkoerper und schneidert am Nutzer vorbei.
        """
        if not morphs:
            return cls._grundnetz(geschlecht)
        try:
            from humanbody_core import CharacterState
            zustand = CharacterState(Charakterdaten.morphdaten(),
                                     Charakterdaten.voreinstellungen())
            zustand.set_body_type(
                bauart or cls.BAUART.get(geschlecht, 'Female_Caucasian'))
            for name, wert in morphs.items():
                try:
                    zustand.set_morph_value(name, float(wert))
                except Exception:
                    logger.debug('GarmentCode: Morph %s uebergangen', name)
            punkte = zustand.compute()
            if punkte is not None:
                return punkte
        except Exception:
            logger.exception('GarmentCode: Figurnetz nicht rechenbar')
        return cls._grundnetz(geschlecht)

    @classmethod
    def _vorlage(cls, geschlecht):
        """Die Masse eines GarmentCode-Referenzkoerpers."""
        import yaml
        from GarmentCode.entwurf import Entwurf
        datei = cls.VORLAGEN.get(geschlecht, cls.VORLAGEN['female'])
        pfad = os.path.join(Entwurf.REPO, 'assets', 'bodies', datei)
        with open(pfad, 'r', encoding='utf-8') as quelle:
            return yaml.safe_load(quelle)['body']

    @staticmethod
    def _grundnetz(geschlecht):
        """Die Vertices des Grundkoerpers in T-Haltung, oder None."""
        import numpy as np
        # HUMANBODY_DATA_DIR zeigt bereits auf `data/humanBody` — der
        # Unterordner darf hier NICHT noch einmal angehaengt werden.
        pfad = os.path.join(str(settings.HUMANBODY_DATA_DIR),
                            'vertices_tpose.npy')
        if not os.path.isfile(pfad):
            logger.warning('GarmentCode: Grundnetz fehlt (%s)', pfad)
            return None
        return np.load(pfad)

    # ---------------------------------------------------------------- erzeugen

    @classmethod
    def erzeugen(cls, vorlage, geschlecht='female', morphs=None, bauart=None,
                 name=None):
        """Ein Kleidungsstueck fuer die gewaehlte Figur bauen."""
        from GarmentCode.entwurf import Entwurf
        masse, _ = cls.masse(geschlecht, morphs=morphs, bauart=bauart)
        name = name or ('%s_%s' % (vorlage, geschlecht))
        logger.info('GarmentCode: erzeuge %s (%s, %d Morphs)',
                    vorlage, geschlecht, len(morphs or {}))
        return Entwurf(vorlage, masse).erzeugen(name=name)

    # --------------------------------------------------------------- 3D

    @staticmethod
    def drapierbereit():
        """Steht die Simulationsumgebung? (eigenes Python + Warp-Fork)"""
        from GarmentCode.drapierung import Drapierung
        return Drapierung.bereit()

    @classmethod
    def drapieren(cls, spezifikation, koerper=None, geschlecht='female',
                  morphs=None, bauart=None):
        """Schnittmuster -> 3D-Netz -> Rig, in einem Zug.

        Die Drapierung allein liefert ein Standbild. Erst das Anziehen macht
        daraus ein Kleidungsstueck, das der Figur folgt: Knochengewichte vom
        Koerper darunter, und die Verankerung, mit der ein Morph-Regler die
        Kleidung in Millisekunden nachzieht statt in drei Minuten.
        """
        from GarmentCode.drapierung import Drapierung
        logger.info('GarmentCode: drapiere %s', spezifikation)
        ergebnis = Drapierung(spezifikation, koerper=koerper).drapieren()
        try:
            ergebnis.update(cls._anziehen(ergebnis, geschlecht, morphs, bauart))
        except Exception:
            # Ein fehlendes Rig macht das Netz nicht wertlos — es ist dann
            # nur nicht animierbar. Deshalb hier kein Abbruch.
            logger.exception('GarmentCode: Anziehen gescheitert')
            ergebnis['rig'] = ''
        return ergebnis

    @classmethod
    def _anziehen(cls, ergebnis, geschlecht, morphs, bauart):
        """Dem drapierten Netz Gewichte und Verankerung geben."""
        import numpy as np
        from GarmentCode.anziehen import Anziehen

        netzdatei = ergebnis.get('netz') or ''
        if not os.path.isfile(netzdatei):
            return {'rig': ''}

        punkte, dreiecke = Anziehen.netz_lesen(netzdatei, aus_garmentcode=True)
        koerpernetz = cls._figurnetz(geschlecht, morphs, bauart)
        netz = Charakterdaten.netzdaten(geschlecht)
        gewichte = getattr(netz, 'skin_weights', None)
        # Ohne Koerpernetz oder Gewichte gibt es kein Rig — dann bleibt das
        # Netz erhalten und nur `rig` leer, statt hier abzustuerzen.
        if koerpernetz is None or not gewichte:
            logger.warning('GarmentCode: kein Rig — Koerpernetz oder '
                           'Gewichte fehlen')
            return {'rig': ''}

        anzieher = Anziehen(np.asarray(koerpernetz), netz.faces,
                            gewichte['weights'], gewichte['bone_names'])
        rig = anzieher.anziehen(punkte)
        ziel = os.path.splitext(netzdatei)[0] + '_rig.json'
        Anziehen.ablegen(ziel, punkte, dreiecke, rig)
        return {
            'rig': ziel,
            'rig_punkte': rig['punkte'],
            'rig_ohne_gewicht': rig['ohne_gewicht'],
        }

    @staticmethod
    def spezifikation(ergebnis):
        """Der Pfad der Spezifikation aus einem Erzeugungsergebnis."""
        ordner = ergebnis.get('ordner', '')
        for datei in ergebnis.get('dateien', []):
            if datei.endswith('_specification.json'):
                return os.path.join(ordner, datei)
        return None

    # ---------------------------------------------------------------- Vorschau

    @staticmethod
    def vorschaubild(ordner):
        """Der Dateiname des Schnittmusterbildes in einem Ergebnisordner."""
        if not os.path.isdir(ordner):
            return None
        for datei in sorted(os.listdir(ordner)):
            if datei.endswith('_pattern.png'):
                return datei
        return None
