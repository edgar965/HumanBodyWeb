# -*- coding: utf-8 -*-
"""BvhDatei — eine BVH-Datei lesen, bearbeiten, zurueckschreiben.

WARUM (Umbau 15.08.2026): `smooth_bvh` (149 Zeilen) und `save_bvh_effects`
(151 Zeilen) waren zu neun Zehnteln DIESELBE Funktion — Kanalordnung aus dem
Kopf lesen, Bewegungsdaten finden, Quaternionen glaetten, alles als Euler
zurueckschreiben, den Retarget-Zwischenspeicher leeren. Zweimal derselbe Code
heisst: zwei Stellen, an denen dieselbe Korrektur gemacht werden muss. Am
13.08.2026 fiel genau das auf, als eine Pfadluecke in BEIDEN Funktionen
geschlossen werden musste.

Die Glaettung laeuft jetzt ueber die ganze Achse statt in verschachtelten
Schleifen — dazu steht die Messung bei `glaetten`.
"""
import logging

import numpy as np

logger = logging.getLogger('core')


class BvhDatei:
    """Bewegungsdaten einer BVH-Datei, bearbeitbar und speicherbar."""

    #: BVH-Positionen stehen in Zentimetern, die Oberflaeche rechnet in Metern.
    CM_JE_METER = 100.0

    def __init__(self, pfad):
        self.pfad = pfad
        from humanbody_core.skeleton.retarget import parse_bvh
        self.bvh = parse_bvh(str(pfad))
        self.angewandt = []

    @property
    def frames(self):
        return self.bvh.frame_count

    @property
    def gelenke(self):
        return len(self.bvh.names)

    # ---------------------------------------------------------------- glaetten

    def glaetten(self, sigma):
        """Gauss-Glaettung auf Quaternionen und Wurzelpositionen.

        Geglaettet wird ueber QUATERNIONEN, nicht ueber Eulerwinkel: Die
        springen bei jedem Umlauf um 360 Grad, und die Glaettung zoege die
        Bewegung durch den Sprung hindurch.

        Vektorisiert (Umbau 15.08.2026): Vorher lief `gaussian_filter1d` in zwei
        verschachtelten Schleifen — je Gelenk und je Komponente, bei 176 Gelenken
        also 704 Aufrufe je Datei. `axis=0` macht dasselbe in einem Aufruf."""
        from scipy.ndimage import gaussian_filter1d
        sigma = float(sigma)
        if sigma <= 0:
            return self
        self._vorzeichen_angleichen()
        self.bvh.quats = gaussian_filter1d(self.bvh.quats, sigma=sigma, axis=0)
        laengen = np.linalg.norm(self.bvh.quats, axis=2, keepdims=True)
        laengen[laengen < 1e-8] = 1.0
        self.bvh.quats /= laengen
        # Nur Kanaele glaetten, in denen ueberhaupt etwas steht — sonst wandert
        # eine konstante Null durch den Filter und bleibt Null (harmlos), kostet
        # aber Zeit.
        belegt = np.any(self.bvh.positions != 0, axis=0)
        for ji, gelenk in enumerate(belegt):
            for c, hat_werte in enumerate(gelenk):
                if hat_werte:
                    self.bvh.positions[:, ji, c] = gaussian_filter1d(
                        self.bvh.positions[:, ji, c], sigma=sigma)
        self.angewandt.append('smooth sigma=%s' % sigma)
        return self

    def _vorzeichen_angleichen(self):
        """Aufeinanderfolgende Quaternionen auf dieselbe Halbkugel bringen.

        q und -q beschreiben dieselbe Drehung; ein Vorzeichenwechsel zwischen
        zwei Frames waere fuer den Filter ein Sprung ueber die halbe Kugel."""
        q = self.bvh.quats
        for f in range(1, len(q)):
            falsch = np.einsum('ij,ij->i', q[f], q[f - 1]) < 0
            q[f][falsch] = -q[f][falsch]

    # ------------------------------------------------------- Wurzel festhalten

    def wurzel_festhalten(self, radius_m):
        """Die Wurzel innerhalb eines Kreises halten (X/Z, in Metern)."""
        radius = float(radius_m) * self.CM_JE_METER
        if radius <= 0:
            return self
        p = self.bvh.positions
        anker_x, anker_z = p[0, 0, 0], p[0, 0, 2]
        dx = p[:, 0, 0] - anker_x
        dz = p[:, 0, 2] - anker_z
        abstand = np.sqrt(dx * dx + dz * dz)
        zu_weit = abstand > radius
        if np.any(zu_weit):
            faktor = radius / abstand[zu_weit]
            p[zu_weit, 0, 0] = anker_x + dx[zu_weit] * faktor
            p[zu_weit, 0, 2] = anker_z + dz[zu_weit] * faktor
        self.angewandt.append('fixed r=%.2fm' % float(radius_m))
        return self

    # --------------------------------------------------------------- speichern

    #: BVH-Kanalnamen auf Achsen. Grossbuchstaben, weil `parse_bvh` die
    #: Reihenfolge als intrinsische Drehfolge liest.
    ACHSEN = {'xrotation': 'X', 'yrotation': 'Y', 'zrotation': 'Z'}
    VORGABE_ORDNUNG = 'ZYX'

    def speichern(self):
        """Bewegungsdaten in die Datei zurueckschreiben (Euler, wie im Kopf)."""
        from scipy.spatial.transform import Rotation
        zeilen = self.pfad.read_text(encoding='utf-8').split('\n')
        ordnungen = self._kanalordnungen(zeilen)
        frame_zeilen = self._frame_zeilen(zeilen)

        for fi in range(min(self.frames, len(frame_zeilen))):
            werte = zeilen[frame_zeilen[fi]].strip().split()
            self._frame_schreiben(Rotation, werte, fi, ordnungen)
            zeilen[frame_zeilen[fi]] = ' '.join(werte)

        with open(str(self.pfad), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(zeilen))
        self.zwischenspeicher_leeren()
        return self.frames

    def _frame_schreiben(self, Rotation, werte, fi, ordnungen):
        stelle = 0
        for ji in range(min(self.gelenke, len(ordnungen))):
            kanaele, ordnung = ordnungen[ji]
            if kanaele >= 6:
                for k in range(3):
                    werte[stelle + k] = '%.6f' % self.bvh.positions[fi, ji, k]
                stelle_rot = stelle + 3
            else:
                stelle_rot = stelle
            euler = Rotation.from_quat(self.bvh.quats[fi, ji]).as_euler(
                ordnung, degrees=True)
            for k in range(3):
                werte[stelle_rot + k] = '%.6f' % euler[k]
            stelle += kanaele if kanaele >= 6 else 3

    @classmethod
    def _kanalordnungen(cls, zeilen):
        """[(Kanalzahl, Drehfolge)] je Gelenk, aus dem Dateikopf."""
        raus = []
        for zeile in zeilen:
            s = zeile.strip()
            if not s.startswith('CHANNELS'):
                continue
            teile = s.split()
            folge = ''.join(cls.ACHSEN[p.lower()] for p in teile[2:]
                            if p.lower() in cls.ACHSEN)
            raus.append((int(teile[1]), folge or cls.VORGABE_ORDNUNG))
        return raus

    @staticmethod
    def _frame_zeilen(zeilen):
        """Zeilennummern der Bewegungsdaten (alles nach MOTION, was mit einer
        Zahl beginnt)."""
        beginn = next(i for i, z in enumerate(zeilen) if z.strip() == 'MOTION')
        raus = []
        for i in range(beginn + 1, len(zeilen)):
            s = zeilen[i].strip()
            if s and (s[0].isdigit() or s[0] == '-'):
                raus.append(i)
        return raus

    def zwischenspeicher_leeren(self):
        """Retarget-Ergebnisse zu dieser Datei verwerfen — sie sind veraltet."""
        stamm = self.pfad.stem
        for datei in self.pfad.parent.glob('%s_retarget_*.json' % stamm):
            try:
                datei.unlink()
            except OSError as e:
                logger.debug('Zwischenspeicher %s bleibt liegen: %s', datei, e)
