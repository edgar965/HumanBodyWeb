# -*- coding: utf-8 -*-
"""Blendimporthautnacharbeit — die Nacharbeit einer gebackenen Haut-Kachel, im Speicher: Felder hinein, Felder heraus (kein Lesen und Schreiben von Zwischendateien).

NACHARBEIT: Wo kein Strahl das Original trifft, ist die gebackene Farbe schwarz. Dort gilt die Kachel von „Mesh to 3D" (Daz-Haut auf den Hautton getönt, darüber die Netzfarbe) — im Ton des
Gebackenen daneben und ohne ihre weißen Löcher (`Blendimportfarbangleich`), die Normale wird flach (128, 128, 255), die Rauheit der Median der getroffenen Texel. Die gebackenen Normalen
werden von falschen Treffern gesäubert (`Blendimportnormalen`, Bericht `normalen_flach`) und auf ihr Feindetail begrenzt (Einstellung `normalen_form`); mit Scham-Stück gilt im Umfeld des
Stücks die Farbe des Originals (`Blendimportumfeld`).

    nach = Blendimporthautnacharbeit(ablage, job, px, umfeld, normalen_grenze, normalen_form, melden)
    e = nach.kachel(1001, farbe, normal, rauheit_rgb)        # {'farbe', 'normalen' (H, W, 3) uint8, 'rauheit' (H, W) uint8, 'deckung' in %, 'farbe_geaendert'}
"""

import logging

import numpy as np

from .blendimportfarbangleich import Blendimportfarbangleich
from .blendimportnormalen import Blendimportnormalen
from .blendimportrand import Blendimportrand

logger = logging.getLogger('core')

__all__ = ['Blendimporthautnacharbeit']


