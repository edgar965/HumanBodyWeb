# -*- coding: utf-8 -*-
u"""`Koerperprofil` und `Koerpermasse`: Masse, deren Antwort bekannt ist.

WARUM (06.09.2026): Der Schnitt war fuer falsche Masse gebaut. Die
Armtrennung an x-Luecken warf auf Brusthoehe 99 % der Scheibenpunkte weg,
`bust` kam roh mit 44,5 cm heraus und wurde von der Baendigung stumm auf
73,8 gehoben — Vorlage 97,4, am Rumpf gemessen 88. Das T-Shirt spannte
vorn und knitterte hinten.

Geprueft wird an einem KUNSTKOERPER, dessen Masse man ausrechnen kann:
ein Rumpf aus Kreisscheiben mit Huefte, Taille und Brust an bekannten
Hoehen, dazu zwei Arme, die im Segment als Arme markiert sind.

    1. Die Messhoehen treffen Huefte, Taille, Brust auf den Zentimeter.
    2. Die Umfaenge sind die Kreisumfaenge — Arme verfaelschen sie nicht.
    3. Eine DUENN besetzte Scheibe (die alte Lueckenfalle) liefert trotzdem
       den vollen Umfang.
    4. Die Linienmasse folgen den gemessenen Hoehen.
    5. Greift die Baendigung, steht 'begrenzt' in der Herkunft — nie
       'gemessen'.
"""
import json
import os
import tempfile

import numpy as np
from django.test import SimpleTestCase

from GarmentCode.armhaltung import Armhaltung
from GarmentCode.koerpermasse import Koerpermasse
from GarmentCode.koerperprofil import Koerperprofil
from GarmentCode.schulterneigung import Schulterneigung

VORLAGE = {
    'height': 166.0, 'head_l': 25.0, 'bust': 97.0, 'underbust': 80.0,
    'waist': 80.0, 'hips': 104.0, 'shoulder_w': 35.0, 'back_width': 46.0,
    'waist_back_width': 38.0, 'hip_back_width': 55.0, 'neck_w': 18.0,
    'bust_line': 25.0, 'vert_bust_line': 21.0, 'waist_line': 36.0,
    'hips_line': 23.0, 'arm_length': 52.0, 'wrist': 16.0, 'leg_circ': 60.0,
    'shoulder_incl': 21.0, 'hip_inclination': 12.0, 'arm_pose_angle': 45.0,
    'armscye_depth': 12.0, 'bust_points': 16.0, 'bum_points': 18.0,
    'crotch_hip_diff': 8.0, 'waist_over_bust_line': 40.0,
}


