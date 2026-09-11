# -*- coding: utf-8 -*-
u"""HumanBody-Figur -> Eingabedateien fuer FastProjectiveSkinning.

WARUM (Edgar, 10.09.2026: „ich nutze das HumanBody Modell, dafuer brauche ich
das!"): FastProjectiveSkinning (Komaritzan/Botsch, MIG 2019) rechnet aus einem
Hautnetz und einem eingebetteten Skelett eine Volumenschicht — Muskel und Fett —
und simuliert sie. Es braucht genau zwei Dateien, beide Text:

    .off    das Hautnetz (Dreiecke)
    .skel   [Zahl der Gelenke] / je Zeile: x y z name elternname

KEINE Hautgewichte, kein Tetraedernetz. Hier wird NUR umgeformt, nichts
gerechnet — das Verfahren steckt im fremden Code.

DREI DINGE, DIE HIER ENTSCHIEDEN WERDEN
=======================================

1. **Was Haut ist.** Das Netz fuehrt 11 Materialien; Zaehne (3.422 Flaechen),
   Augen (1.256), Zunge und Wimpern liegen INNERHALB des Kopfes. Als
   Kollisionskoerper waeren sie Unsinn — dieselbe Falle wie am 07.09.2026 bei
   GarmentCode, wo `face_internal` fehlte und 6.213 Punkte zu
   Kollisionsgeometrie wurden. Genommen werden Haut, Censor und Naegel.

2. **Welche Knochen.** Von den 176 Deform-Knochen sind 49 Gesichtsknochen und
   viele Finger; in einem Weichgewebs-Kollider haben sie nichts zu suchen.
   Genommen wird die Hauptkette: Wirbelsaeule, Arme, Beine (KETTE).
   Blaetter (Hand, Fuss, Kopf) bekommen ihr Endgelenk aus dem `tail` des
   Knochens — ein Gelenk allein bildet kein Segment.

3. **Der Massstab.** FPS' eigenes Beispiel `male` ist 20,86 Einheiten hoch, wir
   sind 1,70 m. Die Voreinstellungen der Simulation (Schwerkraft, Steifigkeit)
   haengen an der Skala, deshalb wird auf DESSEN Hoehe skaliert statt auf Meter.

Aufruf:  python figur_nach_fps.py [--geschlecht female|male]
"""
import argparse
import json
import os
import sys

import numpy as np

WURZELN = {
    'female': r'A:\3DTools\HumanBody\data\humanBody',
    'male': r'A:\3DTools\HumanBody\data\humanBody_male',
}
ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figur')

#: Materialien, die zur AUSSENhaut gehoeren. Alles andere steckt im Kopf.
HAUT = ('HB_Skin', 'HB_Censor', 'HB_Nails_Hand', 'HB_Nails_Feet')

#: Die Kette, die das Weichgewebe treiben soll. Reihenfolge egal, die
#: Elternschaft kommt aus `rig_bones.json`.
KETTE = (
    'DEF-spine', 'DEF-spine.001', 'DEF-spine.002', 'DEF-spine.003',
    'DEF-spine.004', 'DEF-spine.005', 'DEF-spine.006',
    'DEF-shoulder.L', 'DEF-upper_arm.L', 'DEF-upper_arm.L.001',
    'DEF-forearm.L', 'DEF-forearm.L.001', 'DEF-hand.L',
    'DEF-shoulder.R', 'DEF-upper_arm.R', 'DEF-upper_arm.R.001',
    'DEF-forearm.R', 'DEF-forearm.R.001', 'DEF-hand.R',
    'DEF-thigh.L', 'DEF-thigh.L.001', 'DEF-shin.L', 'DEF-shin.L.001',
    'DEF-foot.L', 'DEF-toe.L',
    'DEF-thigh.R', 'DEF-thigh.R.001', 'DEF-shin.R', 'DEF-shin.R.001',
    'DEF-foot.R', 'DEF-toe.R',
)

