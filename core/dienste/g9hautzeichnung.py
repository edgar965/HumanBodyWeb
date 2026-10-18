# -*- coding: utf-8 -*-
"""G9hautzeichnung — Muskel- und Fettzeichnung der Haut als Normalenkarten der Genesis-9-Kacheln (17.10.2026).

Edgar, 17.10.2026: „mach alles was offen ist" — dazu gehört die Muskel- und Fettzeichnung (Tabelle 4 in `genesis9-alter.md`). MB-Labs Verschiebungsbild
(`human_<geschlecht>_displacement.png`, 2048², RGBA) trägt vier Kanäle: R Grundhaut, G Altersfalten (`G9hautfalten`), **B Muskelzeichnung, A Fettgewebe**;
`Hautverschiebung.textur` rechnet `wert = R + alter·(G − 0,5) + tonus·(B − 0,5) + (1 − tonus)·masse·(A − 0,5)`, Verschiebung entlang der Normale um (wert − 0,5)·0,01 m.
Hier werden B und A genauso wie bei den Falten zu Normalen je UDIM-Kachel (der Weg Texel → HumanBody-UV und die Kantenlänge sind dieselben, die Steigung ist also physikalisch):

    R, G   Normale der Muskelzeichnung (x, y); die z-Komponente rechnet der Shader
    B, A   Normale des Fettgewebes (x, y)

Ein Bild je Kachel und Geschlecht, EIN Sampler im Shader statt zwei. Die Gewichte stellt der Nutzer (Regler „Muskelzeichnung", „Fettzeichnung"); sie sind Uniforms.

ABLAGE: `Genesis9/ablage/hautzeichnung_<geschlecht>_v<FASSUNG>_<kachel>.png` und `….json` — die Fassung steht im Namen (`artefakte-benennen.md`).
Bau und Stand wie bei den Falten (`G9hautzeichnungablage` ist die Ablage mit anderem Produkt).
"""
import json
import logging
import time

import numpy as np

from .g9hautfalten import G9hautfalten

logger = logging.getLogger('core')

__all__ = ['G9hautzeichnung']


class G9hautzeichnung(G9hautfalten):
    """`bauen(geschlecht)` rechnet alle Kacheln und schreibt sie in die Ablage."""

    #: Bei Änderungen an Rechnung oder Format erhöhen — die Dateinamen tragen sie.
    FASSUNG = 1
    #: Kanal im Verschiebungsbild → Name: B und A (R ist die Grundhaut, G die Altersfalten).
    KANAELE = ((2, 'muskel'), (3, 'fett'))
    #: Die Nagelkachel bekommt nie eine Zeichnung (siehe `G9hautfalten.OHNE_FALTEN`).
    OHNE_FALTEN = (1005,)
    #: Unter dieser 99-%-Steigung hat ein Kanal einer Kachel nichts zu zeigen; haben beide nichts, gibt es kein Bild.
    STEIGUNG_MIN = 0.01

    @classmethod
    def stamm(cls, geschlecht):
        from Genesis9.pfade import G9pfade
        return G9pfade.ablage() / ('hautzeichnung_%s_v%d' % (geschlecht, cls.FASSUNG))

    @staticmethod
    def _kanal(geschlecht, kanal):
        """(H, W) float32 — ein Kanal des Datenbilds, 0,5 = keine Verschiebung."""
        from .verschiebungstextur import Verschiebungstextur
        return Verschiebungstextur.datenbild(geschlecht)[..., kanal]

    def kachel(self, traeger, abtastung, nummer, quellen):
        """`(bild (S, S, 4) uint8, {name: steigung_p99})` einer Kachel — Muskel in R/G, Fett in B/A; außerhalb der Inseln flach (128)."""
        halb = []
        p99 = {}
        gueltig = None
        drin = abtastung.stellen(nummer)[0]
        for (_kanal, name), quelle in zip(self.KANAELE, quellen, strict=True):
            gueltig, hoehe, kx, ky = self.hoehe_und_mass(traeger, abtastung, nummer, quelle)
            normale, steigung = self.normalen(hoehe, kx, ky)
            halb.append(normale[..., :2])
            p99[name] = float(np.percentile(steigung[drin], 99)) if drin.any() else 0.0
        bild = np.dstack(halb)
        bild[~gueltig] = 128
        return bild, p99

    def bauen(self):
        """Alle Kacheln dieses Geschlechts in die Ablage; → die Liste (`{kachel: {muskel_p99, fett_p99}}`, `sekunden`)."""
        from Genesis9.texturabtastung import G9texturabtastung
        from PIL import Image

        t0 = time.perf_counter()
        abtastung = G9texturabtastung.holen(self.SEITE)
        traeger = self._traeger()
        quellen = [self._kanal(self.geschlecht, kanal) for kanal, _name in self.KANAELE]
        kacheln = {}
        for nummer in abtastung.kacheln:
            if int(nummer) in self.OHNE_FALTEN:
                continue
            bild, p99 = self.kachel(traeger, abtastung, nummer, quellen)
            logger.info('Hautzeichnung %s Kachel %d: Steigung p99 %s (%.1f s)', self.geschlecht, nummer,
                        {k: round(v, 3) for k, v in p99.items()}, time.perf_counter() - t0)
            if max(p99.values()) < self.STEIGUNG_MIN:
                continue
            Image.fromarray(bild, 'RGBA').save(self.bildpfad(self.geschlecht, nummer), 'PNG')
            kacheln[str(nummer)] = {'%s_p99' % k: round(v, 4) for k, v in p99.items()}
        liste = {'geschlecht': self.geschlecht, 'fassung': self.FASSUNG, 'seite': self.SEITE, 'kacheln': kacheln,
                 'sekunden': round(time.perf_counter() - t0, 1)}
        ziel = self.listenpfad(self.geschlecht)
        vorlaeufig = ziel.with_suffix('.neu')
        vorlaeufig.write_text(json.dumps(liste), encoding='utf-8')
        vorlaeufig.replace(ziel)                    # die Liste kommt zuletzt: sie sagt „fertig"
        return liste
