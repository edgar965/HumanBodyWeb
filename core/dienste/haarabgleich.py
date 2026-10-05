# -*- coding: utf-8 -*-
"""Haarabgleich — das Haar im Kopfausschnitt gegen die Fotos, je Höhenband und Sektor der Frisur (02.10.2026).

Prüfung Runde 19 (Fable, Auftrag 2026.10.01.20.10.04): Unter einer angedrückten Kappe hing das Haar seitlich über die
Ohren und als Keil in den Nacken; die Fotos zeigen kurzes Haar, freie Ohren, einen kurzen Nacken. Die Haarregeln
(`IterationHaare`: Länge, Anlegen, Trim) maßen nur den Abstand zum TRELLIS-Netz — der sieht weder Ohr noch Nacken, die
Länge stieg auf 0,4, und das Anlegen der oberen Bänder (in allen acht Sektoren am Anschlag 1,5) machte erst die Stufe
zwischen Kappe und Rest. Diese Messung fragt die Fotos:

- Foto: im Kopfausschnitt (`Pruefbilder.kopfausschnitt`, derselbe wie `Genesishaarrender.bild_kopf`) ist Haar, was in
  der Figur liegt und nicht hautfarben ist (`haar`: warm und bunter als die Schwelle des Fotos). Unter der Halszeile
  (der schmalsten Zeile der Figur zwischen `HALS` m unter dem Scheitel) zählt nichts: dort beginnt der Kragen, ein
  graues Shirt sähe aus wie graues Haar. Langes Haar über den Schultern sieht diese Messung deshalb nicht.
- Render: Kennfarben (Kopfhaar, Bart, Rest) im selben Ausschnitt; das Foto wird waagerecht auf dessen Kopfmitte gelegt.
- je Punkt einer Frisur und Ansicht, in der er zur Kamera zeigt (`BLICK`): Was zeigt das Foto dort? Haut → das Haar
  liegt zu tief oder ist zu lang (Ohr, Nacken, Stirn); leer → es steht ab; Haar → passt.

`befund['haarabgleich']`:
    teile[sorte]   haut, leer: (BAENDER, SEKTOREN) Anteil der gesehenen Punkte (None unter `MINDESTENS` Punkten),
                   geschnitten wie `Befundmessung.zellen` (Bänder unten → oben, Sektor j = −180° + 45° j …)
    ansichten[w]   iou, zuviel (Anteil des Kopfhaars im Render, wo das Foto keins zeigt), fehlt (umgekehrt), hals
    fehler         1 − mittlere IoU des Kopfhaars über die Ansichten — der Haarterm der `Gesamtnote`
    treffer        Selbsttest der Abbildung: Anteil der gesehenen Kopfhaarpunkte, die im Kennfarbenbild auf Haar fallen
"""

import logging

import numpy as np
from PIL import Image

logger = logging.getLogger('core')

__all__ = ['Haarabgleich']


