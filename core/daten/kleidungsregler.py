# -*- coding: utf-8 -*-
"""Kleidungsregler — die Stellschrauben einer Kleidungsanpassung an den Koerper.

WARUM EINE KLASSE (Umbau 15.08.2026): In `garment_fit` wurden ACHT Werte
einzeln aus der Anfrage gelesen — `offset`, `stiffness`, `min_dist`,
`crotch_floor`, `lift`, `crotch_depth`, `color_r/g/b`, `fit_mode` — und dann
dreimal in fast gleiche Aufrufe gestopft. Die Vorgaben kamen teils aus der
Vorlage, teils aus der Anfrage; welcher Wert am Ende gilt, liess sich nur durch
Lesen der ganzen Funktion beantworten.

Nicht zu verwechseln mit `Anpassungsregler`: Der gehoert zum MakeHuman-Proxy
(feste Vertexzuordnung, T-zu-A-Pose). Hier geht es um das Anpassen einer
Vorlage an ein gerechnetes Koerpernetz.
"""


class Kleidungsregler:
    """Werte, die das Ergebnis einer Vorlagen-Anpassung bestimmen."""

    __slots__ = ('abstand', 'steifigkeit', 'mindestabstand_mm',
                 'schrittboden_mm', 'anheben_mm', 'schritttiefe_mm', 'farbe',
                 'verfahren')

    #: Die Vorgaben, die vorher in den GET-Aufrufen standen.
    MINDESTABSTAND_MM = 3.0
    SCHRITTBODEN_MM = 0.0
    ANHEBEN_MM = 0.0
    SCHRITTTIEFE_MM = 0.0

    #: `rig_hull` legt das Stueck um eine Huelle statt um den Koerper.
    HUELLE = 'rig_hull'

    def __init__(self, abstand, steifigkeit, farbe, verfahren='',
                 mindestabstand_mm=None, schrittboden_mm=None,
                 anheben_mm=None, schritttiefe_mm=None):
        self.abstand = abstand
        self.steifigkeit = steifigkeit
        self.farbe = farbe
        self.verfahren = verfahren
        self.mindestabstand_mm = (self.MINDESTABSTAND_MM
                                  if mindestabstand_mm is None
                                  else mindestabstand_mm)
        self.schrittboden_mm = (self.SCHRITTBODEN_MM if schrittboden_mm is None
                                else schrittboden_mm)
        self.anheben_mm = self.ANHEBEN_MM if anheben_mm is None else anheben_mm
        self.schritttiefe_mm = (self.SCHRITTTIEFE_MM if schritttiefe_mm is None
                                else schritttiefe_mm)

    # ------------------------------------------------------------ aus Anfrage

    @classmethod
    def aus_parametern(cls, p, vorlage):
        """Werte aus `request.GET`; was fehlt, kommt aus der Vorlage."""
        return cls(
            abstand=cls._zahl(p, 'offset', vorlage.offset),
            steifigkeit=cls._zahl(p, 'stiffness', vorlage.stiffness),
            farbe=cls._farbe(p, vorlage.color),
            verfahren=p.get('fit_mode', '') or '',
            mindestabstand_mm=cls._zahl(p, 'min_dist', cls.MINDESTABSTAND_MM),
            schrittboden_mm=cls._zahl(p, 'crotch_floor', cls.SCHRITTBODEN_MM),
            anheben_mm=cls._zahl(p, 'lift', cls.ANHEBEN_MM),
            schritttiefe_mm=cls._zahl(p, 'crotch_depth', cls.SCHRITTTIEFE_MM),
        )

    @staticmethod
    def _zahl(p, name, vorgabe):
        wert = p.get(name)
        if wert in (None, ''):
            return vorgabe
        try:
            return float(wert)
        # stumm gewollt: Vorschrift dieser Klasse ist „unbrauchbar → Vorgabe“.
        except (TypeError, ValueError):
            return vorgabe

    @classmethod
    def _farbe(cls, p, vorlagenfarbe):
        return tuple(cls._zahl(p, 'color_%s' % kanal, vorlagenfarbe[i])
                     for i, kanal in enumerate(('r', 'g', 'b')))

    # ----------------------------------------------------------------- fragen

    @property
    def um_huelle(self):
        return self.verfahren == self.HUELLE

    def als_argumente(self, koordinatensystem):
        """Die Schlüsselwortargumente fuer `GarmentFitter.fit_garment`."""
        return dict(offset=self.abstand, stiffness=self.steifigkeit,
                    color=self.farbe, coordinate_system=koordinatensystem,
                    min_dist_mm=self.mindestabstand_mm,
                    crotch_floor_mm=self.schrittboden_mm,
                    lift_mm=self.anheben_mm,
                    crotch_depth_mm=self.schritttiefe_mm)

    def __repr__(self):
        return ('<Kleidungsregler abstand=%.4f steif=%.2f verfahren=%r>'
                % (self.abstand, self.steifigkeit, self.verfahren or 'vorgabe'))
