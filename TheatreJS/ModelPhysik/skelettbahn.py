# -*- coding: utf-8 -*-
u"""Die Weltlage JEDES Knochens, Bild fuer Bild — eine einzige Quelle.

WARUM DIESE DATEI (Edgar, 10.09.2026: „ich will funktionierende Animation
von mir, die auch die Kleider animieren, keine Zombie Videos wo die Kleider
entweder nicht vorhanden sind oder nach und nach verschwinden"):

Bisher kam der Koerper aus einem FPS-Bake und der Stoff aus einer eigenen
LBS-Rechnung. Zwei Quellen fuer dieselbe Bewegung laufen auseinander, und
im Bild sieht das aus, als loese sich die Kleidung auf. Hier entsteht die
Bewegung EINMAL; Koerper und Stoff lesen dieselben Matrizen.

ZWEI GEMESSENE FEHLER STECKEN IN DIESER KLASSE, beide vom 10.09.2026:

1. ALLE 176 KNOCHEN, nicht die Auswahl von 31 oder 69. Das Stoff-Rig
   verweist auf alle 176 Knochen des `def_skeleton`. Wer nur die Auswahl
   aufloest, verliert bei 3.670 von 7.290 Stoffpunkten (50,3 %) einen Teil
   des Gewichts — LBS renormiert den Rest stumm, und der Punkt wandert mit
   dem falschen Knochen davon. Kein Fehler, keine Meldung, nur Fetzen.

2. DIE ZEITSCHRITTWEITE DER QUELLE. Die CMU-Dateien laufen mit 120 Bildern
   je Sekunde. Jedes Bild einzeln in ein 20-fps-Video geschrieben ist
   SECHSFACHE ZEITLUPE — gemessen legt der Fuss in 120 Bildern dann 24 mm
   zurueck statt 2.251 mm, und die Figur sieht aus, als stuende sie still.
"""
import numpy as np


