# -*- coding: utf-8 -*-
"""Smplfiguren — die Referenzkoerper von GarmentCode als Figur der Szene.

WARUM (Edgar, 06.09.2026: „keine experimente, baue erstmal das Online tool
nach!"): Das Online-Tool (garmentcode.ethz.ch, `upstream/gui/gui_pattern.py`)
drapiert auf `mean_all` — GarmentCodes eigenem Durchschnittskoerper — mit den
handvermessenen Massen aus `mean_all.yaml` und der Segmentierung
`ggg_body_segmentation.json`. Nichts wird gemessen. Genau diese Koerper
werden hier angeboten, `mean_all` voran.

SMPL-X STATT SMPL (Edgar, 15.09.2026: „kannst du die SMPL Modelle auf SMPL-X
umstellen (also inkl. Gesichtsknochen)?"): Die beiden SMPL-Durchschnitte
des Tools (`f_/m_smpl_average_A40`, 6.890 Punkte, 24 Gelenke) sind aus dem
Katalog genommen; an ihrer Stelle stehen die SMPL-X-Durchschnittskoerper
(`smplx_female`, `smplx_male`: 10.475 Punkte, 55 Gelenke — Kiefer, Augen,
Finger), gebaut aus dem Modell in derselben A-Haltung (40 Grad,
`SMPL/xkoerper.py`) und abgelegt wie jede Variante (`Smplvarianten`).
Die Masse bleiben die der Tool-YAML — bei Betas 0 exakt, sonst relativ
dazu (`SMPL/masse.py`).

Die alten Namen bleiben LADBAR (gespeicherte Szenen und Projekte): Sie
bekommen das SMPL-X-Skelett uebertragen wie GarmentCodes eigene Koerper.

Skelett und Haut: `core/dienste/smplxrig.py`.
"""

import logging
import os

logger = logging.getLogger('core')


