# -*- coding: utf-8 -*-
"""Blendimportformate — aus welchen Dateien der Modell-Import lesen kann: .blend, .obj, .fbx (10.10.2026).

Edgar (10.10.2026): „einen fbx und obj importer … so ähnlich wie der Blender Importer" und „möglichst gemeinsamen Code mit dem
Blender-Import". Darum gibt es EINE Kette (`Blendimportlauf`) und kein zweites Gerüst: OBJ und FBX bekommen nur den ersten Schritt
„umwandeln" dazu — Blender liest die Datei im Hintergrund und legt sie als `quelle.blend` in die Ablage (`Blendimportumwandeln`,
`blendumwandeln.py`). Von „export" an läuft alles wie bei einer .blend: dieselben Rollen, derselbe Körper, „Mesh to 3D", Stücke,
Haut backen, Augen, Modell.

Was je Format abweicht, steht NUR hier und in `Fremdimporteinstellungen` (Katalog, Pfad, gemerkte Werte):

    blend   die Datei IST die Quelle; Haltung per Auto-Rig-Pro-Knochenkarte möglich
    obj     kein Skelett (die Datei kennt keins) → der Weg „ohne Rig"; Texturen aus der .mtl neben der Datei
    fbx     Skelett und Hautgewichte aus der Datei; Haltung der Datei, sofern es kein Auto-Rig Pro ist
"""

__all__ = ['Blendimportformate']


class Blendimportformate:
    #: Schlüssel → Anzeigename und Endung. Die Reihenfolge ist die der Reiter im Dialog (JSON hat keinen Lauf, er steht nur dort).
    FORMATE = {
        'blend': {'titel': 'Blender', 'endung': '.blend'},
        'obj': {'titel': 'OBJ', 'endung': '.obj'},
        'fbx': {'titel': 'FBX', 'endung': '.fbx'},
    }
    VORGABE = 'blend'

    @classmethod
    def pruefen(cls, name):
        """Der Schlüssel, wenn er bekannt ist — sonst die Vorgabe (alte Aufrufer und Stände kennen kein Format)."""
        return name if name in cls.FORMATE else cls.VORGABE

    @classmethod
    def endung(cls, name):
        return cls.FORMATE[cls.pruefen(name)]['endung']

    @classmethod
    def titel(cls, name):
        return cls.FORMATE[cls.pruefen(name)]['titel']

    @classmethod
    def umwandeln(cls, name):
        """Muss Blender die Datei erst zur .blend machen? Nur eine .blend ist schon eine."""
        return cls.pruefen(name) != 'blend'

    @classmethod
    def einstellungen(cls, name):
        """Die Einstellungs-Klasse des Formats (Katalog, Merken, Prüfen) — die der .blend bleibt `Blendimporteinstellungen`."""
        name = cls.pruefen(name)
        if name == 'blend':
            from .blendimporteinstellungen import Blendimporteinstellungen

            return Blendimporteinstellungen
        from .fremdimporteinstellungen import Fremdimporteinstellungen

        return Fremdimporteinstellungen.fuer(name)
