# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkopfausschnitt — der Kopf aus einem vorbereiteten Ganzkörperfoto (Schritt „kopf" von „2D3D Kleider", 07.10.2026).

Edgar: „extrahiere dazu die bilder vom Kopf, von alle drei seiten". Eingang ist das freigestellte RGBA-Foto des Schritts „Vorbereitung" (`vorbereitet/<name>.png`, Quadrat um die Silhouette,
bei Edgars Fotos 5.500–6.200 px); der Ausschnitt behält die Pixel des Originals — darin liegt der Gewinn gegen den Ganzkörperlauf, der das Foto auf 435 px Körperhöhe verkleinert.

Gefunden wird der Kopf allein an der Silhouette (Alphakanal, keine KI): Die Zeilenbreite hat zwischen Kinn und Schultern ein Minimum, den Hals. Sucht man es im Fenster `HALS_VON`…`HALS_BIS`
der Körperhöhe unter dem Scheitel, liegt darüber der Kopf. Das trägt für Vorderansicht, Rückansicht (langes Haar über dem Hals hat KEIN Minimum — dann gilt `HALS_RUECKFALL`) und Seitenansicht
(Arme hängen daneben). Ein Halsstumpf bleibt stehen (`HALS_DAZU` der Kopfhöhe, seitlich begrenzt), Schultern nicht. Gemessen ist nur, dass die Ausschnitte an Edgars drei Fotos den Kopf mit Hals
zeigen (Sichtprobe); wie gut Hunyuan3D daraus rechnet, entscheidet der Lauf.
"""

import logging

import numpy as np
from PIL import Image

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderkopfausschnitt']


class Engine2d3dKleiderkopfausschnitt:
    #: Suchfenster der Halszeile, in Anteilen der Körperhöhe ab dem Scheitel (Edgar-Foto: Kinn bei 0,145, Schultern ab 0,18 — am Foto abgelesen).
    HALS_VON, HALS_BIS = 0.09, 0.22
    #: Ohne Minimum im Fenster (langes Haar über dem Hals) liegt der Hals hier — ein Kopf ist rund 1/7 der Körperhöhe (Faustregel, nicht gemessen).
    HALS_RUECKFALL = 0.15
    #: Rand um den Kopf oben und Hals unter der Halszeile, in Anteilen der Kopfhöhe (Scheitel bis Halszeile).
    #: Sichtprobe an Edgars Fotos (07.10.2026): bei 0,10 stand der Kragenrand des Hemdes unten im Bild, bei 0,02 schnitt der Ausschnitt von vorne das Kinn an (die engste Zeile ist dort das Kinn,
    #: nicht der Hals) — 0,06 ist der Mittelweg, nicht weiter geprobt.
    RAND_OBEN, HALS_DAZU = 0.08, 0.06
    #: Der Halsstumpf unter der Halszeile bleibt seitlich so viel breiter als der Hals (Anteil der Halsbreite je Seite) — die Schultern fallen weg.
    HALS_SEITE = 0.25
    #: Plausibler Kopf: Anteil an der Körperhöhe. Außerhalb ist es kein Ganzkörperfoto (oder die Silhouette ist kaputt) — dann kein Ausschnitt.
    KOPF_ANTEIL = (0.05, 0.30)
    #: Die Silhouette wird auf diesen Teiler verkleinert gemessen (5.500 px → 690 px); der Schnitt selbst läuft auf dem Original.
    TEILER = 8
    #: Größte Kantenlänge des Ausschnitts — darüber wird verkleinert (Hunyuan3D sieht ohnehin nur 518 px).
    GROESSTE = 2048

    @classmethod
    def ausschnitt(cls, bild):
        """`(Bild, Befund)` — der quadratische RGBA-Ausschnitt des Kopfes aus einem freigestellten Foto. Wirft ValueError, wenn das Foto keine brauchbare Silhouette zeigt."""
        bild = bild.convert('RGBA')
        klein = np.asarray(bild.getchannel('A').reduce(cls.TEILER)) > 127
        zeilen = np.nonzero(klein.any(axis=1))[0]
        if not len(zeilen):
            raise ValueError('Das Foto ist leer (kein Alphakanal)')
        oben, unten = int(zeilen[0]), int(zeilen[-1])
        hoehe = unten - oben + 1
        hals, rueckfall = cls._halszeile(klein, oben, hoehe)
        kopf = hals - oben
        anteil = kopf / hoehe
        if not cls.KOPF_ANTEIL[0] <= anteil <= cls.KOPF_ANTEIL[1]:
            raise ValueError('Kopfhöhe %.1f %% der Körperhöhe — kein Ganzkörperfoto' % (100 * anteil))
        spalten = np.nonzero(klein[oben:hals].any(axis=0))[0]
        links, rechts = int(spalten[0]), int(spalten[-1])
        mitte_x = (links + rechts + 1) / 2.0
        breite = rechts - links + 1
        unterkante = hals + cls.HALS_DAZU * kopf
        oberkante = oben - cls.RAND_OBEN * kopf
        kante = max(unterkante - oberkante, breite * 1.2)
        mitte_y = (oberkante + unterkante) / 2.0
        kasten = [int(round((mitte_x - kante / 2.0) * cls.TEILER)), int(round((mitte_y - kante / 2.0) * cls.TEILER))]
        seite = int(round(kante * cls.TEILER))
        kasten += [kasten[0] + seite, kasten[1] + seite]
        aus = cls._schneiden(bild, kasten)
        aus = cls._schultern_weg(aus, kasten, klein, hals)
        if aus.width > cls.GROESSTE:
            aus = aus.resize((cls.GROESSTE, cls.GROESSTE), Image.LANCZOS)
        befund = {'kasten': kasten, 'breite': aus.width, 'hoehe': aus.height, 'kopf_anteil': round(anteil, 4),
                  'hals_zeile': int(hals * cls.TEILER), 'hals_rueckfall': rueckfall, 'koerperhoehe_px': int(hoehe * cls.TEILER)}
        return aus, befund

    @classmethod
    def _halszeile(cls, klein, oben, hoehe):
        """(Zeile des Halses, ob der Rückfall gilt) — kleinste geglättete Zeilenbreite im Suchfenster."""
        breiten = klein.sum(axis=1).astype(float)
        glatt = np.convolve(breiten, np.ones(max(3, int(0.012 * hoehe))) / max(3, int(0.012 * hoehe)), mode='same')
        von, bis = oben + int(cls.HALS_VON * hoehe), oben + int(cls.HALS_BIS * hoehe)
        fenster = glatt[von:bis]
        i = int(np.argmin(fenster))
        am_rand = i < 0.08 * len(fenster) or i > 0.92 * len(fenster)
        if am_rand:
            return oben + int(cls.HALS_RUECKFALL * hoehe), True
        return von + i, False

    @staticmethod
    def _schneiden(bild, kasten):
        """Der Kasten aus dem Bild; was über den Rand ragt, bleibt durchsichtig."""
        leer = Image.new('RGBA', (kasten[2] - kasten[0], kasten[3] - kasten[1]), (0, 0, 0, 0))
        x0, y0 = max(kasten[0], 0), max(kasten[1], 0)
        x1, y1 = min(kasten[2], bild.width), min(kasten[3], bild.height)
        if x1 > x0 and y1 > y0:
            leer.paste(bild.crop((x0, y0, x1, y1)), (x0 - kasten[0], y0 - kasten[1]))
        return leer

    @classmethod
    def _schultern_weg(cls, aus, kasten, klein, hals):
        """Unter der Halszeile bleibt nur der Hals: seitlich um `HALS_SEITE` der Halsbreite breiter, der Rest wird durchsichtig."""
        zeile = klein[min(hals, klein.shape[0] - 1)]
        spalten = np.nonzero(zeile)[0]
        if not len(spalten):
            return aus
        schon = int(spalten[0]), int(spalten[-1])
        extra = cls.HALS_SEITE * (schon[1] - schon[0] + 1)
        grenze_oben = int(round(hals * cls.TEILER)) - kasten[1]
        x_von = int(round((schon[0] - extra) * cls.TEILER)) - kasten[0]
        x_bis = int(round((schon[1] + 1 + extra) * cls.TEILER)) - kasten[0]
        if grenze_oben >= aus.height:
            return aus
        alpha = np.asarray(aus.getchannel('A')).copy()
        alpha[max(grenze_oben, 0):, :max(x_von, 0)] = 0
        alpha[max(grenze_oben, 0):, max(x_bis, 0):] = 0
        aus.putalpha(Image.fromarray(alpha))
        return aus
