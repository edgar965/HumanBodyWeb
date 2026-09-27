# -*- coding: utf-8 -*-
u"""Exportkartenprüfung — sieht eine `.obj` so an, wie ein fremdes Programm sie liest.

WOZU (26.09.2026): Drei Anläufe lang sah Damira1 in MeshLab falsch aus, und
jedes Mal war die Exportdatei „strukturell in Ordnung": alle Flächen da, jedes
Material zugeordnet, jede Karte vorhanden. Der Fehler saß eine Ebene tiefer —
die Bildkarten lagen auf dem Kopf (`Werkstoffbild.png`, `texture.flipY`).

Der Prüfer stellt deshalb die Frage, die ein Betrachter stellt: TRIFFT JEDE
FLÄCHE ÜBERHAUPT FARBE? Er nimmt je Fläche die Mitte der UV-Koordinaten und
schaut in der zugehörigen Karte nach. Fällt sie auf den leeren Rand der Karte,
ist die Fläche im fremden Programm farblos — das sind die hellen Flecken, die
Edgar an Hals, Knie und Fingern gesehen hat.

DIE RICHTUNGSPROBE ist der eigentliche Fund: dieselbe Messung wird ZWEIMAL
gerechnet, einmal mit der OBJ-Zeilenrichtung (v = 0 unten) und einmal
gespiegelt. Ist die gespiegelte Richtung deutlich besser, steht die Karte in
der Datei auf dem Kopf. Bei `DamiraFein.obj`: 133.552 leere Treffer gegen 0.

WAS DER PRÜFER NICHT KANN (damit niemand mehr hineinliest, als drinsteht):
- Eine Karte ohne erkennbaren leeren Rand (eine flächig gefüllte Haarkarte) ist
  für ihn blind — dort meldet er 0 und weiß nichts.
- Er misst Farbe, nicht Ähnlichkeit: eine Karte, die zur falschen Zone gehört,
  aber auch Haut zeigt, fällt ihm nicht auf.
- Die UV-Mitte steht für die ganze Fläche. Bei Flächen, die größer als die
  Karte sind, ist das zu grob.
"""
from collections import defaultdict
from pathlib import Path


