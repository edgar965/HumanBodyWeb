# -*- coding: utf-8 -*-
u"""Umaregler — die UMA-3-DNA-Regler und Kinder-Posen als Daten lesen (17.10.2026).

Quelle: die Unity-Assets im UMA-Projekt (`UMA/UMAProject/Assets/UMA`, Text-YAML, MIT-Lizenz). Gelesen werden

- die 62 DNA-Regler `UMA3/DNA/Body/*.asset` (28) und `UMA3/DNA/Face/*.asset` (34) mit ihren Wirkungen (`references.RefIds`): `DNAEffect_BoneScale`,
  `…_BoneTranslate`, `…_BoneRotate`, `…_BonePose` (acht Regler verweisen ueber eine GUID auf ein `UMABonePose`-Asset, dessen `.meta` die Datei findet);
- die drei Kinder-Posen: `UMA3/Races/BonePoses/Child.asset`, `UMA2/Races/HumanFemale/DNA/HumanGirl/BonePoses/HumanFemaleToGirlPose.asset`, `…/HumanMaleToBoyPose.asset`.

DIE WERTE (aus `DNAEffect.GetMappedValue` und `UMASkeleton.Morph`, im Quelltext gelesen): Ein DNA-Wert `v` (0…1, Vorgabe 0,5) geht durch die Kurve und wird auf
`[min, max]` abgebildet: `m = min + Kurve(v)·(max − min)`. Skalieren: `s = 1 + Faktor·m` je Achse. Verschieben: `+ Translation·m`. Drehen: `Winkel·m` um die Achse. Pose: je Knochen
`Position·w`, `Skala = 1 + (Skala − 1)·w`, `w = m`. Die Kurve ist Unitys AnimationCurve: kubisch (Hermite) zwischen den Schluesseln mit ihren Tangenten, ausserhalb der Schluessel
konstant (`m_PreInfinity: 2` ist hier „clamp“ — als Schleife gelesen lieferte `breastSize` bei 0 den Wert fuer 1).
"""
import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger('core')

__all__ = ['Umaregler']


class _Lader(yaml.SafeLoader):
    u"""Unitys YAML: Etiketten `!u!114` und Anker `&11400000` — die Etiketten werden als gewoehnliche Mappings gelesen."""


_Lader.add_multi_constructor('tag:unity3d.com,2011:', lambda lader, suffix, knoten: lader.construct_mapping(knoten, deep=True))


