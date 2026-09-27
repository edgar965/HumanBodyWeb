# -*- coding: utf-8 -*-
"""Meshfigurtexelpruefung — Texelfarben von „Mesh to 3D" vor dem Backen säubern (27.09.2026).

Befund Edgar (Auftragsseite, Damira Kopf): „ich brauche das Ergebnis in der 3D-Ansicht, nur
richtig!" In den Kacheln (Herkunftskarten angesehen) lagen drei Fehler aus dem NETZ, nicht aus der
Figur — der Hautfilter des Runners (`meshfigur_textur`) ließ sie durch:

* helle Streifen und Flecken (Unterarm-Innenseite, Rumpfseite): Hunyuans weißliche Füllung
  verdeckter Stellen — farblich Haut, nur viel heller;
* braune Klumpen, wo die Figur nichts traf (Spalt zwischen Arm und Körper): die Füllschicht
  (`punktfarben`, 6 cm Suchweite) und das Einmalen holten dort Schattenfarbe aus dem Spalt;
* eine fleckige Kopfhaut aus braunem Haar und grauen Füllzellen des Kopfnetzes.

Vorgehen je Kachel, nur in den Hautbereichen (`G9netzbereiche` HAUT, ZEHEN — ohne Gesichtskern:
Lippen, Brauen, Lider sind keine Hautfarbe; Hände und Finger bekommen ohnehin keine Netzfarbe):

1. Hautton aus allen Treffern (YCbCr, Median und MAD); gut ist ein Treffer im Ton, der nicht
   zugleich entsättigt und dunkel ist (Schatten im Spalt, `SATT_SCHATTEN`).
2. Umgebungsfeld aus den guten Treffern (normierte Gauß-Faltung, `GROB_PX`); Ausreißer dagegen
   (heller als `LICHT` ×, dunkler als `DUNKEL` ×) fallen weg — Brustwarzen und Nabel liegen
   innerhalb, ein weißer Streifen oder eine Haarspitze nicht. Eine globale Helligkeitsgrenze war
   falsch: Die Netzfarbe trägt Hunyuans Licht, die beleuchtete Brust lag darüber und wurde fleckig.
3. Jedes übrige Hauttexel der Insel (verworfen oder nie getroffen) bekommt das Feld aus den guten
   Nachbarn, fein, wo genug da ist, sonst grob (`GROB_PX`) — Gewicht 1, damit weder Füllschicht noch
   Einmalen darüber kommen.

KOPFHAUT: Hat das Netz dort überwiegend Nicht-Haut getroffen (Haar), bleiben nur Treffer nahe der
Haarfarbe (Median; graue Füllzellen fallen weg), und die ganze Kopfhaut bekommt sie geglättet —
eine gleichmäßig gemalte Frisur statt Flecken. Sonst (Glatze) bleibt sie. Mit der Option
`kopfhaut = haut` liefert der Runner dort keine Treffer, dann geschieht hier nichts.
"""

import numpy as np

__all__ = ['Meshfigurtexelpruefung']


