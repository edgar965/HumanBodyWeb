# -*- coding: utf-8 -*-
u"""Schreibt die HumanBody-Figur in das Dateiformat von `fast-cody`.

WARUM DIESE DATEI (Edgar, 10.09.2026: „was fehlt noch??"): `fast-cody`
liefert seine Beispielfigur fertig aufbereitet mit — unsere nicht. Es
braucht drei Dinge, und alle drei liegen im Projekt schon vor, nur in einer
anderen Form:

    rig.json    V  Hautpunkte            <- morphs/L1/<Bauart>.npy
                W  Hautgewichte          <- skin_weights_base.json
                p0 Ruhelage je Knochen   <- def_skeleton.json
                pI Elternnummern         <- dieselbe Datei
    anim.json   P  Weltlagen je Bild     <- Retarget ueber `Animumsetzung`

ALLES BLEIBT IN METERN. Der FPS-Weg skaliert auf die Hoehe des
`male`-Beispiels (Faktor 20,86/Figurhoehe); `fast-cody` skaliert selbst
(`scale_and_center_geometry`). Zwei Skalierungen hintereinander waren bei
FPS eine der Fehlerquellen.

DIE RUHEPROBE STEHT NICHT HIER, sondern in `koerperlauf.py`: Sie muss durch
DEREN Rechenweg laufen (`world2rel` + `lbs_jacobian`), sonst prueft sie nur
die eigene Arithmetik gegen sich selbst und meldet immer null.

Aufruf:  python figur_nach_cody.py [--geschlecht female] [--bvh <pfad>]
"""
import argparse
import json
import os
import sys

import numpy as np

import figur_nach_fps
from figur_nach_fps import Hautnetz, KETTE, ERSATZELTERN, _HAND_KETTE

ORDNER = os.path.dirname(os.path.abspath(__file__))
WURZEL = {'female': r'A:\3DTools\HumanBody\data\humanBody',
          'male': r'A:\3DTools\HumanBody\data\humanBody_male'}
ZIEL = os.path.join(ORDNER, 'cody')


