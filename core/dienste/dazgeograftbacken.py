# -*- coding: utf-8 -*-
"""Dazgeograftbacken — Farbe, Rauheit und Normalen der Original-Scham auf das angepasste Daz-Geograft übertragen (10.10.2026).

Das angepasste Netz (`Dazgeograftanpassung`) hat die Form des Originals nur in groben Zügen (Punktabstand ≈ 4 mm gegen ≈ 1 mm des Originals). Was darunter liegt, holt der Bake:

    Farbe, Rauheit  je Texel der Punkt der Original-Scham, der nah liegt UND dieselbe Seite zeigt (`Dazgeograftziel.stelle`: an Spalten liegt der nächste Punkt oft auf der Wand gegenüber;
                    Atlas aus der Originaltextur); weiter als `NAH_M` von der Fläche weg (Rand des Originals, dort geht die
                    Scham in die Haut über) blendet es bis `FERN_M` in die gebackene Hauttextur der Figur über (`haut_<kachel>_<kanal>.klein.jpg`, gleiche Quelle)
    Normalen        die Normale des Originals an diesem Punkt, so kodiert, dass three.js sie in SEINEM Tangentenraum (`Dazgeograftraster`) wieder ergibt (OpenGL, G nach +v): die Falten, die das
                    grobe Netz nicht trägt, stehen als Normalenkarte darauf. Wo das Original fehlt, bleibt die glatte Normale des Netzes (flach); zum Rand hin läuft die Karte aus (`RAND_NORMALEN_M`)
Texel ohne Dreieck füllen sich vom Rand her (`Dazgeograftraster.auffuellen`). Ergebnis: Dateien in `ausgabe`, dazu ein Bericht mit Zahlen.
"""
import torch
from KoerperKI_alle.torchfeld import Torchfeld

from .dazgeograftraster import Dazgeograftraster

__all__ = ['Dazgeograftbacken']


