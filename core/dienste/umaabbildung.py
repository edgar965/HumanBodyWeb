# -*- coding: utf-8 -*-
u"""Umaabbildung — welcher UMA-Knochen auf welche Genesis-9-Knochen wirkt (17.10.2026).

UMA-Knochen sind die eines Mixamo-artigen Rigs plus „Adjust“-Knochen (Huellen, die nur ein Stueck Haut an einem Glied halten). Genesis 9 hat Glieder, Verdrillungsknochen
(`l_upperarmtwist1`) und ein Gesichtsrig (`l_cheek`, `l_nostril`, `liplowermiddle` …), auf denen die Haut gewichtet ist. Die Tabelle ordnet jedem UMA-Knochen zu:

    knochen  der Genesis-Knochen, um dessen Gelenk gedreht/skaliert wird
    wirkt    'baum' (Knochen und Nachfahren, wie UMA/Unity: ein skalierter Arm skaliert die Hand) oder die Liste der Knochen, auf deren Haut die Operation wirkt (Adjust)
    welt     True: die Achsen der Angabe sind Weltachsen (Rumpf, Kopf, Gesicht); False: der Knochenrahmen (y entlang des Knochens — Arme, Beine, Haende, Fuesse)
    mitte    Drehpunkt in der Mitte mehrerer Knochen (Nase) statt am Gelenk des ersten
    pivot    ein fester Drehpunkt (der Fussboden fuer `Position`)

ACHSEN (ANNAHME, nicht gemessen): Die Unity-Achsen der UMA-Knochen liegen in einer Binaerdatei (`UmaTPose`), nicht lesbar. Angenommen wird: y entlang des Knochens (an den
Laengenreglern belegt: `forearmLength` skaliert y, `armWidth` am Adjust x und z), Unity-Weltachsen x = rechts der Figur, y = oben, z = vorn; Genesis hat x = links —
deshalb kehrt `Umamorpheaufgenesis` x um. Belegt an `breastCleavage` (links +0,07, rechts −0,07 = zur Mitte) und `legSeparation` (links −0,015 = nach aussen): beide ergeben nur
mit „+x = rechts“ den Sinn des Namens. Die Seite „Rechts“ der Gluteus-Knochen entfaellt: die Genesis-Haut hat EINE Beckenhuelle, `LeftGluteus` traegt beide (UMA stellt
beide Seiten immer gleich).
"""
__all__ = ['Umaabbildung']