class Meshfigurtexelpruefung:
    CHROMA = 4.0
    HELL = 0.40
    SATT = 0.5
    #: Treffer, die entsättigt UND dunkler als der Ton sind: Schatten im Spalt (Damira: Sättigung
    #: 0,45–0,75 des Tons bei Helligkeit 65–79 statt 152 — genau der Saum um die Löcher).
    SATT_SCHATTEN = 0.75
    #: Ausreißer gegen das Umgebungsfeld (`PRUEF_PX` — breiter als Hunyuans weiße Füllflächen, bis
    #: ~150 px; zwei Durchgänge, denn im ersten hebt die Fläche ihr eigenes Feld an). Eine globale
    #: Grenze taugt nicht — die Netzfarbe trägt Hunyuans Licht.
    LICHT = 1.2
    DUNKEL = 0.6
    DURCHGAENGE = 2
    PRUEF_PX = 96.0
    #: … und weißlicher als die Umgebung: heller UND weniger als so viel ihrer Sättigung — Hunyuans
    #: weiße Füllung ist oft kaum heller, aber blass (Unterarm-Streifen, Fläche neben dem Bauch).
    WEISS = 0.7
    #: Haarfarbe nur aus Treffern mit mindestens so viel Sättigung (Anteil am Hautton) — die grauen
    #: Füllzellen des Kopfnetzes zogen den Median sonst ins Graue.
    HAAR_SATT = 0.35
    #: Mindeststreuung je Kanal (Y, Cb, Cr) — wie `meshfigur_abstand.haut_bestimmen`.
    STREUUNG_MIN = np.array([4.0, 2.0, 2.0])
    #: Haarfarbe: Chroma binnen so vielen robusten Streuungen um den Median der Haartreffer.
    HAAR_CHROMA = 3.0
    FEIN_PX = 12.0
    GROB_PX = 48.0

    def __init__(self, abtastung):
        from Genesis9.netzbereiche import G9netzbereiche

        b = G9netzbereiche
        self.abtastung = abtastung
        self.bereich = b.bereiche()
        self.kern = b.gesichtskern()
        self.hautbereiche = (b.HAUT, b.ZEHEN)
        self.kopfhaut = b.KOPFHAUT
        self.tonmodell = None

    @staticmethod
    def ycbcr(rgb):
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        y = 0.299 * r + 0.587 * g + 0.114 * b
        cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
        return np.stack([y, cb, 128 + 0.5 * r - 0.418688 * g - 0.081312 * b], -1)

    @staticmethod
    def satt(ycc):
        """Sättigung (Abstand vom Grau in Cb/Cr) — für (n, 3) oder (3,)."""
        return np.hypot(ycc[..., 1] - 128.0, ycc[..., 2] - 128.0)

    @classmethod
    def modell(cls, ycc):
        mitte = np.median(ycc, axis=0)
        return mitte, 1.4826 * np.median(np.abs(ycc - mitte), axis=0) + cls.STREUUNG_MIN

    def ist_haut(self, ycc):
        """Derselbe Test wie `meshfigur_abstand.ist_haut` (Chroma, Helligkeit, Sättigung)."""
        mitte, streuung = self.tonmodell
        chroma = np.sqrt((((ycc[:, 1:] - mitte[1:]) / streuung[1:]) ** 2).sum(1))
        satt = np.hypot(ycc[:, 1] - 128.0, ycc[:, 2] - 128.0)
        ton = float(np.hypot(mitte[1] - 128.0, mitte[2] - 128.0))
        return (chroma < self.CHROMA) & (ycc[:, 0] > self.HELL * mitte[0]) & (satt > self.SATT * ton)

    @staticmethod
    def glatt(bild, maske, sigma):
        """Normierte Gauß-Faltung: `(Farbe (S, S, 3), Stützgewicht (S, S))` — bei großem `sigma` auf
        einem verkleinerten Bild (Blocksumme, bilinear zurück): dieselbe Wirkung, ein Bruchteil der Zeit
        (erste Fassung: 142 s für fünf Kacheln)."""
        from scipy import ndimage

        s = maske.shape[0]
        f = 1
        while sigma / (2 * f) >= 6 and s % (2 * f) == 0:
            f *= 2
        gewicht = np.concatenate([bild * maske[..., None], maske[..., None].astype(np.float64)], -1)
        if f > 1:
            gewicht = gewicht.reshape(s // f, f, s // f, f, 4).sum((1, 3)) / (f * f)
        glatt = np.stack([ndimage.gaussian_filter(gewicht[..., i], sigma / f) for i in range(4)], -1)
        if f > 1:
            glatt = ndimage.zoom(glatt, (f, f, 1), order=1)
        m = glatt[..., 3]
        return glatt[..., :3] / np.maximum(m, 1e-9)[..., None], m

    # ------------------------------------------------------------- Prüfen

    def pruefen(self, hd):
        """Ein neues `hd` (Kopien) mit gesäuberten Hauttexeln und gemalter Kopfhaut — und der Befund."""
        teile, proben = {}, []
        for kachel in self.abtastung.kacheln:
            if 'farbe_%d' % kachel not in hd:
                continue
            drin, ecken, anteile = self.abtastung.stellen(kachel)
            punkt = ecken[np.arange(len(ecken)), anteile.argmax(1)]
            haut = np.isin(self.bereich[punkt], self.hautbereiche) & ~self.kern[punkt]
            getroffen = np.asarray(hd['gewicht_%d' % kachel]) > 0
            ycc = self.ycbcr(np.asarray(hd['farbe_%d' % kachel], dtype=np.float64))
            teile[kachel] = (drin, haut, self.bereich[punkt] == self.kopfhaut, getroffen, ycc)
            proben.append(ycc[haut & getroffen][::7])
        ton = np.concatenate(proben) if proben else np.zeros((0, 3))
        if len(ton) < 1000:
            return hd, {'grund': 'zu wenige Hauttexel (%d)' % len(ton)}
        self.tonmodell = self.modell(ton)
        neu = dict(hd)
        befund = {'ton_ycbcr': [round(float(c), 1) for c in self.tonmodell[0]]}
        for kachel, (drin, haut, kopf, getroffen, ycc) in teile.items():
            farbe = np.asarray(hd['farbe_%d' % kachel], dtype=np.float64)
            gewicht = np.array(hd['gewicht_%d' % kachel], dtype=np.float32, copy=True)
            eintrag = self._haut(drin, haut, getroffen, ycc, farbe, gewicht)
            if kopf.any():
                eintrag['kopfhaut'] = self._kopfhaut(drin, kopf, getroffen, ycc, farbe, gewicht)
            neu['farbe_%d' % kachel] = np.clip(farbe + 0.5, 0, 255).astype(np.uint8)
            neu['gewicht_%d' % kachel] = gewicht
            befund[str(kachel)] = eintrag
        return neu, befund

    def _bild(self, drin, werte, maske):
        s = self.abtastung.seite
        bild, m = np.zeros((s, s, 3)), np.zeros((s, s), dtype=bool)
        bild[drin] = werte
        m[drin] = maske
        return bild, m

    def _haut(self, drin, haut, getroffen, ycc, farbe, gewicht):
        """Schritte 1–3 des Modulkopfs, in place auf `farbe`/`gewicht`."""
        mitte = self.tonmodell[0]
        satt = self.satt(ycc) / max(float(self.satt(mitte)), 1e-6)
        schatten = (satt < self.SATT_SCHATTEN) & (ycc[:, 0] < mitte[0])
        gut = haut & getroffen & self.ist_haut(ycc) & ~schatten
        ausreisser = np.zeros_like(gut)
        for _ in range(self.DURCHGAENGE):
            bild, maske = self._bild(drin, farbe, gut)
            feld, stuetze = self.glatt(bild, maske, self.PRUEF_PX)
            ycc_feld = self.ycbcr(feld[drin])
            y_feld = ycc_feld[:, 0]
            weisslich = (self.satt(ycc) < self.WEISS * self.satt(ycc_feld)) & (ycc[:, 0] > y_feld)
            neu = gut & (stuetze[drin] > 1e-3) & (
                (ycc[:, 0] > self.LICHT * y_feld) | (ycc[:, 0] < self.DUNKEL * y_feld) | weisslich
            )
            gut &= ~neu
            ausreisser |= neu
        bild, maske = self._bild(drin, farbe, gut)
        fein, m_fein = self.glatt(bild, maske, self.FEIN_PX)
        grob, m_grob = self.glatt(bild, maske, self.GROB_PX)
        fuellung = np.where((m_fein > 0.15)[..., None], fein, grob)[drin]
        ziel = haut & ~gut & (m_grob[drin] > 1e-3)
        farbe[ziel] = fuellung[ziel]
        gewicht[ziel] = 1.0
        return {
            'haut': int(haut.sum()),
            'getroffen': int((haut & getroffen).sum()),
            'verworfen': int((haut & getroffen & ~gut).sum()),
            'ausreisser': int(ausreisser.sum()),
            'gefuellt': int(ziel.sum()),
        }

    def _kopfinsel(self, drin, kopf):
        """(n,) bool: Texel der UV-Inseln, die den Großteil der Kopfhaut tragen — nicht die Ohren
        (deren Rückseite zählt zur Kopfhaut, bekam im ersten Versuch aber Haarfarbe)."""
        from scipy import ndimage

        s = self.abtastung.seite
        flaeche = np.zeros((s, s), dtype=bool)
        flaeche[drin] = True
        nummer, _ = ndimage.label(flaeche)
        je_texel = nummer[drin]
        anzahl = np.bincount(je_texel[kopf], minlength=int(je_texel.max()) + 1)
        return np.isin(je_texel, np.flatnonzero(anzahl >= 0.2 * anzahl.max()))

    def _kopfhaut(self, drin, kopf, getroffen, ycc, farbe, gewicht):
        """Überwiegend Haar getroffen: die Kopfhaut in der geglätteten Haarfarbe malen (in place)."""
        treffer = kopf & getroffen
        haar = treffer & ~self.ist_haut(ycc)
        if not haar.any() or haar.sum() < 0.5 * treffer.sum():
            return {'treffer': int(treffer.sum()), 'haar': int(haar.sum()), 'gemalt': 0}
        satt = self.satt(ycc) / max(float(self.satt(self.tonmodell[0])), 1e-6)
        farbig = haar & (satt >= self.HAAR_SATT)
        mitte, streuung = self.modell(ycc[farbig if farbig.sum() >= max(50, 0.05 * haar.sum()) else haar])
        chroma = np.sqrt((((ycc[:, 1:] - mitte[1:]) / streuung[1:]) ** 2).sum(1))
        hell = (ycc[:, 0] < 1.6 * mitte[0]) & (ycc[:, 0] > 0.5 * mitte[0])
        sauber = haar & (chroma < self.HAAR_CHROMA) & hell
        bild, maske = self._bild(drin, farbe, sauber)
        fein, m_fein = self.glatt(bild, maske, self.FEIN_PX / 4)
        grob, m_grob = self.glatt(bild, maske, self.GROB_PX)
        malen = np.where((m_fein > 0.2)[..., None], fein, grob)[drin]
        # Wo auch die grobe Faltung nichts hat: der Median der sauberen Haarfarbe.
        grundfarbe = np.median(farbe[sauber], axis=0) if sauber.any() else np.median(farbe[haar], axis=0)
        malen[m_grob[drin] <= 1e-3] = grundfarbe
        ziel = kopf & self._kopfinsel(drin, kopf)
        farbe[ziel] = malen[ziel]
        gewicht[ziel] = 1.0
        return {
            'treffer': int(treffer.sum()),
            'haar': int(haar.sum()),
            'haarfarbe': int(sauber.sum()),
            'gemalt': int(ziel.sum()),
        }
