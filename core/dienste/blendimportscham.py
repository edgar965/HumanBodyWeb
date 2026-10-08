# -*- coding: utf-8 -*-
"""Blendimportscham — die Scham des Originals als eigenes Stück der Genesis-Figur (08.10.2026).

Edgar zu „cute girl": „die geometrie und Textur sind noch miserabel, vergleiche mit Blender". Gemessen und gesehen:

* Die Genesis-Fläche trägt die inneren Schamlippen nicht. Der Käfig hat dort ~8 mm Punktabstand, die Stufen 1 und 2 (4 und 2 mm)
  kommen aus ihm durch Unterteilung — eine Form, die feiner ist als der Käfig, gibt es nicht. Eine Käfig-Anpassung in BEIDE
  Richtungen (Figur→Original und zurück, `ProjektTemp/_wegwerf/cutegirl/scham_fit_probe.py`) drückte die Abstände zwar auf Median
  0,4 mm, die Fläche knitterte dabei aber (Käfigpunkte bis 68 mm verschoben, Bilder `fit_bilder/`).
* Die Originalfläche liegt im Bereich der Schamlippen 5–25 mm HINTER der Genesis-Fläche (die Figur überbrückt die Furche);
  von 1.737 Originalpunkten im Kasten wichen 344 um mehr als 5 mm ab (Import 2026.10.08.19.31.50, `scham_stueck_probe3.py`).
* Der Strahl des Backens trifft deshalb falsch: die Farbe der Schamlippen steckt als EIN rosa Streifen in der Karte, der Rest ist
  verschmiert (Kachel 1002, Ausschnitt gesehen 08.10.2026).

WAS HIER GESCHIEHT — der Weg der Originalaugen (`Blendimportaugen`, `G9stueckersatz`): Der Teil des Körpernetzes, der
von der Figur abweicht, wird ein eigenes Stück „<Name> Scham" mit der Fläche und der Haut des Originals:

    Saat       Originalpunkte im Kasten der Nachformung (`Blendimportnachformung.REGIONEN`), die um mehr als `SCHWELLE_MM`
               von der Figurfläche abweichen
    Hülle      konvexe Hülle der Saat in der Vorderansicht, `RAND_MM` weit (die Saat selbst hat Löcher: die Vorderseite der Furche
               weicht kaum ab); dazu nur Punkte in der Tiefe der Saat ± `TIEFE_RAND_MM`
    Rand       die Randpunkte werden über `BAND_MM` (Weg entlang der Kanten, weicher Verlauf) auf die Figurfläche gezogen, höchstens
               um `ANGLEICH_MAX_MM` — dort, wo Original und Figur weiter auseinanderliegen, bleibt der Rand sichtbar (gemeldet)
    Haut       die Inseln der Auswahl aus Farbe, Normalen und Rauheit des Originals, in Originalauflösung (`Blendimportatlas`)

Die Haut der Figur unter dem Stück entfällt im Browser (`Hautverdeckung`); weil das Stück bis 25 mm hinter der Figurfläche liegt,
sagt das Stück das selbst (`G9stueckersatz.haut_tiefe_mm`).
"""

import logging

import numpy as np

from .blendimportatlas import Blendimportatlas
from .blendimportnachformung import Blendimportnachformung

logger = logging.getLogger('core')

__all__ = ['Blendimportscham']