#: Knochen, deren Elternteil ausserhalb der Kette liegt (ORG-*): wohin sie
#: stattdessen gehaengt werden. Am Rig abgelesen, nicht geraten.
ERSATZELTERN = {
    'DEF-spine': None,                      # Wurzel
    'DEF-thigh.L': 'DEF-spine',
    'DEF-thigh.R': 'DEF-spine',
    'DEF-shoulder.L': 'DEF-spine.003',
    'DEF-shoulder.R': 'DEF-spine.003',
    'DEF-upper_arm.L': 'DEF-shoulder.L',
    'DEF-upper_arm.R': 'DEF-shoulder.R',
}

#: Blaetter der Kette: Sie brauchen ein Endgelenk aus ihrem `tail`.
BLAETTER = ['DEF-spine.006', 'DEF-toe.L', 'DEF-toe.R']

#: Finger und ihr Handteller. DIE HAND BRAUCHT IHRE FINGER (10.09.2026,
#: gemessen): Ohne sie schrumpft FPS die ganze Hand samt Fingern auf EIN
#: Segment, die Finger kollabieren auf eine Linie, und die Simulation
#: liefert NaN — schon in der Ruhelage, ohne Fehlermeldung. Das
#: mitgelieferte `male`-Beispiel fuehrt 40 seiner 63 Gelenke allein in den
#: Fingern; unsere erste Fassung hatte 36 Gelenke fuer den ganzen Koerper.
FINGER_AN_TELLER = {
    'f_index': '01', 'f_middle': '02', 'f_ring': '03', 'f_pinky': '04',
}


def _hand_ergaenzen():
    u"""Handteller, Finger und Daumen beider Haende in die Kette."""
    kette, eltern = [], {}
    for seite in ('L', 'R'):
        hand = 'DEF-hand.%s' % seite
        for nummer in ('01', '02', '03', '04'):
            teller = 'DEF-palm.%s.%s' % (nummer, seite)
            kette.append(teller)
            eltern[teller] = hand
        for finger, nummer in FINGER_AN_TELLER.items():
            elternteil = 'DEF-palm.%s.%s' % (nummer, seite)
            for glied in ('01', '02', '03'):
                name = 'DEF-%s.%s.%s' % (finger, glied, seite)
                kette.append(name)
                eltern[name] = elternteil
                elternteil = name
            BLAETTER.append(elternteil)
        elternteil = hand
        for glied in ('01', '02', '03'):
            name = 'DEF-thumb.%s.%s' % (glied, seite)
            kette.append(name)
            eltern[name] = elternteil
            elternteil = name
        BLAETTER.append(elternteil)
    return tuple(kette), eltern


_HAND_KETTE, _HAND_ELTERN = _hand_ergaenzen()
KETTE = KETTE + _HAND_KETTE
ERSATZELTERN.update(_HAND_ELTERN)

#: Hoehe des FPS-Beispiels `male` (data/male/male.off), auf die skaliert wird.
FPS_HOEHE = 20.86
FPS_BODEN = -0.18


