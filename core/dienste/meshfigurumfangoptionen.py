# -*- coding: utf-8 -*-
"""Meshfigurumfangoptionen — die Option `umfang` von „Mesh to 3D“ und Mesh-3D (16.10.2026): die ganze Figur oder nur das Rig.

Edgar zu Mesh3D-AI: „mach doch einen Zwischenschritt — wo du nur das Rigging auf das Mesh machst? Mit Einschalten des Rig-Toggles wird das Rig angezeigt im Mesh.“
Das Rig (Haltung der 22 freien Knochen, Lage, Größe über die Körperregler) steht nach der Körperkette (`koerper`) fest. Gesicht, Eigenmorph, Textur, Vorschau, Frisur und die
Objekte aus dem Netz (Haar, Kleidung) braucht es dafür nicht: `Meshfigurlauf.ausfuehren` hört bei `rig` nach `koerper` auf und lässt die Nebenläufe weg. Die Gelenke liest man dann aus
`arbeit/genesis_koerper_<runde>.npz` + `arbeit/zustand.npz` (`Meshfigurmodell.vorwaerts`). Ein Modell lässt sich aus einem solchen Lauf nicht speichern (kein Gesicht, kein Eigenmorph).
"""

__all__ = ['Meshfigurumfangoptionen']


class Meshfigurumfangoptionen:
    #: Der letzte Schritt bei „nur Rig“.
    RIG_BIS = 'koerper'

    KATALOG = [
        {
            'schluessel': 'umfang',
            'titel': 'Umfang',
            'art': 'wahl',
            'vorgabe': 'figur',
            'werte': [
                ('figur', 'Ganze Figur — Rig, Gesicht, Eigenmorph, Textur, Haar und Kleidung (Vorgabe)'),
                ('rig', 'Nur Rig — Haltung und Größe des Genesis-Skeletts im Netz, endet nach der Körperkette'),
            ],
            'hinweis': '„Nur Rig“ legt das Genesis-Skelett in das Netz (Erkennung und Körperkette: Haltung der 22 Hauptknochen, Lage, Größenregler) und hört dann auf — ohne Gesicht, Eigenmorph, Textur, Vorschau, '
            'Frisur, Haar- und Kleidungsobjekt. Finger und Gesicht stehen in Ruhelage. Aus einem solchen Lauf lässt sich kein Modell speichern.',
        },
    ]

    @classmethod
    def nur_rig(cls, optionen):
        return (optionen or {}).get('umfang') == 'rig'
