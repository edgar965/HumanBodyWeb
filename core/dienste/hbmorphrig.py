# -*- coding: utf-8 -*-
u"""Hbmorphrig — welcher HB-Morph das Skelett mitnehmen muesste.

DER VORFALL (Edgar, 20.09.2026, mit Bild: „HB Cheeks Mass zerstoert den
ganzen Koerper. Deine Testcases meldeten gruen???")
=====================================================================
Das Bild zeigte einen Mund von fast einem Meter am Hals einer geschrumpften
Figur. Gemessen am Netz-Endpunkt (`_wegwerf/hb_cheeks_probe.py`): Cheeks
Mass bewegt 3,9 mm im Gesicht und sonst nichts — der Schuldige war
`hb:Body_Size` -100 % daneben in derselben Liste: 535 mm am Koerper, und
die Anhaenge, die dem Koerper per Projektion folgen (Auto-Follow,
`G9folger`), wurden dabei aufgeblasen: Mund 6,8 -> 94 cm, Wimpern 10 -> 73
cm, Brauen 11 -> 35 cm. Genau das zeigt das Bild.

WARUM: Ein HB-Morph ist eine reine Verschiebung der Kaefigpunkte. Daz'
eigene Proportionsregler (Height, Legs Length) ziehen ueber Formeln die
Knochen mit; die HumanBody-Regler haben solche Formeln nicht. Solange kein
Skelett-Nachzug fuer sie existiert, duerfen nur Morphs ins Bedienfeld, die
die Gelenke NICHT verschieben: Formen (Mass, Tone, Girth, Volume, Groesse
einzelner Zuege), keine Laengen, keine Winkel, keine Gesamtgroesse.

DIE MESSUNG (je Morph, beide Seiten, auf dem Kaefig):
Ein Gelenk wird geschaetzt als gewichtetes Mittel der Kaefigpunkte, die an
seinem Knochen haengen (`G9haut`, vier Einfluesse je Punkt) und naeher als
RADIUS am Gelenkkopf liegen; die Verschiebung des Gelenks ist das
gewichtete Mittel ihrer Deltas. Daraus:

    kopf_mm    Verschiebung des Kopfgelenks — Augen, Mund, Wimpern, Brauen
               haengen daran; wandert es, laufen die Anhaenge weg.
    laenge_mm  groesste Aenderung eines Knochenabstands Kind-Eltern —
               Proportion; das Skelett muesste folgen.

Gemessen am 20.09.2026 (`_wegwerf/hb_gelenke_scan.py`): Body_Size 573 mm
Gelenk / 167 mm Laenge, Legs LowerlegLength 146 / 143, Torso_Length 54 /
14, Neck_Length 34 / 15, Hands_Size 28 / 8,3, Head_SizeZ 19 / 7,6 mit
Kopf 8,4 — gegenueber Torso_BreastMass 0 / 0, Cheeks_Mass 1,9 / 0,1,
Torso_Mass 37 / 7,0 (die Oberflaeche wandert, nicht das Gelenk: die
Schaetzung aus Hautpunkten ueberzeichnet Massemorphe — deshalb zaehlt
nur Laenge und Kopf, nicht der rohe Gelenkwert).
"""
import numpy as np
from Genesis9.formung import G9formung
from Genesis9.haut import G9haut

__all__ = ['Hbmorphrig']


class Hbmorphrig:
    u"""Gelenkverschiebung eines Morphs schaetzen und ueber den Rig-Ausschluss entscheiden."""

    #: Punkte bis hierher (m) vom Gelenkkopf zaehlen fuer das Gelenk.
    RADIUS = 0.08
    #: Mindestgewicht, damit ein Gelenk ueberhaupt geschaetzt wird.
    MINDESTGEWICHT = 0.5
    #: Ab hier muesste das Skelett folgen — der Morph bleibt draussen.
    KOPF_MM = 5.0
    LAENGE_MM = 7.5
    KOPF = 'head'

    def __init__(self, formung=None):
        self.formung = formung or G9formung({})
        self.basis = np.asarray(self.formung.punkte(), dtype=np.float64)
        knochen = self.formung.skelett().gelenkknochen()
        hoch = np.array([0.0, self.formung.boden(), 0.0])
        self.kopf = {k['name']: np.asarray(k['kopf'], dtype=np.float64) + hoch for k in knochen}
        self.eltern = {k['name']: k['eltern'] for k in knochen}
        self.bindung = self._bindung(G9haut.holen())

    def _bindung(self, haut):
        u"""`{knochen: (Punktnummern, Gewichte)}` nahe am jeweiligen Gelenkkopf."""
        spalte = {n: i for i, n in enumerate(haut.knochen)}
        aus = {}
        for name, kopf in self.kopf.items():
            i = spalte.get(name)
            if i is None:
                continue
            gewicht = np.where(haut.index == i, haut.gewicht, 0.0).sum(axis=1)
            nah = (gewicht > 0) & (np.linalg.norm(self.basis - kopf, axis=1) < self.RADIUS)
            if gewicht[nah].sum() >= self.MINDESTGEWICHT:
                aus[name] = (np.nonzero(nah)[0], gewicht[nah])
        return aus

    # ------------------------------------------------------------- messen

    def gelenke(self, nummern, deltas):
        u"""`{knochen: Verschiebung (3,)}` fuer ein Delta-Feld auf Kaefigpunkten."""
        voll = np.zeros_like(self.basis)
        voll[np.asarray(nummern, dtype=np.int64)] = np.asarray(deltas, dtype=np.float64)
        return {name: (voll[nr] * w[:, None]).sum(axis=0) / w.sum()
                for name, (nr, w) in self.bindung.items()}

    def messen(self, nummern, deltas):
        u"""`{kopf_mm, laenge_mm, gelenk_mm}` eines Delta-Felds."""
        v = self.gelenke(nummern, deltas)
        laenge = 0.0
        for name, e in self.eltern.items():
            if name in v and e in v:
                alt = np.linalg.norm(self.kopf[name] - self.kopf[e])
                neu = np.linalg.norm(self.kopf[name] + v[name] - self.kopf[e] - v[e])
                laenge = max(laenge, abs(float(neu - alt)))
        gelenk = max((float(np.linalg.norm(x)) for x in v.values()), default=0.0)
        kopf = float(np.linalg.norm(v.get(self.KOPF, np.zeros(3))))
        return {'kopf_mm': round(kopf * 1000, 2), 'laenge_mm': round(laenge * 1000, 2),
                'gelenk_mm': round(gelenk * 1000, 2)}

    def beide(self, nummern, plus, minus):
        u"""Das Maximum beider Seiten, plus `rig` (True = braucht Skelett-Nachzug)."""
        a, b = self.messen(nummern, plus), self.messen(nummern, minus)
        mass = {k: max(a[k], b[k]) for k in a}
        mass['rig'] = self.braucht_rig(mass)
        return mass

    @classmethod
    def braucht_rig(cls, mass):
        return mass['kopf_mm'] >= cls.KOPF_MM or mass['laenge_mm'] >= cls.LAENGE_MM