class Hautnetz:
    u"""Die Aussenhaut als Dreiecksnetz, ohne Zaehne, Augen und Zunge.

    DIE BASIS IST `morphs/L1/<Bauart>.npy`, NICHT `vertices_tpose.npy`
    (10.09.2026). Die beiden Dateien stehen in verschiedenen HALTUNGEN, und
    der Unterschied faellt im Browser nie auf: Lineares Blend-Skinning
    rechnet `pose * inv(ruhe)`, in der Ruhelage also die Identitaet — gleich
    wo die Knochen liegen. Eine Volumensimulation dagegen zieht die Haut auf
    die Knochen; liegt einer daneben, kollabiert das Glied.

    Gemessen am linken Bein (x-Spanne des Netzes auf Knochenhoehe gegen den
    Gelenkpunkt aus `rig_bones.json`):

        vertices_tpose.npy     Fuss 0,005..0,056   Knochen 0,205   DANEBEN
        L1/Female_Caucasian    Fuss 0,175..0,236   Knochen 0,205   passt

    Im T-Pose-Netz laufen die Beine nach unten ZUSAMMEN, im Skelett nach
    unten auseinander. Alle sechs L1-Netze passen, nur diese eine Datei
    nicht. Dieselbe Falle hat am 07.09.2026 schon einmal zugeschlagen
    (`GarmentcodeDienst._grundnetz` las fest `vertices_tpose.npy`).
    """

    #: Bauart je Geschlecht — die Vorgaben der Web-App. Die uebrigen L1-Netze
    #: (African, Asian, Elf, ...) liegen im selben Ordner und lassen sich ueber
    #: `--bauart` waehlen. DIE TOPOLOGIEN SIND VERSCHIEDEN: weiblich 18.210
    #: Punkte, maennlich 17.996 — deshalb nie das eine Netz mit den Flaechen
    #: des anderen mischen (Befund vom 07.09.2026).
    BAUART = {'female': 'Female_Caucasian', 'male': 'Male_Caucasian'}

    def __init__(self, wurzel, bauart=None, geschlecht='female'):
        self.bauart = bauart or self.BAUART[geschlecht]
        self.punkte = self._basis(wurzel).astype(np.float64)
        self.vierecke = np.load(os.path.join(wurzel, 'faces.npy'))
        pfad = os.path.join(wurzel, 'materials.json')
        mpfad = os.path.join(wurzel, 'face_materials.npy')
        self.materialien = json.load(open(pfad)) if os.path.exists(pfad) else None
        self.flaechenmaterial = np.load(mpfad) if os.path.exists(mpfad) else None

    def _basis(self, wurzel):
        u"""Das L1-Netz der Bauart — dieselbe Quelle wie `CharacterState`.

        Faellt die Datei aus, wird das GESAGT und nicht stumm auf die
        T-Pose-Datei zurueckgefallen: Die liefert ein Netz, das fuer sich
        plausibel aussieht und zum Skelett nicht passt.
        """
        pfad = os.path.join(wurzel, 'morphs', 'L1', self.bauart + '.npy')
        if not os.path.exists(pfad):
            raise SystemExit(u'Basisnetz fehlt: %s' % pfad)
        return np.load(pfad)

    def aussenhaut(self):
        u"""Dreiecke der Aussenhaut und die dazu gehoerenden Punkte."""
        if self.materialien is None:
            # `humanBody_male` fuehrt keine materials.json — dann alles nehmen
            # und das im Bericht sagen, statt stumm etwas anderes zu liefern.
            gewaehlt = np.ones(len(self.vierecke), dtype=bool)
        else:
            nummern = [i for i, n in enumerate(self.materialien) if n in HAUT]
            gewaehlt = np.isin(self.flaechenmaterial, nummern)
        q = self.vierecke[gewaehlt]
        dreiecke = np.vstack([q[:, [0, 1, 2]], q[:, [0, 2, 3]]])
        benutzt = np.unique(dreiecke)
        neu = -np.ones(len(self.punkte), dtype=np.int64)
        neu[benutzt] = np.arange(len(benutzt))
        return self.punkte[benutzt], neu[dreiecke], gewaehlt.sum()

    @staticmethod
    def _kantenlaengen(punkte, dreiecke):
        u"""Alle Kantenlaengen eines Dreiecksnetzes (mit Wiederholung)."""
        return np.concatenate([
            np.linalg.norm(punkte[dreiecke[:, 1]] - punkte[dreiecke[:, 0]], axis=1),
            np.linalg.norm(punkte[dreiecke[:, 2]] - punkte[dreiecke[:, 1]], axis=1),
            np.linalg.norm(punkte[dreiecke[:, 0]] - punkte[dreiecke[:, 2]], axis=1)])

    @staticmethod
    def guete(punkte, dreiecke):
        u"""Radienquotient je Dreieck: 1 = gleichseitig, 0 = entartet.

        Die Zahl, an der die Stabilitaet haengt — siehe `reparieren`.
        """
        a = np.linalg.norm(punkte[dreiecke[:, 1]] - punkte[dreiecke[:, 0]], axis=1)
        b = np.linalg.norm(punkte[dreiecke[:, 2]] - punkte[dreiecke[:, 1]], axis=1)
        c = np.linalg.norm(punkte[dreiecke[:, 0]] - punkte[dreiecke[:, 2]], axis=1)
        s = (a + b + c) / 2.0
        flaeche = np.sqrt(np.maximum(s * (s - a) * (s - b) * (s - c), 1e-30))
        inkreis = flaeche / np.maximum(s, 1e-30)
        umkreis = a * b * c / np.maximum(4 * flaeche, 1e-30)
        return 2 * inkreis / np.maximum(umkreis, 1e-30)

    @staticmethod
    def reparieren(punkte, dreiecke, ziel_dreiecke=10000):
        u"""Loecher schliessen und Winzkanten verschmelzen — mit trimesh.

        WARUM (10.09.2026, gemessen): Ohne diesen Schritt lieferte die
        Simulation NUR NaN, schon in der Ruhelage und ohne jede Bewegung.
        Die Gegenprobe am mitgelieferten `male`-Beispiel lief sauber; der
        Unterschied stand im Netz:

            male   watertight=True   Euler  2   kleinste Flaeche 3,6e-04
            unser  watertight=False  Euler -1   kleinste Flaeche 3,8e-06

        Ein offenes Netz hat kein Inneres, und aus 100-mal kleineren
        Dreiecken werden schlecht konditionierte Tetraeder. Beides zusammen
        sprengt den Loeser — ohne Fehlermeldung, nur mit NaN.

        Gemacht wird das mit **pymeshlab**, nicht von Hand: `trimesh`
        schliesst nur Drei- und Viereckloecher und gab hier `False` zurueck,
        ohne ein einziges Dreieck zu ergaenzen. Alle 88 offenen Kanten liegen
        bei z 1,48 bis 1,57 m — Augenhoehlen und Mund; das sind Ringe aus
        rund 30 Kanten.

        Dezimiert wird auf `ziel_dreiecke`, weil die Autoren „about 3000-5000
        simulated vertices" empfehlen und das Netz mit 11.997 Punkten
        Dreiecke bis herab zu 3,8e-06 Flaecheninhalt fuehrt.
        """
        import pymeshlab
        netz = pymeshlab.Mesh(vertex_matrix=punkte, face_matrix=dreiecke)
        satz = pymeshlab.MeshSet()
        satz.add_mesh(netz, 'haut')
        satz.meshing_remove_duplicate_vertices()
        satz.meshing_remove_duplicate_faces()
        satz.meshing_remove_null_faces()
        # Der Ring am Mund ist der groesste; 200 Kanten sind reichlich.
        satz.meshing_close_holes(maxholesize=200, newfaceselected=False)
        if ziel_dreiecke:
            satz.meshing_decimation_quadric_edge_collapse(
                targetfacenum=int(ziel_dreiecke), preserveboundary=True,
                preservenormal=True, planarquadric=True)
            satz.meshing_close_holes(maxholesize=200, newfaceselected=False)
            # ISOTROPES REMESHING — der Schritt, ohne den der Loeser kippt.
            # Die Dezimierung optimiert die FORM, nicht die Dreiecksgestalt.
            # Gemessen (Radienquotient 2*Inkreis/Umkreis, 1 = gleichseitig):
            #
            #     Netz der Autoren   Median 0,682   keines unter 0,1
            #     nur dezimiert      Median 0,772   11 unter 0,1 (min 0,032)
            #
            # Elf fast entartete Dreiecke ergeben elf flache Tetraeder, deren
            # Steifigkeitsmatrix schlecht konditioniert ist. Der Loeser
            # divergiert daran — mit unserer Figur schon IN RUHE, nach rund
            # 300 Teilschritten, und meldet es nicht: Er liefert NaN.
            # Die Kantenlaenge wird auf den vorhandenen Median gesetzt, damit
            # das Remeshing die Aufloesung haelt statt sie zu veraendern.
            m = satz.current_mesh()
            kanten = Hautnetz._kantenlaengen(
                np.asarray(m.vertex_matrix()), np.asarray(m.face_matrix()))
            satz.meshing_isotropic_explicit_remeshing(
                iterations=6,
                targetlen=pymeshlab.PureValue(float(np.median(kanten))),
                adaptive=False, checksurfdist=True)
            satz.meshing_close_holes(maxholesize=200, newfaceselected=False)
        m = satz.current_mesh()
        return (np.asarray(m.vertex_matrix(), dtype=np.float64),
                np.asarray(m.face_matrix(), dtype=np.int64), None)

    @staticmethod
    def randkanten(dreiecke):
        u"""Kanten, an denen nur EIN Dreieck haengt — also Loecher."""
        kanten = np.vstack([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]],
                            dreiecke[:, [2, 0]]])
        kanten = np.sort(kanten, axis=1)
        _, zahl = np.unique(kanten, axis=0, return_counts=True)
        return int((zahl == 1).sum())