class Haarabgleich:
    FASSUNG = 2
    GROESSE = 256
    #: Haut: Rot ≥ Grün ≥ Blau (bis `WARM`), Buntheit (max − min) ÷ max über der Schwelle des Fotos, Helligkeit über
    #: `HELL`. Die Schwelle teilt die Buntheit der Figur über der Halszeile in zwei Gruppen (Otsu), begrenzt auf `BUNT`:
    #: Messrunde 20 mit fester Schwelle 0,14 — das warm beleuchtete Seitenhaar (Buntheit 0,15–0,25) galt als Haut,
    #: IoU der Seite 0,12. Otsu je Foto: vorn 0,19, hinten 0,18, Seite 0,29 (Haut um 0,4). Bartstoppeln zählen als Haut.
    BUNT = (0.12, 0.32)
    #: Mehrheit im Fenster dieser Kantenlänge (Pixel) — Strähnen und Glanzlichter lassen sonst Löcher im Haar.
    GLAETTEN = 5
    HELL = 0.25
    WARM = 0.02
    HALS = (0.15, 0.32)
    #: Ein Punkt zählt in einer Ansicht, wenn seine waagerechte Richtung von der Achse der Frisur höchstens 60° von der
    #: Kamera weg zeigt — die Rückseite des Kopfes liegt sonst auf dem Gesicht des Fotos.
    BLICK = 0.5
    MINDESTENS = 12
    BAENDER, SEKTOREN = 5, 8
    KENN = {'haar': (1.0, 0.0, 0.0), 'bart': (0.0, 1.0, 0.0), 'sonst': (0.0, 0.0, 1.0)}
    HAAR, BART, SONST = 1, 2, 3
    BARTSORTE = '_beard'

    def __init__(self, ablage, render):
        self.ablage = ablage
        self.render = render

    @property
    def je_m(self):
        return self.GROESSE / self.render.KOPF_HOEHE

    @classmethod
    def schwelle(cls, bunt, werte):
        """Otsu über die Buntheit `werte` (64 Stufen bis 0,64), begrenzt auf `BUNT`."""
        hist, kanten = np.histogram(werte, bins=64, range=(0.0, 0.64))
        mitten = kanten[:-1]
        best, aus = -1.0, cls.BUNT[0]
        for t in range(1, 64):
            w0, w1 = float(hist[:t].sum()), float(hist[t:].sum())
            if w0 and w1:
                trennung = w0 * w1 * (float((hist[:t] * mitten[:t]).sum()) / w0
                                      - float((hist[t:] * mitten[t:]).sum()) / w1) ** 2
                if trennung > best:
                    best, aus = trennung, float(kanten[t])
        return min(max(aus, cls.BUNT[0]), cls.BUNT[1])

    @classmethod
    def haar(cls, rgb, maske, bis):
        """Haar auf dem Foto: in der Figur, nicht hautfarben, geglättet — `bis` ist die Halszeile (für die Schwelle)."""
        from scipy.ndimage import uniform_filter
        f = np.asarray(rgb, dtype=np.float32)[..., :3] / 255.0
        hoch, tief = f.max(axis=2), f.min(axis=2)
        bunt = (hoch - tief) / np.maximum(hoch, 1e-3)
        grenze = cls.schwelle(bunt, bunt[:bis][maske[:bis]])
        warm = (f[..., 0] >= f[..., 1]) & (f[..., 1] >= f[..., 2] - cls.WARM)
        haar = maske & ~(warm & (bunt >= grenze) & (hoch > cls.HELL))
        return (uniform_filter(haar.astype(np.float32), cls.GLAETTEN) > 0.5) & maske, grenze

    @classmethod
    def ist_bart(cls, teil):
        return str(teil.get('sorte') or '').endswith(cls.BARTSORTE)

    def eintragen(self, befund, teile, referenzen, modell_hoehe, aus):
        """Misst und schreibt `befund['haarabgleich']` — nichts ohne Haarteil oder ohne messbare Ansicht."""
        haare = [t for t in teile if t.get('art') == 'haar']
        if not haare or not referenzen:
            return None
        scheitel = max(float(np.asarray(t['punkte'])[:, 1].max()) for t in teile)
        ansichten = []
        for r in referenzen:
            try:
                ansichten.append(self._ansicht(r, teile, float(modell_hoehe), aus))
            except (OSError, ValueError, RuntimeError) as fehler:
                logger.warning('Haarabgleich: %+d° nicht gemessen (%s)', round(r.winkel), fehler)
        if not ansichten:
            return None
        befund['haarabgleich'] = self._auswerten(haare, ansichten, scheitel)
        return befund['haarabgleich']

    def _ansicht(self, r, teile, modell_hoehe, aus):
        from .pruefbilder import Pruefbilder
        g = self.GROESSE
        farben = [self.KENN['bart' if self.ist_bart(t) else 'haar' if t.get('art') == 'haar' else 'sonst']
                  for t in teile]
        pfad = aus / ('haarkennung_%+04d.png' % int(round(r.winkel)))
        self.render.bild_kopf([(t['punkte'], t['dreiecke'], f) for t, f in zip(teile, farben, strict=True)],
                              r.winkel, pfad, groesse=(g, g), kennung=True)
        with Image.open(pfad) as bild:
            kenn = np.asarray(bild.convert('RGB')).astype(np.int16)
        art = np.zeros((g, g), np.int8)
        for wert, kanal in ((self.HAAR, 0), (self.BART, 1), (self.SONST, 2)):
            andere = [k for k in range(3) if k != kanal]
            art[(kenn[..., kanal] > 200) & (kenn[..., andere[0]] < 60) & (kenn[..., andere[1]] < 60)] = wert
        rgb, maske = Pruefbilder(self.ablage, g).kopfausschnitt(r.datei, modell_hoehe, self.render, g)
        oben = int(round(g / 2 - self.render.KOPF_UNTER_SCHEITEL * self.je_m))
        dx = self._versatz(art, oben)
        rgb, maske = np.roll(rgb, dx, axis=1), np.roll(maske, dx, axis=1)
        zeilen = maske.sum(axis=1)
        von, bis = (int(oben + h * self.je_m) for h in self.HALS)
        bereich = np.arange(max(von, 0), min(bis, g))
        bereich = bereich[zeilen[bereich] > 0]
        hals = int(bereich[np.argmin(zeilen[bereich])]) if len(bereich) else g
        haar, grenze = self.haar(rgb, maske, hals)
        return {'winkel': float(r.winkel), 'haar': haar, 'maske': maske, 'art': art, 'hals': hals, 'grenze': grenze,
                'farbe': self._farbe(r, teile, rgb, haar, art == self.HAAR, aus)}

    def _farbe(self, r, teile, rgb, haar, render_haar, aus):
        """Farbe des Haars in dieser Ansicht, Foto gegen Render (`Haarfarbmessung`) — None, wenn der Farbrender nicht gelingt (die Messung der Form läuft trotzdem)."""
        from .genesishaarrender import Genesishaarrender
        from .haarfarbmessung import Haarfarbmessung
        pfad = aus / ('haarfarbe_%+04d.png' % int(round(r.winkel)))
        try:
            self.render.bild_kopf([(t['punkte'], t['dreiecke'], t['farbe'], Genesishaarrender.extra(t)) for t in teile], r.winkel, pfad, groesse=(self.GROESSE, self.GROESSE))
            with Image.open(pfad) as bild:
                return Haarfarbmessung.ansicht(np.asarray(bild.convert('RGB')), rgb, haar, render_haar)
        except (OSError, ValueError, RuntimeError) as fehler:
            logger.warning('Haarabgleich: Haarfarbe %+d° nicht gemessen (%s)', round(r.winkel), fehler)
            return None

    def _versatz(self, art, oben):
        """Pixel, um die das Foto (Kopfmitte in der Bildmitte) nach rechts muss, damit es auf der Kopfmitte des Renders
        liegt — dieselbe Mitte wie in `Pruefbilder.kopfausschnitt`: Spaltenschwerpunkt der Figur bis 2 × 0,13 m."""
        kopf = art[max(oben, 0):int(oben + 2 * self.render.KOPF_UNTER_SCHEITEL * self.je_m)] > 0
        spalten = kopf.sum(axis=0)
        if not spalten.any():
            return 0
        return int(round(np.average(np.arange(len(spalten)), weights=spalten) - len(spalten) / 2))

    def _auswerten(self, haare, ansichten, scheitel):
        g = self.GROESSE
        aus = {'fassung': self.FASSUNG, 'teile': {}, 'ansichten': {}}
        ious = []
        for a in ansichten:
            gilt = np.arange(g)[:, None] < a['hals']
            foto = a['haar'] & gilt & (a['art'] != self.BART)
            modell = (a['art'] == self.HAAR) & gilt
            vereint, schnitt = int((foto | modell).sum()), int((foto & modell).sum())
            iou = schnitt / vereint if vereint else 1.0
            ious.append(iou)
            aus['ansichten']['%+d' % round(a['winkel'])] = {
                'iou': round(iou, 4), 'hals': a['hals'], 'buntheit': round(a['grenze'], 3),
                'zuviel': round(1.0 - schnitt / max(int(modell.sum()), 1), 4),
                'fehlt': round(1.0 - schnitt / max(int(foto.sum()), 1), 4)}
        treffer, gesehen = 0, 0
        mitte_y = scheitel - self.render.KOPF_UNTER_SCHEITEL
        for t in haare:
            p = np.asarray(t['punkte'], dtype=np.float64)
            haut, leer, n = np.zeros(len(p)), np.zeros(len(p)), np.zeros(len(p))
            radial = p[:, [0, 2]] - p[:, [0, 2]].mean(axis=0)
            radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
            for a in ansichten:
                b = np.radians(a['winkel'])
                c, s = np.cos(b), np.sin(b)
                u = np.round(g / 2 + (p[:, 0] * c - p[:, 2] * s) * self.je_m).astype(int)
                v = np.round(g / 2 - (p[:, 1] - mitte_y) * self.je_m).astype(int)
                im = (radial[:, 0] * s + radial[:, 1] * c >= self.BLICK) & (u >= 0) & (u < g) & (v >= 0) & \
                    (v < a['hals'])
                uu, vv = u[im], v[im]
                haut[im] += a['maske'][vv, uu] & ~a['haar'][vv, uu]
                leer[im] += ~a['maske'][vv, uu]
                n[im] += 1
                if not self.ist_bart(t):
                    treffer += int((a['art'][vv, uu] == self.HAAR).sum())
                    gesehen += int(im.sum())
            aus['teile'][t['sorte']] = {'haut': self._zellen(p, haut, n), 'leer': self._zellen(p, leer, n),
                                        'punkte': int((n > 0).sum())}
        aus['fehler'] = round(1.0 - sum(ious) / len(ious), 4)
        aus['treffer'] = round(treffer / gesehen, 3) if gesehen else None
        from .haarfarbmessung import Haarfarbmessung
        farbe = Haarfarbmessung.auswerten([a.get('farbe') for a in ansichten])
        if farbe:
            aus['farbe'] = farbe
        return aus

    def _zellen(self, p, wert, n):
        from Genesis9.ortsmorph import G9ortsmorph
        y = p[:, 1]
        y0, y1 = float(y.min()), float(y.max())
        j = np.clip(((G9ortsmorph._winkel(p, p.mean(axis=0)) + 180.0) / (360.0 / self.SEKTOREN)).astype(int), 0,
                    self.SEKTOREN - 1)
        i = np.clip(((y - y0) / max(y1 - y0, 1e-9) * self.BAENDER).astype(int), 0, self.BAENDER - 1)
        aus = []
        for band in range(self.BAENDER):
            zeile = []
            for k in range(self.SEKTOREN):
                wahl = (i == band) & (j == k) & (n > 0)
                zeile.append(round(float((wert[wahl] / n[wahl]).mean()), 3) if wahl.sum() >= self.MINDESTENS else None)
            aus.append(zeile)
        return aus
