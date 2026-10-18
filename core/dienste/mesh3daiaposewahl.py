# -*- coding: utf-8 -*-
"""Mesh3daiaposewahl — der Zwischenschritt „A-Pose aus dem Netz“ vor dem Netz von Mesh3D-AI, einstellbar (18.10.2026).

Edgar: „Sollen wir den Zwischenschritt der A-Pose berechnen aus dem Mesh einstellbar machen, um den Effekt zu messen? Einstellbar auf /settings/mesh3dai/“ — und am Abend: „mach das auswählbar …,
über welche Methode das Aufrichten in A-Pose geht, mit Mesh-3D oder MIA. Mach eine bessere Kennzeichnung, was die alte Mesh-3D-Methode war“, „eine eigene Klasse für die "alte" posenaufrichtung,
z.B. MeshToRigToPose“, „und für Mia: MeshToRigToPose_MIA“. Die Klassen stehen in der Kette (`ProjektTemp/_wegwerf/mesh3dai_mesh_to_rig_to_pose*.py`); hier nur Wert, Name und Beschreibung.
Drei Werte:
    mia   MeshToRigToPose_MIA — Make-It-Animatable v2 riggt das Netz und bringt es in die A-Pose; fällt seine Prüfung durch, rechnet die Kette MeshToRigToPose (Vorgabe seit 18.10.2026)
    rig   MeshToRigToPose — die alte Methode vom 17.10.2026: Mesh-3D „Nur Rig“ (SAM 3D Body + „Mesh to 3D“) passt eine Genesis-Figur an, das Netz folgt ihrem Käfig in die A-Pose
    aus   kein Zwischenschritt: das Netz von Mesh3D-AI sieht das Netz in seiner Pose („Netz direkt“)
Wer liest: die Kette `mesh3dai_vorstufe.py` (welche Methode gerechnet wird; „aus“ rechnet nichts), die Jobseite (`Mesh3daiwege`: zeigt den jüngsten Lauf DER gewählten Methode, bei „aus“ zuerst
„Netz direkt“; `Mesh3daiapose`: das Zwischenbild dieses Laufs) und die Testseite (`Mesh3daitest`: bei „aus“ das Ergebnis ohne Vorstufe). Welche Methode einen Lauf rechnete, steht in seiner
`kette.json` (`weg`; Läufe vor dem 18.10.2026 haben kein Feld — das war immer MeshToRigToPose).
Der Wert liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL` (Formular als JSON an `/api/ui-prefs/`, wie `Mesh3daistandwahl`). Unbekanntes oder Unlesbares heißt Vorgabe.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Mesh3daiaposewahl']


class Mesh3daiaposewahl:
    SCHLUESSEL = 'mesh3dai_apose_weg'
    #: Wert → Name der Methode (Klasse in der Kette) — Beschriftung auf allen Seiten.
    NAMEN = {'mia': 'MeshToRigToPose_MIA', 'rig': 'MeshToRigToPose', 'aus': 'aus'}
    #: Wo die Klasse steht (die Kette liegt unter `ProjektTemp/_wegwerf/`).
    DATEIEN = {'mia': 'ProjektTemp/_wegwerf/mesh3dai_mesh_to_rig_to_pose_mia.py', 'rig': 'ProjektTemp/_wegwerf/mesh3dai_mesh_to_rig_to_pose.py'}
    WERTE = (
        ('mia', 'MeshToRigToPose_MIA — Make-It-Animatable riggt (neu, 18.10.2026; Rückfall: MeshToRigToPose)'),
        ('rig', 'MeshToRigToPose — Mesh-3D-Figur riggt (alt, 17.10.2026)'),
        ('aus', 'aus — Netz direkt auf der Pose, keine A-Pose'),
    )
    #: Was die Methode tut, mit den Zahlen aus `.claude/rules/mesh3dai-vorstufe.md` (gemessen 17./18.10.2026, vier Prüfposen-Jobs).
    BESCHREIBUNG = {
        'mia': 'Make-It-Animatable v2 (fertiges Werkzeug, CVPR 2025) sagt für jeden Punkt des Netzes Hautgewichte zu 52 Mixamo-Knochen voraus und je Knochen die Drehung in die T-Pose (14–19 s auf '
               'der GPU). Das Netz wird damit wie an jedem Rig in die T-Pose gerechnet, dann werden die Oberarme auf die Genesis-A-Pose gesenkt; Inselregel und Lochfüllung danach. Fällt MIAs '
               'Prüfung durch (Knie, Ellbogen, Füße, Abriss, Hand), rechnet die Kette MeshToRigToPose. Zwischenbild: Körpertiefe Gesäß bis Brust 2,6–8,0 % neben der echten A-Pose.',
        'rig': 'Die alte Methode vom 17.10.2026: ein Mesh-3D-Auftrag „Nur Rig“ (rund 180 s, einmal je Netzdatei) — SAM 3D Body findet 21 Gelenke am Rendering des Netzes, „Mesh to 3D“ passt eine '
               'Genesis-9-Figur in Form und Haltung an. Jeder Punkt des Netzes folgt dann dem Käfig dieser Figur in deren A-Pose; Löcher werden aus der Figur gefüllt. Das Zwischenbild ist verzerrt '
               '(Körpertiefe Gesäß bis Brust 6,9–40,8 % neben der echten A-Pose; MannLaufen: Hände 113–134 mm, Hemd 27 mm) — das ist die A-Pose, die am 17.10.2026 kaputt aussah. Die Gelenke am '
               'Ende lagen trotzdem bei Ø 13,4 mm, weil schon die Genesis-Figur gut sitzt (Ø 16,6 mm).',
        'aus': 'Kein Zwischenschritt: das Netz von Mesh3D-AI sieht das Netz in seiner Pose (vier Prüfposen-Jobs Ø 202,4 mm).',
    }
    VORGABE = 'mia'

    @classmethod
    def aus(cls, prefs):
        """Der Weg aus einem `ui_prefs`-Dict; alles, was keiner der `WERTE` ist, ist die Vorgabe."""
        wert = str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip()
        return wert if wert in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte Wahl — ohne lesbare Einstellungen (keine Datenbank) die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Seiten und Kette sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Mesh3daiaposewahl: Einstellung nicht lesbar (%s) — Weg %s', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, wert)

    @staticmethod
    def methode(kette):
        """Welche Methode einen Lauf rechnete, aus seiner `kette.json`: 'mia' oder 'rig' (ohne Feld `weg` — Läufe vor dem 18.10.2026 — immer 'rig')."""
        return 'mia' if (kette or {}).get('weg') == 'mia' else 'rig'

    @classmethod
    def rueckfall(cls, kette):
        """Rechnete die Kette MeshToRigToPose, weil MeshToRigToPose_MIA durchfiel? (Feld `weg` gesetzt, Grund nicht „Weg MIA aus …“ — dann war MIA eingestellt.)"""
        k = kette or {}
        return k.get('weg') == 'rig' and not str(k.get('weg_grund', '')).startswith('Weg MIA aus')

    @classmethod
    def passt(cls, wahl, kette):
        """Gehört ein Lauf zur Wahl? 'mia': MIA-Läufe und ihre Rückfälle; 'rig': jeder Lauf von MeshToRigToPose."""
        m = cls.methode(kette)
        return m == wahl or (wahl == 'mia' and cls.rueckfall(kette))

    @classmethod
    def name_des_laufs(cls, kette):
        """Beschriftung eines Laufs: Name der Methode, beim Rückfall mit Hinweis."""
        name = cls.NAMEN[cls.methode(kette)]
        return '%s (Rückfall: MIA durchgefallen)' % name if cls.rueckfall(kette) else name