class Blendimporthautnacharbeit:
    FLACH = (128, 128, 255)
    #: Texel mit Helligkeit bis hierher gelten als nicht getroffen (das JPEG verwischt das reine Schwarz um wenige Stufen).
    LEER_BIS = 6

    def __init__(self, ablage, job, px, umfeld=None, normalen_grenze=None, normalen_form='weg', melden=None, geraet=None):
        """`geraet`: das Warp-Gerät, auf dem die Nacharbeit rechnet (`'cuda:0'`, `core/dienste/hautnach`); `None` = die CPU-Fassungen."""
        self.ablage, self.job, self.px = ablage, job, int(px)
        self.geraet = geraet
        self._werkzeug = {}
        self.umfeld = umfeld
        #: Grad ab denen eine gebackene Normale als falscher Treffer gilt; `None` = Vorgabe der Säuberung, `'aus'` = nie.
        self.normalen_grenze = normalen_grenze
        #: `weg` (Vorgabe): nur das Feindetail der gebackenen Normalen gilt; `bleibt`: die ganze Karte.
        self.normalen_form = normalen_form
        self.melden = melden or (lambda anteil, text: None)
        self.normalen_flach = {}
        self.umfeld_bericht = {}

    def normalen(self):
        """Säubern und Feindetail: GPU (`Hautnachnormalen`) oder CPU (`Blendimportnormalen`) — dieselbe Schnittstelle."""
        if not self.geraet:
            return Blendimportnormalen
        if 'normalen' not in self._werkzeug:
            from .hautnach import Hautnachnormalen

            self._werkzeug['normalen'] = Hautnachnormalen(self.geraet)
        return self._werkzeug['normalen']

    def farbangleich(self):
        """Die Ersatzfüllung im Ton der Nachbarschaft: GPU (`Hautnachfarbe`) oder CPU (`Blendimportfarbangleich`)."""
        if not self.geraet:
            return Blendimportfarbangleich
        if 'farbe' not in self._werkzeug:
            from .hautnach import Hautnachfarbe

            self._werkzeug['farbe'] = Hautnachfarbe(self.geraet)
        return self._werkzeug['farbe']

    def meshfigur_kachel(self, kachel):
        from ..daten.meshfigurablage import Meshfigurablage

        name = ((self.job.ergebnis or {}).get('fototextur') or {}).get('kacheln', {}).get(str(kachel))
        pfad = Meshfigurablage(self.job.kennung).ergebnis(name) if name else None
        return pfad if pfad and pfad.is_file() else None

    def farbe_fuellen(self, k, farbe, leer, saum_schliessen=True):
        """`(Farbe, Saum)`: der Saum um die Fehlstellen geschlossen, die Fehlstellen mit der Ersatzkachel von „Mesh to 3D" gefüllt und — mit Scham-Stück — im Umfeld des Stücks mit der Farbe
        des Originals (`Blendimportumfeld`). Der Saum ist ein Zug von Blenders Rand (`Blendimportrand`); ein lokal gebackenes Bild hat ihn nicht (`saum_schliessen=False`)."""
        from PIL import Image

        if saum_schliessen:
            # Der Saum um die Fehlstellen ist nicht rein schwarz und bliebe als dunkle Linie stehen (`Blendimportrand`).
            farbe, saum = Blendimportrand.schliessen(farbe, leer)
        else:
            saum = np.zeros_like(leer)
        ersatz = self.meshfigur_kachel(k)
        if leer.any() and ersatz is not None:
            # Die Ersatzkachel steht in einem anderen Ton als das Gebackene daneben (Asian, Daumenwurzel: beige Flecken zwischen rosa
            # Streifen, ein weißes Loch im Daumen): Löcher stopfen, den Ton an die gebackene Nachbarschaft angleichen.
            hinten = self.farbangleich().hinten(Image.open(ersatz), farbe, leer | saum)
            farbe = np.where(leer[..., None], hinten, farbe)
        if leer.any() and self.umfeld is not None:
            # Um das Scham-Stück gilt in den Fehlstellen die Farbe des Originals, nicht die blasse Ersatzkachel.
            farbe = self.umfeld.fuellen(k, np.array(farbe), leer)
            self.umfeld_bericht[str(k)] = self.umfeld.bericht
        return farbe, saum

    def kachel(self, k, farbe, normal, rauheit_rgb, saum_schliessen=True):
        """Eine Kachel nacharbeiten. `farbe`, `normal`, `rauheit_rgb`: `(H, W, 3)` uint8 — Texel ohne Treffer schwarz bzw. flach. Die Eingabefelder bleiben unverändert."""
        import cv2

        leer = farbe.max(axis=2) <= self.LEER_BIS
        deckung = round(100.0 * (1.0 - leer.mean()), 1)
        farbe, saum = self.farbe_fuellen(k, farbe, leer, saum_schliessen)
        normal = np.array(normal)
        normal[leer | saum] = self.FLACH
        normal, self.normalen_flach[str(k)] = self.saeubern(normal, leer | saum)
        if self.normalen_form != 'bleibt':
            # Die Formdifferenz zwischen Figur und Original steht nicht in der Normalenkarte, sondern in der Fläche.
            normal = self.normalen().feindetail(normal, leer | saum, self.form_px())
        rauh = cv2.cvtColor(np.ascontiguousarray(rauheit_rgb), cv2.COLOR_RGB2GRAY)
        if (~(leer | saum)).any():
            rauh[leer | saum] = int(np.median(rauh[~(leer | saum)]))
        self.melden(0.95, 'Kachel %d nachgearbeitet (%.1f %% getroffen)' % (k, deckung))
        self.warnen(k)
        return {'farbe': farbe, 'normalen': normal, 'rauheit': rauh, 'deckung': deckung, 'farbe_geaendert': bool(leer.any() or saum.any())}

    def form_px(self):
        """Wellenlänge der Form in Pixeln dieser Kachelgröße (`Blendimportnormalen.FORM_PX` gilt bei 8192 px)."""
        return max(3.0, Blendimportnormalen.FORM_PX * self.px / 8192.0)

    def saeubern(self, normal, leer):
        """`(Karte, Anteil geänderter Texel in %)` mit der gewählten Grenze; `'aus'` lässt die Karte, wie sie ist."""
        if self.normalen_grenze == 'aus':
            return normal, 0.0
        grad = float(self.normalen_grenze) if self.normalen_grenze else None
        return self.normalen().saeubern(normal, leer, grad)

    def warnen(self, kachel):
        """Fällt in eine Kachel auffällig viel, steht es im Log und in der Statuszeile des Imports."""
        anteil = self.normalen_flach[str(kachel)]
        if anteil < Blendimportnormalen.WARN_PROZENT:
            return
        text = 'Kachel %d: %.1f %% der Normalen flachgelegt (Warnung ab %.0f %%) — Grenze im Import-Dialog prüfen' % (
            kachel, anteil, Blendimportnormalen.WARN_PROZENT)
        logger.warning('Blender-Import %s: %s', self.ablage.kennung, text)
        self.melden(0.95, text)
