# -*- coding: utf-8 -*-
u"""Die angezogene HumanBody-Figur in Bewegung — ein Video.

WARUM (Edgar, 10.09.2026): „ich will funktionierende Animation von mir, die
auch die Kleider animieren, keine Zombie Videos wo die Kleider entweder
nicht vorhanden sind oder nach und nach verschwinden."

DREI GEMESSENE URSACHEN DER FRUEHEREN VIDEOS, alle hier behoben:

1. ZWEI QUELLEN FUER EINE BEWEGUNG. Der Koerper kam aus einem FPS-Bake,
   der Stoff aus einer eigenen LBS-Rechnung. Jetzt lesen beide dieselben
   Matrizen aus `Skelettbahn` — sie KOENNEN nicht mehr auseinanderlaufen.

2. HALBES SKELETT. Das Stoff-Rig verweist auf alle 176 Knochen, gerechnet
   wurde mit 69. Bei 3.670 von 7.290 Stoffpunkten verschwand damit ein
   Teil des Gewichts, LBS verteilte den Rest stumm um — das waren die
   Fetzen. `Hautbahn` bricht jetzt ab, statt still umzuverteilen.

3. SECHSFACHE ZEITLUPE. Die BVH laeuft mit 120 Bildern je Sekunde; jedes
   Bild einzeln in ein 20-fps-Video geschrieben laesst die Figur
   stillstehen (gemessen: Fuss 24 mm statt 2.251 mm Spanne).

Aufruf:  python hbfilm.py [--bilder 120] [--schritt 5]
"""
import argparse
import os
import sys

import numpy as np

from feinkoerper import Feinkoerper
from figurnetze import Figurnetze
from filmmasken import Filmmasken
from filmphysik import Filmphysik
from filmrender import Filmrender
from hautbahn import Hautbahn
from skelettbahn import Skelettbahn

ORDNER = os.path.dirname(os.path.abspath(__file__))
AUSGABE = os.path.join('A:', os.sep, '3DTools', 'Assets', 'GarmentCode',
                       'ausgabe')
#: GEMESSEN AUSGEWAEHLT, nicht nach dem Dateinamen (`gangwahl.py`, 215
#: Kandidaten an der BVH-Quelle bewertet): Rumpfschwankung 2,2 Grad,
#: Zehen 11 Grad zur Laufrichtung, 4,3 Koerperlaengen Vortrieb, Becken
#: driftet nicht. `01_01.bvh` im selben Ordner ist trotz seines Namens
#: keine Gehbewegung (48 cm Beckenhub), und `136_12.bvh` geht rueckwaerts
#: (Zehen 170 Grad gegen die Bewegung) und ist 45 Grad vorgebeugt.
BVH = os.path.join('A:', os.sep, '3DTools', '3DObjects', 'animations', 'bvh',
                   'Walk', '136_28.bvh')
AB_BILD = 278
#: Die GEMEINSAME Drapierung: beide Stuecke in EINEM Lauf simuliert, also
#: ohne dass der Hosenbund durch das T-Shirt steht (CLAUDE.md, 09.09.2026).
STUECKE = [
    ('T-Shirt', 'gemeinsam_female_56958c9b_t-shirt', (0.29, 0.44, 0.72)),
    ('Hose', 'gemeinsam_female_56958c9b_hose', (0.25, 0.27, 0.33)),
]


