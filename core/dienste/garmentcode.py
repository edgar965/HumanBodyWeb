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
    def masse(cls, geschlecht='female', morphs=None, bauart=None, netz=None,
              koerper=None, meta=None):
        """Koerpermasse der GEWAEHLTEN Figur.

        `koerper` benennt einen SMPL-Referenzkoerper von GarmentCode — dann
        kommen die Masse aus dessen YAML, so wie das Online-Tool sie nimmt,
        und nichts wird gemessen (Edgar, 06.09.2026: „mach das so wie das
        tool"). Sonst werden sie am Netz der Figur gemessen.
        """
        if koerper:
            from .smplfigur import Smplfiguren
            werte = Smplfiguren.masse(koerper)
            return werte, {name: 'vorgegeben' for name in werte}
        return cls._gemessene_masse(geschlecht, morphs, bauart, netz, meta)

    @classmethod
    def _gemessene_masse(cls, geschlecht='female', morphs=None, bauart=None,
                         netz=None, meta=None):
        """Koerpermasse der GEWAEHLTEN Figur, am Netz gemessen.

        `morphs` sind die Reglerwerte der Figur aus der Szene. Ohne sie wird
        der Grundkoerper gemessen — dann bekommt man die Masse der
        Voreinstellung, nicht die der Figur auf dem Bildschirm.

        `netz` nimmt ein schon gerechnetes Figurnetz entgegen. Beim
        Drapieren wird es fuer Masse, Drapierkoerper und Verankerung
        gebraucht; `CharacterState.compute()` laeuft ueber 18.210 Vertices
        und muss dafuer nicht dreimal laufen.
        """
        import numpy as np
        from GarmentCode.koerpermasse import Koerpermasse
        vorlage = cls._vorlage(geschlecht)
        if netz is None:
            netz = cls.figurnetz(geschlecht, morphs, bauart, meta)
        if netz is None:
            return vorlage, {name: 'vorlage' for name in vorlage}
        # Die Segmentierung trennt Arme und Beine ueber die Skinning-
        # Gewichte. Ohne sie trennte `Koerpermasse` an Luecken der Scheibe
        # und verlor den halben Rumpf — `bust` roh 44,5 cm (06.09.2026).
        from .garmentkoerper import Garmentkoerper
        punkte = np.asarray(netz)
        segmente = Garmentkoerper.segmente(geschlecht, len(punkte))
        rechner = Koerpermasse(punkte, vorlage, segmente=segmente,
                               schulter_incl=cls.schulterneigung(geschlecht))
        return rechner.masse(), rechner.herkunft()

    @classmethod
    def schulterneigung(cls, geschlecht):
        """`shoulder_incl` aus dem Schluesselbein des DEF-Skeletts.

        Der Wert steuert im Upstream den Ruhewinkel des Aermels
        (`sleeves.py`: `rest_angle = max(sleeve_angle, _shoulder_incl)`).
        Bis zum 07.09.2026 kam er unveraendert aus der Vorlage — 20,905 aus
        `mean_female.yaml`, waehrend unsere Figuren bei 11,5 Grad stehen.
        Herleitung und die drei verworfenen Netz-Messer: `schulterneigung.py`.
        """
        from django.conf import settings
        from GarmentCode.schulterneigung import Schulterneigung
        ordner = str(settings.HUMANBODY_DATA_DIR)
        if geschlecht == 'male':
            ordner += '_male'
        return Schulterneigung.aus_datenordner(ordner)

    @classmethod
    def figurnetz(cls, geschlecht, morphs, bauart, meta=None):
        """Die Vertices der Figur MIT ihren Morphs, oder das Grundnetz.

        Derselbe Weg wie `/api/character/mesh/`: ein `CharacterState` bekommt
        Bauart und Regler und rechnet die Punkte. Ohne das misst man den
        Grundkoerper und schneidert am Nutzer vorbei.
        """
        # Metaregler (height, mass, tone, age) gehoeren zur Figur wie die
        # Morphs — bis zum 06.09.2026 wurden sie hier nicht gesetzt, und
        # eine Figur mit `height` wurde in Grundgroesse vermessen.
        if not morphs and not meta:
            return cls._grundnetz(geschlecht, bauart)
        try:
            from humanbody_core import CharacterState
            zustand = CharacterState(Charakterdaten.morphdaten(),
                                     Charakterdaten.voreinstellungen())
            zustand.set_body_type(
                bauart or cls.BAUART.get(geschlecht, 'Female_Caucasian'))
            for name, wert in (meta or {}).items():
                try:
                    zustand.set_meta(name, float(wert))
                except Exception:
                    logger.debug('GarmentCode: Meta %s uebergangen', name)
            for name, wert in (morphs or {}).items():
                try:
                    zustand.set_morph_value(name, float(wert))
                except Exception:
                    logger.debug('GarmentCode: Morph %s uebergangen', name)
            punkte = zustand.compute()
            if punkte is not None:
                return punkte
        except Exception:
            logger.exception('GarmentCode: Figurnetz nicht rechenbar')
        return cls._grundnetz(geschlecht, bauart)

    @classmethod
    def _vorlage(cls, geschlecht):
        """Die Masse eines GarmentCode-Referenzkoerpers."""
        import yaml
        from GarmentCode.entwurf import Entwurf
        datei = cls.VORLAGEN.get(geschlecht, cls.VORLAGEN['female'])
        pfad = os.path.join(Entwurf.REPO, 'assets', 'bodies', datei)
        with open(pfad, 'r', encoding='utf-8') as quelle:
            return yaml.safe_load(quelle)['body']

    @classmethod
    def _grundnetz(cls, geschlecht, bauart=None):
        """Die Vertices des Grundkoerpers, oder None.

        BEFUND 07.09.2026: Hier stand fest `vertices_tpose.npy` aus
        `data/humanBody` — der WEIBLICHEN Datenlage. Der maennliche
        Koerper hat aber eine eigene Topologie:

            Female_Caucasian   18.210 Punkte
            Male_Caucasian     17.996 Punkte

        Eine maennliche Figur OHNE Regler wurde damit am weiblichen Netz
        vermessen und mit dessen Punkten abgelegt, waehrend die Flaechen
        aus `data/humanBody_male` kamen (hoechster Index 17.995). Es gab
        keinen Fehler: Der Schnitt entstand aus weiblichen Massen, und die
        letzten 214 Punkte lagen unbenutzt in der OBJ-Datei. Sichtbar
        wurde es erst, als die Segmentierung fuer 18.210 Punkte auf ein
        17.996-Punkte-Netz traf.

        Die Basis kommt deshalb aus derselben Quelle wie bei
        `CharacterState`: `MorphData.l1[<Bauart>]`. Faellt sie aus, wird
        `None` zurueckgegeben — ein falsches Netz waere schlimmer als
        keines.
        """
        import numpy as np
        typ = bauart or cls.BAUART.get(geschlecht, cls.BAUART['female'])
        try:
            basis = Charakterdaten.morphdaten().l1.get(typ)
        except Exception:
            logger.exception('GarmentCode: Morphdaten nicht ladbar')
            basis = None
        if basis is None:
            logger.warning('GarmentCode: keine Basis fuer Bauart %s', typ)
            return None
        return np.asarray(basis, dtype=np.float64)

    # ---------------------------------------------------------------- erzeugen

    @staticmethod
    def regler(vorlage):
        """Die Feineinstellungen eines Kleidungsstuecks."""
        from GarmentCode.katalog import Katalog
        if not Katalog.kennt(vorlage):
            return []
        return Katalog.regler(vorlage)

    @classmethod
    def erzeugen(cls, vorlage, geschlecht='female', morphs=None, bauart=None,
                 name=None, regler=None, koerper=None, meta=None):
        """Ein Kleidungsstueck fuer die gewaehlte Figur bauen."""
        from GarmentCode.entwurf import Entwurf
        masse, _ = cls.masse(geschlecht, morphs=morphs, bauart=bauart,
                             koerper=koerper, meta=meta)
        name = name or ('%s_%s' % (vorlage, koerper or geschlecht))
        logger.info('GarmentCode: erzeuge %s (%s, %d Morphs, %d Regler%s)',
                    vorlage, geschlecht, len(morphs or {}), len(regler or {}),
                    (', Koerper %s' % koerper) if koerper else '')
        return Entwurf(vorlage, masse, regler=regler).erzeugen(name=name)

    # --------------------------------------------------------------- 3D

    @staticmethod
    def drapierbereit():
        """Steht die Simulationsumgebung? (eigenes Python + Warp-Fork)"""
        from GarmentCode.drapierung import Drapierung
        return Drapierung.bereit()

    @classmethod
    def drapieren(cls, spezifikation, koerper=None, geschlecht='female',
                  morphs=None, bauart=None, smpl=False, meta=None):
        """Schnittmuster -> 3D-Netz auf der Figur -> Rig.

        Der Ablauf steht in `garmentdrapierung.py` — er hat mit dem
        Schnittmuster nichts mehr zu tun und braucht den Koerper der Figur.
        """
        from .garmentdrapierung import Garmentdrapierung
        return Garmentdrapierung.lauf(spezifikation, geschlecht=geschlecht,
                                      morphs=morphs, bauart=bauart,
                                      koerper=koerper, smpl=smpl, meta=meta)

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
