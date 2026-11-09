from .engine2d3dkleiderkopfoptionen import Engine2d3dKleiderkopfoptionen
# -*- coding: utf-8 -*-
"""Engine2d3dKleidervorbereitungsoptionen — die Gruppe `vorbereitung` der Optionen von „2D3D Kleider" (03.10.2026).

Der Schritt „Vorbereitung" (`Engine2d3dKleidervorbereitung`) bereitet die Fotos auf, bevor ein Formmodell sie sieht: Hintergrund entfernen
(BiRefNet), Zuschnitt um die Silhouette, Licht ausgleichen — und auf Wunsch den Körper senkrecht stellen. Die ersten Schritte stehen seit
jeher in der Gruppe `netz` (`freistellen`, `licht`); neu ist nur `ausrichten`.

Edgar (03.10.2026): „richte den Körper doch aus, als ersten Schritt … per Option schaltbar", später „dieser Achsen-Anpassungsschritt im UI optional,
als Häkchen bei diesen Bilderanpassungen. Nur wenn das angehakt ist, machst du das vor dem Mesh-Erzeugungsschritt." Das Feld ist deshalb ein Häkchen
(Art `haken`): angehakt = `mitte` (Mittelachse, `VideoToBVH/wrappers/mesh_ausrichtung.py`), sonst `aus`. Die frühere Wahl „An" (Körperachse aller Fotos)
gibt es nicht mehr — sie verschlechterte die Rückenlinie von `4.jpg` auf −3,7° (gemessen, `mesh-vorverarbeitung.md`); ein gespeicherter Wert `an` oder
`ruecken` (verworfene Fassung) wird beim Lesen zu `aus`.
"""

__all__ = ['Engine2d3dKleidervorbereitungsoptionen']


class Engine2d3dKleidervorbereitungsoptionen:
    KATALOG = [
        {'schluessel': 'ausrichten', 'titel': 'Körper senkrecht stellen (Mittelachse)', 'art': 'haken', 'vorgabe': 'aus', 'an': 'mitte', 'aus': 'aus',
         'hinweis': 'Nur wenn angehakt, und vor dem Mesh-Schritt. In den Seitenfotos läuft die Achse durch die Mitte von Kopf, Rumpf (Schulterhöhe) und Hüfte, jeweils zwischen '
                    'der hintersten und der vordersten Stelle der Silhouette; das Foto wird um diese Achse gedreht und dann zeilenweise waagerecht so verschoben, dass alle drei '
                    'Mitten auf EINER senkrechten Achse liegen (höchstens 6 % der Höhe). Die Zeilen werden nur verschoben, nicht gestreckt: Rücken, Brust und Kopf behalten '
                    'ihre Wölbung. Vorne und hinten werden um die Neigung ihrer Körperachse (Rumpf bis Beine) gedreht. Gemessen an Edgars Fotos: Die drei Mitten lagen 2,7 % '
                    '(`seite.jpg`) und 2,2 % (`4.jpg`) der Höhe auseinander, danach 0,3 %; die Körperachse von vorne und hinten neigte sich +0,9° und +0,7°, danach höchstens '
                    '0,07°. Eine Drehung in der Bildebene gleicht keine Kopfneigung nach vorn oder hinten aus. Ob das Netz davon besser wird, ist nicht gemessen.'},
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @staticmethod
    def _erlaubt(eintrag):
        """Die Werte, die ein Feld annehmen darf: bei einer Wahl die Liste, bei einem Häkchen `aus` und `an`."""
        if eintrag['art'] == 'haken':
            return [eintrag['aus'], eintrag['an']]
        return [w for w, _ in eintrag['werte']]

    katalog = classmethod(Engine2d3dKleiderkopfoptionen.katalog.__func__)          # dieselbe Rechnung wie `Engine2d3dKleiderkopfoptionen.katalog` (bis 08.11.2026 eine Kopie hier)

    pruefen = classmethod(Engine2d3dKleiderkopfoptionen.pruefen.__func__)          # dieselbe Rechnung wie `Engine2d3dKleiderkopfoptionen.pruefen` (bis 08.11.2026 eine Kopie hier)
