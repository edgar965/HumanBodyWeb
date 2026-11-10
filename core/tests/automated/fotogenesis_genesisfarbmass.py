# -*- coding: utf-8 -*-
"""Fotogenesisgenesisfarbmass — hat jeder sichtbare Punkt der Genesis-Figur die Farbe, die die Fotos an ihm zeigen? (30.10.2026, Edgar mit einem Bild der Figur von schräg hinten:
„Textur T-Shirt hinten kaputt“, „Textur an den Armen seitlich kaputt (schwarzer streifen)“, „texturfehler am Hals und oberen T-shirt (weisse flecken)“.)

Erste Fassung (Pixel der Figur gegen Pixel des Fotos in derselben Kamera) maß das Falsche: Wo die Figur ein paar mm neben der Person steht, verlangte sie für den Rand des Arms die
Farbe des Hemds dahinter — genau den schwarzen Streifen, den Edgar bemängelt (Lauf 23.02 nach den Farbklassen: 8 → 24 Zellen, alle an Armrändern). Jetzt je Punkt:

  Klasse     des Punkts: Körper nach `genesis.farbklassen` (Haut, Haar, Kleidung je Art, ungesehen = Person), Hüllen nach ihrem Stück (haar, oberteil, unterteil, socken, kleid),
             Augen = Haut
  Fotos      die ihn sehen (Tiefe ≤ TIEFE_MM hinter der vordersten Fläche der ganzen Figur, |Normale · Blick| ≥ NEIGUNG) UND an seinem Pixel dieselbe Klasse zeigen (Maske um RAND_PX
             eingezogen) — ein Foto, das dort etwas anderes zeigt, sagt über seine Farbe nichts
  Abstand    größter Kanal (sRGB) zur Farbe dieser Fotos im Umkreis von SPIEL_MM (nur Pixel derselben Klasse), Helligkeit je Foto und Kanal angeglichen; das kleinste über die Fotos
  weit       zeigt kein Foto die Klasse im Umkreis von SPIEL_MM (die Hüfte liegt im Profil hinter dem Arm, die Figur steht ein paar mm neben der Person), dann um den nächsten Pixel
             der Klasse bis WEIT_MM — sonst blieben gerade die Punkte ungeprüft, deren Farbe das Auffüllen über die Nachbarn rät (30.10.2026: weiße Flecken an der Hüfte, Lauf 01.26,
             `ProjektTemp/_wegwerf/fotogenesis/diag_farbe_bild.py 4 -45`)
  ungesehen  zeigt ihn gar kein Foto (Rumpfseite unter dem Arm: im Profil verdeckt, von vorn und hinten streifend), dann gegen die Fotofarben der Punkte desselben Stücks im
             Umkreis von NAH_MM — seine Farbe ist geraten (Auffüllen) und muss zu den Nachbarn passen (30.10.2026, Lauf 08.24: Hemdpunkte in der Farbe der Tür, an der Hüfte
             als weiße Flecken zu sehen, `ProjektTemp/_wegwerf/fotogenesis/diag_punkt_herkunft.py 20297`)
Ein Punkt ist falsch gefärbt, wenn er in einer Ansicht zu sehen ist (jedes Foto und um DREHUNGEN gedreht) und sein Abstand über ABSTAND liegt; Punkte ohne Foto und ohne
geprüften Nachbarn zählen nicht.
Je Ansicht die Pixel falscher Punkte; eine Zelle von ZELLE_MM mit mindestens ANTEIL davon und MIN_MM2 ist ein Fehler.

    erg = Fotogenesisgenesisfarbmass(ansicht).messen()    # {'zellen': [(Foto, Drehung, Mitte px, Anteil, mm²)], 'punkte': falsche Punkte, 'geprueft': Punkte mit Foto,
                                                     #  'fotofarbe': {Stück: (N, 3) Farbe eines Fotos mit derselben Klasse, NaN ohne} — für Gegenproben}
"""
import numpy as np
from scipy import ndimage

__all__ = ['Fotogenesisgenesisfarbmass']


