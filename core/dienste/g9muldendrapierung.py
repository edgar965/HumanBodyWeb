# -*- coding: utf-8 -*-
u"""G9muldendrapierung — Daz-Oberteile über die Mulden der Haut legen (25.10.2026, Stufe K2c): die Anbindung von `G9drapierer` mit dem Hindernis
`G9muldenhindernis` an die Stückrechnung (`G9stueckteile.netze`), gebaut wie `G9anatomiedrapierung`.

WARUM (Edgar, 25.10.2026: „könnte man diese Einstellungen auch an alle existierenden Genesis-Teile anhängen?“, Empfehlung „Brücke über einen
verallgemeinerten Drapierer“, Antwort „Mach weiter, alle Aufgaben“): Ein Daz-Oberteil liegt in der Brustmitte auf der Haut, weil es auf sie projiziert ist.
Die drei Regler `drapierung:bruecke_*` (`G9drapierung.bruecke`) heißen dasselbe wie die der Brücke an den eigenen Stücken; Ausbreitung 0 (Vorgabe) heißt
„aus“ — dann rechnet hier nichts, und ein Stück sieht aus wie bisher.

BEREICH UND ORT je Käfigpunkt, einmal je Prozess, aus der Grundfigur (wie die Körperkoordinaten `G9koerperkoordinaten`, deren Konstanten hier gelten): Rumpf
(Kette `rumpf` des führenden Knochens, `G9koerperteile.genesis_punkte`) und Beinpunkte über dem Schritt (Rumpfhöhe < 1); die Brücke gilt nicht über
Schulterhöhe (Rumpfhöhe `OBEN_AB` … `OBEN_VOLL`) und nicht an der Achsel (Armanteil eines Rumpfpunkts über −0,15 … −0,05) — dieselben Grenzen wie
`Eigenkleidbruecke._ort` im Browser. Numpy, ohne Grafikkarte: 25.182 Punkte, keine Inselbereinigung (für die Grenzen eines Bereichs genügt der führende
Knochen). Auf die Browserpunkte der Stufe über `G9netzstufe.skalar`.

DIE HAUT ist die der Figur dieser Stellung und Stufe (`G9koerpernetz.koerperflaeche`, ohnehin gemerkt); die Querschnitte darüber je Stellung, Stufe EINMAL
(`_raster`, höchstens `VORRAT` Stellungen). Der Drapierer bekommt als Ausbreitung `RAND_M`: so weit um die überbrückten Hautpunkte darf der Löser den Hub
auslaufen lassen; die Ausbreitung des Reglers wirkt in der Anforderung selbst (wie im Browser).
"""
import logging
import threading

import numpy as np
from Genesis9.drapierer import G9drapierer
from Genesis9.drapierung import G9drapierung
from Genesis9.muldenhindernis import G9muldenhindernis
from Genesis9.querschnitthuelle import G9querschnitthuelle

from .g9hbstoffkorrektur import G9hbstoffkorrektur
from .g9koerperkoordinaten import G9koerperkoordinaten

logger = logging.getLogger('core')

__all__ = ['G9muldendrapierung']


