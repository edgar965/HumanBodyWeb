# -*- coding: utf-8 -*-
"""Haltungsbezug: LaFAN (StayStill) — Null-Lage ohne Haltung, Becken stand 90° verdreht.

Befund (09.10.2026): Nach dem Retarget lag die Querachse der Hüfte DEF gegen Quelle in jedem
Bild 90,00° daneben, jeder Knochen stand um die eigene Achse verdreht, die Brust zeigte auf die
rechte Schulter. `retarget/haltungsbezug.py` (Wurzelbasis, Kindwahl auf der Zielseite, Drehung
um die Achse aus den neutralsten Bildern), nur für Formate mit `HALTUNGSBEZUG = True`.

EICHFALL MIT BEKANNTER WAHRHEIT (wie `test_handausrichtung`): Die Quelle ist die DEF-Ruhelage
selbst, im LaFAN-Skelett und in LaFAN-Art gebaut — jedes Gelenk legt seinen Knochen entlang
lokal +X, mit zufälliger Drehung um diese Achse, die Wurzel ganz zufällig. Bilder 0–11 Ruhe,
12–23 der ganze Körper um eine bekannte Drehung Q gedreht, 24–29 dazu der linke Unterarm 50°
gebeugt. Wahrheit: jede DEF-Weltdrehung = (Q ×) (Beugung ×) Ruhe.

Gemessen beim Bau (`ProjektTemp/_wegwerf/staystill_wurzel/eichfall.py`): neu 0,000° je Knochen
außer `DEF-spine.004` 2,79° (Hals: DEF misst die Achse, die Quelle Gelenk zu Gelenk — bei
allen Formaten so); ohne Haltungsbezug bis 178°.

Sabotage-Gegenprobe: `Haltungsbezug._mit_drehung` nur `schwenk` zurückgeben lassen → Fall 1
rot; `Wurzelbasis.drehung` → `None` → Fall 1 und 3 rot.

GESCHRIEBEN 09.10.2026, NICHT GELAUFEN (Tests nur auf Ansage).
"""

import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton.formats.lafan import SkeletonLaFAN  # noqa: E402
from humanbody_core.skeleton.retarget.bvhdaten import BVHData  # noqa: E402
from humanbody_core.skeleton.retarget.motor import retarget_bvh_to_rigify  # noqa: E402
from humanbody_core.skeleton.retarget.wurzelbasis import Wurzelbasis  # noqa: E402
from humanbody_core.skeleton.skeleton import Skeleton  # noqa: E402

from core.dienste.skelettgeometrie import Skelettgeometrie  # noqa: E402

#: LaFAN-Gelenke (Name, Eltern) in der Reihenfolge des LaFAN-Kopfes.
GELENKE = [
    ('Hips', None), ('LeftUpLeg', 'Hips'), ('LeftLeg', 'LeftUpLeg'), ('LeftFoot', 'LeftLeg'),
    ('LeftToe', 'LeftFoot'), ('RightUpLeg', 'Hips'), ('RightLeg', 'RightUpLeg'),
    ('RightFoot', 'RightLeg'), ('RightToe', 'RightFoot'), ('Spine', 'Hips'), ('Spine1', 'Spine'),
    ('Spine2', 'Spine1'), ('Neck', 'Spine2'), ('Head', 'Neck'), ('LeftShoulder', 'Spine2'),
    ('LeftArm', 'LeftShoulder'), ('LeftForeArm', 'LeftArm'), ('LeftHand', 'LeftForeArm'),
    ('RightShoulder', 'Spine2'), ('RightArm', 'RightShoulder'), ('RightForeArm', 'RightArm'),
    ('RightHand', 'RightForeArm'),
]
X = np.array([1.0, 0.0, 0.0])


def um_achse(achse, grad):
    achse = np.asarray(achse, float) / np.linalg.norm(achse)
    h = np.radians(grad) / 2
    return np.array([*(achse * np.sin(h)), np.cos(h)])


def winkel(a, b):
    return float(np.degrees(2 * np.arccos(min(1.0, abs(float(np.dot(a, b)))))))


