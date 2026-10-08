# -*- coding: utf-8 -*-
"""Herrenhaarstueck — das Herrenhaar eines Auftrags als Haar der Genesis-Bibliothek, „eigen_Herrenhaar" (05.10.2026).

Edgar (Auftrag 2026.10.04.21.41.43): „lege das neue Herrenhaar auch in die Genesis Bibliothek als eigen_Herrenhaar rein." Das Herrenhaar (`Herrenhaar`: Kappe und Strähnen auf der Kopfhaut, Umriss und Haarlinie aus dem Fotohaar) war bis dahin
nur ein Teil der Runden und des Standmodells; die Garderobe kannte es nicht. Hier wird es wie jedes eigene Stück abgelegt (`G9eigenstueck.schreiben`, Hersteller EIGEN, Ordner `People/Genesis 9/Hair/` — so liest die Garderobe es als
Haar, Kategorie „Haare", und „Haar – Generisch" führt es als weitere Frisur).

Aufbau des Stücks:
  * EIN Netz aus der Haarkappe und allen Strähnengruppen (Dreiecke der Röhren), alle Punkte an den Knochen `head` gebunden (Gewicht 1,0: Haar folgt dem Kopf, wie `G9eigenstueck.gewichte_auf` es für Zubehör vorsieht).
  * EIN Material: Die Helligkeitsgruppen (Kappe, fünf Strähnengruppen) liegen als Farbfelder in einem kleinen Bild (`FELD_PX` Bildpunkte je Feld), jede Gruppe zeigt mit ihren UV auf die Mitte ihres Felds — der DSON-Schreiber
    kennt je Stück ein Material. Die Farben sind die der Runden (`Herrenhaar.farben`, mit `HELL` für den Render der Pipeline); im Browser kann es etwas heller wirken.
  * Die Ruhelage wird wie bei den Foto-Stücken zurückgerechnet (`G9gcfigurbau.ruhelage`): Ein Genesis-Stück liegt auf der Grundfigur, die Figur legt beim Anziehen ihre Form darüber — gebaut ist das Haar aber auf der Figur
    des Auftrags (`job.stellung()`). Ohne die Rückrechnung stünde es auf der Figur des Auftrags um deren Morphs daneben.

Es ist das Haar DIESES Auftrags (Kopfform, Haarlinie, Länge und Farbe aus seinen Fotos), kein allgemeines Modell: Auf einer anderen Figur folgt es ihren Morphs wie jedes Genesis-Stück, behält aber Linie und Länge dieses Kopfes. Wer es neu
rechnet, überschreibt das Stück unter demselben Namen (Fassung in `bilanz.json` neben dem Stück, `VERSION`).

    Herrenhaarstueck.ablegen(job) → Bilanz von `G9eigenstueck.schreiben` samt `ruhelage`, `punkte`, `dreiecke`, `gruppen`
"""

import json
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Herrenhaarstueck']


