# -*- coding: utf-8 -*-
u"""Smplfiguren — die Referenzkoerper von GarmentCode als Figur der Szene.

WARUM (Edgar, 06.09.2026: „keine experimente, baue erstmal das Online tool
nach!"): Das Online-Tool (garmentcode.ethz.ch, `upstream/gui/gui_pattern.py`)
drapiert auf `mean_all` — GarmentCodes eigenem Durchschnittskoerper — mit den
handvermessenen Massen aus `mean_all.yaml` und der Segmentierung
`ggg_body_segmentation.json`. Nichts wird gemessen. Genau diese Koerper
werden hier angeboten, `mean_all` voran; dazu die SMPL-Durchschnittskoerper
(`f_/m_smpl_average_A40`), fuer die GarmentCode ebenfalls Masse und eine
eigene Segmentierung (`smpl_vert_segmentation.json`) mitbringt.

Damit laeuft der GarmentCode-Reiter auf dieser Figur exakt so wie das Tool:
Schnitt aus den vorgegebenen Massen, Drapierung mit der zum Koerper
gehoerenden Segmentierung, keine Messung, keine Nachkorrektur. Was dabei
herauskommt, ist der Massstab fuer alles andere.

Die Koerper liegen im Upstream-Klon und werden nur gelesen.
"""

import logging
import os

logger = logging.getLogger('core')