class Hbfilm:
    u"""Koerper und Kleider durch dieselbe Rechnung, dann ins Bild."""

    HAUT = (0.87, 0.78, 0.70)

    def __init__(self, bvh=BVH, bilder=120, ziel_fps=24.0, ab=AB_BILD,
                 stuecke=None, physik=0.0, geschlecht='female',
                 figurpunkte=None, melder=None, ab_sekunden=None,
                 figurfein=None):
        u"""`figurpunkte` sind ALLE Basispunkte der Figur (mit Morphs);
        ohne sie kommt die unverformte Grundfigur. `figurfein` =
        (Unterteiler, Basisflaechen): Dann laufen LBS und Physik auf ALLEN
        Basispunkten und der Film rendert das unterteilte Netz der Szene
        (`Feinkoerper`); ohne bleibt es bei der 18K-Aussenhaut. `melder(phase,
        anteil)` bekommt den Fortschritt — der Videoweg im UI zeigt ihn an."""
        from bvh_nach_anim import Animschreiber
        from figur_nach_cody import Codyfigur

        self.melder = melder or (lambda phase, anteil: None)
        self.melder(u'Figur laden', 0.0)
        figur = Codyfigur(geschlecht, mit_fingern=True)
        alle = None
        if figurpunkte is not None:
            # Die Morphs verschieben Punkte, nicht die Topologie: Dieselben
            # Aussenhaut-Indizes, dieselben Dreiecke, dieselben Gewichte.
            alle = np.asarray(figurpunkte, dtype=np.float64)
            figur.punkte = alle[figur.gewaehlt]
        self.melder(u'Bewegung laden', 0.05)
        daten = Animschreiber('hb_' + geschlecht).spuren(bvh)
        if ab_sekunden is not None:
            # Aus der Szene kommt eine ZEIT, nicht eine Bildnummer — die
            # Bildrate der Quelle kennt erst die Skelettbahn.
            ab = max(1, int(round(ab_sekunden * Skelettbahn._bildrate(daten))))
        self.bahn = Skelettbahn(figur, daten, bilder, ziel_fps, ab)
        self.ziel_fps = ziel_fps
        # Die Zeit je AUSGABEBILD, nicht je Quellbild: Die Geschwindigkeit
        # muss zu den Bildern passen, die im Video aufeinanderfolgen.
        self.bildzeit = self.bahn.schritt / self.bahn.quell_fps
        self.physik = float(physik)
        self.netze = Figurnetze(figur)
        self.teile = []
        self._koerper(figurfein if alle is not None else None, alle)
        for eintrag in (stuecke if stuecke is not None else STUECKE):
            if isinstance(eintrag, dict):
                self._stueck(eintrag['name'], eintrag.get('pfad'),
                             tuple(eintrag.get('farbe') or (0.3, 0.45, 0.7)))
            else:
                name, ordner, farbe = eintrag
                self._stueck(name, os.path.join(
                    AUSGABE, ordner, ordner + '_sim_rig.json'), farbe)
        # Haut unter Stoff und Stoff unter Stoff werden nicht gerendert —
        # in Ruhelage entschieden, wie in der Szene.
        Filmmasken.anwenden(self.teile, self.melder)

    def _koerper(self, fein=None, alle=None):
        teil = {'name': u'Koerper', 'farbe': self.HAUT}
        if fein is not None:
            unterteiler, vierecke = fein
            punkte, dreiecke, gewichte = self.netze.koerper_basis(alle, vierecke)
            teil['unterteiler'] = unterteiler
            teil['fein_dreiecke'] = np.asarray(unterteiler.triangles, dtype=np.int64)
        else:
            punkte, dreiecke, gewichte = self.netze.koerper()
        teil['haut'] = Hautbahn(punkte, gewichte, self.netze.namen, self.bahn)
        teil['dreiecke'] = dreiecke
        self.teile.append(teil)

    def _stueck(self, name, pfad, farbe):
        if not pfad or not os.path.exists(pfad):
            print(u'FEHLT: %s' % pfad)
            return
        punkte, dreiecke, gewichte = self.netze.stueck(pfad)
        haut = Hautbahn(punkte, gewichte, self.netze.namen, self.bahn)
        self.teile.append({'name': name, 'haut': haut, 'dreiecke': dreiecke,
                           'farbe': farbe,
                           'sitz': Figurnetze.sitzprobe(
                               punkte, Feinkoerper.ruhe(self.teile[0]))})

    # -------------------------------------------------------------- Proben

    def proben(self):
        u"""Ruheprobe je Teil — muss null sein, sonst stimmt die Lage nicht."""
        zeilen = []
        for teil in self.teile:
            zeilen.append((teil['name'], len(teil['haut'].punkte),
                           teil['haut'].ruheprobe() * 1000.0,
                           teil.get('sitz'),
                           teil['haut'].ohne_gewicht))
        return zeilen

    def rechnen(self):
        for nummer, teil in enumerate(self.teile):
            self.melder(u'Bewegung: %s' % teil['name'],
                        0.1 + 0.2 * nummer / max(len(self.teile), 1))
            teil['haut'].rechnen()
        if self.physik > 0.0:
            Filmphysik(self.teile, self.bahn, self.bildzeit, self.physik,
                       self.melder).anwenden()

    def gleichlauf(self):
        u"""DIE ENTSCHEIDENDE PROBE: Bleibt der Stoff beim Koerper?

        Gemessen wird der Abstand Stoff-zu-Haut je Bild. Bleibt er wie in
        Bild 0, folgt die Kleidung. Waechst er, loest sie sich ab — genau
        das, was in den frueheren Videos zu sehen war, und was eine
        Gesamt-Bewegungszahl nicht zeigt.
        """
        from scipy.spatial import cKDTree
        zahl = len(self.teile[0]['haut'].folge)
        aus = []
        for teil in self.teile[1:]:
            werte = []
            for nummer in (0, zahl // 2, zahl - 1):
                # Gegen das SICHTBARE Netz — dort liegt der Stoff an.
                baum = cKDTree(Feinkoerper.bild(self.teile[0], nummer))
                abstand, _ = baum.query(teil['haut'].folge[nummer], workers=-1)
                werte.append(float(np.median(abstand)) * 1000.0)
            aus.append((teil['name'], werte))
        return aus

    # -------------------------------------------------------------- Ausgabe

    def bilder_rendern(self, breite=720, hoehe=900):
        return Filmrender(self.teile, self.bahn,
                          self.melder).bilder_rendern(breite, hoehe)

    def schreiben(self, ziel, fps=24.0, schleifen=2):
        return Filmrender(self.teile, self.bahn,
                          self.melder).schreiben(ziel, fps, schleifen)


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--bvh', default=BVH)
    zerleger.add_argument('--bilder', type=int, default=120)
    zerleger.add_argument('--fps', type=float, default=24.0)
    zerleger.add_argument('--physik', type=float, default=0.0,
                          help=u'Hoechster Weichgewebe-Zuschlag in mm, '
                               u'0 = aus')
    zerleger.add_argument('--ab', type=int, default=AB_BILD)
    zerleger.add_argument('--aus', default=os.path.join(
        r'A:\3DTools\Docu\KörperPhysik', 'hb_angezogen_gehen.mp4'))
    werte = zerleger.parse_args()

    film = Hbfilm(werte.bvh, werte.bilder, werte.fps, werte.ab,
                  physik=werte.physik)
    print(u'Bewegung  %s, %d Bilder ab %d'
          % (os.path.basename(werte.bvh), werte.bilder, werte.ab))
    print(u'          Quelle %.0f fps, Video %.0f fps, Zeitschritt %d'
          % (film.bahn.quell_fps, werte.fps, film.bahn.schritt))
    print(u'          Wurzelweg %.2f m, Fuss-Spanne %.0f mm'
          % (film.bahn.wurzelweg(),
             (film.bahn.knochenspanne('DEF-foot.L') or 0) * 1000))
    print(u'\n%-10s %8s %14s %10s %8s'
          % (u'Teil', u'Punkte', u'RUHEPROBE', u'Sitz', u'ohne W.'))
    for name, punkte, ruhe, sitz, leer in film.proben():
        print(u'%-10s %8d %11.6f mm %7s %8d'
              % (name, punkte, ruhe,
                 u'%.0f mm' % sitz if sitz is not None else u'-', leer))

    film.rechnen()
    for name, werte_bahn in film.gleichlauf():
        print(u'\nGLEICHLAUF %s: Abstand zur Haut  Bild 0 %.0f mm, '
              u'Mitte %.0f mm, Ende %.0f mm'
              % (name, werte_bahn[0], werte_bahn[1], werte_bahn[2]))
    for teil in film.teile:
        mittel, groesster = teil['haut'].bewegung()
        print(u'%-10s bewegt sich im Mittel %.0f mm, groesster Weg %.0f mm'
              % (teil['name'], mittel * 1000, groesster * 1000))

    for teil in film.teile:
        b = teil.get('physik')
        if not b:
            continue
        print(u'PHYSIK %-8s Ziel %.0f mm -> Staerke %.4f, erreicht %.1f mm '
              u'(Mittel %.1f, Bild 0 %.2f)'
              % (teil['name'], b['ziel_mm'], b['staerke'], b['groesster_mm'],
                 b['mittlerer_mm'], b['erstes_bild_mm']))
        print(u'       Weichheit Median %.2f, Knochen je Punkt %.1f '
              u'(hoechstens %d), Tempo bis %.2f m/s und %.2f rad/s'
              % (b['weichheit_median'], b['ahnen_je_punkt'][0],
                 b['ahnen_je_punkt'][1], b['tempo_spitze'][0],
                 b['tempo_spitze'][1]))
        if 'durchstich' in b:
            print(u'       STOFF IM KOERPER %.2f %% (ohne Grenze waeren es '
                  u'%.2f %%), %d Punkte gekuerzt'
                  % (b['durchstich'], b['durchstich_ohne_grenze'],
                     b['gekuerzt']))
    pfad, zahl = film.schreiben(werte.aus, fps=werte.fps)
    print(u'\nVideo     %s (%d Bilder, %.1f KB)'
          % (pfad, zahl, os.path.getsize(pfad) / 1024.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