class Skelettauszug:
    u"""Die Hauptkette des DEF-Rigs als Gelenkliste."""

    def __init__(self, wurzel):
        self.knochen = {b['name']: b for b in
                        json.load(open(os.path.join(wurzel, 'rig_bones.json')))['bones']}

    def gelenke(self, mit_fingern=True):
        u"""[(name, punkt, elternname)] — Wurzel zuerst, Eltern vor Kindern.

        `mit_fingern=False` laesst Handteller und Fingerglieder weg. DAS IST
        DERZEIT DIE EINZIGE FASSUNG, DIE DURCHLAEUFT (gemessen 10.09.2026):
        Der Loeser stuerzt ab, sobald die Daumenkette dabei ist.

            34 Gelenke (ohne Hand)              Exit 0
            42 Gelenke (mit Handtellern)        Exit 0
            50 Gelenke (mit Daumen)             Segmentation fault
            82 Gelenke (alle Finger)            Segmentation fault

        Der Grund ist die Netzaufloesung, nicht das Skelett: Bei 10.000
        Dreiecken liegt das knappste Fingergelenk nur 0,3 mm unter der Haut
        (gemessen mit `trimesh.proximity.signed_distance`, alle 82 innen).
        FPS zieht die Haut auf die Knochen; bei diesem Rand bleibt fuer die
        Muskelschicht kein Platz.

        Fuer Muskelwoelbung und Falten an Rumpf und Gliedmassen sind die
        Fingergelenke ohne Belang — die Hand bleibt dann ein Segment.
        """
        aus, gesetzt = [], set()
        kette = KETTE if mit_fingern else tuple(
            n for n in KETTE if n not in _HAND_KETTE)
        blaetter = BLAETTER if mit_fingern else [
            n for n in BLAETTER if n not in _HAND_KETTE]

        def eintragen(name):
            if name in gesetzt:
                return
            knochen = self.knochen.get(name)
            if knochen is None:
                raise KeyError(u'Knochen fehlt im Rig: %s' % name)
            elternteil = ERSATZELTERN.get(name, knochen['parent'])
            if elternteil is not None and elternteil not in gesetzt:
                eintragen(elternteil)
            gesetzt.add(name)
            aus.append((name, np.asarray(knochen['head'], dtype=np.float64),
                        elternteil))

        for name in kette:
            eintragen(name)
        for name in blaetter:
            ende = np.asarray(self.knochen[name]['tail'], dtype=np.float64)
            aus.append((name + '_ende', ende, name))
            gesetzt.add(name + '_ende')
        return aus


