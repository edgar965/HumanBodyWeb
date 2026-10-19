# -*- coding: utf-8 -*-
u"""G9lagenanatomie — getragene Anatomien liegen unter jedem Stück, das ihnen nahe kommt (aus `g9lagenanfrage.py` herausgelöst, 19.10.2026).

UNTER JEDEM STÜCK (11.10.2026, Edgar: „die Kleider müssen so gefittet werden, dass sie inklusive Scham passen"): Die Tiefenregel (`G9lagen.einordnen`:
außen liegt, was weiter von der Haut steht) hielt das Geograft, das 15–40 mm vor der Haut steht, für das äußere Stück — die Hose blieb auf der Haut und die
Scham zeichnete sich durch den Stoff. Zwischen zwei Anatomien bleibt es bei der Tiefenregel.

AUCH OHNE EINORDNUNG (19.10.2026, Edgar: „mach das auch für männliche Genitalien mit Matt0", „checke alle Hosen …"): `G9lagen.einordnen` meldet ein Paar
erst ab `MINDESTZONE` (20) Käfigpunkten je Seite binnen `NAEHE` (3 cm). Der Käfig von `mh_cortu_cargo_pants` (856 Punkte im Browser) bringt das im Schritt
nicht: das Geograft stand weder innen noch außen, Anhebung und Drapierer liefen nicht (`G9stueckteile._drapiert` wurde nicht aufgerufen, im Protokoll keine
Zeile „drapiert"), und an Matt0 lag die Hose ganz hinter dem Genital (im Chrome gesehen). Jetzt kommt eine getragene Anatomie auch dann unter das Stück,
wenn EIN Käfigpunkt des Stücks binnen NAEHE an ihr liegt — ein Hut oder ein Schuh bleibt davon unberührt.
"""
import numpy as np

__all__ = ['G9lagenanatomie']


class G9lagenanatomie:
    u"""`unten(...)` -> `(innen, aussen)` mit den Anatomien an ihrem Platz."""

    @staticmethod
    def unten(kennung, kaefig, andere, innen, aussen, ist_anatomie, naehe):
        u"""`kennung`: das angefragte Stück, `kaefig` (N, 3) sein Käfig; `andere`: `[(kennung, punkte, spaeter)]` der getragenen Stücke; `innen`/`aussen`:
        die Einordnung (`G9lagen.einordnen`); `ist_anatomie(kennung)` -> bool; `naehe` in Metern."""
        if ist_anatomie(kennung):
            return [k for k in innen if ist_anatomie(k)], aussen + [k for k in innen if not ist_anatomie(k)]
        innen = innen + [k for k in aussen if ist_anatomie(k)]
        aussen = [k for k in aussen if not ist_anatomie(k)]
        return innen + G9lagenanatomie._nah(kaefig, andere, innen, aussen, ist_anatomie, naehe), aussen

    @staticmethod
    def _nah(kaefig, andere, innen, aussen, ist_anatomie, naehe):
        u"""Die getragenen Anatomien, die die Einordnung überging, aber binnen `naehe` an einem Käfigpunkt liegen."""
        if not len(kaefig):
            return []
        from scipy.spatial import cKDTree
        baum, dazu = None, []
        for k, punkte, _spaeter in andere:
            if k in innen or k in aussen or not len(punkte) or not ist_anatomie(k):
                continue
            if baum is None:
                baum = cKDTree(np.asarray(kaefig, dtype=np.float64))
            abstand, _i = baum.query(np.asarray(punkte, dtype=np.float64))
            if (abstand < naehe).any():
                dazu.append(k)
        return dazu