class Smplfiguren:
    """Lesender Zugang zu GarmentCodes Referenzkoerpern und den SMPL-X-Koerpern."""

    #: Die Koerper des Dialogs, in seiner Reihenfolge. `smpl` sagt, ob die
    #: Drapierung `smpl_vert_segmentation.json` braucht (SMPL-Topologie,
    #: fuer SMPL-X in der uebertragenen Fassung) oder
    #: `ggg_body_segmentation.json` (GarmentCodes eigenes Koerpermodell,
    #: 23.752 Punkte).
    KOERPER = {
        'mean_all': {'geschlecht': 'female', 'smpl': False, 'anzeige': 'mean_all — Körper des Online-Tools'},
        'mean_female': {'geschlecht': 'female', 'smpl': False, 'anzeige': 'mean_female (GarmentCode)'},
        'mean_male': {'geschlecht': 'male', 'smpl': False, 'anzeige': 'mean_male (GarmentCode)'},
        'smplx_female': {
            'geschlecht': 'female',
            'smpl': True,
            'anzeige': 'SMPL-X weiblich (Durchschnitt, A-Pose 40°)',
        },
        'smplx_male': {
            'geschlecht': 'male',
            'smpl': True,
            'anzeige': 'SMPL-X männlich (Durchschnitt, A-Pose 40°)',
        },
    }

    #: Fassung des Skeletts, das `kette` liefert — steht im Namen der
    #: Retarget-Ablage (`Retargetdaten.ablage`). 1 = SMPL, 24 Gelenke (bis
    #: 14.09.2026); 2 = SMPL-X, 55 Gelenke, Kopf zeigt weiter wie der Hals.
    #: Ohne die Nummer faenden alte Ablagen mit 24 Gelenken weiter Verwendung.
    SKELETTFASSUNG = 2

    #: Die SMPL-Durchschnitte des Tools: nicht mehr im Dialog, aber ladbar —
    #: und ihre YAML ist die Massvorlage der SMPL-X-Koerper.
    VERSTECKT = {
        'f_smpl_average_A40': {'geschlecht': 'female', 'smpl': True},
        'm_smpl_average_A40': {'geschlecht': 'male', 'smpl': True},
    }

    #: Hautfarbige Fotofläche für den ganzen Körper (25.09.2026, „SMPL-X-
    #: Texturen") — abgeleitet aus den Meshcapade-Beispieltexturen für
    #: SMPL/SMPL-X (`f_01_alb.002.png`/`m_01_alb.002.png`, SMPL-Body
    #: CC-BY-4.0, https://github.com/Meshcapade/SMPL_texture_samples):
    #: Gesicht/Hände/Füße sind das Originalfoto, die dort aufgedruckte
    #: Beispiel-Kleidung (Torso/Arme/Beine) wurde durch die echte
    #: Hautfarbe der angrenzenden Fotostellen ersetzt (Inpainting,
    #: `ProjektTemp/_wegwerf/smplxuv/hautfuellen2.py`) — eine erfundene
    #: Ausstrahlung ins Nichts wäre schlimmer als eine glatte Fläche.
    TEXTUR_DATEI = {'female': 'weiblich_haut.jpg', 'male': 'maennlich_haut.jpg'}

    @classmethod
    def textur_pfad(cls, geschlecht):
        """Pfad zur Hautfoto-Textur — oder `None`, wenn sie fehlt."""
        datei = cls.TEXTUR_DATEI.get(str(geschlecht))
        if not datei:
            return None
        pfad = os.path.join(cls.ordner_texturen(), datei)
        return pfad if os.path.isfile(pfad) else None

    @staticmethod
    def ordner_texturen():
        from django.conf import settings

        return os.path.join(str(settings.SMPLX_MODELS_DIR), 'texturen')

    @staticmethod
    def ordner():
        from GarmentCode.entwurf import Entwurf

        return os.path.join(Entwurf.REPO, 'assets', 'bodies')

    @classmethod
    def kennt(cls, name):
        from .smplvarianten import Smplvarianten

        return name in cls.KOERPER or name in cls.VERSTECKT or Smplvarianten.vorhanden(name)

    @classmethod
    def ist_smpl(cls, name):
        """Braucht dieser Koerper die SMPL-Segmentierung?"""
        from .smplvarianten import Smplvarianten

        if Smplvarianten.ist_variante(name):
            return True  # Varianten sind SMPL-X-Netze, immer.
        angaben = cls.KOERPER.get(name) or cls.VERSTECKT.get(name, {})
        return bool(angaben.get('smpl'))

    @classmethod
    def geschlecht(cls, name):
        from .smplvarianten import Smplvarianten

        if Smplvarianten.ist_variante(name):
            return Smplvarianten.geschlecht(name)
        angaben = cls.KOERPER.get(name) or cls.VERSTECKT.get(name, {})
        return angaben.get('geschlecht', 'female')

    @classmethod
    def liste(cls):
        """Die verfuegbaren Koerper mit dem, was die Seite zum Anzeigen braucht."""
        from .smplvarianten import Smplvarianten
        from .smplxrig import Smplxrig

        aus = []
        for name, angaben in cls.KOERPER.items():
            if angaben['smpl']:
                if not Smplxrig.vorhanden(angaben['geschlecht']):
                    continue
                groesse = Smplvarianten.groesse(name)
            else:
                obj = os.path.join(cls.ordner(), name + '.obj')
                if not os.path.isfile(obj):
                    continue
                groesse = os.path.getsize(obj)
            aus.append(
                {
                    'name': name,
                    'anzeige': angaben['anzeige'],
                    'geschlecht': angaben['geschlecht'],
                    'smpl': angaben['smpl'],
                    'bytes': groesse,
                    'masse_vorhanden': True
                    if angaben['smpl']
                    else os.path.isfile(os.path.join(cls.ordner(), name + '.yaml')),
                }
            )
        # Dahinter die GESPEICHERTEN SMPL-X-Figuren (`data/models/*.json` mit
        # `quelle: smpl`, 25.09.2026 — bis dahin zeigte „Charakter hinzufuegen"
        # im SMPL-X-Reiter nur den Katalog, ein gespeichertes Modell wie
        # „SMPLX1" tauchte dort nie auf; Edgar musste es ueber „Datei laden"
        # umgehen). `gespeichert: True`, der Dialog stellt sie in den zweiten
        # Bereich (wie bei Genesis 9, `G9figur._gespeicherte`).
        aus += cls._gespeicherte()
        return aus

    @classmethod
    def _gespeicherte(cls):
        from ..dienste.modellkatalog import Modellkatalog

        aus = []
        for eintrag in Modellkatalog.gespeicherte():
            if eintrag['quelle'] != 'smpl':
                continue
            figur = Modellkatalog.gespeichert(eintrag['name'], 'smpl')
            if figur is None:
                continue
            aus.append(
                {
                    'name': eintrag['name'],
                    'anzeige': eintrag['name'],
                    'geschlecht': figur.get('geschlecht') or 'female',
                    'smpl': True,
                    'bytes': 0,
                    'masse_vorhanden': False,
                    'gespeichert': True,
                }
            )
        return aus

    @classmethod
    def uv_felder(cls, dreiecke):
        u"""`{uv, uv_dreiecke, uv_ursprung}` fuers Browsernetz — oder `None`,
        wenn die UV-Datei fehlt oder die Topologie nicht passt (kein SMPL-X-
        Netz). Nur fuer `smpl`-Koerper aufrufen (25.09.2026, „SMPL-X-
        Texturen"); `Smplxuv` prueft die Dreieckszahl trotzdem selbst.
        """
        from SMPL.xuv import Smplxuv

        if not Smplxuv.vorhanden():
            return None
        try:
            uv, uv_dreiecke, ursprung = Smplxuv.teilen(dreiecke)
        except ValueError as fehler:
            logger.warning('SMPL-X-UV nicht anwendbar: %s', fehler)
            return None
        return {
            'uv': uv.tolist(),
            'uv_dreiecke': uv_dreiecke.tolist(),
            'uv_ursprung': ursprung.tolist(),
        }

    @classmethod
    def masse(cls, name):
        """Die vorgegebenen Masse des Koerpers (dict, Zentimeter)."""
        import yaml

        from .smplvarianten import Smplvarianten

        cls._pruefen(name)
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.masse(name)
        with open(os.path.join(cls.ordner(), name + '.yaml'), encoding='utf-8') as quelle:
            return yaml.safe_load(quelle)['body']

    @classmethod
    def netz(cls, name):
        """Punkte (Meter, Y oben — so wie GarmentCode und Three.js rechnen)
        und Dreiecke. Vierecke werden geteilt."""
        from GarmentCode.anziehen import Anziehen

        from .smplvarianten import Smplvarianten

        cls._pruefen(name)
        if Smplvarianten.ist_variante(name):
            return Smplvarianten.netz(name)
        punkte, dreiecke = Anziehen.netz_lesen(
            os.path.join(cls.ordner(), name + '.obj'), aus_garmentcode=False
        )
        return punkte, dreiecke

    # --------------------------------------------------------- Skelett, Haut

    @classmethod
    def skelett(cls, name, punkte):
        """Das SMPL-X-Skelett zu diesem Netz — oder `None`.

        `None` ist eine Antwort, keine Panne: Ohne Modelldatei gibt es
        keines, und eines zu raten waere schlimmer. Fremde Topologie
        (GarmentCodes eigene Koerper, die alten SMPL-Koerper) wird
        uebertragen (`Smplxrig`).
        """
        from .smplxrig import Smplxrig

        return Smplxrig.skelett(name, punkte, cls.geschlecht(name), cls._armwinkel(name))

    #: Je Koerpername das fertige `Gelenkskelett`. Der Retarget-Motor
    #: braucht dasselbe Skelett wie der Browser, und es entsteht sonst bei
    #: jeder Anfrage neu — mit OBJ-Lesen und, bei fremder Topologie, einem
    #: cKDTree ueber 23.752 Punkte.
    _ketten = {}

    @classmethod
    def kette(cls, name):
        """Das `Gelenkskelett` des Koerpers `name` — oder `None`.

        Der Weg des Retarget-Motors: Er kennt nur den Namen, nicht das
        Netz. Gelesen wird je Name einmal; die Grundkoerper liegen
        unveraenderlich im Upstream, und eine Formvariante traegt einen
        Fingerabdruck ihrer Betas im Namen (`Smplvarianten`).
        """
        from .smplxrig import Smplxrig

        if not name:
            raise ValueError('Ohne Koerpernamen kein SMPL-X-Skelett')
        if name in cls._ketten:
            return cls._ketten[name]
        cls._pruefen(name)
        punkte, _ = cls.netz(name)
        cls._ketten[name] = Smplxrig.kette(name, punkte, cls.geschlecht(name), cls._armwinkel(name))
        return cls._ketten[name]

    @classmethod
    def haut(cls, name, punkte):
        """Hautgewichte fuer dieses Netz — oder `None`.

        `{knochen: [Namen], index: (N,4), gewicht: (N,4)}`, die Felder als
        numpy (base64 im Endpunkt). Knochen als NAMEN: Ihre Nummer im
        `THREE.Skeleton` haengt an der Reihenfolge des Bauplans.
        """
        from .smplxrig import Smplxrig

        return Smplxrig.hautgewichte(name, punkte, cls.geschlecht(name), cls._armwinkel(name))

    @classmethod
    def ketten_vergessen(cls):
        """Den Speicher leeren — fuer Tests und nach einem Datenwechsel."""
        cls._ketten = {}

    #: Ohne Angabe in der YAML die A-Haltung der SMPL-Koerper.
    ARMWINKEL_VORGABE = 40.0

    @classmethod
    def _armwinkel(cls, name):
        """`arm_pose_angle` des Koerpers in Grad — die Haltung, in der ein
        Uebertrag auf fremde Topologie gerechnet wird."""
        try:
            wert = cls.masse(name).get('arm_pose_angle')
            return float(wert) if wert is not None else cls.ARMWINKEL_VORGABE
        # stumm gewollt: ohne lesbare YAML gilt der Winkel der Vorgabe — die Figur
        # laedt trotzdem
        except OSError, ValueError, KeyError, TypeError:
            return cls.ARMWINKEL_VORGABE

    @classmethod
    def _pruefen(cls, name):
        if not cls.kennt(name):
            raise ValueError('Unbekannter Referenzkoerper: %r' % (name,))