class Umaregler:
    u"""Regler und Posen aus den UMA-Assets."""

    WURZEL = Path(__file__).resolve().parents[3] / 'UMA' / 'UMAProject' / 'Assets'
    ORDNER = (('Body', u'Körper'), ('Face', u'Gesicht'))
    POSEN = (
        ('Kind_UMA3', u'Kind (UMA 3, Pose „Child“)', 'UMA/UMA3/Races/BonePoses/Child.asset'),
        ('Maedchen_UMA2', u'Mädchen (UMA 2, Pose Frau → Mädchen)', 'UMA2/Races/HumanFemale/DNA/HumanGirl/BonePoses/HumanFemaleToGirlPose.asset'),
        ('Junge_UMA2', u'Junge (UMA 2, Pose Mann → Junge)', 'UMA2/Races/HumanFemale/DNA/HumanGirl/BonePoses/HumanMaleToBoyPose.asset'),
    )
    _guids = None

    @classmethod
    def vorhanden(cls):
        return (cls.WURZEL / 'UMA' / 'UMA3' / 'DNA' / 'Body').is_dir()

    @staticmethod
    def _yaml(pfad):
        with open(pfad, encoding='utf-8') as f:
            text = f.read()
        for dokument in yaml.load_all(text, Loader=_Lader):
            if isinstance(dokument, dict):
                for wert in dokument.values():
                    if isinstance(wert, dict):
                        return wert
        return {}

    @staticmethod
    def _vektor(v, vorgabe=(0.0, 0.0, 0.0)):
        if not isinstance(v, dict):
            return tuple(vorgabe)
        return (float(v.get('x', 0.0)), float(v.get('y', 0.0)), float(v.get('z', 0.0)))

    # ------------------------------------------------------------------ Posen

    @classmethod
    def pose(cls, pfad):
        u"""`[{knochen, position, rotation (x, y, z, w), skala}]` eines `UMABonePose`-Assets (nur aktivierte Eintraege)."""
        daten = cls._yaml(pfad)
        aus = []
        for p in daten.get('poses') or []:
            if not p.get('enabled', 1):
                continue
            r = p.get('rotation') or {}
            aus.append({'knochen': str(p.get('bone')), 'position': cls._vektor(p.get('position')),
                        'rotation': (float(r.get('x', 0)), float(r.get('y', 0)), float(r.get('z', 0)), float(r.get('w', 1))),
                        'skala': cls._vektor(p.get('scale'), (1.0, 1.0, 1.0))})
        return aus

    @classmethod
    def kinderposen(cls):
        u"""`[{kennung, anzeige, pose}]` der drei Kinder-Posen."""
        return [{'kennung': k, 'anzeige': a, 'pose': cls.pose(cls.WURZEL / pfad)} for k, a, pfad in cls.POSEN]

    @classmethod
    def pose_zu_guid(cls, guid):
        u"""Das Asset zu einer Unity-GUID — ueber die `.meta`-Dateien (einmal gelesen)."""
        if cls._guids is None:
            cls._guids = {}
            for ordner, _u, dateien in os.walk(cls.WURZEL):
                for datei in dateien:
                    if datei.endswith('.asset.meta'):
                        with open(os.path.join(ordner, datei), encoding='utf-8', errors='replace') as f:
                            for zeile in f:
                                if zeile.startswith('guid: '):
                                    cls._guids[zeile[6:].strip()] = os.path.join(ordner, datei[:-5])
                                    break
        return cls._guids.get(guid)

    # ------------------------------------------------------------------ Regler

    @classmethod
    def kurve(cls, daten):
        u"""`[(zeit, wert, in, out)]` aus `curve.m_Curve` — leer = keine Kurve (Wert unveraendert)."""
        schluessel = ((daten or {}).get('curve') or {}).get('m_Curve') or []
        return [(float(k['time']), float(k['value']), float(k.get('inSlope', 0)), float(k.get('outSlope', 0))) for k in schluessel]

    @classmethod
    def regler(cls):
        u"""`[{name, bereich, vorgabe, effekte}]` — `effekte`: `{art, knochen, wert, achse, grad, kurve, min, max, pose}`."""
        aus = []
        for ordner, titel in cls.ORDNER:
            for pfad in sorted((cls.WURZEL / 'UMA' / 'UMA3' / 'DNA' / ordner).glob('*.asset')):
                daten = cls._yaml(pfad)
                refs = {str(r.get('rid')): r for r in (daten.get('references') or {}).get('RefIds') or []}
                effekte = []
                for e in daten.get('effects') or []:
                    ref = refs.get(str(e.get('rid')))
                    eintrag = cls._effekt(ref) if ref else None
                    if eintrag:
                        effekte.append(eintrag)
                aus.append({'name': pfad.stem, 'bereich': titel, 'vorgabe': float(daten.get('defaultValue', 0.5)), 'effekte': effekte})
        return aus

    @classmethod
    def _effekt(cls, ref):
        art = (ref.get('type') or {}).get('class', '')
        d = ref.get('data') or {}
        eintrag = {'kurve': cls.kurve(d), 'min': float(d.get('minMapping', -1)), 'max': float(d.get('maxMapping', 1)), 'knochen': d.get('BoneName')}
        if art == 'DNAEffect_BoneScale':
            eintrag.update(art='skalieren', wert=cls._vektor(d.get('ScaleFactor'), (1.0, 1.0, 1.0)))
        elif art == 'DNAEffect_BoneTranslate':
            eintrag.update(art='verschieben', wert=cls._vektor(d.get('Translation')))
        elif art == 'DNAEffect_BoneRotate':
            eintrag.update(art='drehen', achse=cls._vektor(d.get('RotationAxis'), (1.0, 0.0, 0.0)), grad=float(d.get('RotationAngle', 0)))
        elif art == 'DNAEffect_BonePose':
            guid = ((d.get('bonePose') or {}).get('guid'))
            pfad = cls.pose_zu_guid(guid) if guid else None
            if not pfad:
                logger.warning('UMA: BonePose %s nicht gefunden', guid)
                return None
            eintrag.update(art='pose', pose=cls.pose(pfad))
        else:
            logger.info('UMA: Wirkung %s wird nicht uebernommen', art)
            return None
        return eintrag

    @staticmethod
    def abbilden(kurve, x):
        u"""Unitys Kurve an der Stelle `x`: Hermite zwischen den Schluesseln, ausserhalb konstant; ohne Schluessel `x` selbst."""
        if not kurve:
            return x
        if x <= kurve[0][0]:
            return kurve[0][1]
        if x >= kurve[-1][0]:
            return kurve[-1][1]
        for (t0, v0, _i0, o0), (t1, v1, i1, _o1) in zip(kurve, kurve[1:], strict=False):
            if x <= t1:
                dt = t1 - t0
                t = (x - t0) / dt
                m0, m1 = o0 * dt, i1 * dt
                return ((2 * t ** 3 - 3 * t ** 2 + 1) * v0 + (t ** 3 - 2 * t ** 2 + t) * m0 + (-2 * t ** 3 + 3 * t ** 2) * v1 + (t ** 3 - t ** 2) * m1)
        return kurve[-1][1]

    @classmethod
    def wert(cls, effekt, v):
        u"""Der abgebildete Wert `m` eines Effekts bei DNA-Wert `v`."""
        return effekt['min'] + cls.abbilden(effekt['kurve'], v) * (effekt['max'] - effekt['min'])