class Dazgeograftbacken:
    #: Abstand zum Original (m): bis `NAH_M` gilt nur dessen Atlas, bis `FERN_M` blendet die Haut der Figur dazu.
    NAH_M, FERN_M = 0.004, 0.009
    #: Dasselbe für die NORMALEN: eine Normale des Originals passt nur auf eine Fläche, die ihm nahe ist — das grobe Netz (4 mm Punktabstand) liegt bis p90 2,2 mm daneben, und weiter weg dreht die Karte
    #: das Licht in Flecken mit dreieckigen Kanten (Chrome, 11.10.2026: mit flacher Karte verschwinden sie).
    NAH_NORMALEN_M, FERN_NORMALEN_M = 0.0015, 0.003
    #: Seitlich jenseits des Randes des Originals (`Dazgeograftziel.jenseits`): ab `JENSEITS_ZAEHLEN_M` (m) zählt ein Texel als „jenseits"; der Unterschied Original − Haut am Rand läuft über `FORTSETZEN_M`
    #: aus, die Normalenkarte über ein Band von ± `RAND_BAND_M` um den Rand.
    JENSEITS_ZAEHLEN_M, FORTSETZEN_M, RAND_BAND_M = 0.0005, 0.008, 0.004
    #: Abstand (m) der Proben entlang der Randkanten des Stücks, an denen der Randabstand gemessen wird; Unschärfe (Texel des Atlas) des Unterschieds Original − Haut, der hinter den Rand fortgesetzt wird.
    RAND_PROBE_M, FORTSETZEN_UNSCHARF_PX = 0.0005, 10.0
    #: Vom Rand des Stücks nach innen (m) läuft die Hautfarbe der Figur aus: am Rand ist es die Haut, ab so weit innen gilt der Atlas des Originals.
    RING_M = 0.012
    #: Umkreis (m) um die Mitte des Lochs, dessen Hautdreiecke als Quelle der Hautfarbe zählen.
    HAUT_UMKREIS_M = 0.14
    #: Größte Neigung (Grad) der gebackenen Normale gegen die glatte des Geografts.
    MAX_NEIGUNG_GRAD = 60.0
    #: Vom Rand (Weg über das Netz, m) nach innen läuft die Normalenkarte ein: so weit mischt der Browser die Normalen des Stücks zu denen der Haut (`Stucknormalen.BAND_M`) — dort ist die
    #: Normale, auf der die Karte gebacken wurde, nicht die, auf die sie beim Anzeigen trifft. Eine Karte mit 60° Neigung dreht sich mit ihr (am Ring 17: Stück gegen Haut 160°).
    RAND_NORMALEN_M = 0.010
    #: Weichzeichnen harter Übergänge der Farb- und Rauheitskarte (`_weich`): Sprung zwischen Nachbartexeln (Mittel der Kanäle), Unschärfe (Texel) und Breite der Zone um die Kante (Texel).
    KANTE_SPRUNG, KANTE_SIGMA, KANTE_BREITE = 20.0, 1.5, 2.0

    def __init__(self, ziel, figur, haut_ordner, aufloesung=1024):
        """`ziel`: `Dazgeograftziel`; `figur`: `{punkte, dreiecke, uv, kachel}` der Figur (`Dazgeografthaut.grundfigur`); `haut_ordner`: Ordner der gebackenen `haut_*`-Bilder."""
        self.ziel, self.figur, self.haut_ordner, self.r = ziel, figur, haut_ordner, int(aufloesung)
        self.ziel_netz = ziel.netz()
        self._haut = {}

    # ------------------------------------------------------------ Hilfen

    @staticmethod
    def _abtasten(bild, uv):
        """`(M, 3)` Werte des Bildes (H, W, 3) an `uv` (v nach oben), bilinear."""
        from KoerperKI_alle.kartenbild import map_coordinates

        h, w = bild.shape[:2]
        koordinaten = [(1.0 - uv[:, 1]) * h - 0.5, uv[:, 0] * w - 0.5]
        return Torchfeld.astype(Torchfeld.column_stack([map_coordinates(Torchfeld.astype(bild[..., k], torch.float32), koordinaten, order=1, mode='nearest') for k in range(3)]), torch.float64)

    @staticmethod
    def _baryzentrisch(netz, dreieck, punkte):
        import trimesh

        return trimesh.triangles.points_to_barycentric(netz.triangles[dreieck], punkte)

    #: Größte Kante (px) einer Hautkachel, die hier gelesen wird: die volle 8192er Kachel (200 MB als Feld) wird mit `reduce` verkleinert — der Rand des Stücks braucht keine Poren.
    KACHEL_MAX_PX = 2048
    #: Namen der Hautbilder, in der Reihenfolge der Suche: die verkleinerte Fassung des Browsers (nur bei `browser_px` < `kachel_px`), sonst die volle Kachel.
    KACHEL_NAMEN = ('haut_%d_%s.klein.jpg', 'haut_%d_%s.jpg', 'haut_%d_%s.png')

    def _kachelbild(self, kachel, kanal):
        """Das Hautbild `(kachel, kanal)` als `(H, W, 3)` — `None` ohne Datei. Gesehen 11.10.2026: bei `browser_px = 8192` (Vorgabe, keine Verkleinerung) gibt es keine `.klein.jpg`; der Bake füllte den Rand
        dann mit Grau (128) statt mit der Haut — jetzt gilt die volle Kachel, auf `KACHEL_MAX_PX` verkleinert."""
        from PIL import Image

        schluessel = (int(kachel), kanal)
        if schluessel not in self._haut:
            Image.MAX_IMAGE_PIXELS = None
            pfad = next((p for p in (self.haut_ordner / (n % schluessel) for n in self.KACHEL_NAMEN) if p.is_file()), None)
            bild = None
            if pfad is not None:
                with Image.open(pfad) as roh:
                    roh = roh.convert('RGB')
                    teiler = max(1, max(Torchfeld.groesse(roh)) // self.KACHEL_MAX_PX)
                    bild = Torchfeld.feld(roh.reduce(teiler) if teiler > 1 else roh)
            self._haut[schluessel] = bild
        return self._haut[schluessel]

    def _hautwerte(self, punkte, kanal, mitte):
        """Der Wert der gebackenen Hauttextur `kanal` am nächsten Punkt der Figurfläche um `mitte` → `(M, 3)`."""
        import trimesh

        f = self.figur
        nah = torch.flatten(Torchfeld.linalg_norm(f['punkte'][f['dreiecke']].mean(axis=1) - mitte, dim=1) < self.HAUT_UMKREIS_M).nonzero()[:, 0]
        netz = trimesh.Trimesh(f['punkte'], f['dreiecke'][nah], process=False)
        stelle, _abstand, dreieck = trimesh.proximity.closest_point(netz, punkte)
        bary = self._baryzentrisch(netz, dreieck, stelle)
        ecken = f['dreiecke'][nah][dreieck]
        uv = Torchfeld.einsum('mk,mkj->mj', bary, f['uv'][ecken])
        kachel = f['kachel'][nah][dreieck]
        aus = Torchfeld.full((len(punkte), 3), 128.0)
        for k in Torchfeld.liste(Torchfeld.unique(kachel)):
            bild = self._kachelbild(k, kanal)
            if bild is not None:
                m = kachel == k
                aus[m] = self._abtasten(bild, uv[m])
        return aus

    # ------------------------------------------------------------ Bake

    def backen(self, punkte, dreiecke, uv_ecken, ausgabe):
        """Die drei Bilder nach `ausgabe` (Ordner) schreiben → `({kanal: Pfad}, bericht)`."""
        import trimesh

        punkte = Torchfeld.feld(punkte, dtype=torch.float64)
        dreiecke = Torchfeld.feld(dreiecke, dtype=torch.int64)
        netz = trimesh.Trimesh(punkte, dreiecke, process=False)
        t = Dazgeograftraster.texel(punkte, dreiecke, uv_ecken, self.r, Torchfeld.feld(netz.vertex_normals))
        pos, zeile, spalte = t['position'], t['zeile'], t['spalte']
        abstand = trimesh.proximity.closest_point(self.ziel_netz, pos)[1]          # Abstand zur Fläche: bestimmt, wie weit das Original gilt
        dreieck, bary = self.ziel.stelle(pos, t['normale'])                        # Farbe und Normale von der Seite, auf der das Stück liegt (nicht von der Wand gegenüber)
        w_normal = 1.0 - self._glatt((abstand - self.NAH_M) / (self.FERN_M - self.NAH_M))
        lage = self.ziel.randlage(pos, dreieck, bary)                              # + innerhalb, − seitlich hinter dem Rand des Originals (dort hat es keine Farbe)
        jenseits = Torchfeld.maximum(-lage, 0.0)
        # Zum Rand hin gilt die Hautfarbe der Figur (am Rand ganz): so geht die Textur ohne Stufe in die Haut daneben über. Gemessen 10.10.2026 (`Schammessung`, „cute girl"): ohne das
        # war die Farbe des Stücks am Rand (194,7 / 142,0 / 124,7) gegen die Haut 6–15 mm daneben (199,8 / 148,1 / 128,8) 3,7 % dunkler.
        baum = self._rand_baum(punkte, dreiecke)
        w = w_normal * (self._glatt(baum.query(pos)[0] / self.RING_M) if baum is not None else 1.0)
        mitte = pos.mean(axis=0)
        bericht = {'aufloesung': self.r, 'texel': int(len(pos)), 'original_voll': float((w >= 0.999).mean()), 'abstand_median_mm': round(float(Torchfeld.median(abstand) * 1000), 2),
                   'jenseits_rand': {'texel': int((jenseits > self.JENSEITS_ZAEHLEN_M).sum()), 'anteil': round(float((jenseits > self.JENSEITS_ZAEHLEN_M).mean()), 4)}}
        dateien = {}
        for kanal in ('farbe', 'rauheit'):
            wert = self._farbkarte(kanal, pos, dreieck, bary, w, jenseits, mitte, bericht)
            dateien[kanal] = self._schreiben(wert, zeile, spalte, ausgabe / ('baked_%s.%s' % (kanal, 'jpg' if kanal == 'farbe' else 'png')), weich=True)
        # Die Karte der Normalen endet am Rand des Originals (keine Fortsetzung wie bei der Farbe): über ein Band von ±`RAND_BAND_M` um den Rand läuft sie aus, dahinter gilt die glatte Normale des Netzes.
        # Der Rand des Originals ist ein Zickzack (Schnitt durch Dreiecke des Körpers); ein hartes Ende zeichnete ihn als Sägezahn in die Beleuchtung.
        w_nah = 1.0 - self._glatt((abstand - self.NAH_NORMALEN_M) / (self.FERN_NORMALEN_M - self.NAH_NORMALEN_M))
        w_karte = w_nah * self._glatt((lage + self.RAND_BAND_M) / (2.0 * self.RAND_BAND_M)) * self._glatt(self._randweg(punkte, dreiecke, t) / self.RAND_NORMALEN_M)
        dateien['normalen'] = self._normalen(t, dreieck, bary, w_karte, ausgabe)
        return dateien, bericht

    def _farbkarte(self, kanal, pos, dreieck, bary, w, jenseits, mitte, bericht):
        """`(M, 3)` Werte des Kanals `farbe` oder `rauheit` je Texel: der Atlas des Originals, zum Rand des Stücks und weit vom Original weg die Haut der Figur; jenseits des Randes des Originals
        die Haut mit dem Unterschied Original − Haut am Rand, der mit dem Weg bis `FORTSETZEN_M` ausläuft (der Atlas selbst setzt dort nur den letzten Texel fort: senkrechte Streifen)."""
        uv_orig = Torchfeld.einsum('mk,mkj->mj', bary, self.ziel.uv_ecken[dreieck])
        atlas = self.ziel.bild(kanal)
        wert = self._abtasten(atlas, uv_orig) if atlas is not None else Torchfeld.full((len(pos), 3), 128.0)
        fern, aussen = torch.flatten(w < 0.999).nonzero()[:, 0], torch.flatten(jenseits > self.JENSEITS_ZAEHLEN_M).nonzero()[:, 0]
        if kanal == 'farbe':
            nah = torch.flatten((w >= 0.999) & (jenseits <= self.JENSEITS_ZAEHLEN_M)).nonzero()[:, 0][:20000]
            bericht['haut_gegen_original'] = round(float(Torchfeld.abs(self._hautwerte(pos[nah], kanal, mitte) - wert[nah]).mean()), 1) if len(nah) else None
        if len(aussen):
            from KoerperKI_alle.kartenbild import gaussian_filter

            ort = Torchfeld.einsum('mk,mkj->mj', bary[aussen], self.ziel.punkte[self.ziel.dreiecke[dreieck[aussen]]])
            # Der Unterschied am Rand wird aus dem UNSCHARFEN Atlas geholt: Haar und Poren des Randtexels, ins Hinterland gezogen, wären wieder Streifen.
            grob = Torchfeld.stack([gaussian_filter(Torchfeld.astype(atlas[..., k], torch.float32), self.FORTSETZEN_UNSCHARF_PX) for k in range(3)], axis=-1) if atlas is not None else None
            unterschied = (self._abtasten(grob, uv_orig[aussen]) if grob is not None else wert[aussen]) - self._hautwerte(ort, kanal, mitte)
            wert[aussen] = self._hautwerte(pos[aussen], kanal, mitte) + unterschied * (1.0 - self._glatt(jenseits[aussen] / self.FORTSETZEN_M))[:, None]
        if len(fern):
            wert[fern] = w[fern, None] * wert[fern] + (1.0 - w[fern, None]) * self._hautwerte(pos[fern], kanal, mitte)
        return wert

    def _normalen(self, t, dreieck, bary, w, ausgabe):
        """Normalenkarte: Normale des Originals am nächsten Punkt (zur Außenseite des Geografts gedreht), so kodiert, dass three.js sie im eigenen Tangentenraum wieder ergibt."""
        n_orig = Torchfeld.einsum('mk,mkj->mj', bary, Torchfeld.feld(self.ziel_netz.vertex_normals)[self.ziel.dreiecke[dreieck]])
        n_orig /= Torchfeld.maximum(Torchfeld.linalg_norm(n_orig, dim=1, keepdim=True), 1e-12)
        n_orig *= Torchfeld.sign(Torchfeld.einsum('ij,ij->i', n_orig, t['normale']) + 1e-12)[:, None]
        n_welt = w[:, None] * n_orig + (1.0 - w[:, None]) * t['normale']
        n_welt /= Torchfeld.maximum(Torchfeld.linalg_norm(n_welt, dim=1, keepdim=True), 1e-12)
        ts = self._kodieren(self._begrenzen(n_welt, t['normale']), t)
        return self._schreiben((ts * 0.5 + 0.5) * 255.0, t['zeile'], t['spalte'], ausgabe / 'baked_normalen.png')

    @classmethod
    def _begrenzen(cls, n, normale):
        """Die Neigung von `n` gegen `normale` ist höchstens `MAX_NEIGUNG_GRAD`: wo das Original schärfer faltet als das grobe Netz, entstünden sonst Wirbel (am Spalt gesehen)."""
        kos = Torchfeld.clip(Torchfeld.einsum('ij,ij->i', n, normale), -1.0, 1.0)
        grenze = Torchfeld.radians(cls.MAX_NEIGUNG_GRAD)
        zu_viel = Torchfeld.arccos(kos) > grenze
        if zu_viel.any():
            quer = n[zu_viel] - normale[zu_viel] * kos[zu_viel, None]
            quer /= Torchfeld.maximum(Torchfeld.linalg_norm(quer, dim=1, keepdim=True), 1e-12)
            n = Torchfeld.kopie(n)
            n[zu_viel] = normale[zu_viel] * Torchfeld.cos(grenze) + quer * Torchfeld.sin(grenze)
        return n

    @staticmethod
    def _kodieren(n, t):
        """Der Texelwert `ts` (−1…1), aus dem three.js in `normalize(T·x + B·y + N·z)` die Normale `n` macht: `(T B N)·ts ∥ n`, das Größte auf ±1 gestreckt (nur die Richtung zählt).
        Ist der Tangentenraum entartet (UV ohne Fläche), bleibt der Texel flach."""
        m = Torchfeld.stack([t['tangente'], t['bitangente'], t['normale']], axis=2)
        ok = Torchfeld.abs(Torchfeld.linalg_det(m)) > 1e-3
        ts = torch.zeros((len(n), 3), dtype=torch.float64, device='cuda')
        ts[:, 2] = 1.0
        if ok.any():
            ts[ok] = Torchfeld.linalg_solve(m[ok], n[ok][..., None])[..., 0]
        return ts / Torchfeld.maximum(Torchfeld.amax(Torchfeld.abs(ts), dim=1, keepdim=True), 1e-12)

    def _rand_baum(self, punkte, dreiecke):
        """KD-Baum über dichte Proben (Abstand `RAND_PROBE_M`) entlang der Randkanten des Stücks (Kanten mit einem Dreieck, nach Lage verschweißt) — oder None ohne Rand."""
        from KoerperKI_alle.kartenbaum import Kartenbaum as cKDTree

        _, erste, rep = Torchfeld.unique(Torchfeld.astype(Torchfeld.round(punkte / 1e-5), torch.int64), axis=0, return_index=True, return_inverse=True)
        d, p = rep.ravel()[dreiecke], punkte[erste]
        kanten = torch.sort(Torchfeld.cat([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]]), dim=1, stable=True).values
        eindeutig, zahl = Torchfeld.unique(kanten, axis=0, return_counts=True)
        offen = eindeutig[zahl == 1]
        if not len(offen):
            return None
        a, b = p[offen[:, 0]], p[offen[:, 1]]
        teile = Torchfeld.maximum(1, Torchfeld.astype(Torchfeld.ceil(Torchfeld.linalg_norm(b - a, dim=1) / self.RAND_PROBE_M), torch.int64))
        s = Torchfeld.cat([Torchfeld.arange(n + 1) / n for n in Torchfeld.liste(teile)])
        kante = Torchfeld.repeat_interleave(Torchfeld.arange(len(offen)), teile + 1)
        return cKDTree(a[kante] + s[:, None] * (b[kante] - a[kante]))

    def _randweg(self, punkte, dreiecke, t):
        """Abstand (m) jedes Texels vom Rand des Stücks (Luftlinie zu den dicht abgetasteten Randkanten); ab `2 · RAND_NORMALEN_M` der Ersatzwert 1,0. Gemessen 11.10.2026: der Weg über die Kanten des Netzes
        (Dijkstra) lief nur entlang der Dreieckskanten und zeichnete die Höhenlinie der Normalenkarte als Sägezahn (im Chrome: gezackte Streifen am Rand des Stücks, ohne Karte der Normalen glatt)."""
        baum = self._rand_baum(punkte, dreiecke)
        if baum is None:
            return Torchfeld.full(len(t['dreieck']), 1.0)
        pos = Torchfeld.einsum('mk,mkj->mj', t['bary'], punkte[dreiecke[t['dreieck']]])
        weg = baum.query(pos)[0]
        return torch.where(weg < 2 * self.RAND_NORMALEN_M, weg, 1.0)

    @staticmethod
    def _glatt(x):
        x = Torchfeld.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    @classmethod
    def _weich(cls, bild):
        """Harte Übergänge (Farbe der Wand gegenüber gegen die richtige, Rand einer Lippe) laufen als Zickzack entlang der groben Dreiecke des Stücks und sehen im Bild zerfetzt aus: dort — und nur dort,
        das Haar und die Poren bleiben scharf — wird mit `KANTE_SIGMA` Texeln weichgezeichnet. Eine Kante ist ein Sprung von mindestens `KANTE_SPRUNG` (Mittel der Kanäle) zwischen Nachbartexeln."""
        from KoerperKI_alle.kartenbild import gaussian_filter

        dx = Torchfeld.abs(Torchfeld.diff(bild, dim=1)).mean(axis=2)
        dy = Torchfeld.abs(Torchfeld.diff(bild, dim=0)).mean(axis=2)
        sprung = torch.zeros(bild.shape[:2], dtype=torch.float64, device='cuda')
        sprung[:, :-1], sprung[:-1, :] = Torchfeld.maximum(sprung[:, :-1], dx), Torchfeld.maximum(sprung[:-1, :], dy)
        sprung[:, 1:], sprung[1:, :] = Torchfeld.maximum(sprung[:, 1:], dx), Torchfeld.maximum(sprung[1:, :], dy)
        maske = Torchfeld.clip(gaussian_filter(Torchfeld.astype(sprung >= cls.KANTE_SPRUNG, torch.float64), cls.KANTE_BREITE) * 4.0, 0.0, 1.0)[..., None]
        unscharf = Torchfeld.stack([gaussian_filter(bild[..., k], cls.KANTE_SIGMA) for k in range(3)], axis=-1)
        return bild * (1.0 - maske) + unscharf * maske

    def _schreiben(self, wert, zeile, spalte, pfad, weich=False):
        from PIL import Image

        bild = torch.zeros((self.r, self.r, 3), dtype=torch.float64, device='cuda')
        bild[zeile, spalte] = wert
        bild = Dazgeograftraster.auffuellen(bild, zeile, spalte)
        if weich:
            bild = self._weich(bild)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        ausgabebild = Image.fromarray(Torchfeld.roh(Torchfeld.astype(Torchfeld.clip(bild + 0.5, 0, 255), torch.uint8)))
        if pfad.suffix == '.jpg':
            ausgabebild.save(pfad, quality=93)
        else:
            ausgabebild.save(pfad)
        return pfad