class G9muldendrapierung:
    u"""`fuer(formung, stufen, regler)` -> Drapierung oder None; `anwenden(punkte, flaechen, normalen, regler)` -> (Punkte, Bilanz)."""

    MELDUNG = u'über Mulden gebrückt'
    #: Saum um die überbrückte Haut, in dem der Löser den Hub auslaufen lässt: `RAND_ANTEIL` der Ausbreitung, höchstens `RAND_M` — gesetzt. Mit festen 2 cm
    #: hob der Löser die Brustmitte auch bei Ausbreitung 4 cm auf 34,6 mm (Mulde 38,7 mm, `ProjektTemp/_wegwerf/dazeigen/mulde_probe.py`, 25.10.2026): Die
    #: Membran spannte über die ausgeblendete Mitte hinweg, die Ausbreitung hatte kaum Wirkung.
    RAND_M = 0.02
    RAND_ANTEIL = 0.15
    #: Der Löser rechnet als Membran (Glättung 0): Mit der Platte (Glättung 1) stand der Stoff in der Brustmitte 45,0 mm über der Haut, über der Hülle plus
    #: Abstand (41,9 mm) — „weich“ hob also mehr statt weniger. Die Glättung des Reglers mischt deshalb nur Zelt und Rund in der Anforderung (wie im Browser).
    LOESER_GLAETTUNG = 0.0
    #: Wie `Eigenkleidbruecke.OBEN_AB` / `OBEN_VOLL` und die Achselgrenze in `_ort`.
    OBEN_AB, OBEN_VOLL = 0.12, 0.2
    ACHSEL = (-0.15, -0.05)
    VORRAT = 4

    _kaefig = None
    _raster = {}
    _schloss = threading.Lock()

    def __init__(self, hindernis):
        self.hindernis = hindernis

    @classmethod
    def fuer(cls, formung, stufen, regler):
        u"""Die Drapierung für eine Figur dieser Stellung und Stufe — None, wenn die Ausbreitung 0 ist (keine Brücke gewollt)."""
        _abstand, ausbreitung, glaettung = G9drapierung.bruecke(regler)
        if ausbreitung <= 5.0e-4:
            return None
        haut, normalen, bereich, ort, raster = cls._figur(formung, stufen)
        return cls(G9muldenhindernis(haut, normalen, bereich, ort, ausbreitung, glaettung, raster=raster))

    def anwenden(self, punkte, flaechen, normalen, regler):
        u"""`(punkte (N, 3), bilanz)`: der Stoff mit `flaechen` (Dreiecke oder Vierecke) und seinen Normalen über die Brücke drapiert. Zeigen die Normalen
        überwiegend nach innen (gegen die waagrechte Hubrichtung der Punkte unter der Brücke), werden sie umgedreht — sonst höbe der Löser nach innen."""
        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = G9hbstoffkorrektur.dreiecke(flaechen, len(punkte))
        if not len(punkte) or not len(dreiecke) or normalen is None:
            return punkte, {'gehoben': 0}
        normalen = np.asarray(normalen, dtype=np.float64)
        hub, richtung = self.hindernis._hub(punkte)
        unter = hub > self.hindernis.MINDEST_M
        if unter.any() and float(np.median((normalen[unter] * richtung[unter]).sum(axis=1))) < 0.0:
            normalen = -normalen
        abstand, ausbreitung, _glaettung = G9drapierung.bruecke(regler)
        rand = min(self.RAND_M, self.RAND_ANTEIL * ausbreitung)
        return G9drapierer.drapieren(punkte, dreiecke, normalen, self.hindernis, abstand, rand, self.LOESER_GLAETTUNG)

    def kaefig(self, folger, punkte, regler):
        u"""Die KÄFIGpunkte eines Teils (vor der Unterteilung, `G9koerpernetz.folgernetz`) über die Brücke gelegt -> (Punkte, Bilanz). Auf dem Käfig, nicht auf den
        Browserpunkten: gemessen 25.10.2026 (`ProjektTemp/_wegwerf/dazeigen/mulde_profil.py`, Basic Wear T Shirt auf DamiraAlt, Stufe 1) hatte das Browsernetz
        83.347 Punkte, der Löser brauchte 23 `spsolve` zu je 0,6 s = 18,2 s. Die Unterteilung danach glättet, Kollision und Bindung rechnen auf dem Ergebnis."""
        from Genesis9.netzteilung import G9netzteilung
        punkte = np.asarray(punkte, dtype=np.float64)
        vierecke, dreiecke = G9netzteilung.ecken(folger.polys)
        flaechen = np.vstack([dreiecke.reshape(-1, 3), vierecke.reshape(-1, 4)[:, [0, 1, 2]], vierecke.reshape(-1, 4)[:, [0, 2, 3]]])
        return self.anwenden(punkte, flaechen, G9netzteilung.normalen(punkte, folger.polys), regler)

    # ------------------------------------------------------------------ Figur

    @classmethod
    def _figur(cls, formung, stufen):
        u"""(Haut, Normalen, Bereich, Ort, Querschnitte) der Figur dieser Stellung und Stufe — je Schlüssel einmal."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.koerpernetz import G9koerpernetz
        schluessel = (formung.fingerabdruck(), int(stufen))
        with cls._schloss:
            aus = cls._raster.get(schluessel)
        if aus is not None:
            return aus
        haut, normalen, _baum = G9koerpernetz(formung, stufen=stufen).koerperflaeche()
        bereich_k, ort_k = cls.kaefigwerte()
        stufe = G9basisnetz.holen().netzstufe(stufen)
        bereich = stufe.skalar(bereich_k.astype(np.float64)) > 0.5
        ort = np.clip(stufe.skalar(ort_k), 0.0, 1.0)
        haut = np.asarray(haut, dtype=np.float64)
        aus = (haut, np.asarray(normalen, dtype=np.float64), bereich, ort, G9querschnitthuelle.raster(haut[bereich]))
        with cls._schloss:
            if len(cls._raster) >= cls.VORRAT:
                cls._raster.pop(next(iter(cls._raster)))
            cls._raster[schluessel] = aus
        return aus

    @classmethod
    def kaefigwerte(cls):
        u"""(Bereich (N,) bool, Ort (N,) 0…1) je Käfigpunkt der Grundfigur — einmal je Prozess."""
        with cls._schloss:
            if cls._kaefig is None:
                cls._kaefig = cls._kaefig_rechnen()
            return cls._kaefig

    @staticmethod
    def _glatt(a, b, x):
        t = np.clip((x - a) / (b - a), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    @classmethod
    def _kaefig_rechnen(cls):
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        k = G9koerperkoordinaten
        p = np.asarray(G9basisnetz.holen().punkte, dtype=np.float64)
        teil = G9koerperteile.genesis_punkte(G9haut.holen())
        je_teil = np.array([k.nummer(k.TEIL_KETTE.get(t, 'keine')) for t in G9koerperteile.TEILE] + [0], dtype=np.int64)
        kette = je_teil[teil]                                         # Teil −1 → letzte Zeile = keine
        rumpf = kette == k.nummer('rumpf')
        gelenk = k.gelenke()
        mitte = rumpf & (np.abs(p[:, 0]) < k.SCHRITT_BREITE_M)
        y0, y1 = float(gelenk[k.HALS][1]), float(p[mitte, 1].min())
        hoehe = (y0 - p[:, 1]) / (y0 - y1)
        armanteil = np.full(len(p), k.OHNE)
        for name in ('arm_links', 'arm_rechts'):
            a, b, c = (gelenk[g] for g in k.GLIEDER[name])
            seite = (p[:, 0] > 0) if name.endswith('links') else (p[:, 0] <= 0)
            nah = rumpf & seite & (hoehe < 0.5) & (np.linalg.norm(p - a, axis=1) < k.SCHULTER_M)
            armanteil[nah] = cls._glied(p[nah], a, b, c)
        bein = (kette == k.nummer('bein_links')) | (kette == k.nummer('bein_rechts'))
        bereich = rumpf | (bein & (hoehe < 1.0))
        ort = cls._glatt(cls.OBEN_AB, cls.OBEN_VOLL, hoehe) * (1.0 - cls._glatt(cls.ACHSEL[0], cls.ACHSEL[1], armanteil))
        logger.info('Brücke über Mulden: Bereich %d von %d Käfigpunkten, Halsansatz y %.4f, Schritt y %.4f', int(bereich.sum()), len(p), y0, y1)
        return bereich, np.where(bereich, ort, 0.0)

    @staticmethod
    def _glied(p, a, b, c):
        u"""Anteil entlang a → b → c wie `G9koerperkoordinaten.glied` (numpy, ohne Winkel)."""
        l1, l2 = float(np.linalg.norm(b - a)), float(np.linalg.norm(c - b))

        def stueck(s, e):
            d = e - s
            u = (p - s) @ d / (d @ d)
            return u, np.linalg.norm(p - (s + np.clip(u, 0.0, 1.0)[:, None] * d), axis=1)
        u1, d1 = stueck(a, b)
        u2, d2 = stueck(b, c)
        return np.where(d1 <= d2, np.minimum(u1, 1.0) * l1, l1 + np.maximum(u2, 0.0) * l2) / (l1 + l2)