class Exportkartenpruefung:

    #: Farbabstand, bis zu dem ein Bildpunkt noch als „leerer Rand" gilt.
    #: Der Rand einer exportierten Karte ist eine FLACHE Farbe; Haut rauscht.
    #: An DamiraFein.obj durchgespielt (0/2/5/12/25): die Zahl bewegte sich um
    #: weniger als 1 %, sie hängt also nicht an dieser Grenze.
    ABSTAND = 2

    #: Ab diesem Verhältnis gilt die Gegenrichtung als die bessere.
    FAKTOR = 4

    #: So viel der Karte muss die Randfarbe ausmachen, damit es überhaupt
    #: einen erkennbaren leeren Rand gibt. Darunter ist die Prüfung BLIND
    #: (eine flächig gefüllte Haarkarte) und meldet nichts — lieber kein
    #: Befund als ein falscher (`~/.claude/rules/analysewerkzeuge.md`).
    MINDEST_RAND = 0.03

    #: Und so viel der Flächen muss betroffen sein, damit ein Verdacht
    #: ausgesprochen wird. Einzelne Ausreißer sagen nichts.
    MINDEST_ANTEIL = 0.02

    #: Für die Randfarbe wird nur eine Stichprobe gezählt — bei 4096er Karten
    #: wären es 16 Mio. Bildpunkte. Die Schrittweite richtet sich nach der
    #: Bildgröße, damit ungefähr so viele Punkte übrig bleiben; bei einer
    #: kleinen Karte wird JEDER Punkt gezählt. (Eine feste Schrittweite von 8
    #: ließ von einem 16x16-Testbild ganze vier Punkte übrig — dann ist die
    #: „häufigste Farbe" bedeutungslos.)
    ZIELKANTE = 512

    def __init__(self, obj_pfad):
        self.obj = Path(obj_pfad)
        self.ordner = self.obj.parent
        self.karten = self._karten()

    # ------------------------------------------------------------------ lesen

    def _karten(self):
        u"""Material -> Dateiname der Farbkarte, aus der `.mtl` daneben."""
        mtl = self.obj.with_suffix('.mtl')
        if not mtl.exists():
            return {}
        aus, name = {}, None
        for zeile in mtl.read_text(encoding='utf-8', errors='replace').splitlines():
            if zeile.startswith('newmtl '):
                name = zeile.split(None, 1)[1].strip()
            elif zeile.startswith('map_Kd ') and name:
                aus[name] = zeile.split(None, 1)[1].strip()
        return aus

    def _lesen(self):
        u"""UV-Liste und je Material die Flächen (als UV-Nummern-Tripel)."""
        uvs = []
        flaechen = defaultdict(list)
        material = None
        with self.obj.open('r', encoding='utf-8', errors='replace') as f:
            for zeile in f:
                kopf = zeile[:2]
                if kopf == 'vt':
                    teile = zeile.split()
                    uvs.append((float(teile[1]), float(teile[2])))
                elif kopf == 'f ':
                    if material not in self.karten:
                        continue
                    ecken = [t.split('/') for t in zeile.split()[1:4]]
                    if len(ecken) < 3 or not all(len(e) > 1 and e[1] for e in ecken):
                        continue
                    flaechen[material].append(tuple(int(e[1]) for e in ecken))
                elif zeile.startswith('usemtl '):
                    material = zeile.split(None, 1)[1].strip()
        return uvs, flaechen

    # ------------------------------------------------------------------ prüfen

    def bericht(self):
        u"""
        Je Material ein Eintrag:
        `{flaechen, leer, leer_gespiegelt, anteil, rand_im_bild, karte, groesse}`.
        Dazu `gesamt` und `verdacht_gespiegelt` (Liste der Materialien, bei
        denen die Gegenrichtung deutlich besser abschneidet).
        """
        import numpy as np
        from PIL import Image

        uvs, flaechen = self._lesen()
        if not uvs or not flaechen:
            return {'material': {}, 'gesamt': {'flaechen': 0, 'leer': 0},
                    'verdacht_gespiegelt': [], 'hinweis': 'keine Flächen mit Farbkarte'}
        uvs = np.asarray(uvs, dtype=np.float32)

        je_material = {}
        verdacht = []
        summe_f = summe_l = 0
        for material, liste in sorted(flaechen.items()):
            pfad = self.ordner / self.karten[material]
            if not pfad.exists():
                je_material[material] = {'fehlt': self.karten[material]}
                continue
            bild = Image.open(pfad).convert('RGB')
            feld = np.asarray(bild, dtype=np.int16)
            hoehe, breite = feld.shape[:2]
            rand, rand_anteil = self._randfarbe(feld)

            f = np.asarray(liste, dtype=np.int64) - 1
            u = uvs[f, 0].mean(axis=1) % 1.0
            v = uvs[f, 1].mean(axis=1) % 1.0
            px = np.clip(u * (breite - 1), 0, breite - 1).astype(np.int32)
            gerade = np.clip((1.0 - v) * (hoehe - 1), 0, hoehe - 1).astype(np.int32)
            gedreht = np.clip(v * (hoehe - 1), 0, hoehe - 1).astype(np.int32)
            leer = self._leere(feld, px, gerade, rand)
            leer_gespiegelt = self._leere(feld, px, gedreht, rand)
            anzahl = len(f)
            je_material[material] = {
                'flaechen': anzahl, 'leer': leer, 'leer_gespiegelt': leer_gespiegelt,
                'anteil': leer / anzahl if anzahl else 0.0,
                'rand_im_bild': rand_anteil, 'karte': self.karten[material],
                'groesse': [breite, hoehe],
            }
            # Nur melden, wenn die Karte überhaupt einen erkennbaren leeren
            # Rand hat (sonst ist die Messung blind), genug Flächen betroffen
            # sind, und die Gegenrichtung DEUTLICH besser abschneidet.
            blind = rand_anteil < self.MINDEST_RAND
            genug = anzahl and leer / anzahl >= self.MINDEST_ANTEIL
            if not blind and genug and leer_gespiegelt * self.FAKTOR < leer:
                verdacht.append(material)
            summe_f += anzahl
            summe_l += leer

        return {
            'material': je_material,
            'gesamt': {'flaechen': summe_f, 'leer': summe_l,
                       'anteil': summe_l / summe_f if summe_f else 0.0},
            'verdacht_gespiegelt': verdacht,
        }

    def _randfarbe(self, feld):
        u"""Die Farbe des leeren Kartenrands und ihr Anteil am Bild.

        NICHT der Bildpunkt (0, 0) — daran ist die erste Fassung gescheitert:
        berührt eine UV-Insel die Ecke, gilt plötzlich HAUT als „leer" und
        jede Hautfläche wird gemeldet (im Testfall: 2 von 2). Der leere Rand
        ist stattdessen die HÄUFIGSTE Farbe der Karte — er ist flach, während
        echte Bildinhalte rauschen. Gezählt wird eine Stichprobe.
        """
        import numpy as np
        schritt = max(1, min(feld.shape[0], feld.shape[1]) // self.ZIELKANTE)
        probe = feld[::schritt, ::schritt].reshape(-1, 3).astype(np.int32)
        schluessel = (probe[:, 0] << 16) | (probe[:, 1] << 8) | probe[:, 2]
        werte, anzahl = np.unique(schluessel, return_counts=True)
        haeufigste = int(werte[int(anzahl.argmax())])
        anteil = float(anzahl.max() / len(schluessel))
        farbe = np.array([(haeufigste >> 16) & 255, (haeufigste >> 8) & 255, haeufigste & 255],
                         dtype=np.int16)
        return farbe, anteil

    def _leere(self, feld, px, py, rand):
        u"""Wie viele der abgetasteten Punkte liegen auf dem leeren Rand?"""
        import numpy as np
        return int((np.abs(feld[py, px] - rand).max(axis=1) <= self.ABSTAND).sum())

    @staticmethod
    def zeilen(bericht):
        u"""Den Bericht als Textzeilen — für Protokoll und Kommandozeile."""
        aus = []
        for name, e in sorted(bericht['material'].items()):
            if 'fehlt' in e:
                aus.append(f'{name:<10} KARTE FEHLT: {e["fehlt"]}')
                continue
            aus.append(f'{name:<10} {e["flaechen"]:>9,} Flächen  leer {e["leer"]:>8,} '
                       f'({100 * e["anteil"]:>5.1f} %)  gespiegelt {e["leer_gespiegelt"]:>8,}  '
                       f'Rand im Bild {100 * e["rand_im_bild"]:>4.1f} %  {e["karte"]}')
        g = bericht['gesamt']
        aus.append(f'SUMME: {g["leer"]:,} von {g["flaechen"]:,} Flächen ohne Farbe '
                   f'({100 * g["anteil"]:.1f} %)')
        if bericht['verdacht_gespiegelt']:
            aus.append('KARTE STEHT AUF DEM KOPF: ' + ', '.join(bericht['verdacht_gespiegelt']))
        return aus
