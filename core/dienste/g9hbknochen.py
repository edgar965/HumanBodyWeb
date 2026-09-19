# -*- coding: utf-8 -*-
u"""G9hbknochen — Knochenrahmen von Genesis 9 und HumanBody (DEF), fuer eine
Paarung der Koerper, die Pose und Proportion NICHT voraussetzt.

WARUM (19.09.2026, erste Paarung nach naechsten Punkten): Die Grundfiguren
stehen verschieden — HumanBody haelt die Arme flacher (Aussenpunkt x 0,74 m
gegen 0,63, Armmitte 1,09 m hoch gegen 0,98), die Beine weiter (0,19 gegen
0,13) und den Rumpf 6 cm weiter vorn. Nach naechsten Punkten lag die Paarung
im Median 40 mm daneben, an den Armen bis 181 mm — das Stueck wuerde
zerrissen.

Deshalb wird jeder Genesis-Punkt in den RAHMEN SEINES KNOCHENS gebracht
(staerkster Knochen aus der Haut; Zwischenknochen ohne DEF-Gegenstueck —
Twist, Mittelhand, `spine4`, `neck2` — gehen auf den naechsten gepaarten
Vorfahren): Ursprung der Knochenkopf, erste Achse die Richtung zum
KINDGELENK (wie der Retarget seit dem 19.09.2026: `Richtungskorrektur`,
Gelenk zu Gelenk), zweite Achse die Aufwaertsrichtung ohne Anteil entlang
des Knochens (bei senkrechten Knochen die Vorwaertsrichtung), dritte das
Kreuzprodukt. Im Rahmen des DEF-Gegenstuecks (`DEF_ZU_G9`) wieder
zusammengesetzt — mit dem HOEHENMASSSTAB, nicht mit dem Laengenverhaeltnis
der Knochen: `hip` ist bei Genesis ein 2,2-cm-Stummel, `DEF-spine` 15 cm,
die Zehen 5 gegen 15 cm; das Verhaeltnis haette jeden Versatz versiebenfacht
(gemessen: Rumpf-Median 103 mm, p90 690 mm). Die Gliedmassen sind auf beiden
Seiten fast gleich lang (Oberarm 24,8 gegen 26,2 cm, Oberschenkel 40,5
gegen 41,4) — dort landet der Punkt, wo er an der HumanBody-Figur
hingehoert: Arme flacher, Beine weiter.

DER RUMPF GEHT ALS GANZES: Seine Knochen decken sich nicht Kopf fuer Kopf
(Genesis `hip` sitzt in Beckenmitte auf 0,97 m, `DEF-spine` am Schritt auf
0,81 und zeigt nach oben, `pelvis` nach unten). Fuer alle Rumpfknochen
(`RUMPF`) gilt EINE Aehnlichkeitsabbildung (Umeyama: Drehung, Massstab,
Verschiebung), gepasst ueber die Gelenke, die beide Rigs haben — Wirbel,
Hals, Kopf, Schultern, Hueft- und Oberarmgelenke.

Genesis liefert Kopf und Schwanz je Knochen (`G9formung.skelett().bauen()`,
Meter, Y oben, Fuesse am Boden); DEF liefert Kopf, Laenge und Weltdrehung
(`Skelettgeometrie`, Achse -Z) — der Schwanz eines Kettenknochens ist der
Kopf seines Kindes, sonst Kopf + Laenge entlang der Achse.
"""
import numpy as np

from humanbody_core.quaternion import Quat
from humanbody_core.skeleton.formats.g9_zuordnung import DEF_ZU_G9

__all__ = ['G9hbknochen']


