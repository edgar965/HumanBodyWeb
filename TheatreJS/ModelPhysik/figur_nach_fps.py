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

from hautnetz import Hautnetz    # Aussenhaut, seit 12.09.2026 eigene Datei

WURZELN = {
    'female': r'A:\3DTools\HumanBody\data\humanBody',
    'male': r'A:\3DTools\HumanBody\data\humanBody_male',
}
ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figur')


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


class Handkette:
    u"""Handteller, Finger und Daumen beider Haende in die Kette."""

    @staticmethod
    def ergaenzen():
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


_HAND_KETTE, _HAND_ELTERN = Handkette.ergaenzen()
KETTE = KETTE + _HAND_KETTE
ERSATZELTERN.update(_HAND_ELTERN)

#: Hoehe des FPS-Beispiels `male` (data/male/male.off), auf die skaliert wird.
FPS_HOEHE = 20.86
FPS_BODEN = -0.18


class Skelettauszug:
    u"""Die Hauptkette des DEF-Rigs als Gelenkliste."""

    def __init__(self, wurzel):
        with open(os.path.join(wurzel, 'rig_bones.json'), encoding='utf-8') as datei:
            knochen = json.load(datei)['bones']
        self.knochen = {b['name']: b for b in knochen}

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


class FpsAusgabe:
    u"""Netz (.off), Skelett (.skel) und .ini fuer FastProjectiveSkinning."""

    @classmethod
    def schreiben(cls, geschlecht, dreiecke_ziel=10000, mit_fingern=True, bauart=None):
        wurzel = WURZELN[geschlecht]
        netz = Hautnetz(wurzel, bauart=bauart, geschlecht=geschlecht)
        punkte, dreiecke, hautflaechen = netz.aussenhaut()
        vorher = (len(punkte), len(dreiecke), Hautnetz.randkanten(dreiecke))
        punkte, dreiecke, _ = Hautnetz.reparieren(punkte, dreiecke, dreiecke_ziel)
        gelenke = Skelettauszug(wurzel).gelenke(mit_fingern=mit_fingern)

        # Massstab und Lage: Fuesse auf FPS_BODEN, Hoehe wie das male-Beispiel.
        unten, oben = punkte[:, 2].min(), punkte[:, 2].max()
        faktor = FPS_HOEHE / (oben - unten)
        mitte = np.array([punkte[:, 0].mean(), punkte[:, 1].mean(), unten])

        def umrechnen(p):
            return (p - mitte) * faktor + np.array([0.0, 0.0, FPS_BODEN])

        punkte_fps = umrechnen(punkte)
        dateien = cls._dateien(geschlecht, punkte_fps, dreiecke, gelenke, umrechnen)
        cls._bericht(netz, punkte, dreiecke, punkte_fps, hautflaechen, vorher, faktor)
        # Die Probe, die FPS' README verlangt: „Make sure, that the skeleton is
        # inside of your mesh."
        aussen = [n for n, p, _ in gelenke
                  if not cls._im_netz(umrechnen(p), punkte_fps)]
        print(u'Skelett  %d Gelenke, Wurzel %s' % (len(gelenke), gelenke[0][0]))
        print(u'         Gelenke ausserhalb der Netzhuelle: %s'
              % (', '.join(aussen) if aussen else 'keine'))
        print(u'Dateien  %s' % ', '.join(os.path.basename(p) for p in dateien))
        return dateien

    @staticmethod
    def _dateien(geschlecht, punkte_fps, dreiecke, gelenke, umrechnen):
        u"""`.off`, `.skel` und `.ini` unter `ZIEL`; gibt die drei Pfade."""
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
        return off, skel, ini

    @staticmethod
    def _bericht(netz, punkte, dreiecke, punkte_fps, hautflaechen, vorher, faktor):
        u"""Jede Zahl, an der man einen Fehler sehen wuerde."""
        loecher = Hautnetz.randkanten(dreiecke)
        euler = len(punkte) - (len(dreiecke) * 3 // 2) + len(dreiecke)
        unten, oben = punkte[:, 2].min(), punkte[:, 2].max()
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

    @staticmethod
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
    FpsAusgabe.schreiben(werte.geschlecht, werte.dreiecke,
                         not werte.ohne_finger, werte.bauart)
    return 0


if __name__ == '__main__':
    sys.exit(main())