class Skelettbahn:
    u"""Weltmatrizen aller Knochen je Bild, aus einer Retargetspur."""

    #: Bild 0 des Retargets ist ein Startzustand, kein Bewegungsbild.
    ERSTES_BILD = 1

    def __init__(self, figur, daten, bilder=120, ziel_fps=24.0, ab=1):
        self.knochen = figur.knochen
        self.namen = list(figur.knochen.keys())
        self.spuren = daten.tracks
        self.quell_fps = self._bildrate(daten)
        # DER ZEITSCHRITT GEHOERT ZUR DATEI, nicht zum Aufruf. CMU laeuft
        # mit 120 Bildern je Sekunde, Mixamo mit 30. Ein fester Schritt
        # zeigt das eine in Zeitlupe (gemessen: Fuss 24 mm statt 2.251 mm
        # Spanne) und das andere im Zeitraffer.
        self.schritt = max(1, int(round(self.quell_fps / ziel_fps)))
        self.folge = [max(ab, self.ERSTES_BILD) + i * self.schritt
                      for i in range(bilder)]
        letztes = daten.frame_count - 1
        if self.folge[-1] > letztes:
            # Abgeschnitten wird am ANFANG, nicht am Ende: Sonst
            # wiederholt sich das letzte Bild, und die Figur bleibt in
            # den letzten Sekunden stehen.
            self.folge = [n - (self.folge[-1] - letztes) for n in self.folge]
        self.folge = [max(self.ERSTES_BILD, min(n, letztes))
                      for n in self.folge]
        self.orte = self.wurzelbahn(daten)
        self.ruhe = self._welt(None, 0, None)
        self.ruhe_um = self._umkehrungen(self.ruhe)
        self.lagen = [self._bild(n) for n in self.folge]

    # -------------------------------------------------------------- Eingabe

    @staticmethod
    def _bildrate(daten):
        u"""Bilder je Sekunde der Quelle, aus Bildzahl und Dauer.

        Die Retargetdaten fuehren keine `frame_time`, aber `duration` —
        gemessen an `136_28.bvh`: 1.115 Bilder in 9,29 s = 120,0 fps.
        """
        dauer = float(getattr(daten, 'duration', 0.0) or 0.0)
        if dauer <= 0.0:
            return 30.0
        return float(daten.frame_count) / dauer

    @staticmethod
    def wurzelbahn(daten):
        u"""Die Ortsbewegung der Wurzel, in der Lage des Rigs — `None` ohne Spur.

        Die Spur kommt in Three.js-Lage (y oben), das Rig steht in
        Blender-Lage (z oben): (x, y, z) -> (x, -z, y). Ohne diese Zeile
        laeuft die Figur in die Tiefe statt nach vorn.
        """
        if not daten.position_track:
            return None
        roh = np.asarray(daten.position_track['values'],
                         dtype=np.float64).reshape(-1, 3)
        return np.column_stack([roh[:, 0], -roh[:, 2], roh[:, 1]])

    def _bild(self, nummer):
        ort = None
        if self.orte is not None:
            ort = self.orte[nummer] - self.orte[self.folge[0]]
        return self._welt(self.spuren, nummer, ort)

    # -------------------------------------------------------------- Skelett

    def _welt(self, spuren, nummer, ort):
        u"""(position, weltdrehung) je Knochen — Ruhe oder eine Pose."""
        from anim_umsetzung import Animumsetzung
        from figur_nach_cody import Codyfigur
        welt = {}

        def loesen(name):
            if name in welt:
                return welt[name]
            knochen = self.knochen[name]
            spur = (spuren or {}).get(name)
            if spur is not None and nummer * 4 + 4 <= len(spur):
                lokal = Codyfigur.nach_blender(
                    np.asarray(spur[nummer * 4:nummer * 4 + 4],
                               dtype=np.float64))
            else:
                lokal = Animumsetzung._wxyz(knochen['local_quaternion'])
            versatz = np.asarray(knochen['local_position'], dtype=np.float64)
            elternteil = knochen.get('parent')
            if not elternteil or elternteil not in self.knochen:
                # Die Wurzel sitzt NICHT im Ursprung: `DEF-spine` steht bei
                # z = 0,81.
                if ort is not None:
                    versatz = versatz + np.asarray(ort, dtype=np.float64)
                welt[name] = (versatz, lokal)
            else:
                ep, eq = loesen(elternteil)
                welt[name] = (ep + Animumsetzung.drehen(eq, versatz),
                              Animumsetzung.mul(eq, lokal))
            return welt[name]

        for name in self.namen:
            loesen(name)
        return welt

    @staticmethod
    def dreh(quat):
        u"""3 x 3 aus einer Drehung."""
        from anim_umsetzung import Animumsetzung
        return np.column_stack([Animumsetzung.drehen(quat, e)
                                for e in np.eye(3)])

    def _umkehrungen(self, ruhe):
        u"""Die Umkehrung der Ruhelage je Knochen.

        Ohne sie waere LBS kein Verformen, sondern ein Versetzen in den
        Weltursprung: Jeder Punkt bekaeme die Weltlage seines Knochens
        aufaddiert, statt seine Lage RELATIV zur Ruhe zu behalten.
        """
        aus = {}
        for name, (punkt, quat) in ruhe.items():
            d = self.dreh(quat)
            aus[name] = (d.T, -d.T @ np.asarray(punkt))
        return aus

    # ---------------------------------------------------------------- Masse

    def wurzelweg(self):
        u"""Wie weit die Figur ueber die Bildfolge laeuft, in Metern."""
        if self.orte is None:
            return 0.0
        return float(np.linalg.norm(self.orte[self.folge[-1]]
                                    - self.orte[self.folge[0]]))

    def knochenspanne(self, name):
        u"""Groesste Ausdehnung der Bahn eines Knochens, in Metern."""
        if name not in self.ruhe:
            return None
        p = np.array([lage[name][0] for lage in self.lagen])
        return float(np.linalg.norm(p.max(axis=0) - p.min(axis=0)))