class LafanEichfall(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skel = Skelettgeometrie.holen()
        cls.karte = SkeletonLaFAN.BONE_MAP_TO_RIGIFY
        cls.bvh, cls.q, cls.beuge = cls._bauen(np.random.default_rng(7))
        cls.neu = SkeletonLaFAN.retarget_to_rigify(cls.bvh, cls.skel, body_height=1.68)
        cls.alt = retarget_bvh_to_rigify(cls.bvh, cls.skel, mapping=cls.karte, body_height=1.68,
                                         haltungsbezug=False)

    @classmethod
    def _bauen(cls, rng):
        welt = cls.skel.compute_world_transforms()
        namen = [g[0] for g in GELENKE]
        eltern = np.array([namen.index(e) if e else -1 for _, e in GELENKE])
        kinder = {i: [j for j in range(len(namen)) if eltern[j] == i] for i in range(len(namen))}
        pos = np.array([welt[cls.karte[n]]['world_pos'] * 100.0 for n in namen])
        w = []
        for j, n in enumerate(namen):
            if eltern[j] < 0:
                q = rng.normal(size=4)
                w.append(q / np.linalg.norm(q))
                continue
            d = (pos[kinder[j][0]] - pos[j]) if kinder[j] else Quat.rotate(
                cls.skel.bones[cls.karte[n]].world_rest_quat, np.array([0, 0, -1.0]))
            w.append(Quat.norm(Quat.mul(Quat.from_unit_vectors(X, d / np.linalg.norm(d)),
                                        um_achse(X, rng.uniform(-180, 180)))))
        offsets = np.zeros((len(namen), 3))
        for j in range(len(namen)):
            if eltern[j] >= 0:
                offsets[j] = Quat.rotate(Quat.inv(w[eltern[j]]), pos[j] - pos[eltern[j]])
        q_dreh = Quat.norm(Quat.mul(um_achse([0, 1, 0], 35), um_achse([1, 0, 0], 20)))
        arm = welt['DEF-hand.L']['world_pos'] - welt['DEF-forearm.L']['world_pos']
        beuge = um_achse(np.cross(arm, [0, 1, 0]), 50)
        fa = namen.index('LeftForeArm')
        quats = np.zeros((30, len(namen), 4))
        for f in range(30):
            wf = [Quat.mul(q_dreh, x) for x in w] if f >= 12 else list(w)
            if f >= 24:
                for j in (fa, namen.index('LeftHand')):
                    wf[j] = Quat.mul(q_dreh, Quat.mul(beuge, w[j]))
            for j in range(len(namen)):
                e = eltern[j]
                quats[f, j] = wf[j] if e < 0 else Quat.norm(Quat.mul(Quat.inv(wf[e]), wf[j]))
        positions = np.tile(pos[0], (30, len(namen), 1))
        bvh = BVHData(names=namen, parents=eltern, offsets=offsets, quats=quats,
                      positions=positions, frametime=1 / 30.0, frame_count=30, children=kinder)
        return bvh, q_dreh, beuge

    def _welt(self, spuren, name, bild):
        kette, n = [], name
        while n:
            kette.append(n)
            n = self.skel.bones[n].parent_name
        q = Quat.ID.copy()
        for k in reversed(kette):
            spur = spuren.tracks.get(k)
            lokal = np.asarray(spur[bild * 4:bild * 4 + 4]) if spur else self.skel.bones[k].rest_local_quat
            q = Quat.norm(Quat.mul(q, lokal))
        return q

    def _wahrheit(self, name, bild):
        ruhe = self.skel.bones[name].world_rest_quat
        if bild < 12:
            return ruhe
        if bild >= 24 and name in ('DEF-forearm.L', 'DEF-hand.L'):
            return Quat.mul(self.q, Quat.mul(self.beuge, ruhe))
        return Quat.mul(self.q, ruhe)

    def _groesster_fehler(self, spuren):
        return max(winkel(self._welt(spuren, n, b), self._wahrheit(n, b))
                   for n in spuren.tracks if n != 'DEF-spine.004' for b in range(30))

    def test_1_jeder_knochen_trifft_die_wahrheit(self):
        self.assertLess(self._groesster_fehler(self.neu), 0.05)

    def test_2_ohne_haltungsbezug_ist_es_falsch(self):
        """Gegenprobe: derselbe Fall durch den alten Weg muss weit daneben liegen."""
        self.assertGreater(self._groesster_fehler(self.alt), 30.0)

    def test_3_becken_querachse_wie_die_quelle(self):
        for bild in (0, 15, 27):
            q = self._welt(self.neu, 'DEF-spine', bild)
            self.assertLess(winkel(q, self._wahrheit('DEF-spine', bild)), 0.05)

    def test_4_hals_bleibt_beim_bekannten_rest(self):
        """DEF-spine.004: Achse gegen Gelenk-zu-Gelenk, 2,79° beim Bau — nicht mehr."""
        fehler = max(winkel(self._welt(self.neu, 'DEF-spine.004', b),
                            self._wahrheit('DEF-spine.004', b)) for b in range(30))
        self.assertLess(fehler, 3.5)


class LafanEichfallMitAusnahmen(LafanEichfall):
    """Wie oben, aber die Schlüsselbeine sind von der Richtungskorrektur ausgenommen (wie auf Genesis 9).

    Befund (09.10.2026, abends): `Haltungsbezug` gab ausgenommenen Knochen die Korrektur des Elternknochens; auf Genesis 9
    stand das Schlüsselbein 93,3° neben der Quelle. Jetzt `Starrlage`: Ruhelage plus Quelldrehung. Gemessen
    (`staystill_wurzel/eichfall.py motor`, SKIP=1): Schlüsselbeine 0,000°; mit dem alten Stand (SKIPALT=1) 130,6° / 114,6°,
    Oberarme bis 87°. Sabotage: `Haltungsbezug._starr` → `self._geerbt(name, korr)` macht Fall 1 rot.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.neu = SkeletonLaFAN.retarget_to_rigify(cls.bvh, cls.skel, body_height=1.68,
                                                   skip_bones=['DEF-shoulder.L', 'DEF-shoulder.R'])


class StarrlageTest(SimpleTestCase):
    databases = set()

    def test_bekannte_drehung_wird_getroffen(self):
        """W · V = starr für ein bekanntes V — auch wenn das Vorzeichen der Quaternionen springt."""
        from humanbody_core.skeleton.retarget.starrlage import Starrlage

        rng = np.random.default_rng(3)
        w = rng.normal(size=(12, 4))
        w /= np.linalg.norm(w, axis=1)[:, None]
        v = Quat.norm(um_achse([0.2, 1.0, 0.4], 61))
        ruhe = Quat.norm(um_achse([1.0, 0.3, 0.0], 25))
        starr = Quat.mul_reihe(w, np.tile(v, (12, 1)))
        w[::2] *= -1.0  # dieselbe Drehung, anderes Vorzeichen
        korr = Starrlage.korrektur(w, starr, ruhe)
        self.assertLess(winkel(Quat.mul(korr, ruhe), v), 0.01)

    def test_gelenkrichtung_nur_wo_das_ziel_sie_fuehrt(self):
        """`_ruhe`: Weg von Gelenk zu Gelenk bei `gelenkrichtung`, sonst die Achse."""
        from humanbody_core.skeleton.retarget.haltungsbezug import Haltungsbezug

        class Knochen:
            world_rest_quat = Quat.ID.copy()

        class Ziel:
            richtungsachse = np.array([0.0, 0.0, -1.0])
            bones = {'A': Knochen(), 'B': Knochen()}

            def __init__(self, gelenkrichtung):
                self.gelenkrichtung = gelenkrichtung

            def compute_world_transforms(self):
                return {'A': {'world_pos': np.zeros(3)}, 'B': {'world_pos': np.array([0.2, 0.0, -1.0])}}

        for gelenkrichtung, erwartet in ((True, np.array([0.2, 0.0, -1.0])), (False, np.array([0.0, 0.0, -1.0]))):
            h = Haltungsbezug(Ziel(gelenkrichtung), None, {}, {}, 'A', {})
            h._kindziel['A'] = 'B'
            self.assertLess(np.linalg.norm(h._ruhe('A') - erwartet / np.linalg.norm(erwartet)), 1e-9)


class WurzelbasisTest(SimpleTestCase):
    databases = set()

    def test_bekannte_drehung_wird_getroffen(self):
        """Quelle = Zielstrahlen, um Q gedreht: die Basis muss Q sein."""
        skel = Skelettgeometrie.holen()
        welt = skel.compute_world_transforms()
        q = Quat.norm(um_achse([0.3, 1.0, -0.2], 77))
        ziele = ['DEF-thigh.L', 'DEF-thigh.R', 'DEF-spine.001']
        offsets = np.array([[0, 0, 0]] + [Quat.rotate(q, welt[z]['world_pos'] - welt['DEF-spine']['world_pos'])
                                          for z in ziele])
        bvh = BVHData(names=['W', 'A', 'B', 'C'], parents=np.array([-1, 0, 0, 0]), offsets=offsets,
                      quats=np.tile(Quat.ID, (1, 4, 1)), positions=np.zeros((1, 4, 3)),
                      frametime=1 / 30.0, frame_count=1, children={0: [1, 2, 3]})
        zuordnung = {'DEF-spine': 'W', 'DEF-thigh.L': 'A', 'DEF-thigh.R': 'B', 'DEF-spine.001': 'C'}
        basis = Wurzelbasis(skel, bvh, zuordnung, {'W': 0, 'A': 1, 'B': 2, 'C': 3}, 'DEF-spine').drehung()
        self.assertLess(winkel(basis, q), 0.01)


class NurLafanTest(SimpleTestCase):
    databases = set()

    def test_nur_lafan_traegt_den_haltungsbezug(self):
        from humanbody_core.skeleton import formats  # noqa: F401  (registriert alle Formate)

        mit = sorted(k for k, cls in Skeleton._registry.items() if cls.HALTUNGSBEZUG)
        self.assertEqual(mit, ['LAFAN'])
