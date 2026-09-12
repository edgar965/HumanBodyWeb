# -*- coding: utf-8 -*-
u"""Die Aussenhaut der HumanBody-Figur als geschlossenes Dreiecksnetz.

Herausgeloest aus `figur_nach_fps.py` (12.09.2026, die Datei war ueber
400 Zeilen). Gebraucht vom FPS-Export dort und von `figur_nach_cody.py`;
`HAUT` nennt die Materialien der Aussenhaut, alles andere steckt im Kopf.
"""
import json
import os

import numpy as np

#: Materialien, die zur AUSSENhaut gehoeren. Alles andere steckt im Kopf.
HAUT = ('HB_Skin', 'HB_Censor', 'HB_Nails_Hand', 'HB_Nails_Feet')


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
        if self.materialien is None or self.flaechenmaterial is None:
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
        # Paare zu EINER Zahl gefaltet: `np.unique(axis=0)` sortiert
        # zeilenweise und ist um ein Vielfaches langsamer (Lehre
        # `unique-axis-vermeiden`).
        breite = int(kanten.max()) + 1 if len(kanten) else 1
        schluessel = kanten[:, 0].astype(np.int64) * breite + kanten[:, 1]
        _, zahl = np.unique(schluessel, return_counts=True)
        return int((zahl == 1).sum())
