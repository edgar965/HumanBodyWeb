"""Blendimportschamrauheit — das Scham-Stück glänzt so wie die Haut um es herum (10.10.2026).

Edgar: „Rauheit: Der Körper hat eine Rauheitskarte, das Stück nicht." Gemessen am BodyParts3D-Körper (OBJ, `Ns 30`): Blender macht daraus EINE
Zahl am Eingang „Roughness" des Principled BSDF (0,827), keine Karte. Der Schritt „haut" backt sie trotzdem in die vier Kacheln (Wert 211 von 255
überall), der Hautshader nimmt Karte mal 1,0 — die Haut hat also 0,83. Das Stück bekam bisher weder Karte noch Zahl und fiel im Browser auf den
Vorgabewert 0,6 (`Genesis9netz.haut`): glänzender als seine Umgebung, am Rand des Stücks als Streifen im Glanzlicht zu erwarten (im Browser nicht gesehen).

Hat der Körper eine Rauheitskarte, bleibt alles, wie es war (der Atlas des Stücks trägt sie). Ohne Karte geht die Zahl als `shininess`
(1 − Rauheit) ans Material — `G9materialkanaele` schreibt daraus „Glossy Roughness", der Browser nimmt sie nur ohne Karte (`rauheitwert`).
"""

__all__ = ['Blendimportschamrauheit']


class Blendimportschamrauheit:
    @staticmethod
    def anwenden(material, quelle):
        """`material` (Wörterbuch für den Schreiber) mit `shininess` aus `quelle['rauheit_wert']`, wenn `quelle` keine Rauheitskarte hat.
        Gibt `material` zurück; ohne Zahl oder mit Karte ändert sich nichts."""
        wert = quelle.get('rauheit_wert')
        if quelle.get('rauheit') or not isinstance(wert, (int, float)) or isinstance(wert, bool):
            return material
        material['shininess'] = 1.0 - min(1.0, max(0.0, float(wert)))
        return material
