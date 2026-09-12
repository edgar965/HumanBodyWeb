# -*- coding: utf-8 -*-
u"""BVH -> `.anim` fuer FastProjectiveSkinning.

Der Weg benutzt den VORHANDENEN Retarget (`SkeletonRigify.retarget_bvh`) —
hier wird nichts nachgebaut, nur umgeformt. Was dabei umgerechnet werden muss
und warum, steht in `anim_umsetzung.py`.

Das Zielformat (aus `Animator::load_animation`, Zeile 486 ff.):

    nTS nJ
    je Keyframe:  zeit
                  nJ Zeilen  achse_x achse_y achse_z
                  nJ Werte   winkel            (Radiant)

Aufruf:
    python bvh_nach_anim.py --bvh <pfad.bvh> [--name gehen] [--bilder 60]

Ohne `--bvh` wird die erste BVH aus `3DObjects/animations/bvh/Walk/`
genommen. Geschrieben wird nach `figur/` neben die `.off` und `.skel`.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, r'A:\3DTools\HumanBody')

from anim_umsetzung import Animumsetzung                    # noqa: E402

DATEN = r'A:\3DTools\HumanBody\data\humanBody'
BVH_ORDNER = r'A:\3DTools\3DObjects\animations\bvh'
ZIEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figur')


class Animschreiber:
    u"""Schreibt eine Bewegung als `.anim` und prueft sie nach."""

    def __init__(self, stamm='hb_female'):
        self.stamm = stamm
        self.knochen = {b['name']: b for b in
                        json.load(open(os.path.join(DATEN, 'def_skeleton.json')))['bones']}
        self.gelenke, self.punkte = self._skel_lesen()
        self.umsetzung = Animumsetzung(self.knochen, self.gelenke,
                                       self._knochenlaengen(),
                                       punkte=self.punkte)

    def _knochenlaengen(self):
        u"""`tail - head` je Knochen, in Metern — fuer die Endgelenke."""
        rig = json.load(open(os.path.join(DATEN, 'rig_bones.json')))['bones']
        return {b['name']: float(np.linalg.norm(
            np.asarray(b['tail']) - np.asarray(b['head']))) for b in rig}

    def _skel_lesen(self):
        u"""Die `.skel`, die `figur_nach_fps.py` geschrieben hat.

        Sie ist die Wahrheit ueber Reihenfolge und Elternschaft — eine
        zweite Liste im Code liefe irgendwann auseinander.
        """
        pfad = os.path.join(ZIEL, self.stamm + '.skel')
        if not os.path.exists(pfad):
            raise SystemExit(u'Erst `figur_nach_fps.py` laufen lassen: %s fehlt'
                             % pfad)
        zeilen = open(pfad).read().strip().splitlines()
        gelenke, punkte = [], {}
        for zeile in zeilen[1:]:
            teile = zeile.split()
            name, elternteil = teile[3], teile[4]
            gelenke.append((name, None if elternteil == 'root' else elternteil))
            punkte[name] = np.array([float(x) for x in teile[:3]])
        return gelenke, punkte

    # ------------------------------------------------------------- Bewegung

    def spuren(self, bvh_pfad, hoehe=1.68):
        u"""Die Bewegung, ueber DENSELBEN Weg wie die Web-App.

        NICHT `SkeletonRigify.retarget_bvh` direkt aufrufen (10.09.2026,
        gemessen). Das ist im Projekt nur der RUECKFALL fuer ein unerkanntes
        Format; `Retargetdaten.holen` waehlt vorher die Bauart und nimmt
        deren eigene Zuordnung:

            bauart = Skeleton.detect_format(bvh.names)
            if bauart and bauart.BONE_MAP_TO_RIGIFY:
                return bauart.retarget_to_rigify(...)

        Mit dem Rueckfall auf einer CMU-Datei standen die ARME nach oben
        statt herunterzuhaengen — der Oberarm 121 Grad ueber der Senkrechten,
        und in der Simulation zerriss er. Die Beine sahen dabei richtig aus,
        weil deren Zuordnung auch ohne Bauart trifft.

        Das faellt sonst nirgends auf: Die Positionsprobe vergleicht die
        FPS-Kinematik gegen UNSERE — beide bekommen dieselben Spuren, also
        meldet sie 0,00 mm, gleich wie falsch die Spuren sind.

        Django wird gebraucht, weil `Skelettgeometrie` seine Pfade aus den
        Einstellungen nimmt. Es einzurichten ist billiger, als die Wahl der
        Bauart hier ein zweites Mal hinzuschreiben — zwei Fassungen laufen
        irgendwann auseinander.
        """
        self._django()
        from core.dienste.retargetdaten import Retargetdaten
        return Retargetdaten(bvh_pfad, body_height=hoehe).holen()

    @staticmethod
    def _django():
        u"""Django einrichten, falls es noch nicht steht."""
        import django
        from django.apps import apps
        if apps.ready:
            return
        web = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        if web not in sys.path:
            sys.path.insert(0, web)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')
        django.setup()

    #: Bild 0 der Retarget-Ausgabe ist ein STARTZUSTAND, keine Pose der
    #: Bewegung. Gemessen an `Walk/01_01` (10.09.2026): Zwischen Bild 0
    #: und 1 dreht sich `DEF-forearm.L` um 136 Grad, `DEF-upper_arm.R` um
    #: 80 — ab Bild 2 liegt der Median bei 1,22 Grad und kein einziges
    #: Bild ueber 10. Fuer eine Weichgewebe-Simulation ist dieser eine
    #: Sprung fatal: Der Loeser bekommt einen Schlag und schwingt ueber
    #: die ganze Ablage nach (gemessen 10 % der Punkte ueber 100 mm je
    #: Bild). Beim Abspielen im Browser faellt derselbe Sprung nicht
    #: auf, weil LBS kein Gedaechtnis hat — jedes Bild steht fuer sich.
    ERSTES_BILD = 1

    def schreiben(self, bewegung, name, hoechstzahl=None):
        u"""`.anim` fuer FPS. Gibt (Pfad, Bilder) zurueck."""
        spuren = bewegung.tracks
        ab = self.ERSTES_BILD
        gesamt = bewegung.frame_count - ab
        bilder = gesamt if not hoechstzahl else min(gesamt, hoechstzahl)
        pfad = os.path.join(ZIEL, '%s%s.anim' % (self.stamm, name))
        with open(pfad, 'w') as datei:
            datei.write('%d %d\n' % (bilder, len(self.umsetzung.namen)))
            for f in range(ab, ab + bilder):
                drehungen = self.umsetzung.bild(spuren, f)
                datei.write('%.6f\n' % (bewegung.times[f] - bewegung.times[ab]))
                winkel = []
                for gelenk in self.umsetzung.namen:
                    achse, wert = Animumsetzung.achse_winkel(drehungen[gelenk])
                    datei.write('%.6f %.6f %.6f\n' % tuple(achse))
                    winkel.append(wert)
                datei.write('\n'.join('%.6f' % w for w in winkel) + '\n')
        return pfad, bilder

    def pruefen(self, bewegung, bilder, roh=False):
        u"""Gegenprobe ohne FPS: FPS-Kinematik gegen unser Rig.

        Wenn die Umrechnung stimmt, stehen die Gelenke am selben Ort. Der
        Massstab der `.skel` ist der von FPS (Faktor 12,28 gegenueber
        Metern), deshalb wird durch ihn geteilt, um mm zu bekommen.
        """
        massstab = self._massstab()
        schlimmster, wo, erstes = 0.0, '', None
        ab = self.ERSTES_BILD
        for f in (ab, ab + bilder // 2, ab + bilder - 1):
            abweichung = self.umsetzung.gegenprobe(bewegung.tracks, f,
                                                   self.punkte, massstab, roh)
            if erstes is None:
                erstes = max(abweichung.values())
            for gelenk, wert in abweichung.items():
                if wert > schlimmster:
                    schlimmster, wo = wert, '%s (Bild %d)' % (gelenk, f)
        return schlimmster, wo, erstes

    def _massstab(self):
        u"""Einheiten je Meter, aus zwei Gelenken mit bekanntem Abstand."""
        a, b = 'DEF-spine', 'DEF-spine.001'
        in_fps = np.linalg.norm(self.punkte[b] - self.punkte[a])
        kopf_a = np.asarray(self.knochen[a]['head'] if 'head' in self.knochen[a]
                            else [0, 0, 0])
        del kopf_a
        # Der Abstand in Metern steht als `local_position` des Kindes.
        in_meter = np.linalg.norm(self.knochen[b]['local_position'])
        return in_fps / in_meter


def _erste_bvh():
    for wurzel, _ordner, dateien in os.walk(os.path.join(BVH_ORDNER, 'Walk')):
        for datei in sorted(dateien):
            if datei.lower().endswith('.bvh'):
                return os.path.join(wurzel, datei)
    return None


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--bvh', default=None)
    zerleger.add_argument('--name', default='0')
    zerleger.add_argument('--bilder', type=int, default=120)
    zerleger.add_argument('--stamm', default='hb_female')
    werte = zerleger.parse_args()

    bvh = werte.bvh or _erste_bvh()
    if not bvh or not os.path.exists(bvh):
        raise SystemExit(u'Keine BVH gefunden — bitte --bvh angeben')
    print(u'BVH      %s' % bvh)

    schreiber = Animschreiber(werte.stamm)
    bewegung = schreiber.spuren(bvh)
    print(u'Retarget %d Bilder, %d Spuren, %.2f s'
          % (bewegung.frame_count, len(bewegung.tracks), bewegung.duration))
    fehlend = [n for n, _ in schreiber.gelenke
               if not n.endswith('_ende') and n not in bewegung.tracks]
    print(u'         ohne eigene Spur: %s'
          % (', '.join(fehlend) if fehlend else 'keines'))

    pfad, bilder = schreiber.schreiben(bewegung, werte.name, werte.bilder)
    print(u'Datei    %s (%d Bilder)' % (os.path.basename(pfad), bilder))
    _probe(schreiber, bewegung, bilder)
    ini = _ini_ergaenzen(werte.stamm, werte.name)
    print(u'         %s ergaenzt' % os.path.basename(ini))
    return 0


def _probe(schreiber, bewegung, bilder):
    u"""Die Gelenkprobe — und ihre Sabotage-Gegenprobe."""
    schlimmster, wo, erstes = schreiber.pruefen(bewegung, bilder)
    print(u'Probe    groesste Abweichung der Gelenke: %.2f mm bei %s'
          % (schlimmster, wo))
    print(u'         (Bild 0: %.2f mm)' % erstes)
    # Sabotage-Gegenprobe: ohne das Delta gegen die Ruhelage MUSS die Probe
    # ausschlagen. Eine Probe, die immer 0,00 meldet, ist keine.
    kaputt, _wo, _erst = schreiber.pruefen(bewegung, bilder, roh=True)
    print(u'         Sabotage (Rigify-Drehung roh): %.1f mm — %s'
          % (kaputt, u'Probe greift' if kaputt > 10.0 else u'PROBE IST BLIND'))


def _ini_ergaenzen(stamm, name):
    u"""Die ANIMATION-Zeile der `.ini` auf diese Datei setzen."""
    ini = os.path.join(ZIEL, stamm + '.ini')
    with open(ini, encoding='utf-8') as datei:
        zeilen = [z for z in datei.read().splitlines() if not z.startswith('ANIMATION')]
    zeilen.append('ANIMATION   %s%s.anim %s' % (stamm, name, stamm))
    with open(ini, 'w', encoding='utf-8') as datei:
        datei.write('\n'.join(zeilen) + '\n')
    return ini


if __name__ == '__main__':
    sys.exit(main())
