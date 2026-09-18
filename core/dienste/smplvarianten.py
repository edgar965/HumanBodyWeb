# -*- coding: utf-8 -*-
"""Smplvarianten — SMPL-X-Koerper in Form und A-Haltung, so abgelegt, wie
GarmentCode sie zum Drapieren braucht.

WARUM (Edgar, 06.09.2026: „5 Testfälle für das Fitting mit unterschiedlichen
SMPL Modellen"): GarmentCode liefert nur die Durchschnittskoerper. Eine
Variante entsteht hier aus dem Modell des Projekts (Blendshapes + A-Haltung
40 Grad, `SMPL/xkoerper.py`) und bekommt ihre Masse RELATIV zur Tool-YAML
(`SMPL/masse.py`).

SEIT DEM 15.09.2026 SMPL-X (Edgar: „die SMPL Modelle auf SMPL-X umstellen").
Abgelegt wird in `GarmentCode/koerper/smplx/`: `<name>.obj` (Meter, Y oben),
`<name>.yaml` und daneben `smpl_vert_segmentation.json` — die SMPL-Datei
des Tools, ueber die Transferdaten von SMPL-X auf 10.475 Punkte uebertragen
(`SMPL/xsegmentierung.py`). `PathCofig(smpl_body=True)` findet dort alles.

Auch die DURCHSCHNITTSKOERPER (Betas 0) sind hier Varianten — `smplx_female`
und `smplx_male`, mit festem Namen statt Fingerabdruck, denn sie stehen im
Dialog. Ihre Masse sind exakt die YAML des SMPL-Durchschnitts des Tools
(Verhaeltnis 1); `arm_length` kommt aus den SMPL-X-Gelenken.

Die alten SMPL-Varianten (`smpl_f_…` in `koerper/smpl/`) bleiben LADBAR,
damit gespeicherte Szenen aufgehen; neu erzeugt wird dort nichts mehr.
"""

import hashlib
import logging
import os

import numpy as np
from django.conf import settings

logger = logging.getLogger("core")


