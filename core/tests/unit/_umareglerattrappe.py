# -*- coding: utf-8 -*-
u"""Umareglerattrappe — ein winziges UMA3-Verzeichnis mit Regler-Dateien.

Nachgebaut nach den echten Dateien unter `UMA/UMAProject/Assets/UMA/UMA3/DNA/`
(Unity-YAML mit `%TAG`-Kopf und `!u!114`-Dokumenten): zwei Körper-Regler,
ein Gesichts-Regler mit einer Farb-Wirkung (die übergangen wird) und einer
abgeschalteten Wirkung, eine Grundpose. Die Kennungen (`guid`) stehen in
den `.meta`-Dateien, wie in Unity.
"""
from pathlib import Path

__all__ = ['Umareglerattrappe']


class Umareglerattrappe:

    GUIDS = {
        'height': '0' * 31 + '1',
        'legSeparation': '0' * 31 + '2',
        'noseCurve': '0' * 31 + '3',
        'FemaleBodyDNA': '0' * 31 + '4',
        'FemaleBody_BonePose': '0' * 31 + '5',
    }

    KOPF = ('%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n'
            '--- !u!114 &11400000\nMonoBehaviour:\n'
            '  m_ObjectHideFlags: 0\n'
            '  m_Script: {fileID: 11500000, guid: 4ad596f39ce5a904d93ccd9240c400e1, type: 3}\n')

    KURVE = ('        curve:\n          serializedVersion: 2\n          m_Curve:\n'
             '          - serializedVersion: 3\n            time: 0\n            value: 0.2\n'
             '            inSlope: 0.6\n            outSlope: 0.6\n            tangentMode: 0\n'
             '          - serializedVersion: 3\n            time: 0.5\n            value: 0.5\n'
             '            inSlope: 0.6\n            outSlope: 0.6\n            tangentMode: 34\n'
             '          - serializedVersion: 3\n            time: 1\n            value: 0.8\n'
             '            inSlope: 0.6\n            outSlope: 0.6\n            tangentMode: 34\n'
             '          m_PreInfinity: 2\n          m_PostInfinity: 2\n')
    LEERE_KURVE = '        curve:\n          serializedVersion: 2\n          m_Curve: []\n'

    @classmethod
    def gruppe(cls, name, bereich, mitglieder):
        zeilen = ''.join('  - {fileID: 11400000, guid: %s, type: 2}\n' % cls.GUIDS[m]
                         for m in mitglieder)
        return (cls.KOPF + '  m_Name: %s\n  m_EditorClassIdentifier: UMA_Core::UMA.DNAGroup\n'
                '  DNAArea: %s\n  dnaList:\n%s  MaxTotalValue: 0\n' % (name, bereich, zeilen or ''))

    @classmethod
    def regler(cls, name, vorgabe, wirkungen):
        rids = ''.join('  - rid: %d\n' % (100 + i) for i in range(len(wirkungen)))
        refs = ''.join(
            '    - rid: %d\n      type: {class: %s, ns: UMA, asm: UMA_Core}\n      data:\n%s'
            % (100 + i, klasse, daten) for i, (klasse, daten) in enumerate(wirkungen))
        return (cls.KOPF + '  m_Name: %s\n  m_EditorClassIdentifier: UMA_Core::UMA.DNA\n'
                '  defaultValue: %s\n  effects:\n%s  displayName: %s\n'
                '  references:\n    version: 2\n    RefIds:\n%s'
                % (name, vorgabe, rids, name, refs))

    @classmethod
    def dateien(cls):
        skalieren = (cls.KURVE + '        minMapping: -1\n        maxMapping: 1\n'
                     '        EffectName: Hips\n        BoneName: Hips\n'
                     '        ScaleFactor: {x: 0.5, y: 0.5, z: 0.5}\n')
        links = (cls.LEERE_KURVE + '        minMapping: -1\n        maxMapping: 1\n'
                 '        BoneName: LeftUpLeg\n        Translation: {x: -0.02, y: 0, z: 0}\n')
        rechts = links.replace('LeftUpLeg', 'RightUpLeg').replace('x: -0.02', 'x: 0.02')
        drehen = (cls.LEERE_KURVE + '        minMapping: -1\n        maxMapping: 1\n'
                  '        BoneName: NoseBase\n        RotationAxis: {x: 1, y: 0, z: 0}\n'
                  '        RotationAngle: 20\n')
        farbe = '        colorName: Skin\n'
        aus = (cls.LEERE_KURVE + '        minMapping: -1\n        maxMapping: 1\n'
               '        enabled: 0\n        BoneName: NoseBase\n'
               '        ScaleFactor: {x: 1, y: 1, z: 1}\n')
        pose = ('        curve:\n          serializedVersion: 2\n          m_Curve:\n'
                '          - serializedVersion: 3\n            time: 0\n            value: 0.5\n'
                '            inSlope: 0\n            outSlope: 0\n'
                '          - serializedVersion: 3\n            time: 1\n            value: 0.5\n'
                '            inSlope: 0\n            outSlope: 0\n'
                '        minMapping: 0\n        maxMapping: 1\n        EffectName: \n'
                '        bonePose: {fileID: 11400000, guid: %s, type: 2}\n'
                '        isBasePose: 1\n' % cls.GUIDS['FemaleBody_BonePose'])
        posen = (cls.KOPF + '  m_Name: FemaleBody_BonePose\n'
                 '  m_EditorClassIdentifier: UMA_Core::UMA.PoseTools.UMABonePose\n  poses:\n'
                 '  - bone: LeftEye\n    hash: 1\n    position: {x: 0.001, y: -0.0128, z: 0}\n'
                 '    rotation: {x: 0, y: 0, z: 0, w: 1}\n    scale: {x: 1, y: 1, z: 1}\n'
                 '    category: \n    enabled: 1\n'
                 '  - bone: Spine\n    hash: 2\n    position: {x: 0, y: 0, z: 0}\n'
                 '    rotation: {x: 0.1, y: 0.2, z: 0.3, w: 0.9}\n    scale: {x: 1.1, y: 1, z: 1}\n'
                 '    category: \n    enabled: 1\n'
                 '  - bone: Weg\n    hash: 3\n    position: {x: 1, y: 1, z: 1}\n'
                 '    rotation: {x: 0, y: 0, z: 0, w: 1}\n    scale: {x: 1, y: 1, z: 1}\n'
                 '    category: \n    enabled: 0\n')
        return {
            'DNA/FemaleBody.asset': cls.gruppe('FemaleBody', 'Body', ['height', 'legSeparation']),
            'DNA/MaleBody.asset': cls.gruppe('MaleBody', 'Body', ['height']),
            'DNA/MaleFace.asset': cls.gruppe('MaleFace', 'Face', ['noseCurve']),
            'DNA/FemalePose.asset': cls.gruppe('FemalePose', 'Pose', ['FemaleBodyDNA']),
            'DNA/MalePose.asset': cls.gruppe('MalePose', 'Pose', []),
            'DNA/Body/height.asset': cls.regler(
                'height', 0.5, [('DNAEffect_BoneScale', skalieren)]),
            'DNA/Body/legSeparation.asset': cls.regler(
                'legSeparation', 0.5, [('DNAEffect_BoneTranslate', links),
                                       ('DNAEffect_BoneTranslate', rechts)]),
            'DNA/Face/noseCurve.asset': cls.regler(
                'noseCurve', 0.5, [('DNAEffect_BoneRotate', drehen),
                                   ('DNAEffect_SharedColor', farbe),
                                   ('DNAEffect_BoneScale', aus)]),
            'DNA/Pose/RacePoses/FemaleBodyDNA.asset': cls.regler(
                'FemaleBodyDNA', 1, [('DNAEffect_BonePose', pose)]),
            'DNA/Pose/RacePoses/FemaleBody_BonePose.asset': posen,
        }

    @classmethod
    def anlegen(cls, wurzel):
        u"""Das Verzeichnis unter `wurzel` (= UMA3) schreiben; gibt `wurzel` zurück."""
        wurzel = Path(wurzel)
        for relativ, text in cls.dateien().items():
            pfad = wurzel / relativ
            pfad.parent.mkdir(parents=True, exist_ok=True)
            pfad.write_text(text, encoding='utf-8')
            guid = cls.GUIDS.get(pfad.stem)
            if guid:
                Path(str(pfad) + '.meta').write_text(
                    'fileFormatVersion: 2\nguid: %s\n' % guid, encoding='utf-8')
        return wurzel
