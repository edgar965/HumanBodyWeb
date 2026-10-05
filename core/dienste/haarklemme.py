# -*- coding: utf-8 -*-
"""Haarklemme — die Frisur darf nicht weiter vom Kopf abstehen als das Haar der Fotos (04.10.2026).

Edgar (Auftrag 2026.10.04.11.11.44, zum dritten Mal): „Haar oben viel zu lang". Die Frisurwahl (`Meshfigurfrisur`) nimmt die Frisur der Garderobe, deren HÜLLE (je Richtung vom Kopf der weiteste Punkt,
`Haarhuelle`) im Mittel über alle Richtungen der Hülle des Netzhaars am nächsten kommt. Ein Tolle (Mavick Hair Style) passte an Seiten und Hinterkopf auf 2 mm und stand oben vorn trotzdem 39 mm
(Mittel, größtes Feld 62 mm) und am Scheitel 19 mm über der Hülle des Fotohaars — ein kurzer Haarschnitt im Foto, eine hohe Tolle im Modell (gemessen mit `ProjektTemp/_wegwerf/sapiens/haar_profil.py`
und `frisur_oben.py`: die anderen Frisuren der Liste stehen oben vorn 3–51 mm drüber, keine trifft überall).

Statt eine andere Frisur zu wählen, die dann an anderer Stelle schlechter sitzt, wird die gewählte an die Hülle des Fotohaars geklemmt: Ein Punkt, der in seiner Richtung (vom Kopfmittelpunkt aus) weiter
als die Hülle liegt, rückt weich an sie heran — `Hülle + TOLERANZ_M · tanh(Überstand ÷ TOLERANZ_M)`: kleine Überstände bleiben fast, große enden eine Toleranz über der Hülle. Haar, das innerhalb der Hülle
liegt, bleibt unberührt; Richtungen ohne Netzhaar (Gesicht, die Hülle ist dort leer) auch.

Die Hülle des Netzhaars schreibt der Schritt „Frisur" (`ergebnis/haar_huelle.npz`: `mitte`, `karte`, in der Lage der Bühne); Aufträge von davor haben nur `ergebnis/haar.glb` (das Haar des Netzes als
Objekt) — daraus wird sie gerechnet. Fehlt beides, klemmt nichts. Aufgerufen von `Kleidermodellbau.teile`, damit Bühne, Runden, Film und Export dieselbe Frisur sehen.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Haarklemme']


class Haarklemme:
    DATEI = 'haar_huelle.npz'
    #: Überstand über der Hülle des Fotohaars, ab dem ein Punkt nicht mehr weiter hinausgeht (Meter).
    TOLERANZ_M = 0.008
    #: Proben auf dem Netzhaar für die Hülle (wie `Meshfigurfrisur.PROBEN`).
    PROBEN = 60000
    #: Feld ohne Netzhaar: so groß, dass nichts geklemmt wird.
    OFFEN = 10.0
    #: Teile, die keine Kopfhaare sind (`Haarzonen.OHNE`).
    OHNE = ('_beard',)

    def __init__(self, karte, mitte):
        from Haar.haarhuelle import Haarhuelle

        self.mitte = np.asarray(mitte, dtype=np.float64)
        self.feld = float(Haarhuelle.FELD_GRAD)
        roh = np.asarray(karte, dtype=np.float64)
        self.roh = roh                                  # die Hülle des Netzhaars je Feld, NaN ohne Netzhaar (die Haarkappe, `Haarkappe`, liest sie ungeglättet)
        # Die Hülle nach außen wie ein Haarfeld glätten (das Maximum der Nachbarn): einzelne Felder mit zu wenig Proben dürfen kein Loch in die Grenze schneiden.
        from scipy import ndimage
        groesst = ndimage.maximum_filter(np.where(np.isnan(roh), -np.inf, roh), size=3, mode=('nearest', 'wrap'))
        self.grenze = np.where(np.isfinite(groesst), groesst, self.OFFEN)

    # ------------------------------------------------------------------ Laden

    @classmethod
    def fuer(cls, ablage, koerper=None):
        """Die Klemme eines Auftrags — None, wenn weder `haar_huelle.npz` noch `haar.glb` da sind. `koerper`: Punkte der Haut (N, 3) in der Lage der Bühne; nur für die Rechnung aus `haar.glb` gebraucht."""
        try:
            pfad = ablage.ergebnis(cls.DATEI)
            if pfad.is_file():
                with np.load(pfad) as d:
                    return cls(d['karte'], d['mitte'])
            glb = ablage.ergebnis('haar.glb')
            if glb.is_file() and koerper is not None:
                return cls._aus_glb(glb, koerper)
        except Exception:  # noqa: BLE001 — ohne Klemme bleibt die Frisur wie gewählt (Warnung im Log)
            logger.exception('Haarklemme: Hülle des Fotohaars nicht gelesen')
        return None

    @staticmethod
    def kopfmitte(koerper):
        """Kopfmittelpunkt aus den Hautpunkten: x und z aus der Spanne des Kopfes (0,20 m unter dem Scheitel), y = Scheitel − 0,10 m (wie `Meshfigurfrisur._messung`)."""
        p = np.asarray(koerper, dtype=np.float64)
        scheitel = float(p[:, 1].max())
        kopf = p[p[:, 1] > scheitel - 0.20]
        return np.array([0.5 * float(kopf[:, 0].min() + kopf[:, 0].max()), scheitel - 0.10, 0.5 * float(kopf[:, 2].min() + kopf[:, 2].max())])

    @classmethod
    def _aus_glb(cls, glb, koerper):
        import trimesh
        from Haar.haarhuelle import Haarhuelle

        szene = trimesh.load(str(glb), force='scene')
        punkte, flaechen, ab = [], [], 0
        for g in szene.geometry.values():
            punkte.append(np.asarray(g.vertices, dtype=np.float64))
            flaechen.append(np.asarray(g.faces, dtype=np.int64) + ab)
            ab += len(g.vertices)
        mitte = cls.kopfmitte(koerper)
        karte = Haarhuelle(mitte).karte(Haarhuelle.proben(np.vstack(punkte), np.vstack(flaechen), cls.PROBEN))
        return cls(karte, mitte)

    @classmethod
    def ablegen(cls, ablage, mitte, karte):
        """Die Hülle des Netzhaars für später ablegen (Schritt „Frisur")."""
        np.savez_compressed(ablage.ergebnis(cls.DATEI), mitte=np.asarray(mitte, dtype=np.float64), karte=np.asarray(karte, dtype=np.float64))

    # ------------------------------------------------------------------ Anwenden

    def _grenze_je_punkt(self, d, r, karte=None):
        """Radius der Hülle in der Richtung jedes Punkts (bilinear zwischen den Feldern, Azimut umlaufend); `karte`: eine andere Karte derselben Felder (Vorgabe: die geklemmte Grenze)."""
        from scipy import ndimage

        grenze = self.grenze if karte is None else karte
        hoehe, breite = grenze.shape
        az = np.degrees(np.arctan2(d[:, 0], d[:, 2])) % 360.0
        el = np.degrees(np.arcsin(np.clip(d[:, 1] / np.maximum(r, 1e-12), -1.0, 1.0)))
        zeile = np.clip((el + 90.0) / self.feld - 0.5, 0.0, hoehe - 1.0)
        spalte = az / self.feld - 0.5 + 1.0                      # +1: eine Spalte Umlauf vorn
        rund = np.concatenate([grenze[:, -1:], grenze, grenze[:, :1]], axis=1)
        return ndimage.map_coordinates(rund, [zeile, spalte], order=1, mode='nearest')

    def klemmen(self, punkte):
        """`(neue Punkte, Anzahl bewegt, größte Bewegung in m)` für Punkte (N, 3) in der Lage der Bühne."""
        p = np.asarray(punkte, dtype=np.float64)
        d = p - self.mitte
        r = np.linalg.norm(d, axis=1)
        h = self._grenze_je_punkt(d, r)
        ueber = r - h
        wirkt = (ueber > 0.0) & (h < self.OFFEN)
        if not wirkt.any():
            return p, 0, 0.0
        neu_r = h[wirkt] + self.TOLERANZ_M * np.tanh(ueber[wirkt] / self.TOLERANZ_M)
        aus = p.copy()
        aus[wirkt] = self.mitte + d[wirkt] * (neu_r / np.maximum(r[wirkt], 1e-12))[:, None]
        return aus, int(wirkt.sum()), float((r[wirkt] - neu_r).max())

    def anwenden(self, teile):
        """Die Kopfhaar-Teile (`art == 'haar'`, ohne Bart) an die Hülle klemmen — `punkte` und, bei Strähnen, `kurven.punkte`; die Teile selbst werden ersetzt, nicht verändert (der Teilevorrat hält die Originale)."""
        aus = []
        for t in teile:
            if t.get('art') != 'haar' or any(o in str(t.get('sorte')) for o in self.OHNE):
                aus.append(t)
                continue
            punkte, n, weit = self.klemmen(t['punkte'])
            neu = dict(t, punkte=punkte)
            if t.get('kurven'):
                kp, _n2, _w2 = self.klemmen(t['kurven']['punkte'])
                neu['kurven'] = dict(t['kurven'], punkte=kp.astype(np.asarray(t['kurven']['punkte']).dtype))
            logger.info('Haarklemme %s: %d von %d Punkten an die Hülle des Fotohaars gerückt (am weitesten %.1f mm)', t.get('sorte'), n, len(punkte), weit * 1000.0)
            aus.append(neu)
        return aus