def schreiben(geschlecht, dreiecke_ziel=10000, mit_fingern=True, bauart=None):
    wurzel = WURZELN[geschlecht]
    netz = Hautnetz(wurzel, bauart=bauart, geschlecht=geschlecht)
    punkte, dreiecke, hautflaechen = netz.aussenhaut()
    vorher = (len(punkte), len(dreiecke), Hautnetz.randkanten(dreiecke))
    punkte, dreiecke, _ = Hautnetz.reparieren(punkte, dreiecke, dreiecke_ziel)
    loecher = Hautnetz.randkanten(dreiecke)
    euler = len(punkte) - (len(dreiecke) * 3 // 2) + len(dreiecke)

    skelett = Skelettauszug(wurzel)
    gelenke = skelett.gelenke(mit_fingern=mit_fingern)

    # Massstab und Lage: Fuesse auf FPS_BODEN, Hoehe wie das male-Beispiel.
    unten, oben = punkte[:, 2].min(), punkte[:, 2].max()
    faktor = FPS_HOEHE / (oben - unten)
    mitte = np.array([punkte[:, 0].mean(), punkte[:, 1].mean(), unten])

    def umrechnen(p):
        return (p - mitte) * faktor + np.array([0.0, 0.0, FPS_BODEN])

    punkte_fps = umrechnen(punkte)

    os.makedirs(ZIEL, exist_ok=True)
    stamm = 'hb_%s' % geschlecht
    off = os.path.join(ZIEL, stamm + '.off')
    with open(off, 'w') as datei:
        datei.write('OFF\n%d %d 0\n' % (len(punkte_fps), len(dreiecke)))
        for p in punkte_fps:
            datei.write('%.6f %.6f %.6f\n' % tuple(p))
        for d in dreiecke:
            datei.write('3 %d %d %d\n' % tuple(d))

    skel = os.path.join(ZIEL, stamm + '.skel')
    with open(skel, 'w') as datei:
        datei.write('%d\n' % len(gelenke))
        for name, punkt, elternteil in gelenke:
            p = umrechnen(punkt)
            datei.write('%.6f\t%.6f\t%.6f\t%s\t%s\n'
                        % (p[0], p[1], p[2], name,
                           elternteil if elternteil else 'root'))

    ini = os.path.join(ZIEL, stamm + '.ini')
    with open(ini, 'w') as datei:
        datei.write('SIMMESH     %s.off\n' % stamm)
        datei.write('SKELETON    %s.skel\n' % stamm)

    # --- Bericht: jede Zahl, an der man einen Fehler sehen wuerde -----------
    print(u'Netz     %d Punkte, %d Dreiecke (aus %d Haut-Vierecken von %d)'
          % (len(punkte_fps), len(dreiecke), hautflaechen, len(netz.vierecke)))
    print(u'         vor der Reparatur: %d Punkte, %d Dreiecke, %d Randkanten'
          % vorher)
    print(u'         Randkanten jetzt: %d   Euler: %d (geschlossen = 2)'
          % (loecher, euler))
    kanten = np.linalg.norm(punkte[dreiecke[:, 0]] - punkte[dreiecke[:, 1]], axis=1)
    print(u'         kuerzeste Kante: %.2e m' % kanten.min())
    print(u'         Hoehe %.3f m -> %.2f Einheiten (Faktor %.3f)'
          % (oben - unten, FPS_HOEHE, faktor))
    print(u'         Huelle x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f'
          % (punkte_fps[:, 0].min(), punkte_fps[:, 0].max(),
             punkte_fps[:, 1].min(), punkte_fps[:, 1].max(),
             punkte_fps[:, 2].min(), punkte_fps[:, 2].max()))
    print(u'Skelett  %d Gelenke, Wurzel %s' % (len(gelenke), gelenke[0][0]))

    # Die Probe, die FPS' README verlangt: „Make sure, that the skeleton is
    # inside of your mesh."
    aussen = [n for n, p, _ in gelenke
              if not _im_netz(umrechnen(p), punkte_fps)]
    print(u'         Gelenke ausserhalb der Netzhuelle: %s'
          % (', '.join(aussen) if aussen else 'keine'))
    print(u'Dateien  %s' % ', '.join(os.path.basename(p) for p in (off, skel, ini)))
    return off, skel, ini


def _im_netz(punkt, punkte):
    u"""Grobe Probe: liegt das Gelenk innerhalb der Netz-Huelle?

    Keine echte Innen-Aussen-Pruefung — die braeuchte einen Strahltest. Sie
    faengt den Fall ab, der wirklich vorkommt: ein Gelenk, das durch einen
    Massstabs- oder Achsenfehler weit neben dem Koerper liegt.
    """
    return bool(np.all(punkt >= punkte.min(axis=0) - 1e-6)
                and np.all(punkt <= punkte.max(axis=0) + 1e-6))


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--geschlecht', default='female',
                          choices=sorted(WURZELN))
    zerleger.add_argument('--bauart', default=None,
                          help=u'L1-Netz, z.B. Female_Asian (Vorgabe: Caucasian)')
    zerleger.add_argument('--dreiecke', type=int, default=10000,
                          help=u'Ziel der Dezimierung (die Autoren: 3000-5000 '
                               u'Punkte, also rund 6000-10000 Dreiecke)')
    zerleger.add_argument('--ohne-finger', action='store_true',
                          help=u'Hand als ein Segment. NOETIG, solange die '
                               u'Fingerknochen nur knapp im Netz liegen — '
                               u'siehe Skelettauszug.gelenke.')
    werte = zerleger.parse_args()
    schreiben(werte.geschlecht, werte.dreiecke, not werte.ohne_finger,
              werte.bauart)
    return 0


if __name__ == '__main__':
    sys.exit(main())
