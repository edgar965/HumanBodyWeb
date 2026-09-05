# -*- coding: utf-8 -*-
u"""Attrappen für die UMA-Prüfungen: eine Mixamo-BVH, ein +Y-Skelett, eine GLB.

Führender Unterstrich: keine Testdatei (wie `_skelettattrappen.py`).

WARUM SYNTHETISCH: Die echte GLB (27 MB) liegt in `Figuren/uma/`; die echten
BVH-Dateien liegen unter `HumanBody/data`, und ein Retarget schreibt seinen
Zwischenspeicher NEBEN die Datei. Beides gehört nicht in einen Test. Die
Attrappen hier sind klein und tragen genau die Eigenheiten, um die es geht:
Joint-Dubletten, Nicht-Joint-Vorfahren mit halber Drehung um Y, Knochen
entlang +Y, eine Skalierung, und eine Bindpose, die nicht die Knotenpose ist.
"""
import json
import math
import struct

import numpy as np

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402


class Umaattrappe:
    u"""Baukasten: BVH-Text, +Y-Skelett und GLB-Bytes für die UMA-Prüfungen."""

    # ---------------------------------------------------------- Mixamo-BVH

    #: (Name, Elter, Versatz in cm) — T-Pose, Arme entlang ±X.
    GELENKE = [
        ('Hips', None, (0, 100, 0)),
        ('Spine', 'Hips', (0, 10, 0)), ('Spine1', 'Spine', (0, 10, 0)),
        ('Spine2', 'Spine1', (0, 10, 0)), ('Neck', 'Spine2', (0, 10, 0)),
        ('Head', 'Neck', (0, 10, 0)),
        ('LeftShoulder', 'Spine2', (5, 8, 0)),
        ('LeftArm', 'LeftShoulder', (10, 0, 0)),
        ('LeftForeArm', 'LeftArm', (25, 0, 0)),
        ('LeftHand', 'LeftForeArm', (25, 0, 0)),
        ('RightShoulder', 'Spine2', (-5, 8, 0)),
        ('RightArm', 'RightShoulder', (-10, 0, 0)),
        ('RightForeArm', 'RightArm', (-25, 0, 0)),
        ('RightHand', 'RightForeArm', (-25, 0, 0)),
        ('LeftUpLeg', 'Hips', (10, 0, 0)), ('LeftLeg', 'LeftUpLeg', (0, -45, 0)),
        ('LeftFoot', 'LeftLeg', (0, -45, 0)),
        ('RightUpLeg', 'Hips', (-10, 0, 0)),
        ('RightLeg', 'RightUpLeg', (0, -45, 0)),
        ('RightFoot', 'RightLeg', (0, -45, 0)),
    ]
    #: Endstücke der Blätter — ohne sie hätte ein Blattknochen keine Richtung.
    ENDEN = {'Head': (0, 10, 0), 'LeftHand': (10, 0, 0), 'RightHand': (-10, 0, 0),
             'LeftFoot': (0, -5, 15), 'RightFoot': (0, -5, 15)}
    KANAELE_WURZEL = 'Xposition Yposition Zposition Zrotation Xrotation Yrotation'
    KANAELE = 'Zrotation Xrotation Yrotation'

    @classmethod
    def bvh_text(cls, bilder, bildzeit=1.0 / 30):
        u"""Eine Mixamo-BVH. `bilder`: je Bild ``{Gelenk: (Z, X, Y) in Grad}``;
        ``'_position'`` setzt die Wurzellage, alles Fehlende ist 0."""
        kinder = {}
        for name, elter, _ in cls.GELENKE:
            kinder.setdefault(elter, []).append(name)
        versatz = {name: off for name, _, off in cls.GELENKE}
        zeilen = ['HIERARCHY']
        reihenfolge = []
        cls._gelenk_schreiben('Hips', 0, True, kinder, versatz, zeilen, reihenfolge)
        zeilen += ['MOTION', 'Frames: %d' % len(bilder),
                   'Frame Time: %.6f' % bildzeit]
        for bild in bilder:
            werte = []
            for name in reihenfolge:
                if name == 'Hips':
                    werte += list(bild.get('_position', (0, 0, 0)))
                werte += list(bild.get(name, (0, 0, 0)))
            zeilen.append(cls._zahlen(werte))
        return '\n'.join(zeilen) + '\n'

    @classmethod
    def _gelenk_schreiben(cls, name, tiefe, wurzel, kinder, versatz, zeilen,
                          reihenfolge):
        ein = '  ' * tiefe
        zeilen.append('%s%s %s' % (ein, 'ROOT' if wurzel else 'JOINT', name))
        zeilen.append(ein + '{')
        zeilen.append('%s  OFFSET %s' % (ein, cls._zahlen(versatz[name])))
        zeilen.append('%s  CHANNELS %s' % (
            ein, ('6 ' + cls.KANAELE_WURZEL) if wurzel else ('3 ' + cls.KANAELE)))
        reihenfolge.append(name)
        for kind in kinder.get(name, []):
            cls._gelenk_schreiben(kind, tiefe + 1, False, kinder, versatz,
                                  zeilen, reihenfolge)
        if name in cls.ENDEN:
            zeilen.extend(['%s  End Site' % ein, '%s  {' % ein,
                           '%s    OFFSET %s' % (ein, cls._zahlen(cls.ENDEN[name])),
                           '%s  }' % ein])
        zeilen.append(ein + '}')

    @staticmethod
    def _zahlen(werte):
        return ' '.join('%.4f' % v for v in werte)

    # ---------------------------------------------------------- +Y-Skelett

    #: Halbe Drehung um Y — so steht die Wurzel der echten UMA-GLB.
    YAW_180 = (0.0, 1.0, 0.0, 0.0)
    _S45 = math.sqrt(0.5)

    @staticmethod
    def knochen(name, elter, pos, quat=(0.0, 0.0, 0.0, 1.0)):
        return {'name': name, 'parent': elter,
                'local_position': list(pos), 'local_quaternion': list(quat)}

    @classmethod
    def _seite(cls, seite, vz):
        u"""Arm und Bein einer Seite; `vz` = +1 links, -1 rechts."""
        k, s = cls.knochen, cls._S45
        return [
            # +Y nach ±X: eine Vierteldrehung um Z.
            k(seite + 'Shoulder', 'Spine1', (0.05 * vz, 0.15, 0), (0, 0, -s * vz, s)),
            k(seite + 'Arm', seite + 'Shoulder', (0, 0.1, 0)),
            k(seite + 'ForeArm', seite + 'Arm', (0, 0.3, 0)),
            k(seite + 'Hand', seite + 'ForeArm', (0, 0.25, 0)),
            k(seite + 'HandFinger03_01', seite + 'Hand', (0, 0.08, 0)),
            # +Y nach -Y: eine halbe Drehung um Z.
            k(seite + 'UpLeg', 'Hips', (0.1 * vz, 0, 0), (0, 0, 1, 0)),
            k(seite + 'Leg', seite + 'UpLeg', (0, 0.45, 0)),
            k(seite + 'Foot', seite + 'Leg', (0, 0.45, 0)),
            k(seite + 'ToeBase', seite + 'Foot', (0, 0.1, 0.05)),
        ]

    @classmethod
    def uma_knochen(cls):
        u"""Ein UMA-artiges Skelett in Three.js-Form, Knochen entlang +Y,
        Wurzel ungedreht (blickt nach +Z). `gedreht()` setzt die halbe Drehung."""
        k = cls.knochen
        return [
            k('Global', None, (0, 0, 0)),
            k('Position', 'Global', (0, 0, 0)),
            k('Hips', 'Position', (0, 1.0, 0)),
            k('LowerBack', 'Hips', (0, 0.05, 0)),
            k('Spine', 'LowerBack', (0, 0.15, 0)),
            k('Spine1', 'Spine', (0, 0.15, 0)),
            k('Neck', 'Spine1', (0, 0.2, 0)),
            k('Head', 'Neck', (0, 0.1, 0)),
            k('HeadAdjust_end', 'Head', (0, 0.1, 0)),
        ] + cls._seite('Left', 1) + cls._seite('Right', -1)

    @classmethod
    def gedreht(cls, knochen=None, quat=YAW_180):
        u"""Dieselbe Liste, die Wurzel mit `quat` — wie die echte UMA-GLB."""
        raus = []
        for eintrag in (knochen if knochen is not None else cls.uma_knochen()):
            neu = dict(eintrag)
            if not eintrag['parent']:
                neu['local_quaternion'] = list(quat)
            raus.append(neu)
        return raus

    # ----------------------------------------------------------------- GLB

    CHUNK_JSON = 0x4E4F534A
    CHUNK_BIN = 0x004E4942
    #: Die Bindpose weicht von der Knotenpose ab: alles ab den Hueften um
    #: diesen Vektor verschoben (Weltkoordinaten).
    BIND_VERSATZ = np.array([0.0, 0.0, 0.3])

    @classmethod
    def glb_bytes(cls, gltf, binaer=b''):
        u"""Eine GLB aus JSON und Binaerteil — beide auf 4 Byte aufgefuellt."""
        js = json.dumps(gltf).encode()
        js += b' ' * (-len(js) % 4)
        binaer += b'\0' * (-len(binaer) % 4)
        rumpf = struct.pack('<II', len(js), cls.CHUNK_JSON) + js
        if binaer:
            rumpf += struct.pack('<II', len(binaer), cls.CHUNK_BIN) + binaer
        return b'glTF' + struct.pack('<II', 2, 12 + len(rumpf)) + rumpf

    @staticmethod
    def _welt(knochen):
        u"""Weltlage (pos, rot, skal) je Knochen — Eltern zuerst in der Liste."""
        welt = {}
        for k in knochen:
            t = np.array(k['local_position'], dtype=float)
            q = np.array(k['local_quaternion'], dtype=float)
            s = np.array(k.get('scale', (1, 1, 1)), dtype=float)
            if k['parent']:
                ep, er, es = welt[k['parent']]
                welt[k['name']] = (ep + Quat.rotate(er, es * t),
                                   Quat.norm(Quat.mul(er, q)), es * s)
            else:
                welt[k['name']] = (t, q, s)
        return welt

    @staticmethod
    def _matrix(pos, rot, skal):
        m = np.eye(4)
        m[:3, :3] = Quat.matrix(rot) * skal
        m[:3, 3] = pos
        return m

    @classmethod
    def glb_beispiel(cls):
        u"""``(gltf, binaer)``: das +Y-Skelett unter `Avatar` (halbe Drehung)
        und `Root` (beide keine Joints), `LeftFoot` skaliert, `Hips` doppelt
        in der Joint-Liste, Bindmatrizen mit versetzter Bindpose."""
        joints = [dict(k) for k in cls.uma_knochen()]
        for k in joints:
            if k['name'] == 'LeftFoot':
                k['scale'] = [1.0, 2.0, 1.0]
        knoten = cls._knotenliste(joints)
        netz_nummer = len(knoten)
        knoten.append({'name': 'Netz', 'skin': 0, 'mesh': 0})
        knoten[0]['children'] = [1, netz_nummer]
        nummer = {k['name']: i + 2 for i, k in enumerate(joints)}
        joint_liste = [nummer[k['name']] for k in joints] + [nummer['Hips']]
        binaer = cls._bindmatrizen(joints, joint_liste, knoten)
        gltf = {
            'asset': {'version': '2.0'},
            'nodes': knoten,
            'skins': [{'joints': joint_liste, 'inverseBindMatrices': 0}],
            'accessors': [{'bufferView': 0, 'componentType': 5126,
                           'count': len(joint_liste), 'type': 'MAT4'}],
            'bufferViews': [{'buffer': 0, 'byteOffset': 0,
                             'byteLength': len(binaer)}],
            'buffers': [{'byteLength': len(binaer)}],
            'meshes': [{'primitives': []}],
        }
        return gltf, binaer

    @classmethod
    def _knotenliste(cls, joints):
        u"""glTF-Knoten: `Avatar`, `Root`, dann die Joints mit Kinderlisten."""
        knoten = [{'name': 'Avatar', 'rotation': list(cls.YAW_180)},
                  {'name': 'Root', 'children': [2]}]
        nummer = {k['name']: i + 2 for i, k in enumerate(joints)}
        for k in joints:
            eintrag = {'name': k['name'], 'translation': k['local_position'],
                       'rotation': k['local_quaternion']}
            if 'scale' in k:
                eintrag['scale'] = k['scale']
            knoten.append(eintrag)
        for k in joints:
            if k['parent']:
                knoten[nummer[k['parent']]].setdefault('children', []).append(
                    nummer[k['name']])
        return knoten

    @classmethod
    def _bindmatrizen(cls, joints, joint_liste, knoten):
        u"""Inverse Bindmatrizen (spaltenweise float32) — Knotenpose samt
        Avatar-Drehung, ab den Hueften um BIND_VERSATZ verschoben."""
        kette = [cls.knochen('Avatar', None, (0, 0, 0), cls.YAW_180),
                 cls.knochen('Root', 'Avatar', (0, 0, 0))]
        welt = cls._welt(kette + [dict(k, parent=k['parent'] or 'Root')
                                  for k in joints])
        netz_welt = cls._matrix(*welt['Avatar'])
        eltern = {k['name']: k['parent'] for k in joints}
        matrizen = []
        for j in joint_liste:
            name = knoten[j]['name']
            pos, rot, _skal = welt[name]
            if cls._unter(name, 'Hips', eltern):
                pos = pos + cls.BIND_VERSATZ
            bind = cls._matrix(pos, rot, np.ones(3))
            ibm = np.linalg.inv(bind) @ netz_welt
            matrizen.append(ibm.T.astype('<f4').tobytes())
        return b''.join(matrizen)

    @staticmethod
    def _unter(name, vorfahr, eltern):
        while name:
            if name == vorfahr:
                return True
            name = eltern.get(name)
        return False