class Codyfigur:
    u"""Netz, Gewichte, Skelett und Bewegung in der Form von `fast-cody`."""

    def __init__(self, geschlecht='female', bauart=None, mit_fingern=False):
        self.wurzel = WURZEL[geschlecht]
        self.geschlecht = geschlecht
        netz = Hautnetz(self.wurzel, bauart=bauart, geschlecht=geschlecht)
        self.punkte, self.dreiecke, _ = netz.aussenhaut()
        self.gewaehlt = self._hautindizes(netz)
        rohbau = json.load(
            open(os.path.join(self.wurzel, 'def_skeleton.json')))
        if isinstance(rohbau, dict) and 'bones' in rohbau:
            rohbau = rohbau['bones']
        if isinstance(rohbau, list):
            rohbau = {b['name']: b for b in rohbau}
        self.knochen = rohbau
        self.namen = self._auswahl(mit_fingern)

    @staticmethod
    def _hautindizes(netz):
        u"""Die urspruenglichen Nummern der Aussenhautpunkte.

        `aussenhaut()` gibt die Punkte gefiltert zurueck, aber nicht ihre
        Nummern — und genau die braucht die Gewichtstabelle, die nach dem
        BASISNETZ nummeriert ist.
        """
        if netz.materialien is None:
            gewaehlt = np.ones(len(netz.vierecke), dtype=bool)
        else:
            nummern = [i for i, n in enumerate(netz.materialien)
                       if n in figur_nach_fps.HAUT]
            gewaehlt = np.isin(netz.flaechenmaterial, nummern)
        q = netz.vierecke[gewaehlt]
        return np.unique(np.vstack([q[:, [0, 1, 2]], q[:, [0, 2, 3]]]))

    def _auswahl(self, mit_fingern):
        u"""Die Knochen, die mitrechnen — Eltern immer vor Kindern."""
        kette = KETTE if mit_fingern else tuple(
            n for n in KETTE if n not in _HAND_KETTE)
        aus, gesetzt = [], set()

        def eintragen(name):
            if name in gesetzt or name not in self.knochen:
                return
            elternteil = ERSATZELTERN.get(
                name, self.knochen[name].get('parent'))
            if elternteil in kette:
                eintragen(elternteil)
            if name in gesetzt:
                return
            gesetzt.add(name)
            aus.append(name)

        for name in kette:
            eintragen(name)
        return aus

    # ------------------------------------------------------------- Gewichte

    def gewichte(self):
        u"""n x b Hautgewichte, auf Zeilensumme 1 gebracht.

        Knochen ausserhalb der Auswahl (Finger, Gesicht) geben ihr Gewicht
        an den naechsten Vorfahren AB, statt es zu verlieren: Sonst haette
        eine Hand Zeilensumme 0,3 und fiele beim Skinning zusammen.
        """
        tabelle = json.load(
            open(os.path.join(self.wurzel, 'skin_weights_base.json')))
        namen, roh = tabelle['bone_names'], tabelle['weights']
        spalte = {name: i for i, name in enumerate(self.namen)}
        umleitung = {}
        for name in namen:
            ziel, lauf = None, name
            while lauf:
                if lauf in spalte:
                    ziel = spalte[lauf]
                    break
                lauf = (self.knochen.get(lauf) or {}).get('parent')
            umleitung[name] = ziel

        aus = np.zeros((len(self.punkte), len(self.namen)))
        for zeile, alt in enumerate(self.gewaehlt):
            for name, wert in self._paare(roh[int(alt)], namen):
                ziel = umleitung.get(name)
                if ziel is not None:
                    aus[zeile, ziel] += float(wert)
        summe = aus.sum(axis=1, keepdims=True)
        leer = int((summe <= 1e-9).sum())
        return aus / np.maximum(summe, 1e-9), leer

    @staticmethod
    def _paare(eintrag, namen):
        u"""(Knochenname, Gewicht) — die Tabelle kennt drei Schreibweisen."""
        if isinstance(eintrag, dict):
            if 'bones' in eintrag:
                return list(zip(eintrag['bones'], eintrag['weights']))
            return list(eintrag.items())
        if eintrag and isinstance(eintrag[0], (list, tuple)):
            return [(namen[int(i)], w) for i, w in eintrag]
        return [(namen[i], w) for i, w in enumerate(eintrag) if w]

    # -------------------------------------------------------------- Skelett

    def _welt(self, spuren=None, nummer=0, ort=None):
        u"""(position, weltdrehung) je Knochen — Ruhe oder eine Pose.

        `ort` ist die Ortsbewegung der Wurzel. OHNE SIE GIBT ES KEINE
        PHYSIK: Eine Figur, die auf der Stelle tritt, erfaehrt keine
        Beschleunigung, und genau die treibt das Nachschwingen.
        """
        from anim_umsetzung import Animumsetzung
        welt = {}

        def loesen(name):
            if name in welt:
                return welt[name]
            knochen = self.knochen[name]
            spur = (spuren or {}).get(name)
            if spur is not None:
                lokal = self.nach_blender(
                    np.asarray(spur[nummer * 4:nummer * 4 + 4],
                               dtype=np.float64))
            else:
                lokal = Animumsetzung._wxyz(knochen['local_quaternion'])
            versatz = np.asarray(knochen['local_position'], dtype=np.float64)
            elternteil = knochen.get('parent')
            if not elternteil or elternteil not in self.knochen:
                # Die Wurzel sitzt NICHT im Ursprung: `DEF-spine` steht bei
                # z = 0,81 (Befund vom 10.09.2026).
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
    def nach_blender(q):
        u"""Retargetdrehung von Three.js-Lage in die Lage des Rigs.

        DER FEHLER, DER DREI TAGE GEKOSTET HAT. Die Retargetspuren kommen
        in Three.js-Lage (y oben), `def_skeleton.json` steht in Blender-Lage
        (z oben, gemessen: `DEF-spine.local_position` = (0, -0,019, 0,810),
        die Wurzelbahn derselben Bewegung = (0, 0,810, 0,019)). Der Weg
        hinueber ist `[x, z, -y, w]` (CLAUDE.md, `to_threejs`), also
        zurueck `[x, -z, y, w]`.

        OHNE DIESE ZEILE stehen beide Haende in Bild 0 bei z = 1,84, also
        UEBER dem Kopf und in der Koerpermitte — die „erhobenen Arme" des
        FPS-Videos. Becken, Beine und Kopf sehen dabei richtig aus, weil
        deren Ruhelage nahe der Drehachse liegt; erst der Arm mit 0,6 m
        Hebel macht es sichtbar.

        BELEGT gegen die BVH-Quelle (Walk/01_01, unabhaengige Referenz):
        dort steht die linke Hand in Bild 5 bis 40 UEBER der Schulter und
        die rechte weit darunter — dieselbe Asymmetrie, die diese
        Umrechnung liefert. Eine Probe gegen das eigene Rig kann das nicht
        finden: Sie fuettert beide Seiten mit derselben, falsch
        verstandenen Eingabe und meldet 0,00 mm.
        """
        return np.array([q[0], -q[2], q[1], q[3]], dtype=np.float64)

    @staticmethod
    def _matrix(punkt, quat):
        u"""3 x 4 aus Weltposition und Weltdrehung."""
        from anim_umsetzung import Animumsetzung
        dreh = np.column_stack([Animumsetzung.drehen(quat, e)
                                for e in np.eye(3)])
        return np.hstack([dreh, np.asarray(punkt).reshape(3, 1)])

    def ruhelagen(self):
        u"""b x 3 x 4 — die Lage jedes Knochens in der Ruhehaltung."""
        welt = self._welt()
        return np.array([self._matrix(*welt[n]) for n in self.namen])

    def eltern(self):
        u"""Elternnummer je Knochen, -1 fuer die Wurzel."""
        nummer = {n: i for i, n in enumerate(self.namen)}
        aus = []
        for name in self.namen:
            lauf = ERSATZELTERN.get(name, self.knochen[name].get('parent'))
            while lauf and lauf not in nummer:
                lauf = (self.knochen.get(lauf) or {}).get('parent')
            aus.append(nummer.get(lauf, -1) if lauf else -1)
        return np.array(aus, dtype=np.int64)

    #: Bild 0 des Retargets ist ein STARTZUSTAND, kein Bewegungsbild: Von
    #: Bild 0 auf 1 springen die Knochenlagen im Median von 0,027 auf
    #: 0,123 m. Ein Loeser sieht darin eine unendliche Beschleunigung und
    #: liefert ab Bild 30 NaN. Derselbe Befund wie im FPS-Weg
    #: (`bvh_nach_anim.ERSTES_BILD`).
    ERSTES_BILD = 1

    #: Vorlaufbilder in der ANFANGSHALTUNG, bevor die Bewegung einsetzt.
    #: Sie geben dem Weichgewebe Zeit, sich zu setzen — sonst zappelt es
    #: aus dem Stand heraus los.
    VORLAUF = 30

    def bahn(self, spuren, bilder, orte=None):
        u"""bilder x b x 3 x 4 — die Weltlage jedes Knochens je Bild.

        `orte` ist die Wurzelbahn, gegen BILD 0 verrechnet: Die Ruhelage
        `p0` steht am Ursprung, und ein absoluter Startversatz waere ein
        Sprung im ersten Bild — genau der Fehler, der beim FPS-Weg 136 Grad
        Sprung erzeugt hat.
        """
        erst = self.ERSTES_BILD
        folge = [erst] * self.VORLAUF + list(range(erst, erst + bilder))
        aus = np.zeros((len(folge), len(self.namen), 3, 4))
        for platz, nummer in enumerate(folge):
            ort = None
            if orte is not None:
                ort = np.asarray(orte[nummer]) - np.asarray(orte[erst])
            welt = self._welt(spuren, nummer, ort)
            for i, name in enumerate(self.namen):
                aus[platz, i] = self._matrix(*welt[name])
        return aus

    # -------------------------------------------------------------- Ausgabe

    def schreiben(self, ordner, spuren=None, bilder=0, orte=None):
        os.makedirs(ordner, exist_ok=True)
        gewichte, leer = self.gewichte()
        p0 = self.ruhelagen()
        rig = os.path.join(ordner, 'hb_%s_rig.json' % self.geschlecht)
        with open(rig, 'w') as datei:
            json.dump({'V': self.punkte.tolist(),
                       'F': self.dreiecke.tolist(),
                       'W': gewichte.tolist(),
                       'p0': p0.tolist(),
                       'lengths': [0.0] * len(self.namen),
                       'pI': self.eltern().tolist(),
                       'namen': self.namen}, datei)
        anim = None
        if spuren and bilder:
            anim = os.path.join(ordner, 'hb_%s_anim.json' % self.geschlecht)
            with open(anim, 'w') as datei:
                json.dump({'P': self.bahn(spuren, bilder, orte).tolist()},
                          datei)
        return rig, anim, gewichte, leer