class Fotogenesisgenesisfarbmass:
    RAND_PX, NEIGUNG, TIEFE_MM, SPIEL_MM, ABSTAND = 1, 0.3, 10.0, 4.0, 70
    #: Setzung (30.10.2026): etwa eine Armbreite halb — so weit liegt das Hemd neben dem Arm, der die Hüfte im Profil verdeckt
    WEIT_MM = 40.0
    #: Umkreis (mm, im Raum) der Nachbarn mit Foto für ungesehene Punkte (Setzung, 30.10.2026)
    NAH_MM = 30.0
    DREHUNGEN = (0, 45, -45)
    ZELLE_MM, ANTEIL, MIN_MM2 = 30.0, 0.3, 150.0
    #: Klasse je Stück; der Körper je Punkt aus `farbklassen` (`Figurfarben.KLASSEN`)
    KLASSEN = ('haut', 'haar', 'kleid', 'person', 'oberteil', 'unterteil', 'socken')
    STUECK_KLASSE = {'augen': 'haut', 'haar': 'haar', 'kleid': 'kleid', 'oberteil': 'oberteil', 'unterteil': 'unterteil', 'socken': 'socken'}

    def __init__(self, ansicht):
        self.a = ansicht
        self.p = ansicht.p

    def _klasse(self, name, n):
        """(n,) Index in KLASSEN je Punkt des Stücks."""
        if name == 'koerper':
            fk = self.a.g.get('farbklassen')
            return self.p.feld(fk, 'u1').astype(np.int64)[:n] if fk else np.full(n, self.KLASSEN.index('person'))
        return np.full(n, self.KLASSEN.index(self.STUECK_KLASSE.get(name, 'person')))

    def _masken(self, datei, form):
        """(C, h, w) bool je Klasse im Raster, eingezogen."""
        m, k = self.p.masken(datei), self.p.klassen(datei)
        h, w = form
        kl = self.a.verkleinern(k)[:h, :w]
        person, haut = self.a.verkleinern(m['person'])[:h, :w], self.a.verkleinern(m['haut'])[:h, :w]
        haar = self.a.verkleinern(m['haar'] | m.get('bart', np.zeros_like(m['haar'])))[:h, :w]

        def art(*namen):
            return np.isin(kl, self.p.klassen_index(*namen)) & person
        alle = {'haut': haut & person, 'haar': haar & person, 'kleid': person & ~haut & ~haar, 'person': person, 'oberteil': art('Upper_Clothing'),
                'unterteil': art('Lower_Clothing'), 'socken': art('Left_Sock', 'Right_Sock', 'Left_Shoe', 'Right_Shoe')}
        return np.stack([ndimage.binary_erosion(alle[n], iterations=self.RAND_PX) for n in self.KLASSEN])

    def _foto_abstand(self, nr, f, farbe_von):
        """{Stück: (Abstand je Punkt, inf ohne Foto)} aus Foto `nr` — Farbe der Punkte gegen das Foto, wo es dieselbe Klasse zeigt."""
        r = self.a.rastern(nr, f)
        h, w = r['stueck'].shape
        bild = self.a.verkleinern(self.p.bild(f['datei']).astype(np.float64), mittel=True)[:h, :w]
        masken = self._masken(f['datei'], (h, w))
        ort = np.asarray(f['kamera']['ort'], dtype=np.float64)
        rad = max(1, int(round(self.SPIEL_MM / (self.p.mm_je_px(nr) / self.a.m))))
        dy, dx = np.meshgrid(np.arange(-rad, rad + 1), np.arange(-rad, rad + 1), indexing='ij')
        rund = dy ** 2 + dx ** 2 <= rad ** 2
        dy, dx = dy[rund], dx[rund]
        mitte = int(np.nonzero((dy == 0) & (dx == 0))[0][0])
        weit = self.WEIT_MM / (self.p.mm_je_px(nr) / self.a.m)
        naechst = {c: ndimage.distance_transform_edt(~masken[c], return_indices=True) for c in range(len(self.KLASSEN)) if masken[c].any()}
        teile = {}
        for name, x, tri, fa in self.a.stuecke(nr):
            fa = farbe_von(name, fa) if farbe_von else fa
            if fa is None:
                continue
            uv, z = self.p.projektion(f, x)
            ix, iy = np.floor(uv[:, 0] * self.a.m).astype(np.int64), np.floor(uv[:, 1] * self.a.m).astype(np.int64)
            drin = (ix >= 0) & (iy >= 0) & (ix < w) & (iy < h)
            ixc, iyc = ix.clip(0, w - 1), iy.clip(0, h - 1)
            sicht = drin & (z <= r['tiefe'][iyc, ixc] + self.TIEFE_MM / 1000) & (self.a._neigung(x, tri, ort) >= self.NEIGUNG)
            kl = self._klasse(name, len(x))
            qy, qx = (iyc[:, None] + dy[None]).clip(0, h - 1), (ixc[:, None] + dx[None]).clip(0, w - 1)
            fern = sicht & ~masken[kl[:, None], qy, qx].any(1)
            for c in np.unique(kl[fern]):
                if c in naechst:
                    abst, (ny, nx) = naechst[c]
                    i = np.nonzero(fern & (kl == c))[0]
                    i = i[abst[iyc[i], ixc[i]] <= weit]
                    iyc[i], ixc[i] = ny[iyc[i], ixc[i]], nx[iyc[i], ixc[i]]
            qy, qx = (iyc[:, None] + dy[None]).clip(0, h - 1), (ixc[:, None] + dx[None]).clip(0, w - 1)
            gleich = masken[kl[:, None], qy, qx]
            teile[name] = (sicht & gleich.any(1), fa, bild[qy, qx], gleich)
        # Helligkeit je Kanal: Summenverhältnis über die Punkte mit Foto (die Farben der Figur sind an das erste Foto angeglichen)
        mit = [(fa[s], b[s][:, mitte]) for s, fa, b, _g in teile.values() if s.any()]
        gain = sum(m.sum(0) for m, _b in mit) / np.maximum(sum(b.sum(0) for _m, b in mit), 1e-6) if mit else np.ones(3)
        aus = {}
        for name, (s, fa, b, gleich) in teile.items():
            d = np.where(gleich, np.abs(fa[:, None] - b * gain).max(2), np.inf).min(1)
            aus[name] = (np.where(s, d, np.inf), np.where(s[:, None] & gleich[:, mitte, None], b[:, mitte] * gain, np.nan))
        return aus

    def _ungesehen(self, abstand, fotofarbe, farbe_von):
        """Abstand der Punkte ohne Foto (inf) = kleinster Abstand ihrer Farbe zu den Fotofarben der Punkte desselben Stücks im Umkreis von NAH_MM; bleibt inf ohne solche."""
        from scipy.spatial import cKDTree
        fotos = self.p.fotos()
        if not fotos:
            return
        for name, x, _tri, fa in self.a.stuecke(fotos[0][0]):
            fa = farbe_von(name, fa) if farbe_von else fa
            if fa is None or name not in abstand:
                continue
            ff = fotofarbe[name]
            mit, ohne = ~np.isnan(ff).any(1), np.nonzero(~np.isfinite(abstand[name]))[0]
            if not mit.any() or not len(ohne):
                continue
            nachbarn = cKDTree(x[mit]).query_ball_point(x[ohne], self.NAH_MM / 1000)
            ffm = ff[mit]
            abstand[name][ohne] = [np.abs(fa[i] - ffm[j]).max(1).min() if j else np.inf for i, j in zip(ohne, nachbarn, strict=True)]

    def messen(self, farbe_von=None):
        """`farbe_von(Stück, Farben (N, 3))` ersetzt die Farben der Figur (Gegenproben)."""
        fotos = self.p.fotos()
        abstand, fotofarbe = {}, {}
        for nr, f in fotos:
            for name, (d, ff) in self._foto_abstand(nr, f, farbe_von).items():
                abstand[name] = np.minimum(abstand.get(name, np.inf), d)
                fotofarbe[name] = np.where(np.isnan(fotofarbe.get(name, ff)), ff, fotofarbe.get(name, ff))
        self._ungesehen(abstand, fotofarbe, farbe_von)
        falsch = {name: np.isfinite(d) & (d > self.ABSTAND) for name, d in abstand.items()}
        geprueft = sum(int(np.isfinite(d).sum()) for d in abstand.values())
        zellen = []
        for nr, f in fotos:
            mm_px = self.p.mm_je_px(nr) / self.a.m
            for grad in self.DREHUNGEN:
                r = self.a.rastern(nr, f) if not grad else self.a.rastern(nr, f, self.a.gedreht(nr, f, grad))
                st, pk = r['stueck'], r['punkt']
                schlecht = np.zeros(st.shape, dtype=bool)
                for si, name in enumerate(self.a.namen):
                    if name in falsch:
                        auf = st == si
                        schlecht[auf] = falsch[name][pk[auf]]
                da = st >= 0
                zelle = self.a.zellen(nr, st.shape, self.ZELLE_MM)
                n = np.bincount(zelle[da], minlength=zelle.max() + 1)
                b = np.bincount(zelle[schlecht], minlength=zelle.max() + 1)
                for z in np.nonzero((b >= self.ANTEIL * np.maximum(n, 1)) & (b * mm_px ** 2 >= self.MIN_MM2))[0]:
                    yx = np.argwhere(schlecht & (zelle == z)).mean(0) / self.a.m
                    zellen.append((f['datei'], grad, (int(yx[1]), int(yx[0])), round(float(b[z] / n[z]), 2), int(b[z] * mm_px ** 2)))
        return {'zellen': sorted(zellen, key=lambda z: -z[4]), 'punkte': int(sum(v.sum() for v in falsch.values())), 'geprueft': geprueft, 'fotofarbe': fotofarbe}