def kunstkoerper(punkte_je_ring=48):
    u"""Ein 1,66 m grosser Kunstkoerper mit ausrechenbaren Massen.

    Rumpf 0,80–1,45 m mit Huefte (r 15) bei 0,92, Taille (r 10) bei 1,08,
    Brust (r 14) bei 1,24; darueber ein Hals-/Kopfstueck bis 1,66; Beine
    0,00–0,80 als eigene Segmente; Arme seitlich bei z 1,00–1,40. Die volle
    Groesse ist noetig: `Koerpermasse` skaliert die Vorlage mit der Hoehe,
    und ein 65-cm-Rumpf allein liesse die Baendigung jeden Umfang klemmen.
    Gibt (vertices, segmente) zurueck.
    """
    def radius(z):
        stuetzen = [(0.80, 0.12), (0.92, 0.15), (1.08, 0.10), (1.24, 0.14),
                    (1.40, 0.12), (1.45, 0.06), (1.66, 0.06)]
        zs, rs = zip(*stuetzen)
        return float(np.interp(z, zs, rs))
    rumpf, arme, beine = [], [], []
    phi = np.linspace(0, 2 * np.pi, punkte_je_ring, endpoint=False)
    for z in np.arange(0.80, 1.6601, 0.01):
        r = radius(z)
        rumpf.extend([[r * np.cos(p), r * np.sin(p), z] for p in phi])
    for z in np.arange(1.00, 1.4001, 0.01):
        for seite in (-1, 1):
            arme.extend([[seite * (0.30 + 0.04 * np.cos(p)),
                          0.04 * np.sin(p), z] for p in phi[::4]])
    for z in np.arange(0.00, 0.7901, 0.01):
        for seite in (-1, 1):
            beine.extend([[seite * 0.08 + 0.07 * np.cos(p),
                           0.07 * np.sin(p), z] for p in phi[::4]])
    v = np.array(rumpf + arme + beine)
    n_rumpf, n_arme = len(rumpf), len(arme)
    segmente = {'body': list(range(n_rumpf)),
                'left_arm': list(range(n_rumpf, n_rumpf + n_arme // 2)),
                'right_arm': list(range(n_rumpf + n_arme // 2, n_rumpf + n_arme)),
                'left_leg': list(range(n_rumpf + n_arme,
                                       n_rumpf + n_arme + len(beine) // 2)),
                'right_leg': list(range(n_rumpf + n_arme + len(beine) // 2, len(v))),
                'face_internal': []}
    return v, segmente


class KoerperprofilTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.v, self.seg = kunstkoerper()
        arme = self.seg['left_arm'] + self.seg['right_arm']
        self.profil = Koerperprofil(self.v, self.seg['body'], arme)

    def test_messhoehen_treffen(self):
        h = self.profil.hoehen()
        self.assertIsNotNone(h)
        self.assertAlmostEqual(h['huefte'], 0.92, delta=0.015)
        self.assertAlmostEqual(h['taille'], 1.08, delta=0.015)
        self.assertAlmostEqual(h['brust'], 1.24, delta=0.015)

    def test_umfaenge_sind_kreisumfaenge_ohne_arme(self):
        h = self.profil.hoehen()
        # Kreisumfang 2*pi*r in cm; die Huelle eines 48-Ecks ist ~0,3 % kleiner.
        self.assertAlmostEqual(h['brust_umfang'], 2 * np.pi * 14, delta=1.0)
        self.assertAlmostEqual(h['huefte_umfang'], 2 * np.pi * 15, delta=1.0)
        # Ein MINIMUM wird durch die 3-cm-Scheibe systematisch etwas zu gross
        # gemessen — die Nachbarringe sind dicker, und die Huelle nimmt den
        # groessten. An diesem spitz zulaufenden Kunstkoerper sind das
        # 1,9 cm (+3 %); eine echte Taille ist weicher.
        self.assertAlmostEqual(h['taille_umfang'], 2 * np.pi * 10, delta=2.5)
        # Mit Armen in der Scheibe waere die Huelle 60 cm breit — das darf
        # auf Brusthoehe nicht passieren.
        self.assertLess(self.profil.breite(1.24), 30.0)

    def test_ruecken_ist_der_halbe_umfang(self):
        u"""Ein Massband von Seite zu Seite ueber den Ruecken: pi*r."""
        self.assertAlmostEqual(self.profil.ruecken(1.24), np.pi * 14, delta=1.5)

    def test_duenne_scheibe_bleibt_ganz(self):
        u"""Die alte Lueckenfalle: wenige Punkte je Ring, grosse x-Luecken."""
        v, seg = kunstkoerper(punkte_je_ring=10)
        p = Koerperprofil(v, seg['body'], seg['left_arm'] + seg['right_arm'])
        u = p.umfang(1.24)
        self.assertIsNotNone(u)
        # 10-Eck-Huelle eines Kreises r=14: 2*10*14*sin(pi/10) = 86,5 cm
        self.assertGreater(u, 80.0, 'die Scheibe hat Punkte verloren')


class KoerpermasseTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.v, self.seg = kunstkoerper()

    def test_masse_und_linien_folgen_dem_netz(self):
        k = Koerpermasse(self.v, VORLAGE, segmente=self.seg)
        m = k.masse()
        self.assertAlmostEqual(m['bust'], 2 * np.pi * 14, delta=1.0)
        self.assertAlmostEqual(m['hips'], 2 * np.pi * 15, delta=1.0)
        # Taille ist ein MINIMUM — die 3-cm-Scheibe misst es an diesem spitz
        # zulaufenden Kunstkoerper 1,9 cm zu gross (siehe Profil-Test).
        self.assertAlmostEqual(m['waist'], 2 * np.pi * 10, delta=2.5)
        # Hoehe 166 cm; head_l 25 cm (Vorlage, Faktor 1) -> Schulterlinie
        # bei 1,41 m. waist_line = 1,41 - 1,08 = 33 cm, hips_line = 16 cm.
        schulter = 1.66 - 0.25
        self.assertAlmostEqual(m['waist_line'], (schulter - 1.08) * 100, delta=2.0)
        self.assertAlmostEqual(m['hips_line'], (1.08 - 0.92) * 100, delta=2.0)
        # 2/3 vert + 1/3 bust muss die Brusthoehe treffen.
        misch = (2.0 / 3.0) * m['vert_bust_line'] + (1.0 / 3.0) * m['bust_line']
        self.assertAlmostEqual(misch, (schulter - 1.24) * 100, delta=2.0)

    def test_baendigung_ist_sichtbar(self):
        u"""Ein geklemmter Wert heisst 'begrenzt', nie 'gemessen'."""
        enge = dict(VORLAGE)
        enge['bust'] = 300.0            # skaliert bleibt das weit ueber dem Netz
        k = Koerpermasse(self.v, enge, segmente=self.seg)
        k.masse()
        self.assertEqual(k.herkunft()['bust'], 'begrenzt')
        self.assertEqual(k.herkunft()['waist'], 'gemessen')

    def test_ohne_segmente_heisst_ungetrennt(self):
        k = Koerpermasse(self.v, VORLAGE)
        k.masse()
        self.assertEqual(k.herkunft()['bust'], 'ungetrennt')


class DuenneScheibeTest(SimpleTestCase):
    u"""Eine Scheibe mit wenigen Punkten darf keine Messhoehe werden.

    BEFUND 07.09.2026: Beim 195-cm-Mann fuehrt das Rumpfsegment kurz ueber
    dem Schritt nur den Zwickel zwischen den Beinen — Ruecken und Flanken
    gehoeren dort zu den Beinsegmenten. Eine konvexe Huelle ueber zehn
    Punkte unterschaetzt den Umfang, und beim MINIMUM (der Taille) gewinnt
    ausgerechnet der zu kleine Wert:

        z 1,060   10 Punkte    79,8 cm   <- wurde Taille
        z 1,240   61 Punkte    85,5 cm   <- die Taille

    Die Taille lag dadurch bei 54 % der Koerperhoehe statt bei 65 %, und
    mit ihr jedes Linienmass. Sichtbar wurde es erst dadurch, dass der
    3D-Aufbau aller fuenf Stuecke mit `FittedShirt` abbrach.

    Hier steht derselbe Fall als Kunstkoerper: ein duenner Ring dicht
    ueber der Huefte, dessen Huelle kleiner ist als die echte Taille.
    """

    databases = []

    #: Hoehe des kuenstlich ausgeduennten Rings — zwischen Huefte (0,92)
    #: und Taille (1,08), also mitten im Suchbereich.
    DUENN_Z = 0.99

    def _profil(self, ausgeduennt):
        v, seg = kunstkoerper()
        if ausgeduennt:
            rumpf = np.asarray(seg['body'], dtype=int)
            # Der GANZE Scheibenbereich muss duenn werden, nicht nur ein
            # Ring: `scheibe()` nimmt alles im Abstand HALBSCHEIBE_M, und
            # ein voller Nachbarring stellt den Umfang sofort wieder her
            # (gemessen: 82,4 statt der erwarteten 20 cm).
            fenster = Koerperprofil.HALBSCHEIBE_M + 0.005
            nah = rumpf[np.abs(v[rumpf, 2] - self.DUENN_Z) < fenster]
            # Je Ring bleiben ein paar Punkte nahe der Achse stehen — wie
            # der Zwickel zwischen den Beinen beim echten Netz.
            behalten = []
            for z in sorted({round(float(x), 3) for x in v[nah, 2]}):
                ring = [i for i in nah.tolist() if abs(v[i, 2] - z) < 1e-6]
                behalten.extend(ring[:3])
            v[behalten] = v[behalten] * [0.2, 0.2, 1.0]
            weg = [i for i in nah.tolist() if i not in set(behalten)]
            # Die uebrigen aus der Scheibe schieben, statt sie zu loeschen:
            # die Segmentlisten sollen unveraendert bleiben.
            v[weg, 2] = self.DUENN_Z - 0.10
        arme = seg['left_arm'] + seg['right_arm']
        return Koerperprofil(v, seg['body'], arme)

    def test_duenner_ring_wird_nicht_zur_taille(self):
        hoehen = self._profil(ausgeduennt=True).hoehen()
        self.assertIsNotNone(hoehen)
        self.assertAlmostEqual(hoehen['taille'], 1.08, delta=0.02,
                               msg='Taille bei %.3f statt 1,08'
                                   % hoehen['taille'])

    def test_die_ausduennung_wirkt_ueberhaupt(self):
        u"""Gegenprobe: Ohne die Mindestbesetzung MUSS der duenne Ring
        gewinnen — sonst prueft der Test oben nichts.

        Gemessen wird der Umfang der praeparierten Scheibe direkt: Er
        liegt unter dem der echten Taille, ist also ein Minimum, das die
        Suche ohne Schranke nehmen wuerde.
        """
        profil = self._profil(ausgeduennt=True)
        duenn = profil.umfang(self.DUENN_Z)
        taille = profil.umfang(1.08)
        self.assertIsNotNone(duenn)
        self.assertLess(duenn, taille,
                        'praeparierte Scheibe %.1f, Taille %.1f'
                        % (duenn or 0, taille or 0))
        self.assertLess(len(profil.scheibe(self.DUENN_Z)),
                        len(profil.scheibe(1.08)))

    def test_ohne_ausduennung_bleibt_alles_wie_vorher(self):
        u"""Die Schranke darf den gesunden Fall nicht verschieben."""
        hoehen = self._profil(ausgeduennt=False).hoehen()
        self.assertAlmostEqual(hoehen['huefte'], 0.92, delta=0.015)
        self.assertAlmostEqual(hoehen['taille'], 1.08, delta=0.015)
        self.assertAlmostEqual(hoehen['brust'], 1.24, delta=0.015)


class ArmlochtiefeTest(SimpleTestCase):
    u"""`armscye_depth` haengt am Oberkoerper, nicht an der Koerperhoehe.

    BEFUND 07.09.2026: Sie kam aus der Vorlage, linear mit der Groesse
    skaliert. Beim 195-cm-Mann waren das 14,3 cm bei nur 17,0 cm Abstand
    zwischen Schulter- und Brustlinie — das Armloch reichte fast bis zur
    Brust. Beim Zuschnitt wird die Armlochform in die Schulterecke
    projiziert (`operators.cut_corner`); passt sie nicht hinein, laeuft
    die Optimierung an den Rand und `subdivide_param` erzeugt eine Kante
    der Laenge null. Fuenf von fuenfzehn Stuecken (alle mit
    `FittedShirt`) waren so nicht baubar.

    Die drei Koerper, die GarmentCode mitbringt, halten 57 %:

        mean_male    13,1 von 23,0 cm      mean_all  12,9 von 22,7
        mean_female  12,6 von 22,4

    Uebernommen wird deshalb das VERHAELTNIS der Vorlage.
    """

    databases = []

    def setUp(self):
        v, seg = kunstkoerper()
        self.rechner = Koerpermasse(v, dict(VORLAGE), segmente=seg)
        self.masse = self.rechner.masse()

    def _vorlagenverhaeltnis(self):
        misch = ((2.0 / 3.0) * VORLAGE['vert_bust_line']
                 + (1.0 / 3.0) * VORLAGE['bust_line'])
        return VORLAGE['armscye_depth'] / misch

    def test_armloch_folgt_dem_schulter_brust_abstand(self):
        misch = ((2.0 / 3.0) * self.masse['vert_bust_line']
                 + (1.0 / 3.0) * self.masse['bust_line'])
        self.assertAlmostEqual(self.masse['armscye_depth'] / misch,
                               self._vorlagenverhaeltnis(), delta=0.02)

    def test_armloch_endet_ueber_der_brustlinie(self):
        u"""Die Aussage, auf die es ankommt: Das Armloch darf die
        Brustlinie nicht erreichen."""
        misch = ((2.0 / 3.0) * self.masse['vert_bust_line']
                 + (1.0 / 3.0) * self.masse['bust_line'])
        self.assertLess(self.masse['armscye_depth'], misch)

    def test_es_ist_nicht_der_vorlagenwert(self):
        u"""Gegenprobe: Am Kunstkoerper liegt die Brustlinie enger unter
        der Schulter als bei der Vorlage. Waere der Wert einfach
        uebernommen (oder nur mit der Hoehe skaliert), stuende hier die
        Zahl der Vorlage."""
        self.assertNotAlmostEqual(self.masse['armscye_depth'],
                                  VORLAGE['armscye_depth'], delta=1.0)
        self.assertEqual(self.rechner.herkunft()['armscye_depth'],
                         'gemessen')


# ----------------------------------------------------------------- Armhaltung

def armkoerper(winkel_grad, hand_punkte=0, punkte_je_ring=16):
    u"""Ein Kunstkörper, dessen Arme um einen BEKANNTEN Winkel hängen.

    Rumpf als Säule (er liefert den Schwerpunkt, gegen den die Armrichtung
    orientiert wird), daran zwei gerade Arme vom Schulterpunkt aus, um
    `winkel_grad` unter die Waagrechte geneigt.

    `hand_punkte` hängt ans Ende jedes Arms einen dichten Klumpen — die
    Gegenprobe gegen den Messer, der auf die Punktdichte hereinfällt: Eine
    Hauptachse über die Punktwolke folgt dem Klumpen, die Mittellinie nicht.
    """
    rumpf, arme = [], []
    phi = np.linspace(0, 2 * np.pi, punkte_je_ring, endpoint=False)
    for z in np.arange(0.80, 1.4501, 0.02):
        rumpf.extend([[0.14 * np.cos(p), 0.10 * np.sin(p), z] for p in phi])
    w = np.radians(winkel_grad)
    richtung = np.array([np.cos(w), 0.0, -np.sin(w)])
    quer1, quer2 = np.array([0.0, 1.0, 0.0]), np.cross(richtung, [0, 1, 0])
    for seite in (1, -1):
        start = np.array([seite * 0.16, 0.0, 1.40])
        achse = richtung * np.array([seite, 1, 1])
        for t in np.arange(0.0, 0.6001, 0.01):
            mitte = start + achse * t
            arme.extend([mitte + 0.045 * (np.cos(p) * quer1
                                          + np.sin(p) * quer2) for p in phi])
        if hand_punkte:
            ende = start + achse * 0.62
            rng = np.random.default_rng(7)
            arme.extend(ende + rng.normal(0, 0.02, (hand_punkte, 3)))
    v = np.array(rumpf + [list(p) for p in arme], dtype=float)
    n_r, n_a = len(rumpf), len(arme)
    return v, {'body': list(range(n_r)),
               'left_arm': list(range(n_r, n_r + n_a // 2)),
               'right_arm': list(range(n_r + n_a // 2, n_r + n_a)),
               'left_leg': [], 'right_leg': [], 'face_internal': []}


class ArmhaltungTest(SimpleTestCase):
    u"""`arm_pose_angle` wird gemessen, nicht aus der Vorlage genommen.

    BEFUND 07.09.2026: Der Wert kam als 45,487 aus `mean_female.yaml`,
    während die Figuren bei 31 bis 33 Grad stehen. `sleeves.py` (Zeile 340)
    dreht den Ärmel final um genau diesen Winkel, `bodice.py` (Zeile 297)
    setzt ihn mit `gap = -1 - winkel/10` an. Am fertigen T-Shirt gemessen:
    Arm 32,67 Grad, Ärmelachse 17 bis 22 Grad — der Ärmel stand nach oben ab.
    """

    databases = []

    def test_bekannter_winkel_wird_getroffen(self):
        u"""Der Arbeitsbereich: T-Pose (0) bis A-Haltung (45)."""
        for soll in (0.0, 20.0, 32.0, 45.0):
            v, seg = armkoerper(soll)
            gemessen = Armhaltung(v, seg, oben=2).winkel()
            self.assertIsNotNone(gemessen, 'Winkel %s nicht messbar' % soll)
            self.assertAlmostEqual(gemessen, soll, delta=1.5,
                                   msg='Soll %.1f, gemessen %.2f'
                                       % (soll, gemessen))

    def test_sehr_steiler_arm_ist_die_bekannte_grenze(self):
        u"""Ueber 45 Grad laesst die Genauigkeit nach — gemessen, nicht
        behauptet: Bei 60 Grad liegt der Messer 4,7 Grad daneben, weil die
        grobe Achse (Armschwerpunkt gegen Koerperschwerpunkt) dann fast
        waagrecht laeuft und die Scheiben den Arm schraeg schneiden.

        Ein zweiter Durchgang wuerde das beheben (0,48 Grad) und die echten
        Koerper verschlechtern (1,25 -> 4,14) — siehe `armhaltung.py`.
        Stehende Figuren liegen zwischen 0 und 45; der Fall ist damit
        festgehalten, nicht behoben. Der Test haelt fest, dass er nicht
        SCHLIMMER wird."""
        gemessen = Armhaltung(*armkoerper(60.0), oben=2).winkel()
        self.assertAlmostEqual(gemessen, 60.0, delta=5.0)
        self.assertLess(gemessen, 60.0, 'der Fehler zeigt nach unten')

    def test_die_hand_verzieht_das_ergebnis_nicht(self):
        u"""Der Grund, warum nicht über die Hauptachse gemessen wird.

        Bei SMPL trägt die Hand 802 Punkte gegen 284 im Oberarm. Ein
        dichter Klumpen am Armende darf den Winkel nicht verschieben.
        """
        ohne = Armhaltung(*armkoerper(32.0), oben=2).winkel()
        mit = Armhaltung(*armkoerper(32.0, hand_punkte=900), oben=2).winkel()
        self.assertAlmostEqual(mit, ohne, delta=0.5,
                               msg='ohne Hand %.2f, mit Hand %.2f' % (ohne, mit))

    def test_koerpermasse_nimmt_den_messwert(self):
        u"""Nicht die 45 Grad aus der Vorlage — den gemessenen Winkel."""
        v, seg = armkoerper(30.0)
        masse = Koerpermasse(v, dict(VORLAGE), segmente=seg).masse()
        self.assertAlmostEqual(masse['arm_pose_angle'], 30.0, delta=2.0)
        self.assertNotAlmostEqual(masse['arm_pose_angle'],
                                  VORLAGE['arm_pose_angle'], delta=2.0)

    def test_herkunft_sagt_gemessen(self):
        v, seg = armkoerper(30.0)
        rechner = Koerpermasse(v, dict(VORLAGE), segmente=seg)
        rechner.masse()
        self.assertEqual(rechner.herkunft()['arm_pose_angle'], 'gemessen')

    def test_ohne_segmente_bleibt_die_vorlage(self):
        u"""Ein geratener Haltungswinkel wäre schlimmer als der aus der
        Vorlage — er sähe gemessen aus."""
        v, _ = armkoerper(30.0)
        rechner = Koerpermasse(v, dict(VORLAGE))
        self.assertIsNone(rechner.armhaltung())
        self.assertAlmostEqual(rechner.masse()['arm_pose_angle'],
                               VORLAGE['arm_pose_angle'], delta=0.01)

    def test_winkel_skaliert_nicht_mit_der_groesse(self):
        u"""Er ist eine Haltung, kein Längenmaß: Ein doppelt so großer
        Körper in derselben Haltung hat denselben Winkel."""
        v, seg = armkoerper(35.0)
        klein = Armhaltung(v, seg, oben=2).winkel()
        gross = Armhaltung(v * 2.0, seg, oben=2).winkel()
        self.assertAlmostEqual(klein, gross, delta=0.1)


# ------------------------------------------------------------ Schulterneigung

class SchulterneigungTest(SimpleTestCase):
    u"""`shoulder_incl` kommt aus dem Schlüsselbein, nicht aus der Vorlage.

    BEFUND 07.09.2026 (Edgar: „warum sind die Ärmel vom T-Shirt nach
    oben?"): Der Wert steuert im Upstream den Ruhewinkel des Ärmels —
    `sleeves.py` Zeile 118 und 216: `rest_angle = max(sleeve_angle,
    _shoulder_incl)`. Da `sleeve_angle` in der Vorgabe auf 10 steht (dem
    Minimum, und im Online-Werkzeug steht der Regler ebenso ganz links),
    entscheidet die Schulterneigung allein. Gemeldet wurden 20,905 aus
    `mean_female.yaml`, das Schlüsselbein der Figur liegt bei 11,5.
    """

    databases = []

    def skelett(self, hals, gelenk):
        u"""Ein Minimalskelett mit zwei Knochen an bekannten Orten."""
        return {'bone_count': 2, 'bones': [
            {'name': Schulterneigung.HALS, 'parent': None,
             'local_position': list(hals), 'local_quaternion': [1, 0, 0, 0]},
            {'name': Schulterneigung.GELENK, 'parent': Schulterneigung.HALS,
             'local_position': [gelenk[i] - hals[i] for i in range(3)],
             'local_quaternion': [1, 0, 0, 0]},
        ]}

    def schreiben(self, ordner, daten):
        pfad = os.path.join(ordner, 'def_skeleton.json')
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(daten, datei)
        return pfad

    def test_bekannter_winkel(self):
        u"""Ein Schlüsselbein, das auf 0,10 m Länge um 0,10 m fällt,
        steht 45 Grad geneigt — Z ist oben."""
        for dz, soll in ((0.0, 0.0), (-0.10, 45.0), (-0.0577, 30.0)):
            with tempfile.TemporaryDirectory() as ordner:
                pfad = self.schreiben(ordner, self.skelett(
                    (0.03, 0.0, 1.37), (0.13, 0.0, 1.37 + dz)))
                self.assertAlmostEqual(Schulterneigung(pfad).grad(), soll,
                                       delta=0.2, msg='dz=%s' % dz)

    def test_elternkette_wird_gerechnet(self):
        u"""Der Kopf des Schlüsselbeins hängt an der Wirbelsäule — ohne
        die Kette säße er im Ursprung, und der Winkel wäre ein anderer."""
        daten = {'bone_count': 3, 'bones': [
            {'name': 'DEF-spine.003', 'parent': None,
             'local_position': [0.0, 0.0, 1.30], 'local_quaternion': [1, 0, 0, 0]},
            {'name': Schulterneigung.HALS, 'parent': 'DEF-spine.003',
             'local_position': [0.03, 0.0, 0.07], 'local_quaternion': [1, 0, 0, 0]},
            {'name': Schulterneigung.GELENK, 'parent': Schulterneigung.HALS,
             'local_position': [0.10, 0.0, -0.10], 'local_quaternion': [1, 0, 0, 0]},
        ]}
        with tempfile.TemporaryDirectory() as ordner:
            pfad = self.schreiben(ordner, daten)
            messer = Schulterneigung(pfad)
            self.assertAlmostEqual(messer.grad(), 45.0, delta=0.2)
            lagen = messer.lagen()
            # Die Weltlage muss die Wirbelsäulenhöhe tragen.
            self.assertAlmostEqual(lagen[Schulterneigung.HALS][0][2], 1.37,
                                   delta=1e-6)

    def test_fehlendes_skelett_gibt_none(self):
        u"""Kein Skelett heißt: Vorlagenwert behalten, nicht raten."""
        with tempfile.TemporaryDirectory() as ordner:
            self.assertIsNone(Schulterneigung.aus_datenordner(ordner))

    def test_echtes_skelett_liegt_bei_elf_grad(self):
        u"""Die Figur selbst — im Browser über `matrixWorld` gegengeprüft
        (11,66 Grad), und weit weg von den 20,905 der Vorlage."""
        from django.conf import settings
        ordner = str(settings.HUMANBODY_DATA_DIR)
        if not os.path.isfile(os.path.join(ordner, 'def_skeleton.json')):
            self.skipTest('kein Skelett im Datenordner')
        grad = Schulterneigung.aus_datenordner(ordner)
        self.assertIsNotNone(grad)
        self.assertAlmostEqual(grad, 11.6, delta=1.0)
        self.assertLess(grad, VORLAGE['shoulder_incl'] - 5.0,
                        'der Vorlagenwert war nicht nur leicht daneben')

    def test_koerpermasse_nimmt_den_wert(self):
        v, seg = armkoerper(30.0)
        masse = Koerpermasse(v, dict(VORLAGE), segmente=seg,
                             schulter_incl=11.52).masse()
        self.assertAlmostEqual(masse['shoulder_incl'], 11.52, delta=0.01)

    def test_ohne_angabe_bleibt_die_vorlage(self):
        v, seg = armkoerper(30.0)
        rechner = Koerpermasse(v, dict(VORLAGE), segmente=seg)
        self.assertAlmostEqual(rechner.masse()['shoulder_incl'],
                               VORLAGE['shoulder_incl'], delta=0.01)
        self.assertEqual(rechner.herkunft()['shoulder_incl'], 'vorlage')