class G9hbknochen:
    u"""Rahmen je Knochen auf beiden Seiten; `schaetzen` fuehrt Punkte hinueber."""

    #: Genesis-Knochen -> sein Kindgelenk in der Kette (beide Seiten gespiegelt).
    KINDER_LINKS = {
        'hip': 'spine1', 'spine1': 'spine2', 'spine2': 'spine3', 'spine3': 'neck1',
        'neck1': 'head', 'l_shoulder': 'l_upperarm', 'l_upperarm': 'l_forearm',
        'l_forearm': 'l_hand', 'l_hand': 'l_mid1', 'l_thigh': 'l_shin', 'l_shin': 'l_foot',
        'l_foot': 'l_toes', 'l_thumb1': 'l_thumb2', 'l_thumb2': 'l_thumb3',
        'l_index1': 'l_index2', 'l_index2': 'l_index3', 'l_mid1': 'l_mid2',
        'l_mid2': 'l_mid3', 'l_ring1': 'l_ring2', 'l_ring2': 'l_ring3',
        'l_pinky1': 'l_pinky2', 'l_pinky2': 'l_pinky3',
    }
    #: Unter diesem Sinus gilt ein Knochen als senkrecht: Aufwaerts taugt nicht.
    SENKRECHT = 0.2
    #: Rumpfknochen — eine Aehnlichkeitsabbildung fuer alle (Modulkopf).
    RUMPF = ('hip', 'pelvis', 'spine1', 'spine2', 'spine3', 'spine4', 'neck1', 'neck2',
             'head', 'l_pectoral', 'r_pectoral')
    #: Die Gelenke, ueber die die Rumpfabbildung gepasst wird.
    RUMPFGELENKE = ('spine1', 'spine2', 'spine3', 'neck1', 'head', 'l_shoulder',
                    'r_shoulder', 'l_upperarm', 'r_upperarm', 'l_thigh', 'r_thigh')

    def __init__(self, g9_knochen, def_welt, massstab=1.0):
        u"""`g9_knochen`: `[{name, eltern, kopf, schwanz}]`; `def_welt`:
        `SkeletonGeometry.compute_world_transforms()`; `massstab`: Hoehe
        HumanBody / Hoehe Genesis."""
        self.massstab = float(massstab)
        self.g9 = {k['name']: k for k in g9_knochen}
        self.g9_zu_def = {g9: d for d, g9 in DEF_ZU_G9.items() if g9}
        self.kinder = dict(self.KINDER_LINKS)
        self.kinder.update({'r' + k[1:]: 'r' + v[1:] for k, v in self.KINDER_LINKS.items()
                            if k.startswith('l_')})
        self.rahmen_g9 = {}
        self.rahmen_def = {}
        for name in self.g9:
            paar = self.gepaart(name)
            if paar is None or paar in self.rahmen_g9:
                continue
            defname = self.g9_zu_def[paar]
            if defname not in def_welt:
                continue
            self.rahmen_g9[paar] = self._rahmen(self._kopf_g9(paar), self._schwanz_g9(paar))
            self.rahmen_def[paar] = self._rahmen(
                np.asarray(def_welt[defname]['world_pos'], dtype=np.float64),
                self._schwanz_def(defname, paar, def_welt))
        self.rumpf = self._rumpfabbildung(def_welt)

    # ------------------------------------------------------------ Knochen

    def gepaart(self, name):
        u"""Der Knochen selbst, wenn er ein DEF-Gegenstueck hat, sonst der naechste
        Vorfahre mit einem — None ohne (Gesicht, Anhaenge)."""
        while name:
            if name in self.g9_zu_def:
                return name
            name = (self.g9.get(name) or {}).get('eltern')
        return None

    def _kopf_g9(self, name):
        return np.asarray(self.g9[name]['kopf'], dtype=np.float64)

    def _schwanz_g9(self, name):
        kind = self.kinder.get(name)
        if kind in self.g9:
            return self._kopf_g9(kind)
        return np.asarray(self.g9[name]['schwanz'], dtype=np.float64)

    def _schwanz_def(self, defname, g9name, welt):
        kind = self.kinder.get(g9name)
        kind_def = self.g9_zu_def.get(kind) if kind else None
        if kind_def in welt:
            return np.asarray(welt[kind_def]['world_pos'], dtype=np.float64)
        b = welt[defname]
        return np.asarray(b['world_pos'], dtype=np.float64) + Quat.rotate(
            np.asarray(b['world_quat'], dtype=np.float64), np.array([0.0, 0.0, -b['length']]))

    @classmethod
    def _rahmen(cls, kopf, schwanz):
        u"""`(kopf, Achsen (3, 3), Laenge)` — Achsen zeilenweise."""
        weg = schwanz - kopf
        laenge = float(np.linalg.norm(weg))
        if laenge < 1e-9:
            weg, laenge = np.array([0.0, 1.0, 0.0]), 1e-3
        d = weg / laenge
        hilfe = np.array([0.0, 0.0, 1.0]) if abs(d[1]) > 1.0 - cls.SENKRECHT else np.array([0.0, 1.0, 0.0])
        zweite = hilfe - np.dot(hilfe, d) * d
        zweite /= max(np.linalg.norm(zweite), 1e-9)
        return kopf, np.stack([d, zweite, np.cross(d, zweite)]), laenge

    def _rumpfabbildung(self, welt):
        u"""(R, s, t) mit HB = s·R·G9 + t ueber die Rumpfgelenke (Umeyama)."""
        quelle, ziel = [], []
        for name in self.RUMPFGELENKE:
            defname = self.g9_zu_def.get(name)
            if name in self.g9 and defname in welt:
                quelle.append(self._kopf_g9(name))
                ziel.append(np.asarray(welt[defname]['world_pos'], dtype=np.float64))
        if len(quelle) < 3:
            return np.eye(3), self.massstab, np.zeros(3)
        q, z = np.asarray(quelle), np.asarray(ziel)
        mq, mz = q.mean(axis=0), z.mean(axis=0)
        h = (q - mq).T @ (z - mz)
        u, sig, vt = np.linalg.svd(h)
        d = np.eye(3)
        d[2, 2] = np.sign(np.linalg.det(vt.T @ u.T))
        r = vt.T @ d @ u.T
        s = float(np.trace(np.diag(sig) @ d) / max(((q - mq) ** 2).sum(), 1e-12))
        return r, s, mz - s * (r @ mq)

    # ---------------------------------------------------------- Schaetzen

    def schaetzen(self, punkte, knochen):
        u"""(N, 3) Genesis-Punkte mit ihrem staerksten Knochen (Namen) -> (N, 3)
        Schaetzung in der HumanBody-Lage; Punkte ohne gepaarten Knochen
        bleiben, wo sie sind (`getroffen` sagt, welche)."""
        p = np.asarray(punkte, dtype=np.float64)
        aus = p.copy()
        getroffen = np.zeros(len(p), dtype=bool)
        namen = np.asarray([self.gepaart(k) or '' for k in knochen])
        r, s, t = self.rumpf
        rumpf = np.isin(namen, self.RUMPF)
        if rumpf.any():
            aus[rumpf] = (s * (p[rumpf] @ r.T)) + t
            getroffen[rumpf] = True
        for name in set(namen[~rumpf]) - {''}:
            wo = namen == name
            kopf, achsen, _laenge = self.rahmen_g9[name]
            kopf_d, achsen_d, _laenge_d = self.rahmen_def[name]
            lokal = (p[wo] - kopf) @ achsen.T * self.massstab
            aus[wo] = kopf_d + lokal @ achsen_d
            getroffen[wo] = True
        return aus, getroffen
