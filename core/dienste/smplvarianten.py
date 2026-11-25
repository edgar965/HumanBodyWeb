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
import json
import logging
import os
import threading

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from django.conf import settings

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')


class Smplvarianten:
    """Erzeugt, benennt und legt SMPL-X-Varianten ab."""

    #: Woher das SMPL-X-Modell und die Transferdaten kommen.
    MODELLE = str(settings.SMPLX_MODELS_DIR)

    PRAEFIX = 'smplx_'
    PRAEFIX_ALT = 'smpl_'

    #: Der Durchschnittskoerper (Betas 0) je Geschlecht — fester Name.
    DURCHSCHNITT = {'female': 'smplx_female', 'male': 'smplx_male'}

    #: Der SMPL-Durchschnitt des Tools je Geschlecht — er traegt die YAML,
    #: die Massvorlage aller Varianten.
    VORLAGE = {'female': 'f_smpl_average_A40', 'male': 'm_smpl_average_A40'}

    #: Die Betas einer Variante, von der nur die Form gerechnet ist (`form`): Masse, OBJ und YAML entstehen daraus, wenn sie jemand braucht (`sicherstellen`).
    BETAS = '.betas.json'

    _erzeugt = {}
    _segmentierung = None
    _schloss = threading.RLock()

    @staticmethod
    def ordner():
        from GarmentCode.koerperablage import Koerperablage

        return os.path.join(Koerperablage.ORDNER, 'smplx')

    @staticmethod
    def ordner_alt():
        from GarmentCode.koerperablage import Koerperablage

        return os.path.join(Koerperablage.ORDNER, 'smpl')

    # ---------------------------------------------------------------- Namen

    @classmethod
    def name(cls, geschlecht, betas):
        betas = Torchfeld.feld(betas if betas is not None else [], dtype=torch.float64)
        b = torch.zeros(max(10, len(betas)), dtype=torch.float64, device='cuda')
        b[: len(betas)] = betas
        if not Torchfeld.any(Torchfeld.abs(b) >= 0.0005):
            return cls.DURCHSCHNITT[geschlecht]
        # Fingerabdruck ueber zehn Betas, solange 10.. leer sind — so behalten
        # alle Varianten von vor den Massreglern (25.09.2026) ihren Namen und
        # ihre abgelegte Datei; mit Massreglern ueber alle.
        if not Torchfeld.any(Torchfeld.abs(b[10:]) >= 0.0005):
            b = b[:10]
        rohbytes = Torchfeld.als_bytes(Torchfeld.astype(Torchfeld.round(b, 3), torch.float32))
        kennung = hashlib.sha1(rohbytes).hexdigest()[:12]
        return '%s%s_%s' % (cls.PRAEFIX, geschlecht[0], kennung)

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
        teile = str(name).split('_')
        kurz = teile[1] if len(teile) > 1 else ''
        return 'male' if kurz in ('m', 'male') else 'female'

    @classmethod
    def _ordner_von(cls, name):
        return cls.ordner_alt() if cls.ist_alt(name) else cls.ordner()

    @classmethod
    def vorhanden(cls, name):
        if not cls.ist_variante(name):
            return False
        if name in cls.DURCHSCHNITT.values():
            return True  # wird beim ersten Zugriff gebaut
        return any(os.path.isfile(os.path.join(cls._ordner_von(name), name + e)) for e in ('.obj', cls.BETAS))

    @classmethod
    def vorlage(cls, name):
        """Der Koerper, dessen YAML die Winkel einer SMPL-X-Variante vorgibt — sonst der Name selbst."""
        return cls.VORLAGE[cls.geschlecht(name)] if str(name).startswith(cls.PRAEFIX) else name

    @classmethod
    def groesse(cls, name):
        """Bytes der abgelegten OBJ — 0, solange sie noch nicht gebaut ist."""
        pfad = os.path.join(cls._ordner_von(name), name + '.obj')
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
    def form(cls, geschlecht, betas):
        """Nur die Form einer Variante — das, was ein Reglerzug braucht (18 ms; mit Massen und Ablage 13,5 s, gemessen 25.11.2026). Masse und Dateien: `sicherstellen`."""
        name, modell = cls.name(geschlecht, betas), cls.modell(geschlecht)
        v = modell.a40(betas)
        betas = [float(x) for x in (betas if betas is not None else [])]
        pfad = os.path.join(cls.ordner(), name + cls.BETAS)
        if not cls._abgelegt(name) and name not in cls.DURCHSCHNITT.values() and not os.path.isfile(pfad):
            AtomarSchreiber.json_schreiben(pfad, betas, einzug=None)
        return {'name': name, 'ordner': cls.ordner(), 'geschlecht': geschlecht, 'betas': betas, 'punkte': v, 'dreiecke': modell.faces,
                'hoehe': float(v[:, 1].max() - v[:, 1].min())}

    @classmethod
    def _abgelegt(cls, name):
        return all(os.path.isfile(os.path.join(cls._ordner_von(name), name + e)) for e in ('.obj', '.yaml'))

    @classmethod
    def erzeugen(cls, geschlecht, betas):
        with cls._schloss:                  # zwei Anfragen nach derselben Variante messen sie nur einmal
            return cls._erzeugen(geschlecht, betas)

    @classmethod
    def _erzeugen(cls, geschlecht, betas):
        """Koerper, Masse und Ablage einer Variante.

        Rueckgabe: {name, ordner, geschlecht, betas, punkte (Meter, Y oben),
        dreiecke, hoehe, masse, herkunft}.
        """
        from GarmentCode.koerperablage import Koerperablage
        from SMPL.masse import Smplmasse

        from .smplvariantenmasse import Smplvariantenmasse

        name = cls.name(geschlecht, betas)
        if name in cls._erzeugt:
            return cls._erzeugt[name]

        modell = cls.modell(geschlecht)
        daten = cls.form(geschlecht, betas)
        v = daten['punkte']
        masse, herkunft = Smplvariantenmasse.von(geschlecht, betas, v)

        ordner = cls.ordner()
        if not cls._abgelegt(name):
            # Koerperablage rechnet Projekt -> GarmentCode; die Punkte hier
            # SIND schon GarmentCode-Lage, also erst hin, damit sie zurueck
            # genau so landen.
            Koerperablage(name, Smplmasse.projekt(v), modell.faces, ordner=ordner).ablegen(masse)
        daten.update(masse=masse, herkunft=herkunft)
        cls._erzeugt[name] = daten
        logger.info(
            'SMPL-X-Variante %s: %s, Betas %s, %.1f cm, Taille %.0f cm',
            name,
            geschlecht,
            daten['betas'][:10] + (['… %d Betas' % len(daten['betas'])] if len(daten['betas']) > 10 else []),
            daten['hoehe'] * 100,
            masse.get('waist', 0),
        )
        return daten

    @classmethod
    def aus_reglern(cls, geschlecht, groesse=0.0, fuelle=0.0, weitere=None, masse=None):
        """Eine Variante samt Massen und Ablage aus Reglern (der Reglerzug nimmt `betas_aus_reglern` und `form`)."""
        return cls.erzeugen(geschlecht, cls.betas_aus_reglern(geschlecht, groesse, fuelle, weitere, masse))

    @classmethod
    def betas_aus_reglern(cls, geschlecht, groesse=0.0, fuelle=0.0, weitere=None, masse=None):
        """Der Weg, den das Bedienfeld geht: Regler statt roher Betas.

        `weitere`: die acht ungemessenen Formregler (`Smplform.WEITERE_SCHLUESSEL`).
        Die Umrechnung samt der je Geschlecht verschiedenen Vorzeichen steht
        in `SMPL/form.py` — dort auch, warum sie gemessen und nicht geraten ist.
        `masse`: die benannten Massregler {armlaenge: -100..100, …}
        (`SMPL/xmassregler.py`) — sie addieren ihre kalibrierte Richtung
        ueber 300 Betas auf die zehn der Formregler.
        """
        from SMPL.form import Smplform
        from SMPL.xmassregler import Smplxmassregler

        betas = Smplform.betas(geschlecht, groesse, fuelle, weitere)
        if masse and any(abs(float(w or 0)) >= 0.5 for w in masse.values()):
            zusatz = Smplxmassregler.betas(cls.massregler(geschlecht), masse, Smplxmassregler.BETAS)
            voll = torch.zeros(Smplxmassregler.BETAS, dtype=torch.float64, device='cuda')
            voll[: len(betas)] = betas
            betas = [float(x) for x in Torchfeld.liste(Torchfeld.round(voll + zusatz, 4))]
        return betas

    _massregler = {}

    @classmethod
    def massregler(cls, geschlecht):
        """Die abgelegten Richtungen der Massregler (einmal je Geschlecht)."""
        from SMPL.xmassregler import Smplxmassregler

        if geschlecht not in cls._massregler:
            cls._massregler[geschlecht] = Smplxmassregler.laden(cls.MODELLE, geschlecht)
        return cls._massregler[geschlecht]

    @classmethod
    def sicherstellen(cls, name):
        """OBJ und YAML bauen, falls sie fehlen: Durchschnittskoerper, und Varianten, von denen nur die Form gerechnet ist (`form`)."""
        if cls._abgelegt(name):
            return
        pfad = os.path.join(cls.ordner(), str(name) + cls.BETAS)
        if name in cls.DURCHSCHNITT.values():
            cls.erzeugen(cls.geschlecht(name), None)
        elif os.path.isfile(pfad):
            with open(pfad, encoding='utf-8') as quelle:
                cls.erzeugen(cls.geschlecht(name), json.load(quelle))

    @classmethod
    def masse_abgelegt(cls, name):
        """Die Masse, wenn sie schon gemessen sind — sonst {}; misst nie."""
        return cls.masse(name) if cls._abgelegt(name) else {}

    # ----------------------------------------------------------------- lesen

    @classmethod
    def masse(cls, name):
        """Die abgelegten Masse einer Variante (aus ihrer YAML)."""
        import yaml

        cls.sicherstellen(name)
        pfad = os.path.join(cls._ordner_von(name), name + '.yaml')
        with open(pfad, encoding='utf-8') as quelle:
            return yaml.safe_load(quelle)['body']

    @classmethod
    def netz(cls, name):
        """Punkte (Meter, Y oben) und Dreiecke einer abgelegten Variante."""
        from GarmentCode.anziehen import Anziehen

        cls.sicherstellen(name)
        return Anziehen.netz_lesen(os.path.join(cls._ordner_von(name), name + '.obj'), aus_garmentcode=False)
