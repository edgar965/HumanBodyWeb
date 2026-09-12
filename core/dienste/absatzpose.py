# -*- coding: utf-8 -*-
"""Absatzpose — die Fussbeugung eines Absatzschuhs als Teil der Pose.

WARUM HIER, NICHT IM BETRACHTER (11.09.2026, Edgar: „der Betrachter soll
bei einem Absatzschuh gar nichts tun, sondern das Programm soll die Pose
ändern!"): Bis dahin drehte `garmentcode_absatz.js` die Fussknochen
selbst — alle zwei Sekunden nachgesehen, Vorzeichen per Probedrehung,
Hub an der Figurgruppe. Jetzt rechnet der Server die Beugung in die
Pose hinein: `Posen.pose` liefert jede Pose (auch die Ruhelage) mit den
Fuss- und Zehendrehungen, und der Betrachter wendet sie an wie jede
andere Pose (`Posenanwendung.anwenden`). Der Hub steht als `hebung_m`
daneben, weil eine Pose nur Drehungen kennt.

DIE RECHNUNG: Posen sind Deltas im KNOCHENRAUM (`q_rest * delta`,
`PoseData`). Der Fuss soll um die Querachse der Figur (x) um den
Beugewinkel drehen, die Ferse steigt; die Zehen drehen dieselbe Achse
zurück und um die Sprengung weiter, damit sie flach liegen bzw. die
Spitze steigt. Ein Weltdreh `R` wird zum Knochendelta über die Ruhelage
des Knochens in der Welt: `delta = q_welt^-1 * R * q_welt` — `q_welt`
aus `def_skeleton.json` (lokale Quaternionen, Elternkette). Trägt die
Pose den Fuss schon gedreht, wird das Absatzdelta dahinter angehängt
(`pose_delta * absatz_delta`): die Beugung folgt dem Bein.

Alles in Blenders Achsen ([w, x, y, z], Z oben); die Querachse x ist in
beiden Welten dieselbe, und `to_threejs` benennt am Ende um wie bei jeder
Pose ([x, z, -y, w]).
"""
import json
import math
import os

from django.conf import settings

__all__ = ['Absatzpose']


class Absatzpose:
    """Fuss- und Zehendeltas für einen Absatz, zum Einrechnen in eine Pose."""

    FUSS = ('DEF-foot.L', 'DEF-foot.R')
    ZEHEN = ('DEF-toe.L', 'DEF-toe.R')
    #: Was der Betrachter mitschickt (Grad, cm) — `Fussbeugung.beschreibung`.
    FELDER = ('winkel_grad', 'sprengung_grad', 'hebung_cm', 'plateau_cm')

    _skelette = {}

    def __init__(self, winkel_grad=0.0, sprengung_grad=0.0, hebung_cm=0.0,
                 plateau_cm=0.0, geschlecht='female'):
        self.winkel_grad = float(winkel_grad or 0.0)
        self.sprengung_grad = float(sprengung_grad or 0.0)
        self.hebung_cm = float(hebung_cm or 0.0)
        self.plateau_cm = float(plateau_cm or 0.0)
        self.geschlecht = geschlecht

    @classmethod
    def aus_anfrage(cls, werte, geschlecht='female'):
        """Aus den Abfrageparametern einer Anfrage — None ohne Absatz."""
        def zahl(name):
            try:
                return float(werte.get(name) or 0.0)
            # stumm gewollt: ein unlesbarer Abfrageparameter heisst 'kein Absatz'
            except (TypeError, ValueError):
                return 0.0
        pose = cls(*[zahl(name) for name in cls.FELDER], geschlecht=geschlecht)
        return pose if pose.aktiv else None

    @property
    def aktiv(self):
        return self.winkel_grad > 0.0 or self.sprengung_grad > 0.0

    @property
    def hebung_m(self):
        return (self.hebung_cm + self.plateau_cm) / 100.0

    def beschreibung(self):
        return {'winkel_grad': self.winkel_grad, 'sprengung_grad': self.sprengung_grad,
                'hebung_cm': self.hebung_cm, 'plateau_cm': self.plateau_cm}

    # ------------------------------------------------------------- Skelett

    @classmethod
    def skelettdatei(cls, geschlecht):
        ordner = str(settings.HUMANBODY_DATA_DIR)
        if geschlecht == 'male':
            ordner += '_male'
        return os.path.join(ordner, 'def_skeleton.json')

    @classmethod
    def ruhelagen(cls, geschlecht):
        """{Knochen: Weltquaternion [w,x,y,z] in der Ruhelage} — einmal gelesen."""
        if geschlecht not in cls._skelette:
            with open(cls.skelettdatei(geschlecht), 'r', encoding='utf-8') as datei:
                knochen = {b['name']: b for b in json.load(datei)['bones']}
            welt = {}

            def weltlage(name):
                if name in welt:
                    return welt[name]
                eintrag = knochen[name]
                lokal = eintrag.get('local_quaternion') or [1.0, 0.0, 0.0, 0.0]
                eltern = eintrag.get('parent')
                welt[name] = (cls.mal(weltlage(eltern), lokal)
                              if eltern in knochen else list(lokal))
                return welt[name]

            for name in cls.FUSS + cls.ZEHEN:
                if name in knochen:
                    weltlage(name)
            cls._skelette[geschlecht] = welt
        return cls._skelette[geschlecht]

    # ------------------------------------------------------------- Rechnen

    @staticmethod
    def mal(a, b):
        """Hamilton-Produkt zweier [w, x, y, z]."""
        w1, x1, y1, z1 = a
        w2, x2, y2, z2 = b
        return [w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2]

    @staticmethod
    def invers(q):
        return [q[0], -q[1], -q[2], -q[3]]

    @staticmethod
    def um_x(grad):
        """Drehung um die Querachse der Figur, [w, x, y, z]."""
        halb = math.radians(grad) / 2.0
        return [math.cos(halb), math.sin(halb), 0.0, 0.0]

    def deltas(self):
        """{Knochen: Delta [w,x,y,z] im Knochenraum} — Fuss und Zehen."""
        welt = self.ruhelagen(self.geschlecht)
        aus = {}
        for namen, grad in ((self.FUSS, self.winkel_grad),
                            (self.ZEHEN, -(self.winkel_grad + self.sprengung_grad))):
            for name in namen:
                if name not in welt:
                    continue
                q = welt[name]
                aus[name] = self.mal(self.mal(self.invers(q), self.um_x(grad)), q)
        return aus

    def einrechnen(self, def_bones):
        """Eine Pose ({DEF-Name: [w,x,y,z]}) um den Absatz ergänzen — Kopie."""
        pose = {name: list(q) for name, q in (def_bones or {}).items()}
        for name, delta in self.deltas().items():
            pose[name] = self.mal(pose.get(name, [1.0, 0.0, 0.0, 0.0]), delta)
        return pose

    @staticmethod
    def to_threejs(def_bones):
        """Wie `PoseData.to_threejs`: Blender [w,x,y,z] -> Three.js [x,z,-y,w]."""
        return {name: [q[1], q[3], -q[2], q[0]] for name, q in def_bones.items()}