class Smplfiguren:
    u"""Lesender Zugang zu GarmentCodes Referenzkoerpern."""

    #: Name -> Geschlecht, Segmentierung, Anzeige. `smpl` sagt, ob die
    #: Drapierung `smpl_vert_segmentation.json` braucht (SMPL-Topologie,
    #: 6.890 Punkte) oder `ggg_body_segmentation.json` (GarmentCodes eigenes
    #: Koerpermodell, 23.752 Punkte). Reihenfolge = Reihenfolge im Dialog.
    KOERPER = {
        'mean_all': {'geschlecht': 'female', 'smpl': False,
                     'anzeige': 'mean_all — Körper des Online-Tools'},
        'mean_female': {'geschlecht': 'female', 'smpl': False,
                        'anzeige': 'mean_female (GarmentCode)'},
        'mean_male': {'geschlecht': 'male', 'smpl': False,
                      'anzeige': 'mean_male (GarmentCode)'},
        'f_smpl_average_A40': {'geschlecht': 'female', 'smpl': True,
                               'anzeige': 'SMPL weiblich (Durchschnitt, A-Pose 40°)'},
        'm_smpl_average_A40': {'geschlecht': 'male', 'smpl': True,
                               'anzeige': 'SMPL männlich (Durchschnitt, A-Pose 40°)'},
    }

    @staticmethod
    def ordner():
        from GarmentCode.entwurf import Entwurf
        return os.path.join(Entwurf.REPO, 'assets', 'bodies')

    @classmethod
    def kennt(cls, name):
        from .smplvarianten import Smplvarianten
        return name in cls.KOERPER or Smplvarianten.vorhanden(name)

    @classmethod
    def ist_smpl(cls, name):
        u"""Braucht dieser Koerper die SMPL-Segmentierung?"""
        from .smplvarianten import Smplvarianten
        if Smplvarianten.ist_variante(name):
            return True          # Varianten sind SMPL-Netze, immer.
        return bool(cls.KOERPER.get(name, {}).get('smpl'))

    @classmethod
    def geschlecht(cls, name):
        from .smplvarianten import Smplvarianten
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.geschlecht(name)
        return cls.KOERPER.get(name, {}).get('geschlecht', 'female')

    @classmethod
    def liste(cls):
        u"""Die verfuegbaren Koerper mit dem, was die Seite zum Anzeigen braucht."""
        aus = []
        for name, angaben in cls.KOERPER.items():
            obj = os.path.join(cls.ordner(), name + '.obj')
            yaml_datei = os.path.join(cls.ordner(), name + '.yaml')
            if not os.path.isfile(obj):
                continue
            aus.append({
                'name': name,
                'anzeige': angaben['anzeige'],
                'geschlecht': angaben['geschlecht'],
                'smpl': angaben['smpl'],
                'bytes': os.path.getsize(obj),
                'masse_vorhanden': os.path.isfile(yaml_datei),
            })
        return aus

    @classmethod
    def masse(cls, name):
        u"""Die vorgegebenen Masse des Koerpers (dict, Zentimeter)."""
        import yaml
        from .smplvarianten import Smplvarianten
        cls._pruefen(name)
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.masse(name)
        with open(os.path.join(cls.ordner(), name + '.yaml'), 'r',
                  encoding='utf-8') as quelle:
            return yaml.safe_load(quelle)['body']

    @classmethod
    def netz(cls, name):
        u"""Punkte (Meter, Y oben — so wie GarmentCode und Three.js rechnen)
        und Dreiecke. Vierecke werden geteilt."""
        from GarmentCode.anziehen import Anziehen
        from .smplvarianten import Smplvarianten
        cls._pruefen(name)
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.netz(name)
        punkte, dreiecke = Anziehen.netz_lesen(
            os.path.join(cls.ordner(), name + '.obj'), aus_garmentcode=False)
        return punkte, dreiecke

    @classmethod
    def skelett(cls, name, punkte):
        u"""Das SMPL-Skelett zu diesem Netz — oder `None`.

        `None` ist hier eine Antwort, keine Panne: GarmentCodes eigene
        Koerper (`mean_all`, `mean_female`, `mean_male`) sind keine
        SMPL-Netze (23.752 statt 6.890 Punkte). Fuer sie wird das Skelett
        UEBERTRAGEN (`_uebertragen`); scheitert auch das, gibt es keines,
        und eines zu raten waere schlimmer.
        """
        kette = cls._kette(name, punkte)
        if kette is None:
            return None
        return {'name': cls._skelettname(name, punkte),
                'knochen': kette.bauplan()}

    #: Je Koerpername das fertige `Gelenkskelett`. Der Retarget-Motor
    #: braucht dasselbe Skelett wie der Browser, und es entsteht sonst bei
    #: jeder Anfrage neu — mit OBJ-Lesen und, bei fremder Topologie, einem
    #: cKDTree ueber 23.752 Punkte.
    _ketten = {}

    @classmethod
    def kette(cls, name):
        u"""Das `Gelenkskelett` des Koerpers `name` — oder `None`.

        Der Weg des Retarget-Motors: Er kennt nur den Namen, nicht das
        Netz. Gelesen wird je Name einmal; die Grundkoerper liegen
        unveraenderlich im Upstream, und eine Formvariante traegt einen
        Fingerabdruck ihrer Betas im Namen (`Smplvarianten`).
        """
        if not name:
            raise ValueError('Ohne Koerpernamen kein SMPL-Skelett')
        if name in cls._ketten:
            return cls._ketten[name]
        cls._pruefen(name)
        punkte, _ = cls.netz(name)
        cls._ketten[name] = cls._kette(name, punkte)
        return cls._ketten[name]

    @classmethod
    def haut(cls, name, punkte):
        u"""Hautgewichte fuer dieses Netz — oder `None`.

        `{knochen: [Namen], index: (N,4), gewicht: (N,4)}` — die beiden
        Felder als numpy, damit der Endpunkt sie base64-kodiert ausliefern
        kann (23.752 Punkte x 8 Zahlen sind als JSON-Liste 1,5 MB). Die
        Knochen stehen als NAMEN da: Ihre Nummer im `THREE.Skeleton` haengt
        an der Reihenfolge des Bauplans, und die soll sich aendern duerfen,
        ohne dass die Gewichte still verrutschen.

        Ohne Gewichte bleibt die Figur ein starres Netz — sichtbar erst
        beim Abspielen, wenn das Skelett sich bewegt und die Haut nicht.
        """
        from django.conf import settings
        from SMPL.gelenke import Smplgelenke
        from SMPL.haut import Smplhaut
        try:
            gewichte = Smplhaut.aus_modell(cls.geschlecht(name),
                                           str(settings.SMPL_MODELS_DIR))
            zuordnung = (None if Smplgelenke.passt(punkte)
                         else cls._hautzuordnung(name, punkte))
            index, anteil = gewichte.fuer_punkte(len(punkte), zuordnung)
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('SMPL-Hautgewichte fuer %s nicht baubar: %s',
                           name, fehler)
            return None
        return {'knochen': Smplhaut.knochennamen(),
                'index': index, 'gewicht': anteil}

    @classmethod
    def _hautzuordnung(cls, name, punkte):
        u"""Je Punkt des fremden Netzes der naechste SMPL-Punkt.

        Die UMGEKEHRTE Richtung zu `_zuordnung`: Dort wird je SMPL-Punkt ein
        fremder gesucht (6.890 Eintraege, Eingabe des Regressors), hier je
        fremdem Punkt ein SMPL-Punkt (23.752 Eintraege, ein Gewicht je
        Punkt des angezeigten Netzes). Wer die eine fuer die andere haelt,
        legt 6.890 Gewichte auf 23.752 Punkte — die Figur zerrisse beim
        ersten Bild.
        """
        from django.conf import settings
        from SMPL.koerper import Smplkoerper
        from SMPL.uebertrag import Netzuebertrag
        modell = Smplkoerper.laden(cls.geschlecht(name),
                                   str(settings.SMPL_MODELS_DIR))
        referenz = modell.a40(None, grad=cls._armwinkel(name))
        uebertrag = Netzuebertrag.bauen(punkte, referenz)
        guete = uebertrag.guete
        logger.info('SMPL-Hautgewichte uebertragen auf %s: Zuordnung Median '
                    '%.4f, p90 %.4f der Koerperhoehe',
                    name, guete['median'], guete['p90'])
        return uebertrag.zuordnung

    @classmethod
    def ketten_vergessen(cls):
        u"""Den Speicher leeren — fuer Tests und nach einem Datenwechsel."""
        cls._ketten = {}

    @classmethod
    def _kette(cls, name, punkte):
        from django.conf import settings
        from SMPL.gelenke import Smplgelenke
        try:
            gelenke = Smplgelenke.aus_modell(cls.geschlecht(name),
                                             str(settings.SMPL_MODELS_DIR))
            if Smplgelenke.passt(punkte):
                return gelenke.kette(punkte)
            return gelenke.kette_uebertragen(
                punkte, cls._zuordnung(name, punkte, gelenke))
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('SMPL-Skelett fuer %s nicht baubar: %s', name, fehler)
            return None

    @classmethod
    def _skelettname(cls, name, punkte):
        from SMPL.gelenke import Smplgelenke
        return ('SMPL (24 Gelenke)' if Smplgelenke.passt(punkte)
                else 'SMPL (24 Gelenke, uebertragen)')

    @classmethod
    def _zuordnung(cls, name, punkte, gelenke):
        u"""Der `Netzuebertrag` fuer GarmentCodes eigene Koerper (GGG-Topologie).

        `mean_all`, `mean_female` und `mean_male` haben 23.752 Punkte, der
        Regressor 6.890 Spalten. Zugeordnet wird ueber einen SMPL-Koerper
        IN DERSELBEN HALTUNG: `arm_pose_angle` steht in der YAML des
        Koerpers (mean_all: 45,483 Grad, die SMPL-Koerper stehen bei 40).
        Wer das ueberspringt, verzieht Schulter und Ellbogen.
        """
        from django.conf import settings
        from SMPL.koerper import Smplkoerper
        haltung = cls._armwinkel(name)
        modell = Smplkoerper.laden(cls.geschlecht(name),
                                   str(settings.SMPL_MODELS_DIR))
        referenz = modell.a40(None, grad=haltung)
        uebertrag = gelenke.uebertragen(punkte, referenz)
        guete = uebertrag.guete
        logger.info('SMPL-Skelett uebertragen auf %s (%d Punkte, %.1f Grad): '
                    'Zuordnung Median %.4f, p90 %.4f der Koerperhoehe',
                    name, len(punkte), haltung, guete['median'], guete['p90'])
        return uebertrag

    #: Ohne Angabe in der YAML die A-Haltung der SMPL-Koerper.
    ARMWINKEL_VORGABE = 40.0

    @classmethod
    def _armwinkel(cls, name):
        u"""`arm_pose_angle` des Koerpers in Grad."""
        try:
            wert = cls.masse(name).get('arm_pose_angle')
            return float(wert) if wert is not None else cls.ARMWINKEL_VORGABE
        # stumm gewollt: ohne lesbare YAML gilt der Winkel der Vorgabe — die Figur
        # laedt trotzdem
        except (OSError, ValueError, KeyError, TypeError):
            return cls.ARMWINKEL_VORGABE

    @classmethod
    def _pruefen(cls, name):
        if not cls.kennt(name):
            raise ValueError('Unbekannter Referenzkoerper: %r' % (name,))
