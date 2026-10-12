# -*- coding: utf-8 -*-
"""Mesh3dschritte — die Schritte eines Imports, wie die Jobseite „Mesh-3D“ sie zeigt (11.10.2026).

Die Seite „Mesh-3D“ ist keine zweite Pipeline: ein Auftrag dort IST ein Modell-Import (`Blendimportlauf`, derselbe Ablauf wie
„Datei → Modell importieren…“ auf der Charakter-Seite). Diese Klasse gibt den Schritten ihre Titel und Kurztexte und liest aus
`stand.json`, in welchem Zustand jeder ist: `fertig`, `laeuft`, `gescheitert`, `angehalten`, `uebersprungen` (der Schritt lief, tat aber
nichts — `ergebnis.<schritt>.aus`) oder `offen`.
"""

from .blendimportlauf import Blendimportlauf

__all__ = ['Mesh3dschritte']


class Mesh3dschritte:
    TITEL = {
        'umwandeln': 'Umwandeln', 'export': 'Lesen', 'umposen': 'Umposen (Rig)', 'pose': 'Pose (SAM 3D Body)', 'koerper': 'Körpernetz', 'segmentierung': 'Segmentierung (Sapiens)',
        'figur': 'Figur', 'finger': 'Finger', 'stuecke': 'Kleider und Haar', 'haut': 'Haut', 'augen': 'Augen', 'modell': 'Modell',
    }
    HINWEIS = {
        'umwandeln': 'Blender macht aus der OBJ-, FBX- oder GLB-Datei eine .blend (nur bei diesen Formaten).',
        'export': 'Blender liest Netze, Materialien und Gewichte; die Rollen (Körper, Kleid, Haar, Auge) werden zugeordnet.',
        'umposen': 'Mit dem Rig des Modells in die Genesis-Haltung (nur Auto-Rig Pro); sonst gilt die Haltung der Datei.',
        'pose': 'SAM 3D Body findet die Gelenke am Rendering des Körpers — für Modelle, die nicht in A-Haltung stehen.',
        'koerper': 'Körper und Augen als eine GLB für „Mesh to 3D“.',
        'figur': '„Mesh to 3D“ passt die Genesis-9-Figur an den Körper an (Regler, Gesicht, Eigenmorph).',
        'finger': 'Die Finger der Figur an die Hände des Originals anpassen.',
        'stuecke': 'Kleider, Haar, Augen und Scham werden eigene Genesis-Stücke in der Garderobe.',
        'haut': 'Die Originalhaut wird auf die Genesis-Kacheln gebacken.',
        'augen': 'Das Augenbild des Originals ins Genesis-Auge.',
        'modell': 'Das Genesis-Modell mit Reglern, Stücken, Haut und Augen wird gespeichert.',
    }

    #: Was die Schritte beim Weg „netz“ (ein verschmolzenes Netz, `Blendimportweg`) tun — die übrigen Texte gelten unverändert.
    HINWEIS_NETZ = {
        'koerper': 'Das ganze Netz wird die Eingabe von „Mesh to 3D“; liegt seine Höhe außerhalb von 1,4–2,3 m, wird es gestreckt (ein Bild-zu-3D-Netz hat keinen Maßstab).',
        'segmentierung': 'Sapiens2 zerlegt vier Ansichten des Netzes in Haut, Kleidung und Haar; „Mesh to 3D“ nimmt den Hautton von Gesicht und Händen statt von der Robe und trennt Kleidung und Haar nach den Etiketten.',
        'figur': '„Mesh to 3D“ passt die Genesis-9-Figur an das GANZE Netz an (Kleidung, Hut und Bart ziehen schwach), wählt eine Frisur und speichert das Modell „<Name> Mesh“.',
    }

    @classmethod
    def namen(cls, stand):
        """Die Schritte, die die Kette HEUTE für das Format und den Weg kennt (ein Stand aus der Zeit vor dem Schritt „pose“ nennt ihn nicht — er steht dann auf „offen“)."""
        return list(Blendimportlauf.schritte_fuer((stand.get('quelle') or {}).get('format'), stand.get('weg')))

    @classmethod
    def liste(cls, stand):
        """`[{schluessel, titel, hinweis, zustand, dauer_s}]` in der Reihenfolge des Laufs."""
        dauer = stand.get('dauer') or {}
        ergebnis = stand.get('ergebnis') or {}
        aktuell, status = stand.get('schritt'), stand.get('status')
        aus = []
        for name in cls.namen(stand):
            e = ergebnis.get(name)
            if name == aktuell and status in ('laeuft', 'gescheitert', 'angehalten'):
                zustand = {'laeuft': 'laeuft', 'gescheitert': 'gescheitert', 'angehalten': 'angehalten'}[status]
            elif isinstance(e, dict) and e.get('aus'):
                zustand = 'uebersprungen'
            elif name in dauer or e is not None:
                zustand = 'fertig'
            else:
                zustand = 'offen'
            hinweis = (cls.HINWEIS_NETZ if stand.get('weg') == 'netz' else {}).get(name) or cls.HINWEIS.get(name, '')
            aus.append({'schluessel': name, 'titel': cls.TITEL.get(name, name), 'hinweis': hinweis,
                        'zustand': zustand, 'dauer_s': dauer.get(name)})
        return aus