class Smplvarianten:
    """Erzeugt, benennt und legt SMPL-X-Varianten ab."""

    #: Woher das SMPL-X-Modell und die Transferdaten kommen.
    MODELLE = str(settings.SMPLX_MODELS_DIR)

    PRAEFIX = "smplx_"
    PRAEFIX_ALT = "smpl_"

    #: Der Durchschnittskoerper (Betas 0) je Geschlecht — fester Name.
    DURCHSCHNITT = {"female": "smplx_female", "male": "smplx_male"}

    #: Der SMPL-Durchschnitt des Tools je Geschlecht — er traegt die YAML,
    #: die Massvorlage aller Varianten.
    VORLAGE = {"female": "f_smpl_average_A40", "male": "m_smpl_average_A40"}

    _erzeugt = {}
    _segmentierung = None

    @staticmethod
    def ordner():
        from GarmentCode.koerperablage import Koerperablage

        return os.path.join(Koerperablage.ORDNER, "smplx")

    @staticmethod
    def ordner_alt():
        from GarmentCode.koerperablage import Koerperablage

        return os.path.join(Koerperablage.ORDNER, "smpl")

    # ---------------------------------------------------------------- Namen

    @classmethod
    def name(cls, geschlecht, betas):
        b = np.zeros(10)
        betas = np.asarray(betas or [], dtype=np.float64)
        b[: min(10, len(betas))] = betas[:10]
        if not np.any(np.abs(b) >= 0.0005):
            return cls.DURCHSCHNITT[geschlecht]
        rohbytes = np.round(b, 3).astype(np.float32).tobytes()
        kennung = hashlib.sha1(rohbytes).hexdigest()[:12]
        return "%s%s_%s" % (cls.PRAEFIX, geschlecht[0], kennung)

    @classmethod
    def ist_variante(cls, name):
        name = str(name)
        return name.startswith(cls.PRAEFIX) or name.startswith(cls.PRAEFIX_ALT)

    @classmethod
    def ist_alt(cls, name):
        """Eine SMPL-Variante von vor dem 15.09.2026 (6.890 Punkte)?"""
        name = str(name)
        return name.startswith(cls.PRAEFIX_ALT) and not name.startswith(cls.PRAEFIX)

    @classmethod
    def geschlecht(cls, name):
        """Das Geschlecht steckt im Namen (`smplx_female`, `smplx_f_…`, `smpl_m_…`)."""
        teile = str(name).split("_")
        kurz = teile[1] if len(teile) > 1 else ""
        return "male" if kurz in ("m", "male") else "female"

    @classmethod
    def _ordner_von(cls, name):
        return cls.ordner_alt() if cls.ist_alt(name) else cls.ordner()

    @classmethod
    def vorhanden(cls, name):
        if not cls.ist_variante(name):
            return False
        if name in cls.DURCHSCHNITT.values():
            return True  # wird beim ersten Zugriff gebaut
        return os.path.isfile(os.path.join(cls._ordner_von(name), name + ".obj"))

    @classmethod
    def groesse(cls, name):
        """Bytes der abgelegten OBJ — 0, solange sie noch nicht gebaut ist."""
        pfad = os.path.join(cls._ordner_von(name), name + ".obj")
        return os.path.getsize(pfad) if os.path.isfile(pfad) else 0

    # ------------------------------------------------------------- erzeugen

    @classmethod
    def modell(cls, geschlecht):
        from .smplxrig import Smplxrig

        return Smplxrig.koerper(geschlecht)

    @classmethod
    def segmentierung(cls):
        """Die SMPL-X-Segmentierung — einmal gebaut, dann von der Platte."""
        from SMPL.xsegmentierung import Smplxsegmentierung
        from .smplfigur import Smplfiguren

        if cls._segmentierung is None:
            quelle = os.path.join(Smplfiguren.ordner(), Smplxsegmentierung.DATEINAME)
            Smplxsegmentierung.bereitstellen(quelle, cls.MODELLE, cls.ordner())
            cls._segmentierung = Smplxsegmentierung.lesen(cls.ordner())
        return cls._segmentierung

    @classmethod
    def erzeugen(cls, geschlecht, betas):
        """Koerper, Masse und Ablage einer Variante.

        Rueckgabe: {name, ordner, geschlecht, betas, punkte (Meter, Y oben),
        dreiecke, hoehe, masse, herkunft}.
        """
        from GarmentCode.koerperablage import Koerperablage
        from SMPL.masse import Smplmasse
        from .smplfigur import Smplfiguren

        name = cls.name(geschlecht, betas)
        if name in cls._erzeugt:
            return cls._erzeugt[name]

        modell = cls.modell(geschlecht)
        v = modell.a40(betas)
        v_avg = modell.a40(None)
        yaml_avg = Smplfiguren.masse(cls.VORLAGE[geschlecht])
        # Die Armlaenge kommt aus den Gelenken, nicht aus der YAML: dort
        # stehen 80 cm bei 165 cm Koerpergroesse (siehe Smplkoerper.armlaenge).
        masse, herkunft = Smplmasse(cls.segmentierung()).relativ(
            v, v_avg, yaml_avg, zusatz={"arm_length": modell.armlaenge(betas)}
        )

        ordner = cls.ordner()
        if not os.path.isfile(os.path.join(ordner, name + ".obj")):
            # Koerperablage rechnet Projekt -> GarmentCode; die Punkte hier
            # SIND schon GarmentCode-Lage, also erst hin, damit sie zurueck
            # genau so landen.
            Koerperablage(name, Smplmasse.projekt(v), modell.faces, ordner=ordner).ablegen(masse)
        daten = {
            "name": name,
            "ordner": ordner,
            "geschlecht": geschlecht,
            "betas": [float(x) for x in (betas or [])],
            "punkte": v,
            "dreiecke": modell.faces,
            "hoehe": float(v[:, 1].max() - v[:, 1].min()),
            "masse": masse,
            "herkunft": herkunft,
        }
        cls._erzeugt[name] = daten
        logger.info(
            "SMPL-X-Variante %s: %s, Betas %s, %.1f cm, Taille %.0f cm",
            name,
            geschlecht,
            daten["betas"],
            daten["hoehe"] * 100,
            masse.get("waist", 0),
        )
        return daten

    @classmethod
    def aus_reglern(cls, geschlecht, groesse=0.0, fuelle=0.0):
        """Der Weg, den das Bedienfeld geht: zwei Regler statt zehn Betas.

        Die Umrechnung samt der je Geschlecht verschiedenen Vorzeichen steht
        in `SMPL/form.py` — dort auch, warum sie gemessen und nicht geraten ist.
        """
        from SMPL.form import Smplform

        return cls.erzeugen(geschlecht, Smplform.betas(geschlecht, groesse, fuelle))

    @classmethod
    def sicherstellen(cls, name):
        """Einen Durchschnittskoerper bauen, falls seine Dateien fehlen."""
        for geschlecht, durchschnitt in cls.DURCHSCHNITT.items():
            if name == durchschnitt and not os.path.isfile(os.path.join(cls.ordner(), name + ".obj")):
                cls.erzeugen(geschlecht, None)

    # ----------------------------------------------------------------- lesen

    @classmethod
    def masse(cls, name):
        """Die abgelegten Masse einer Variante (aus ihrer YAML)."""
        import yaml

        cls.sicherstellen(name)
        pfad = os.path.join(cls._ordner_von(name), name + ".yaml")
        with open(pfad, "r", encoding="utf-8") as quelle:
            return yaml.safe_load(quelle)["body"]

    @classmethod
    def netz(cls, name):
        """Punkte (Meter, Y oben) und Dreiecke einer abgelegten Variante."""
        from GarmentCode.anziehen import Anziehen

        cls.sicherstellen(name)
        return Anziehen.netz_lesen(os.path.join(cls._ordner_von(name), name + ".obj"), aus_garmentcode=False)