class Blendimportscham:
    #: Abstand (mm) des Originalpunkts zur Figurfläche, ab dem er zur Scham zählt.
    SCHWELLE_MM = 5.0
    #: Weniger Saatpunkte: die Figur trifft das Original dort schon; es gibt kein Stück.
    MINDEST_SAAT = 40
    #: Rand der Hülle um die Saat (Vorderansicht, mm) und Tiefenzugabe vor und hinter der Saat (mm).
    RAND_MM = 10.0
    TIEFE_RAND_MM = 20.0
    #: Breite des Bandes am Rand, in dem die Fläche auf die Figur gezogen wird (mm Weg entlang der Kanten).
    BAND_MM = 12.0
    #: Weiter als das wird nicht gezogen (mm) — die Fläche würde sich sonst sichtbar verbiegen.
    ANGLEICH_MAX_MM = 8.0
    #: So tief hinter der Haut darf das Stück liegen und verdeckt sie trotzdem (mm) — bleibt im Stück als `haut_tiefe_mm`.
    HAUT_TIEFE_MM = 30.0
    #: Suchraum um die Saat in der Vorderansicht (m): halbe Breite und halbes Höhenband um ihren Schwerpunkt.
    SUCH_BREITE_M = 0.12
    SUCH_HOEHE_M = 0.08
    #: Bilder des Originals, die in den Atlas gehen: Schlüssel im Inventar → (Dateiendung, Modus, Qualität).
    BILDER = {'farbe': ('.jpg', 'RGB', 92), 'normalen': ('.png', 'RGB', None), 'rauheit': ('.png', 'L', None)}

    def __init__(self, lage, koerper, material):
        """`koerper`: `{punkte (Blender-Achsen), dreiecke, uv_ecken}` des Originalkörpers; `material`: sein Eintrag im Inventar
        (`farbe`, `normalen`, `rauheit`, `detailnormalen`, `detail_kachel`)."""
        self.lage = lage
        self.koerper = koerper
        self.material = material or {}

    # ------------------------------------------------------------ Auswahl

    @staticmethod
    def huelle_abstand(ecken, punkte_xy):
        """Vorzeichenbehafteter Abstand (m) der Punkte zur konvexen Hülle (Ecken gegen den Uhrzeigersinn): negativ = innen."""
        a, b = ecken, np.roll(ecken, -1, axis=0)
        kante = b - a
        t = np.clip(((punkte_xy[:, None, :] - a) * kante).sum(-1) / np.maximum((kante ** 2).sum(-1), 1e-18), 0.0, 1.0)
        weg = np.linalg.norm(punkte_xy[:, None, :] - (a + t[..., None] * kante), axis=-1).min(axis=1)
        links = kante[None, :, 0] * (punkte_xy[:, None, 1] - a[None, :, 1]) - kante[None, :, 1] * (punkte_xy[:, None, 0] - a[None, :, 0])
        return np.where((links >= 0).all(axis=1), -weg, weg)

    def saat(self, ruhe, flaeche, sohle, hoehe):
        """Maske der Originalpunkte im Kasten, die um mehr als `SCHWELLE_MM` von der Figurfläche abweichen."""
        import trimesh

        r = Blendimportnachformung.REGIONEN['scham']
        zmed = float(np.median(ruhe[:, 2]))
        # Wie der Kasten der Nachformung, hinten etwas weiter (der Damm hängt hinter dem Schritt).
        kasten = ((ruhe[:, 1] > sohle + r['hoehe'][0] * hoehe) & (ruhe[:, 1] < sohle + r['hoehe'][1] * hoehe)
                  & (np.abs(ruhe[:, 0]) < r['breite_m'] * hoehe / 1.75) & (ruhe[:, 2] > zmed - 0.03))
        abstand = np.zeros(len(ruhe))
        idx = np.flatnonzero(kasten)
        if len(idx):
            abstand[idx] = trimesh.proximity.closest_point(flaeche, ruhe[idx])[1] * 1000.0
        return kasten & (abstand > self.SCHWELLE_MM)

    def auswahl(self, ruhe, saat):
        """Maske der Punkte in der Hülle der Saat (Vorderansicht, `RAND_MM`), in ihrer Tiefe ± `TIEFE_RAND_MM`."""
        from scipy.spatial import ConvexHull

        xy = ruhe[saat][:, [0, 1]]
        ecken = xy[ConvexHull(xy).vertices]            # gegen den Uhrzeigersinn
        z = ruhe[saat][:, 2]
        zugabe = self.TIEFE_RAND_MM / 1000.0
        nah = ((ruhe[:, 2] > z.min() - zugabe) & (ruhe[:, 2] < z.max() + zugabe) & (np.abs(ruhe[:, 0]) < self.SUCH_BREITE_M)
               & (np.abs(ruhe[:, 1] - ruhe[saat][:, 1].mean()) < self.SUCH_HOEHE_M))
        maske = np.zeros(len(ruhe), dtype=bool)
        kandidaten = np.flatnonzero(nah)
        maske[kandidaten[self.huelle_abstand(ecken, ruhe[kandidaten][:, [0, 1]]) < self.RAND_MM / 1000.0]] = True
        return maske

    @staticmethod
    def randpunkte(dreiecke):
        """Punkte an offenen Kanten (Kante in genau einem Dreieck)."""
        kanten = np.sort(np.concatenate([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]], dreiecke[:, [2, 0]]]), axis=1)
        roh, zaehl = np.unique(kanten, axis=0, return_counts=True)
        return np.unique(roh[zaehl == 1])

    # --------------------------------------------------------------- Rand

    def angleichen(self, punkte, dreiecke, flaeche):
        """`(neue Punkte, bericht)`: das Randband wird weich auf die Figurfläche gezogen (höchstens `ANGLEICH_MAX_MM`)."""
        import trimesh
        from scipy import sparse
        from scipy.sparse import csgraph

        rand = self.randpunkte(dreiecke)
        n = len(punkte)
        a = np.concatenate([dreiecke[:, 0], dreiecke[:, 1], dreiecke[:, 2]])
        b = np.concatenate([dreiecke[:, 1], dreiecke[:, 2], dreiecke[:, 0]])
        graph = sparse.csr_matrix((np.linalg.norm(punkte[a] - punkte[b], axis=1) * 1000.0, (a, b)), shape=(n, n))
        weg = csgraph.dijkstra(graph, directed=False, indices=rand, min_only=True)
        band = np.flatnonzero(weg < self.BAND_MM)
        nah = trimesh.proximity.closest_point(flaeche, punkte[band])[0]
        zug = nah - punkte[band]
        laenge = np.linalg.norm(zug, axis=1)
        zu_weit = laenge > self.ANGLEICH_MAX_MM / 1000.0
        zug[zu_weit] *= (self.ANGLEICH_MAX_MM / 1000.0 / laenge[zu_weit])[:, None]
        t = np.clip(weg[band] / self.BAND_MM, 0.0, 1.0)
        neu = np.asarray(punkte, dtype=np.float64).copy()
        neu[band] += (1.0 - (3.0 * t ** 2 - 2.0 * t ** 3))[:, None] * zug
        vorher = trimesh.proximity.closest_point(flaeche, punkte[rand])[1] * 1000.0
        nachher = trimesh.proximity.closest_point(flaeche, neu[rand])[1] * 1000.0
        return neu, {'rand_punkte': int(len(rand)), 'band_punkte': int(len(band)), 'nicht_ganz_gezogen': int(zu_weit.sum()),
                     'rand_vorher_median_mm': round(float(np.median(vorher)), 2),
                     'rand_nachher_median_mm': round(float(np.median(nachher)), 2),
                     'rand_nachher_p90_mm': round(float(np.percentile(nachher, 90)), 2),
                     'rand_nachher_max_mm': round(float(nachher.max()), 1)}

    # ---------------------------------------------------------------- Haut

    def haut(self, uv_ecken, ordner, kennung):
        """`(uv_ecken im Atlas, quelle, bericht)`: die Bilder der Auswahl als Atlas in `ordner`; `quelle` wie ein Eintrag des
        Inventars (Pfade der Atlasbilder, `detail_kachel` auf den Atlas umgerechnet)."""
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None
        insel = Blendimportatlas.inseln(uv_ecken)
        with Image.open(self.material['farbe']) as b:
            groesse = b.size
        rechtecke = Blendimportatlas.rechtecke(uv_ecken, insel, groesse)
        orte, atlas = Blendimportatlas.packen(rechtecke)
        quelle = dict(self.material)
        for kanal, (endung, modus, qualitaet) in self.BILDER.items():
            pfad = self.material.get(kanal)
            if not pfad:
                continue
            with Image.open(pfad) as b:
                bild = np.asarray(b.convert(modus))
            if (bild.shape[1], bild.shape[0]) != tuple(groesse):
                raise ValueError('Bild %s: %s px, die Farbe hat %s' % (kanal, bild.shape[1::-1], groesse))
            ziel = ordner / ('%s_atlas_%s%s' % (kennung, kanal, endung))
            Image.fromarray(Blendimportatlas.schneiden(bild, rechtecke, orte, atlas)).save(ziel, **({'quality': qualitaet} if qualitaet else {}))
            quelle[kanal] = str(ziel)
        kachel = self.material.get('detail_kachel')
        if kachel:
            quelle['detail_kachel'] = [kachel[0] * groesse[0] / atlas[0], kachel[1] * groesse[1] / atlas[1]]
        uv = Blendimportatlas.neue_uv(uv_ecken, insel, rechtecke, orte, groesse, atlas)
        return uv, quelle, {'inseln': len(rechtecke), 'atlas_px': list(atlas), 'quelle_px': list(groesse)}

    # ---------------------------------------------------------------- Lauf

    def bauen(self, ordner, kennung, flaeche):
        """`{punkte, dreiecke, uv_ecken, quelle, bericht}` in Ruhelage der Figur (Y oben) — oder `{'aus': Grund}`."""
        punkte = self.lage.ruhelage(self.koerper['punkte'])
        dreiecke = np.asarray(self.koerper['dreiecke'], dtype=np.int64)
        sohle, hoehe = float(punkte[:, 1].min()), float(punkte[:, 1].max() - punkte[:, 1].min())
        saat = self.saat(punkte, flaeche, sohle, hoehe)
        if saat.sum() < self.MINDEST_SAAT:
            return {'aus': 'nur %d Originalpunkte weichen mehr als %.0f mm ab (Mindestens %d)' % (
                saat.sum(), self.SCHWELLE_MM, self.MINDEST_SAAT)}
        maske = self.auswahl(punkte, saat)
        je_dreieck = maske[dreiecke].all(axis=1)
        benutzt, neu = np.unique(dreiecke[je_dreieck], return_inverse=True)
        sel_punkte, sel_dreiecke = punkte[benutzt], neu.reshape(-1, 3)
        sel_punkte, rand = self.angleichen(sel_punkte, sel_dreiecke, flaeche)
        uv, quelle, atlas = self.haut(np.asarray(self.koerper['uv_ecken'])[je_dreieck], ordner, kennung)
        bericht = {'saat': int(saat.sum()), 'punkte': int(len(sel_punkte)), 'dreiecke': int(len(sel_dreiecke)), 'rand': rand, 'atlas': atlas}
        logger.info('Scham-Stück: %s', bericht)
        return {'punkte': sel_punkte, 'dreiecke': sel_dreiecke, 'uv_ecken': uv, 'quelle': quelle, 'bericht': bericht}
