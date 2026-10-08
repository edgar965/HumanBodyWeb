# -*- coding: utf-8 -*-
"""Meshfigurlandmarkmorphe — drei neue Eigenmorphe für Brauen, Mund und Nase, die den Rest über die Reglergrenzen hinaus holen (07.10.2026, nur „2D3D Kleider"; die Lider seit 08.10.2026 nicht mehr, siehe `BEREICHE`).

Edgar: „augenform auch nicht … mundproportionen und nasenproportionen stimmen nicht", „erweitere ggf. die Augen-, Mund- und Nasenregler, … baue neue Morphs". Gemessen an `Edgar 10 - Hunyan Kopf`
(`…17.45.25`): 21 Gesichtsregler stehen am Anschlag (`Eyes Upper Outer/Middle/Inner`, `Eyelids Lower Height Center`, `Lip Upper Pout/Peaks Size/Fuller/…`, `Nose Septum Width`, …), und die
EIGENEN Landmarken der Figur liegen 1,5 (Lippen), 2,2 (Augen), 3,2 (Nase) und 3,3 mm (Brauen) neben denen des Kopfnetzes; die Augenöffnung des Modells ist 0,87/0,76 cm gegen 0,49/0,57 cm im Netz,
der innere Mundspalt links 2,8 gegen 0,4 mm („Mund halb offen"). Die Fläche selbst sitzt dabei auf 0,4 mm am Netz — die Gesichtsmerkmale (Lidrand, Lippenlinie, Nasenflügel) liegen nur an der
falschen Stelle der Fläche, und die Regler können sie nicht mehr dorthin schieben.

Was hier gerechnet wird, je Bereich (`brauen`, `mund`, `nase`; bis 07.10.2026 abends `augen` mit Brauen):
1. Ziele: die Landmarken des Netzes (Ruhelage, Kopfhaltung zurückgedreht — `Engine2d3dKleiderGesichtslage`), auf die Netzfläche gelegt (bis 8 mm; sie schweben im Mittel 1,3–2,5 mm darüber, und
   ein Morph auf eine schwebende Landmarke höbe die Fläche ab).
2. Reste: Ziel minus die eigene Landmarke der Figur (Dreieck + Anteile) auf dem Käfig MIT dem geglätteten Rest-Morph; je Landmarke höchstens `KLEMME` (8 mm).
3. Ein Gauß-RBF (`SIGMA` 10 mm, `REGULARISIERUNG` 0,1) über die Landmarken des Bereichs verschiebt die Käfigpunkte im Umkreis; der Morph ist diese Verschiebung. Ein Bereich ist EIN Morph mit EINEM
   Regler (Wert 1,0 in der Stellung, `Engine2d3dKleiderauftrag.stellung`), die drei sind unabhängig voneinander einstellbar.
Probe an der fertigen Figur (σ 10 mm): Landmarken Lippen 1,53 → 0,47, Nase 3,19 → 0,36, Augen 2,22 → 0,49, Brauen 3,31 → 0,21 mm; größter Verschiebungsunterschied je Kante / Kantenlänge 0,69 (1,0 wäre eine Falte).
Das Gesichtsoval (Schläfen, Kinn) bleibt draußen: im Netz liegt dort Haar und Bart, die Figur hat keins.
"""

import logging

import numpy as np

from .engine2d3dkleidergesichtslage import Engine2d3dKleiderGesichtslage

logger = logging.getLogger('core')

__all__ = ['Meshfigurlandmarkmorphe']