class Umaabbildung:
    u"""`ziel(uma_knochen)` -> `{knochen, wirkt, welt, mitte?, pivot?}` oder None."""

    ALLE = None      # `wirkt: None` = baum

    #: Seitenlose und seitenweise Knochen; `{S}` = `l`/`r`, `{U}` = `Left`/`Right`.
    GLIED = {
        'Position': {'knochen': 'hip', 'pivot': (0.0, 0.0, 0.0), 'welt': True},
        'Hips': {'knochen': 'hip', 'welt': True},
        'LowerBack': {'knochen': 'spine1', 'welt': True},
        'Spine': {'knochen': 'spine2', 'welt': True},
        'Spine1': {'knochen': 'spine3', 'welt': True},
        'Neck': {'knochen': 'neck1', 'welt': True},
        'Head': {'knochen': 'head', 'welt': True},
        'Mandible': {'knochen': 'lowerjaw', 'welt': True},
        'LowerBackAdjust': {'knochen': 'spine1', 'wirkt': ['spine1'], 'welt': True},
        'LowerBackBelly': {'knochen': 'spine1', 'wirkt': ['spine1'], 'welt': True},
        'SpineAdjust': {'knochen': 'spine2', 'wirkt': ['spine2'], 'welt': True},
        'Spine1Adjust': {'knochen': 'spine3', 'wirkt': ['spine3', 'spine4'], 'welt': True},
        'NeckAdjust': {'knochen': 'neck1', 'wirkt': ['neck1', 'neck2'], 'welt': True},
        'HeadAdjust': {'knochen': 'head', 'wirkt': ['head'], 'welt': True},
        'MandibleAdjust': {'knochen': 'lowerjaw', 'wirkt': ['lowerjaw'], 'welt': True},
        'NeckAdjust_end': None,
        # Nase und Lippen in der Mitte
        'NoseBaseAdjust': {'knochen': 'l_nostril', 'wirkt': ['l_nostril', 'r_nostril'], 'welt': True, 'mitte': ['l_nostril', 'r_nostril']},
        'NoseMiddleAdjust': {'knochen': 'l_nostril', 'wirkt': ['l_nostril', 'r_nostril'], 'welt': True, 'mitte': ['l_nostril', 'r_nostril']},
        'NoseTopAdjust': {'knochen': 'l_infraorbital', 'wirkt': ['l_infraorbital', 'r_infraorbital'], 'welt': True, 'mitte': ['l_infraorbital', 'r_infraorbital']},
        'LipsSuperiorAdjust': {'knochen': 'lipuppermiddle', 'wirkt': ['lipuppermiddle'], 'welt': True},
        'UpperLipsAdjust': {'knochen': 'lipuppermiddle', 'wirkt': ['lipuppermiddle', 'l_lipupper', 'r_lipupper'], 'welt': True, 'mitte': ['lipuppermiddle']},
        'LipsInferiorAdjust': {'knochen': 'liplowermiddle', 'wirkt': ['liplowermiddle'], 'welt': True},
    }

    SEITE = {
        '{U}Shoulder': {'knochen': '{S}_shoulder', 'welt': False},
        '{U}ShoulderAdjust': {'knochen': '{S}_shoulder', 'wirkt': ['{S}_shoulder'], 'welt': False},
        '{U}Trapezius': {'knochen': '{S}_shoulder', 'wirkt': ['{S}_shoulder'], 'welt': True},
        '{U}Arm': {'knochen': '{S}_upperarm', 'welt': False},
        '{U}ArmAdjust': {'knochen': '{S}_upperarm', 'wirkt': ['{S}_upperarm', '{S}_upperarmtwist1', '{S}_upperarmtwist2'], 'welt': False},
        '{U}ForeArm': {'knochen': '{S}_forearm', 'welt': False},
        '{U}ForeArmAdjust': {'knochen': '{S}_forearm', 'wirkt': ['{S}_forearm', '{S}_forearmtwist1', '{S}_forearmtwist2'], 'welt': False},
        '{U}ForeArmTwistAdjust': {'knochen': '{S}_forearmtwist1', 'wirkt': ['{S}_forearmtwist1', '{S}_forearmtwist2'], 'welt': False},
        '{U}Hand': {'knochen': '{S}_hand', 'welt': False},
        '{U}UpLeg': {'knochen': '{S}_thigh', 'welt': False},
        '{U}UpLegAdjust': {'knochen': '{S}_thigh', 'wirkt': ['{S}_thigh', '{S}_thightwist1', '{S}_thightwist2'], 'welt': False},
        '{U}Leg': {'knochen': '{S}_shin', 'welt': False},
        '{U}LegAdjust': {'knochen': '{S}_shin', 'wirkt': ['{S}_shin'], 'welt': False},
        '{U}Foot': {'knochen': '{S}_foot', 'welt': False},
        '{U}ToeBase': {'knochen': '{S}_toes', 'welt': False},
        '{U}OuterBreast': {'knochen': '{S}_pectoral', 'welt': True},
        '{U}InnerBreast': {'knochen': '{S}_pectoral', 'welt': True},
        '{U}Eye': {'knochen': '{S}_eye', 'welt': True},
        '{U}CheekAdjust': {'knochen': '{S}_cheek', 'wirkt': ['{S}_cheek'], 'welt': True},
        '{U}LowCheekAdjust': {'knochen': '{S}_cheeklower', 'wirkt': ['{S}_cheeklower'], 'welt': True},
        '{U}LowMaxilarAdjust': {'knochen': '{S}_cheeklower', 'wirkt': ['{S}_cheeklower'], 'welt': True},
        '{U}EarAdjust': {'knochen': '{S}_ear', 'wirkt': ['{S}_ear'], 'welt': True},
        '{U}EyeAdjust': {'knochen': '{S}_eyelidupper', 'wirkt': ['{S}_eyelidupper', '{S}_eyelidlower', '{S}_squint', '{S}_infraorbital'], 'welt': True,
                         'mitte': ['{S}_eyelidupper']},
        '{U}EyebrowLowAdjust': {'knochen': '{S}_browinner', 'wirkt': ['{S}_browinner'], 'welt': True},
        '{U}EyebrowMiddleAdjust': {'knochen': '{S}_browouter', 'wirkt': ['{S}_browouter', '{S}_browinner'], 'welt': True, 'mitte': ['{S}_browouter', '{S}_browinner']},
        '{U}EyebrowUpAdjust': {'knochen': '{S}_browouter', 'wirkt': ['{S}_browouter'], 'welt': True},
        '{U}LipsAdjust': {'knochen': '{S}_lipcorner', 'wirkt': ['{S}_lipcorner'], 'welt': True},
        '{U}LipsInferiorAdjust': {'knochen': '{S}_liplower', 'wirkt': ['{S}_liplower'], 'welt': True},
        '{U}LipsSuperiorMiddleAdjust': {'knochen': '{S}_lipupper', 'wirkt': ['{S}_lipupper'], 'welt': True},
        '{U}NoseAdjust': {'knochen': '{S}_nostril', 'wirkt': ['{S}_nostril'], 'welt': True},
        '{U}UpperLidAdjust': {'knochen': '{S}_eyelidupper', 'wirkt': ['{S}_eyelidupper'], 'welt': True},
    }
    #: Der Gluteus: eine Huelle fuer beide Seiten (siehe Kopf).
    GLUTEUS = {'LeftGluteus': {'knochen': 'pelvis', 'wirkt': ['pelvis'], 'welt': True, 'mitte': ['l_thigh', 'r_thigh']}, 'RightGluteus': None}

    @classmethod
    def ziel(cls, uma_knochen):
        u"""Die Zuordnung zu `uma_knochen` mit aufgeloesten Seiten — None, wenn es keine gibt oder der Knochen entfaellt."""
        if uma_knochen in cls.GLUTEUS:
            return cls._fertig(cls.GLUTEUS[uma_knochen], 'l')
        for name in (uma_knochen, uma_knochen + 'Adjust'):         # die Posen nennen die Gesichtsknochen oft ohne „Adjust“ (`LeftEyebrowLow`, `NoseBase`)
            if name in cls.GLIED:
                return cls._fertig(cls.GLIED[name], 'l')
            for seite, u in (('l', 'Left'), ('r', 'Right')):
                if name.startswith(u):
                    schluessel = '{U}' + name[len(u):]
                    if schluessel in cls.SEITE:
                        return cls._fertig(cls.SEITE[schluessel], seite)
        return None

    @staticmethod
    def _fertig(eintrag, seite):
        if eintrag is None:
            return None
        def ersetzen(wert):
            if isinstance(wert, str):
                return wert.replace('{S}', seite)
            if isinstance(wert, list):
                return [ersetzen(w) for w in wert]
            return wert
        return {k: ersetzen(v) for k, v in eintrag.items()}
