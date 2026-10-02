# -*- coding: utf-8 -*-
"""Brauenfarbe — Brauen und Wimpern in der Haarfarbe des Modells statt im Daz-Schwarz (01.10.2026).

Befund (Testauftrag 2026.10.01.12.38.09, Kopf neben dem Foto): Brauen und Wimpern fast schwarz und dick wie Lidstrich,
Edgars Brauen sind grau-braun. Die Daz-Bilder sind dunkel; ein glTF-Farbfaktor darf nicht über 1 — also wird das Bild
getönt: Helligkeit je Pixel relativ zu ihrem Mittel (die Struktur der Härchen bleibt) × Zielfarbe × `DUNKLER` (Brauen
sind etwas dunkler als das Kopfhaar). Die getönten Bilder liegen je Farbe einmal bei den komponierten Kleidtexturen.

    Brauenfarbe().anwenden(netz, '#a88f8f')   # netz von `G9koerpernetz(...).bauen()`, wird verändert
"""

import hashlib

import numpy as np

__all__ = ['Brauenfarbe']


class Brauenfarbe:
    ANHAENGE = ('brauen', 'wimpern')
    DUNKLER = {'brauen': 0.75, 'wimpern': 0.45}

    @staticmethod
    def _rgb(hexfarbe):
        h = str(hexfarbe or '').lstrip('#')
        return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0 if len(h) == 6 else None

    def _toenen(self, albedo, farbe, faktor):
        """→ Bildpfad in Bibliotheksform (`G9kleidtexturen.BILDPFAD` + komponiert/…) — `G9material.datei` nimmt
        keine freien Pfade an."""
        from Genesis9.kleidtexturen import G9kleidtexturen
        from Genesis9.material import G9material
        from PIL import Image
        quelle = G9material.datei(albedo)
        if quelle is None:
            return albedo
        kennung = hashlib.sha1(('%s|%s|%.3f' % (quelle, farbe.round(3).tolist(), faktor)).encode()).hexdigest()[:12]
        name = 'braue_%s.png' % kennung
        ordner = G9kleidtexturen.ordner() / G9kleidtexturen.KOMPONIERT
        ziel = ordner / name
        if not ziel.is_file():
            with Image.open(quelle) as roh:
                bild = np.asarray(roh.convert('RGB'), dtype=np.float64) / 255.0
            hell = bild @ np.array([0.299, 0.587, 0.114])
            rel = hell / max(float(hell.mean()), 1e-3)
            neu = np.clip(rel[..., None] * farbe[None, None, :] * faktor, 0.0, 1.0)
            ordner.mkdir(parents=True, exist_ok=True)
            Image.fromarray((neu * 255).astype(np.uint8)).save(ziel)
        return G9kleidtexturen.BILDPFAD + G9kleidtexturen.KOMPONIERT + '/' + name

    def anwenden(self, netz, hexfarbe):
        """Die Albedo der Gruppen von Brauen und Wimpern durch getönte Kopien ersetzen → Zahl der getönten Gruppen."""
        farbe = self._rgb(hexfarbe)
        if farbe is None:
            return 0
        zahl = 0
        for a in netz.get('anhaenge') or []:
            if a.get('schluessel') not in self.ANHAENGE:
                continue
            faktor = self.DUNKLER[a['schluessel']]
            for g in a.get('gruppen') or []:
                b = g.setdefault('bilder', {})
                if b.get('albedo'):             # Brauen: Bild getönt, der (dunkle) Daz-Faktor fällt weg
                    b['albedo'] = self._toenen(b['albedo'], farbe, faktor)
                    b['farbe'] = [1.0, 1.0, 1.0]
                else:                           # Wimpern: nur Maske und Faktor (0, 0, 0) — der Faktor wird die Farbe
                    b['farbe'] = [round(float(c), 4) for c in np.clip(farbe * faktor, 0.0, 1.0)]
                zahl += 1
        return zahl