class Meshfigurlandmarkmorphe:
    G = Engine2d3dKleiderGesichtslage.GRUPPEN
    #: Bereich → MediaPipe-Landmarken des Bereichs.
    #: **Die Lider (`Augen`) sind seit 08.10.2026 NICHT mehr dabei** (Edgar: „augen sind noch kaputt"): das Kopfnetz hat gemalte, halb geschlossene Augen in einer Mulde; zog der Morph die Lidränder
    #: zu diesen Landmarken (bis 8 mm), saßen die Lider auf den Augäpfeln und weißer Augapfel stand unter ihnen heraus (Nahbild `hals_bild/augen_nah_vergleich.png`: Lauf ohne Morph heil, mit Morph zerstört;
    #: dasselbe Standmodell mit nur dem Augenmorph aus wieder heil). Die Lider formen die Genesis-Regler; die Brauen bleiben im Morph.
    BEREICHE = {'brauen': sorted(G['Brauen']), 'mund': sorted(G['Lippen']), 'nase': sorted(G['Nase'])}
    SIGMA = 0.010
    REGULARISIERUNG = 0.1
    KLEMME = 0.008
    #: Käfigpunkte weiter als so viele σ von jeder Landmarke des Bereichs bleiben unberührt.
    REICHWEITE = 4.0

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    # ----------------------------------------------------------------------------- Aufruf

    def bauen(self, rest, gewicht, name, stellung):
        """`{bereich: {regler, punkte, max_mm, landmarken_mm: {vorher, nachher}}}` — legt je Bereich einen Eigenmorph `<name> <bereich>` ab. `rest`/`gewicht` (N,3)/(N,) sind der Rest des Laufs
        (vor dem Glätten), `stellung` die Reglerstellung OHNE Rest-Morph und ohne diese Morphe (so rechnet der Schritt „rest"); leer, wenn Netz oder Landmarken fehlen."""
        from Genesis9.eigenmorphe import G9eigenmorphe
        from Genesis9.restmorph import G9restmorph

        lage = Engine2d3dKleiderGesichtslage.berechnen(self.job, self.ablage, stellung)
        if lage['netz_pfad'] is None or lage['modell_gesicht'] is None:
            return {}
        ruhe = lage['ruhe']
        if len(ruhe) != len(rest):
            return {}
        punkte = ruhe + G9restmorph.glaetten(rest, gewicht)         # die Figur, so wie der Rest-Morph des Laufs sie ablegen wird
        modell = Engine2d3dKleiderGesichtslage._modell_gesicht(self.ablage, punkte)
        ziel = Engine2d3dKleiderGesichtslage.auf_flaeche(lage)
        ergebnis = {}
        for bereich, indizes in self.BEREICHE.items():
            nutzbar = [i for i in indizes if np.isfinite(modell[i]).all() and np.isfinite(ziel[i]).all()]
            if len(nutzbar) < 4:
                continue
            reste = self._klemmen(ziel[nutzbar] - modell[nutzbar])
            feld = self._feld(modell[nutzbar], reste, punkte)
            nummern = np.flatnonzero(np.linalg.norm(feld, axis=1) > 1e-5).astype(np.int32)
            if not len(nummern):
                continue
            vorher = np.linalg.norm(ziel[nutzbar] - modell[nutzbar], axis=1) * 1000.0
            nachher = np.linalg.norm(ziel[nutzbar] - (modell[nutzbar] + self._feld(modell[nutzbar], reste, modell[nutzbar])), axis=1) * 1000.0
            regler = G9eigenmorphe.ablegen(
                '%s %s' % (name, bereich), nummern, feld[nummern],
                {'quelle': 'mesh to 3d', 'art': 'landmarkmorph', 'auftrag': self.job.kennung, 'bereich': bereich},
            )
            ergebnis[bereich] = {
                'regler': regler, 'punkte': int(len(nummern)), 'max_mm': round(float(np.linalg.norm(feld[nummern], axis=1).max()) * 1000.0, 2),
                'landmarken': len(nutzbar), 'landmarken_mm': {'vorher': round(float(np.median(vorher)), 2), 'nachher': round(float(np.median(nachher)), 2)},
            }
        return ergebnis

    # ----------------------------------------------------------------------------- Rechnung

    @classmethod
    def _klemmen(cls, reste):
        laenge = np.linalg.norm(reste, axis=1)
        zu_lang = laenge > cls.KLEMME
        aus = np.array(reste, dtype=float, copy=True)
        aus[zu_lang] *= (cls.KLEMME / laenge[zu_lang])[:, None]
        return aus

    @classmethod
    def _feld(cls, zentren, reste, orte):
        """Gauß-RBF: die Verschiebung an `orte` (M, 3), die an `zentren` (K, 3) die `reste` (K, 3) hervorbringt (mit Regularisierung); 0 jenseits der `REICHWEITE`."""
        abstand = np.linalg.norm(zentren[:, None] - zentren[None], axis=2)
        gewichte = np.linalg.solve(np.exp(-((abstand / cls.SIGMA) ** 2)) + cls.REGULARISIERUNG * np.eye(len(zentren)), reste)
        aus = np.zeros((len(orte), 3))
        for anfang in range(0, len(orte), 4000):
            stueck = orte[anfang:anfang + 4000]
            d = np.linalg.norm(stueck[:, None] - zentren[None], axis=2)
            nah = d.min(axis=1) <= cls.REICHWEITE * cls.SIGMA
            aus[anfang:anfang + 4000][nah] = np.exp(-((d[nah] / cls.SIGMA) ** 2)) @ gewichte
        return aus
