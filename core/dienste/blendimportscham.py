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
               weicht kaum ab); dazu nur Punkte in der Tiefe der Saat ± `TIEFE_RAND_MM`. Die Saat reicht seitlich höchstens
               `SAAT_BREITE_M` (die Leistenfalten gehören nicht dazu: dort liefen helle Flügel an den Oberschenkeln entlang)
    Schnitt    die Dreiecke werden an der Kontur der Hülle EXAKT geteilt (`Blendimportschamschnitt`), nicht ganz gewählt oder
               weggelassen — der Rand ist die glatte Kontur, nicht die Zähne der Dreiecke (Edgar, 09.10.2026: „keine helle,
               gesägte Zipfel an den Rändern")
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
from .blendimportschamgeograft import Blendimportschamgeograft
from .blendimportschamschnitt import Blendimportschamschnitt

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
    #: Weiter als das wird nicht gezogen (mm) — die Fläche würde sich sonst sichtbar verbiegen. Versucht am 09.10.2026: Band 18 mm und
    #: 25 mm Höchstverschiebung (in den Leisten liegt der Rand bis 15 mm hinter der Haut): der Rand lag dann auf der Haut, aber die
    #: Schamlippen, nur 20 mm vom schmaleren Rand, wurden mitgezogen und verbogen (Chrome) — verworfen.
    ANGLEICH_MAX_MM = 8.0
    #: So tief hinter der Haut darf das Stück liegen und verdeckt sie trotzdem (mm) — bleibt im Stück als `haut_tiefe_mm`.
    HAUT_TIEFE_MM = 30.0
    #: Suchraum um die Saat in der Vorderansicht (m): halbe Breite und halbes Höhenband um ihren Schwerpunkt.
    SUCH_BREITE_M = 0.12
    SUCH_HOEHE_M = 0.08
    #: Die Saat reicht seitlich mindestens so weit (m, bei 1,75 m Körperhöhe) — und nicht weiter, außer ein Kern tief vor der Figur
    #: (`KERN_MM`, mindestens `KERN_MIN` Punkte) verlangt es: Labia, Hoden und Penis liegen innen, die Leistenfalten außen. Gesehen
    #: 09.10.2026 („cute girl", „Fallout ranger"): mit ±70 mm reichte die Hülle ±80 mm, das Stück lief als helle, halbtransparente
    #: Flügel an den Oberschenkeln entlang, und Hautsplitter aus den Leisten ragten davor (gesägte Zipfel).
    SAAT_BREITE_M = 0.026
    KERN_MM = 25.0
    KERN_MIN = 40
    KERN_RAND_M = 0.006
    #: Der Kasten der Saat wächst um diesen Anteil der Körperhöhe, wenn Saatpunkte höchstens `GRENZ_BAND_M` (m) an seiner oberen oder
    #: unteren Grenze liegen — höchstens `SCHRITTE_MAX` Mal. Ohne Genital-Anbauten (die Scham von „cute girl") bleibt er, wie er war.
    SCHRITT_HOEHE = 0.03
    SCHRITTE_MAX = 4
    GRENZ_BAND_M = 0.012
    #: Bilder des Originals, die in den Atlas gehen: Schlüssel im Inventar → (Dateiendung, Modus, Qualität).
    BILDER = {'farbe': ('.jpg', 'RGB', 92), 'normalen': ('.png', 'RGB', None), 'rauheit': ('.png', 'L', None)}

    def __init__(self, lage, koerper, material):
        """`koerper`: `{punkte (Blender-Achsen), dreiecke, uv_ecken, material (Nummer je Dreieck, optional)}` des Originalkörpers;
        `material`: sein Eintrag im Inventar (`farbe`, `normalen`, `rauheit`, `detailnormalen`, `detail_kachel`) — oder die LISTE aller
        Materialien des Körpers (Character-Creator-Körper haben vier Hautmaterialien): dann gilt das der meisten gewählten Dreiecke."""
        self.lage = lage
        self.koerper = koerper
        self.materialien = [m or {} for m in material] if isinstance(material, (list, tuple)) else [material or {}]
        self.material = self.materialien[0] if self.materialien else {}
        #: Von … bis (Anteil der Körperhöhe), in dem die Saat zuletzt gesucht wurde (`saat`) — steht im Bericht.
        self.kastenhoehe = None
        #: Abstand (mm) jedes Originalpunkts zur Figurfläche im letzten Kasten und die seitliche Breite der Saat (`begrenzen`).
        self.abstand = None
        self.saat_breite_mm = None

    def waehle_material(self, slot):
        """Der Eintrag des Materials `slot` (über die Liste hinaus: das letzte); er gilt danach als `self.material`."""
        if self.materialien:
            self.material = self.materialien[min(max(int(slot), 0), len(self.materialien) - 1)]
        return self.material

    def material_slot(self, je_dreieck):
        """`(Nummer des häufigsten Materials unter den gewählten Dreiecken, Anzahl der gewählten Dreiecke eines anderen Materials)`.
        Ohne `material` im Körper (Läufe vor dem 09.10.2026): Material 0, keine Fremden."""
        mat = self.koerper.get('material')
        if mat is None:
            return 0, 0
        gewaehlt = np.asarray(mat)[np.asarray(je_dreieck, dtype=bool)]
        if not len(gewaehlt):
            return 0, 0
        slot = int(np.bincount(gewaehlt.astype(np.int64)).argmax())
        return slot, int((gewaehlt != slot).sum())

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
        """Maske der Originalpunkte im Kasten, die um mehr als `SCHWELLE_MM` von der Figurfläche abweichen. Der Kasten rückt oben
        und unten schrittweise hinaus (`SCHRITT_HOEHE`, höchstens `SCHRITTE_MAX` Mal), solange Saatpunkte an seiner Grenze liegen —
        so gehören hängende Hoden oder ein hochstehender Penis dazu (`Kastenhoehe`)."""
        unten, oben = Blendimportnachformung.REGIONEN['scham']['hoehe']
        for _ in range(self.SCHRITTE_MAX + 1):
            saat = self.saat_im_kasten(ruhe, flaeche, sohle, hoehe, unten, oben)
            self.kastenhoehe = (round(unten, 3), round(oben, 3))
            y = ruhe[saat][:, 1]
            weiter_unten = bool(len(y)) and float(y.min()) < sohle + unten * hoehe + self.GRENZ_BAND_M
            weiter_oben = bool(len(y)) and float(y.max()) > sohle + oben * hoehe - self.GRENZ_BAND_M
            if not (weiter_unten or weiter_oben):
                break
            unten -= self.SCHRITT_HOEHE if weiter_unten else 0.0
            oben += self.SCHRITT_HOEHE if weiter_oben else 0.0
        return self.begrenzen(ruhe, saat, hoehe)

    def saat_im_kasten(self, ruhe, flaeche, sohle, hoehe, unten, oben):
        """Die Saat in einem Kasten der Höhe `unten … oben` (Anteile der Körperhöhe über der Sohle)."""
        import trimesh

        r = Blendimportnachformung.REGIONEN['scham']
        zmed = float(np.median(ruhe[:, 2]))
        # Wie der Kasten der Nachformung, hinten etwas weiter (der Damm hängt hinter dem Schritt).
        kasten = ((ruhe[:, 1] > sohle + unten * hoehe) & (ruhe[:, 1] < sohle + oben * hoehe)
                  & (np.abs(ruhe[:, 0]) < r['breite_m'] * hoehe / 1.75) & (ruhe[:, 2] > zmed - 0.03))
        abstand = np.zeros(len(ruhe))
        idx = np.flatnonzero(kasten)
        if len(idx):
            abstand[idx] = trimesh.proximity.closest_point(flaeche, ruhe[idx])[1] * 1000.0
        self.abstand = abstand                                    # mm; für `begrenzen`
        return kasten & (abstand > self.SCHWELLE_MM)

    def begrenzen(self, ruhe, saat, hoehe):
        """Die Saat seitlich auf den Kern beschneiden: höchstens `SAAT_BREITE_M` (auf 1,75 m Körperhöhe bezogen) — bei Anbauten, die
        tief vor der Figurfläche liegen (Hoden, Penis: Abweichung ab `KERN_MM`), so weit wie dieser Kern reicht (98. Perzentil von |x|)
        plus `KERN_RAND_M`. Gemessen 09.10.2026 an „cute girl": Abweichung über 12 mm nur bis 35 mm seitlich, darüber 5–9 mm (die
        Leistenfalten); an „Asian Female" bis 55 mm. Bericht: `saat_breite_mm`."""
        skala = hoehe / 1.75
        breite = self.SAAT_BREITE_M * skala
        kern = saat & (self.abstand >= self.KERN_MM)
        if int(kern.sum()) >= self.KERN_MIN:
            breite = max(breite, (float(np.percentile(np.abs(ruhe[kern][:, 0]), 98)) + self.KERN_RAND_M * skala))
        self.saat_breite_mm = round(breite * 1000.0, 1)
        return saat & (np.abs(ruhe[:, 0]) < breite)

    def schnittwerte(self, ruhe, saat, punkte=None):
        """Je Punkt ein Wert für den Schnitt (`Blendimportschamschnitt`): negativ = im Stück, 0 = auf der Kontur. Die Kontur ist die
        Hülle der Saat (Vorderansicht), `RAND_MM` nach außen, begrenzt auf die Tiefe der Saat ± `TIEFE_RAND_MM` und den Suchraum — das
        Größte aus den Abständen (m) zu diesen Grenzen, jeder Punkt hat einen endlichen Wert. `punkte`: andere Punkte (die Haut der
        Figur, `verschweissen`), für die derselbe Wert gilt; ohne sind es die Punkte des Originals (`ruhe`)."""
        from scipy.spatial import ConvexHull

        xy = ruhe[saat][:, [0, 1]]
        ecken = xy[ConvexHull(xy).vertices]            # gegen den Uhrzeigersinn
        z = ruhe[saat][:, 2]
        zugabe = self.TIEFE_RAND_MM / 1000.0
        p = ruhe if punkte is None else np.asarray(punkte, dtype=np.float64)
        w = self.huelle_abstand(ecken, p[:, [0, 1]]) - self.RAND_MM / 1000.0
        grenzen = [z.min() - zugabe - p[:, 2], p[:, 2] - (z.max() + zugabe),
                   np.abs(p[:, 0]) - self.SUCH_BREITE_M, np.abs(p[:, 1] - ruhe[saat][:, 1].mean()) - self.SUCH_HOEHE_M]
        for g in grenzen:
            w = np.maximum(w, g)
        return w

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
                bild = b.convert(modus)
                if bild.size != tuple(groesse):
                    # Die Karten einer .blend haben nicht immer dieselbe Größe (Asian girl: Farbe 8192², Normalen 12288², gemessen
                    # 09.10.2026 — dort fiel das Scham-Stück deshalb ganz aus). UV gilt je Bild gleich: auf die Größe der Farbe bringen.
                    bild = bild.resize(tuple(groesse), Image.LANCZOS)
                bild = np.asarray(bild)
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
        w = self.schnittwerte(punkte, saat)
        je_dreieck = (w[dreiecke] < 0.0).any(axis=1)
        # Mehrere Hautmaterialien (Character Creator: Kopf, Körper, Arme, Beine — je eigene Bilder): nur Dreiecke des häufigsten
        # Materials, ihre UV gehören zu EINEM Bildsatz; die anderen fallen aus dem Stück und stehen im Bericht.
        slot, fremd = self.material_slot(je_dreieck)
        if fremd:
            je_dreieck &= np.asarray(self.koerper['material']) == slot
        self.waehle_material(slot)
        geschnitten = int(((w[dreiecke[je_dreieck]] < 0.0).sum(axis=1) < 3).sum())
        alle_punkte, schnitt_dreiecke, schnitt_uv = Blendimportschamschnitt.schneiden(
            punkte, dreiecke[je_dreieck], np.asarray(self.koerper['uv_ecken'])[je_dreieck], w)
        benutzt, neu = np.unique(schnitt_dreiecke, return_inverse=True)
        sel_punkte, sel_dreiecke = alle_punkte[benutzt], neu.reshape(-1, 3)
        sel_punkte, rand = self.angleichen(sel_punkte, sel_dreiecke, flaeche)
        # Geograft: das Loch in der Haut ist ein Kantenring der Figur, der Rand des Stücks liegt genau darauf (`Blendimportschamgeograft`).
        naht = Blendimportschamgeograft.verschweissen(flaeche, self.schnittwerte(punkte, saat, flaeche.vertices), sel_punkte, sel_dreiecke, schnitt_uv)
        if 'aus' not in naht:
            sel_punkte, sel_dreiecke, schnitt_uv = naht['punkte'], naht['dreiecke'], naht['uv_ecken']
        uv, quelle, atlas = self.haut(schnitt_uv, ordner, kennung)
        bericht = {'saat': int(saat.sum()), 'punkte': int(len(sel_punkte)), 'dreiecke': int(len(sel_dreiecke)), 'rand': rand, 'atlas': atlas,
                   'kasten_hoehe': list(self.kastenhoehe), 'material': slot, 'material_fremd': fremd, 'geschnitten': geschnitten,
                   'saat_breite_mm': self.saat_breite_mm, 'naht': naht['bericht'] if 'aus' not in naht else {'aus': naht['aus']}}
        logger.info('Scham-Stück: %s', bericht)
        return {'punkte': sel_punkte, 'dreiecke': sel_dreiecke, 'uv_ecken': uv, 'quelle': quelle, 'bericht': bericht,
                'loch': naht.get('loch')}
