# -*- coding: utf-8 -*-
"""Bildmodellfreistellergrundlage — was der Browser braucht, um die Vorschau SELBST zu rechnen.

Edgar (21.09.2026): „die slider sollen sofort wirken, mach websocket dafür oder sowas!" Ein
Reglerzug kostete einen Server-Umlauf (Bild lesen, Maske, Alpha, PNG — 0,3–1 s). Jetzt holt das
Fenster EINMAL die Grundlage in Vorschaugröße (`VORSCHAU_PX`) und rechnet Rand, Schwelle,
Weichzeichnen, Striche und Hintergrund in der Leinwand (`freistellervorschau.js`, Millisekunden):

    bild      RGB-JPEG der Vorschau
    maske     die weiche Maske nach Modell, Matting, Punkten und GrabCut — alles, was ein Netz
              oder den Server braucht
    abstand   nur Positivliste: ΔE zur nächsten Palettenfarbe (× ABSTAND_MAL als 8 Bit) — der
              Browser schwellt sie mit der Positivschwelle selbst, ohne Umlauf, behält nur die
              am Kern hängenden Flecken und vereinigt sie mit dem Kern
    kern      nur Positivliste: die Figur, die ganz bleibt (erodiertes Innere + Marken)
    f         Vorschau / Bild (Rand und Weich sind in Bildpixeln angegeben)

Neu geholt wird sie nur, wenn sich etwas Serverseitiges ändert (Modell, Matting, Punkte,
Verfeinern; Striche bei GrabCut und Positivliste). `speichern` rechnet unverändert in voller
Größe auf dem Server — dieselben Formeln (`Bildmodellfreisteller.alpha`)."""
import base64

import numpy as np

__all__ = ['Bildmodellfreistellergrundlage']


class Bildmodellfreistellergrundlage:
    ABSTAND_MAL = 4.0

    def __init__(self, freisteller):
        self.f = freisteller

    @staticmethod
    def _daten(bild, art, **param):
        import cv2

        if art == 'jpeg':
            ok, roh = cv2.imencode('.jpg', cv2.cvtColor(bild, cv2.COLOR_RGB2BGR),
                                  [cv2.IMWRITE_JPEG_QUALITY, 92])
        else:
            ok, roh = cv2.imencode('.png', bild)
        if not ok:
            raise RuntimeError('Grundlage nicht kodiert (%s)' % art)
        return 'data:image/%s;base64,%s' % (art, base64.b64encode(roh.tobytes()).decode('ascii'))

    def holen(self, datei, regler):
        """`{breite, hoehe, f, bild, maske, abstand, sicher}` für die Vorschau im Browser."""
        import cv2

        from .bildmodellfreistellerkorrektur import Bildmodellfreistellerkorrektur as K
        from .bildmodellhauttonmaske import Bildmodellhauttonmaske as H

        regler = self.f.regler_pruefen(regler)
        rgb = self.f._rgb(datei)
        h, w = rgb.shape[:2]
        f = min(1.0, self.f.VORSCHAU_PX / float(max(h, w)))
        groesse = (max(1, int(w * f)), max(1, int(h * f)))
        abstand = None
        maske = self.f.maske(datei, regler=regler)
        if regler.get('verfeinern') == 'grabcut':
            a = K.grabcut(rgb, maske.astype(np.float32) / 255.0, regler.get('striche'))
            maske = np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)
        kern = None
        if regler.get('positiv'):
            kern = H.kern(maske, regler)
            karte = H.abstandskarte(rgb, kern)
            if karte is not None:
                abstand = np.clip(karte[0] * self.ABSTAND_MAL + 0.5, 0, 255).astype(np.uint8)
                abstand = cv2.resize(abstand, groesse, interpolation=cv2.INTER_LINEAR)
            kern = cv2.resize(kern.astype(np.uint8) * 255, groesse, interpolation=cv2.INTER_AREA) if f < 1.0 \
                else kern.astype(np.uint8) * 255
        klein = cv2.resize(rgb, groesse, interpolation=cv2.INTER_AREA) if f < 1.0 else rgb
        maske_klein = cv2.resize(maske, groesse, interpolation=cv2.INTER_AREA) if f < 1.0 else maske
        return {
            'breite': groesse[0], 'hoehe': groesse[1], 'f': f, 'sicher': self.f.SICHER,
            'bild': self._daten(np.ascontiguousarray(klein), 'jpeg'),
            'maske': self._daten(np.ascontiguousarray(maske_klein), 'png'),
            'abstand': self._daten(np.ascontiguousarray(abstand), 'png') if abstand is not None else None,
            'abstand_mal': self.ABSTAND_MAL,
            'kern': self._daten(np.ascontiguousarray(kern), 'png') if kern is not None else None,
        }
