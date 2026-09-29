# -*- coding: utf-8 -*-
"""Posenspuren — eine BVH-Bewegung (schon auf Genesis 9 gerechnet) als Blender-Keyframes.

Ersetzt seit 29.09.2026 den Weg über das fremde Blender-Addon `retarget_bvh`
(`bvhretarget.Bvhretarget`, Thomas Larsson): Das Addon erkennt Rest-Pose und
T-Pose seines Ziels selbst — bei unserem reinen TRS-Rig (Übersetzung ohne
Rollangabe) falsch, das Ergebnis stand kopfüber. Hier kommen die Drehungen
NICHT aus einem zweiten Retargeter, sondern aus dem projekteigenen,
im Browser (`/Charakter/`) nachgewiesen richtigen Python-Kern
(`core.dienste.retargetdaten.Retargetdaten`, Ziel `genesis9`) — demselben
Datensatz, den auch die Studio-Vorschau abspielt
(`static/viewer/studio/vorschau.js`: `bone.quaternion`/`bone.position`-Spuren
aus `tracks`/`position_track`). Hier werden dieselben Werte auf die Pose-Bones
der importierten GLB-Armature gesetzt, Bild für Bild.

FORM DER JSON: `{duration, times, tracks: {bone: [x,y,z,w, ...]}, position_track:
{bone, values: [x,y,z, ...]} oder None, frame_count, mapped_bones}` — aus
`humanbody_core.skeleton.bewegungsspuren.Bewegungsspuren.als_dict()`.

ACHSEN: Die Werte stehen im GLB-Koordinatenraum (Y oben, wie glTF/Three.js).
Blender ist Z oben; der glTF-Importer dreht nur die SZENE beim Laden, nicht
Werte, die von aussen — wie hier — dazukommen. `_yup_zu_zup` rechnet daher
jeden Punkt der Wurzelspur um; die Rotationen selbst sind Blender-Bone-lokal
(Kopf zeigt lokal +Y Richtung Kind) und brauchen keine Umrechnung, weil
Blenders glTF-Import Bones nach genau dieser Regel aus den Gelenkpositionen
baut — derselben, mit der `Genesis9.skelett.G9skelett.kette()` das Zielskelett
fuer den Retarget-Kern aufbaut.
"""
import bpy  # noqa: E402  # pyright: ignore[reportMissingImports]  (Blender)
from mathutils import Quaternion, Vector  # pyright: ignore[reportMissingImports]

__all__ = ['Posenspuren']


class Posenspuren:
    def __init__(self, daten):
        self.daten = daten

    @staticmethod
    def _yup_zu_zup(x, y, z):
        """glTF/Three.js (Y oben) -> Blender (Z oben)."""
        return Vector((x, -z, y))

    def anwenden(self, rig, hoechstens=0):
        """Setzt Rotation (und Wurzelort) jedes Bilds als Keyframe auf `rig`.

        Gibt `(gesetzte_bilder, unbekannte_knochen)` zurück — Knochen aus den
        Spuren, die im Rig fehlen, sind eine Meldung, kein stiller Ausfall.
        """
        pose = rig.pose
        tracks = self.daten.get('tracks') or {}
        bekannt = {name: pose.bones[name] for name in tracks if name in pose.bones}
        unbekannt = sorted(set(tracks) - set(bekannt))
        wurzel = self.daten.get('position_track')
        wurzel_bone = None
        wurzel_rest = None
        if wurzel and wurzel.get('bone') in pose.bones:
            wurzel_bone = pose.bones[wurzel['bone']]
            wurzel_rest = rig.data.bones[wurzel_bone.name].matrix_local.copy()
        bilder = int(self.daten.get('frame_count') or 0)
        if hoechstens:
            bilder = min(bilder, hoechstens)
        for bone in bekannt.values():
            bone.rotation_mode = 'QUATERNION'
        for i in range(bilder):
            bpy.context.scene.frame_set(i + 1)
            for name, bone in bekannt.items():
                x, y, z, w = tracks[name][i * 4:i * 4 + 4]
                bone.rotation_quaternion = Quaternion((w, x, y, z))
                bone.keyframe_insert('rotation_quaternion', frame=i + 1)
            if wurzel_bone is not None:
                x, y, z = wurzel['values'][i * 3:i * 3 + 3]
                ziel = self._yup_zu_zup(x, y, z)
                versatz = wurzel_rest.to_3x3().inverted() @ (ziel - wurzel_rest.translation)
                wurzel_bone.location = versatz
                wurzel_bone.keyframe_insert('location', frame=i + 1)
        bpy.context.scene.frame_set(1)
        return bilder, unbekannt
