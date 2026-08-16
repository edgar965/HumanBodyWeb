# -*- coding: utf-8 -*-
"""Anpassungsregler — die Stellschrauben einer Kleidungsanpassung.

WARUM EINE KLASSE (Umbau 15.08.2026): In `mh_proxy_fit` wurden sieben Werte
einzeln aus der Anfrage gelesen und durch acht Rechenschritte gereicht —
`stiffness`, `offset`, `scale`, `y_offset`, `push_dist`, `use_mh_body`,
`tpose_displacement`. Jeder Schritt las sie erneut aus `request.GET`, mit je
eigener Vorgabe und eigener Umrechnung (Millimeter zu Meter an einer Stelle,
Meter an der anderen). Mehr als drei zusammengehoerige Werte, die ihre Funktion
verlassen: eine Klasse.

Die Vorgabewerte stehen jetzt EINMAL hier und nicht verstreut in acht
`request.GET.get(..., x)`-Aufrufen.
"""


class Anpassungsregler:
    """Werte aus der Anfrage, die das Ergebnis einer Anpassung bestimmen."""

    __slots__ = ('steifigkeit', 'abstand', 'skalierung', 'hoehenversatz',
                 'ausschieben_m', 'mh_koerper', 'tpose_verschiebung', 'farbe')

    #: Vorgaben — dieselben Werte, die vorher in den GET-Aufrufen standen.
    STEIFIGKEIT = 0.5
    ABSTAND = 0.006
    SKALIERUNG = 1.0
    HOEHENVERSATZ = 0.0
    AUSSCHIEBEN_MM = 3.0
    VORGABEFARBE = (0.3, 0.35, 0.5)

    def __init__(self, steifigkeit=None, abstand=None, skalierung=None,
                 hoehenversatz=None, ausschieben_mm=None, mh_koerper=True,
                 tpose_verschiebung=True, farbe=None):
        self.steifigkeit = self.STEIFIGKEIT if steifigkeit is None else steifigkeit
        self.abstand = self.ABSTAND if abstand is None else abstand
        self.skalierung = self.SKALIERUNG if skalierung is None else skalierung
        self.hoehenversatz = (self.HOEHENVERSATZ if hoehenversatz is None
                              else hoehenversatz)
        mm = self.AUSSCHIEBEN_MM if ausschieben_mm is None else ausschieben_mm
        self.ausschieben_m = mm / 1000.0
        self.mh_koerper = bool(mh_koerper)
        self.tpose_verschiebung = bool(tpose_verschiebung)
        self.farbe = farbe

    # ------------------------------------------------------------ aus Anfrage

    @classmethod
    def aus_parametern(cls, p):
        """Aus einem dict-artigen Zugriff (`request.GET`)."""
        return cls(
            steifigkeit=cls._zahl(p, 'stiffness', cls.STEIFIGKEIT),
            abstand=cls._zahl(p, 'offset', cls.ABSTAND),
            skalierung=cls._zahl(p, 'scale', cls.SKALIERUNG),
            hoehenversatz=cls._zahl(p, 'y_offset', cls.HOEHENVERSATZ),
            ausschieben_mm=cls._zahl(p, 'push_dist', cls.AUSSCHIEBEN_MM),
            mh_koerper=p.get('use_mh_body', '1') == '1',
            tpose_verschiebung=p.get('tpose_displacement', '1') == '1',
            farbe=cls._farbe(p),
        )

    @staticmethod
    def _zahl(p, name, vorgabe):
        try:
            wert = p.get(name)
            return vorgabe if wert in (None, '') else float(wert)
        except (TypeError, ValueError):
            return vorgabe

    @classmethod
    def _farbe(cls, p):
        """Nur wenn ALLE drei Kanaele da sind — sonst gilt die Materialfarbe."""
        werte = [p.get('color_r'), p.get('color_g'), p.get('color_b')]
        if any(w in (None, '') for w in werte):
            return None
        try:
            return tuple(float(w) for w in werte)
        except (TypeError, ValueError):
            return None

    # ----------------------------------------------------------------- fragen

    @property
    def glaettet(self):
        return self.steifigkeit < 0.99

    @property
    def glaettungsschritte(self):
        """Weicher Stoff wird oefter geglaettet als steifer."""
        return max(1, int(10 * (1 - self.steifigkeit)))

    @property
    def glaettungsstaerke(self):
        return 0.3 + (1 - self.steifigkeit) * 0.4        # 0,3 bis 0,7

    def farbe_oder(self, ersatz):
        """Angeforderte Farbe, sonst die Materialfarbe, sonst die Vorgabe."""
        if self.farbe:
            return self.farbe
        if ersatz:
            return tuple(ersatz)
        return self.VORGABEFARBE

    def __repr__(self):
        return ('<Anpassungsregler steif=%.2f abstand=%.3f skal=%.2f '
                'ausschieben=%.1fmm>' % (self.steifigkeit, self.abstand,
                                         self.skalierung,
                                         self.ausschieben_m * 1000))