def main():
    zerleger = argparse.ArgumentParser(description=__doc__)
    zerleger.add_argument('--geschlecht', default='female')
    zerleger.add_argument('--bauart', default=None)
    zerleger.add_argument('--bilder', type=int, default=240)
    zerleger.add_argument('--bvh', default=None)
    werte = zerleger.parse_args()

    figur = Codyfigur(werte.geschlecht, werte.bauart)
    print(u'Haut      %d Punkte, %d Dreiecke'
          % (len(figur.punkte), len(figur.dreiecke)))
    print(u'Skelett   %d Knochen (ohne Finger)' % len(figur.namen))

    spuren, bilder, orte = None, 0, None
    if werte.bvh:
        from bvh_nach_anim import Animschreiber
        daten = Animschreiber('hb_%s' % werte.geschlecht).spuren(werte.bvh)
        spuren = daten.tracks
        bilder = min(werte.bilder,
                     daten.frame_count - Codyfigur.ERSTES_BILD)
        if daten.position_track:
            # ACHSENWECHSEL: Die Wurzelbahn kommt in Three.js-Lage (y oben),
            # Netz und `local_position` stehen in Blender-Lage (z oben).
            # Geprueft an Bild 0: Bahn (0, 0,8102, 0,0189) entspricht
            # `DEF-spine.local_position` (0, -0,0189, 0,8102) — also
            # (x, y, z) -> (x, -z, y). Ohne diesen Schritt laeuft die Figur
            # seitwaerts in den Boden, ohne dass ein Fehler entsteht.
            bahn = np.asarray(daten.position_track['values'],
                              dtype=np.float64).reshape(-1, 3)
            orte = np.column_stack([bahn[:, 0], -bahn[:, 2], bahn[:, 1]])
        print(u'Bewegung  %d Spuren, %d von %d Bildern, Wurzelbahn %s'
              % (len(spuren), bilder, daten.frame_count,
                 u'ja' if orte is not None else u'nein'))

    rig, anim, gewichte, leer = figur.schreiben(ZIEL, spuren, bilder, orte)
    print(u'Gewichte  Zeilensumme min %.4f, Punkte ohne Gewicht %d'
          % (float(gewichte.sum(axis=1).min()), leer))
    print(u'Rig       %s (%.1f MB)' % (rig, os.path.getsize(rig) / 1048576.0))
    if anim:
        print(u'Anim      %s (%.1f MB)'
              % (anim, os.path.getsize(anim) / 1048576.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