class Herrenhaarstueck:
    #: Name in der Garderobe und Anzeigename; die Kennung der Garderobe ist `eigen_herrenhaar`.
    NAME = 'eigen_Herrenhaar'
    KATEGORIE = ('Follower/Hair', '/Default/Hair')
    KNOCHEN = 'head'
    #: Breite und Höhe eines Farbfelds im Bild (Bildpunkte) — breit genug, dass die Filterung zwischen Feldern die Mitte nicht erreicht.
    FELD_PX = 16
    #: Zählt hoch, wenn sich der Aufbau des Stücks ändert (steht in der Bilanz).
    VERSION = 1

    @classmethod
    def teile(cls, job, ablage=None):
        """`(teile, haarfarbe)`: Kappe und Strähnengruppen des Herrenhaars auf der Figur des Auftrags (Füße auf 0, A-Pose) — ValueError, wo `Herrenhaar` nicht gilt (keine Hülle des Fotohaars, kein kurzes Haar)."""
        from Genesis9.modellmitkleidern import ModellMitKleidern
        from Genesis9.modellrezept import G9rezept

        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from .haarumbau import Haarumbau
        from .iterationsoptionen import Iterationsoptionen
        from .kleidermodellbau import Kleidermodellbau
        from .standvorabkleider import Standvorabkleider
        ablage = ablage or Engine2d3dKleiderablage(job.kennung)
        modell = ModellMitKleidern()
        G9rezept.anwenden(modell, '\n'.join(Standvorabkleider.rezept(job)) + '\n')        # die Haarfarbe der Fotos (`haar_farbe`) wie im Stand vor den Iterationen
        haarfarbe = (modell.farben or {}).get('haar')
        bau = Kleidermodellbau(job.stellung(), None, kacheln={}, ablage=ablage, haarumbau='herren')
        teile = Haarumbau.herrenhaar(bau.koerper(), ablage, haarfarbe, laenge=Iterationsoptionen.haarlaenge(job))     # die Länge der Optionen des Auftrags (`haar_laenge_unten/oben`)
        if not teile:
            raise ValueError('Herrenhaar nicht gebaut: keine Hülle des Fotohaars oder kein kurzes Haar (Log: „Herrenhaar")')
        return teile, haarfarbe

    @staticmethod
    def _farbe(teil):
        """Die Farbe eines Teils (sRGB 0–1): die Strähnengruppen tragen sie im Feld `farbe`, die Haarkappe (`farbe` weiß) in ihrem Bild — dessen Mittel."""
        for textur in teil.get('textur') or []:
            if textur.get('albedo'):
                from PIL import Image
                with Image.open(textur['albedo']) as bild:
                    return [float(c) / 255.0 for c in np.asarray(bild.convert('RGB'), dtype=np.float64).reshape(-1, 3).mean(axis=0)]
        return [float(c) for c in teil['farbe'][:3]]

    @classmethod
    def netz(cls, teile):
        """`(punkte (N, 3), netz, felder (G, 3))`: alle Teile als ein Netz im Format von `G9objleser.lesen` — `flaechen`/`flaechen_uv` als Listen, `uvs` je Gruppe auf die Mitte ihres Farbfelds; `felder` die Farben je Gruppe."""
        punkte, flaechen, flaechen_uv, felder = [], [], [], []
        versatz = 0
        for nummer, teil in enumerate(teile):
            p = np.asarray(teil['punkte'], dtype=np.float64).reshape(-1, 3)
            d = np.asarray(teil['dreiecke'], dtype=np.int64).reshape(-1, 3) + versatz
            punkte.append(p)
            flaechen.extend(d.tolist())
            flaechen_uv.extend([[nummer, nummer, nummer]] * len(d))
            felder.append(cls._farbe(teil))
            versatz += len(p)
        n = len(teile)
        uvs = np.array([[(i + 0.5) / n, 0.5] for i in range(n)])
        netz = {'punkte': np.vstack(punkte), 'uvs': uvs, 'flaechen': flaechen, 'flaechen_uv': flaechen_uv, 'farbe': (1.0, 1.0, 1.0), 'bild': None}
        return netz['punkte'], netz, np.array(felder)

    @classmethod
    def bild(cls, felder, pfad):
        """Das Farbfeldbild (G Felder nebeneinander, sRGB) nach `pfad` schreiben."""
        from PIL import Image
        farben = (np.clip(np.asarray(felder), 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
        pixel = np.repeat(farben[None, :, :], cls.FELD_PX, axis=0)
        pixel = np.repeat(pixel, cls.FELD_PX, axis=1)
        Image.fromarray(pixel).save(pfad)
        return pfad

    @classmethod
    def ablegen(cls, job, ablage=None):
        """Das Herrenhaar des Auftrags als Stück „eigen_Herrenhaar" in die eigene Genesis-Bibliothek schreiben → Bilanz (`stueck`: Kennung der Garderobe)."""
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.gcfigurbau import G9gcfigurbau
        teile, haarfarbe = cls.teile(job, ablage)
        punkte, netz, felder = cls.netz(teile)
        kennung, anzeige = G9eigenstueck.kennung_und_name(cls.NAME)
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        bild = cls.bild(felder, ordner / 'farbfelder.png')
        material = {'name': kennung + '_Mat', 'farbe': (1.0, 1.0, 1.0), 'bild': str(bild), 'shininess': None, 'opacity': None}
        # Kennung = Name der Ablage: ein Neubau überschreibt dasselbe Stück (Edgars Name), die Fassung steht in der Bilanz
        bilanz = G9eigenstueck.schreiben(punkte, netz, kennung, anzeige, cls.KATEGORIE, material, heben=False, knochen=cls.KNOCHEN, art_ordner='Hair')
        figur = dict(job.stellung() or {})
        ruhe, bericht = G9gcfigurbau.ruhelage(bilanz['stueck'], figur, punkte, punkte)
        bilanz = G9eigenstueck.schreiben(ruhe, netz, kennung, anzeige, cls.KATEGORIE, material, heben=False, knochen=cls.KNOCHEN, art_ordner='Hair')
        bilanz.update(ruhelage=bericht, angezogen=G9gcfigurbau.pruefen(bilanz['stueck'], figur, punkte), gruppen=len(teile), dreiecke=len(netz['flaechen']),
                      haarfarbe=haarfarbe, fassung=cls.VERSION, auftrag=job.kennung)
        (ordner / 'herrenhaar.json').write_text(json.dumps(bilanz, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
        logger.info('Herrenhaarstück %s: %d Punkte, %d Dreiecke, %d Gruppen, angezogen %s', bilanz['stueck'], bilanz['punkte'], bilanz['dreiecke'], bilanz['gruppen'], bilanz['angezogen'])
        return bilanz
