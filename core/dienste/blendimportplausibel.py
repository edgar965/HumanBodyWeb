# -*- coding: utf-8 -*-
"""Blendimportplausibel — passt das Ergebnis eines Imports zu dem, was ein Mensch sein kann? (Wächter, 10.10.2026)

Edgar (10.10.2026): „warum musst du immer manuelle schritte machen, und der Import ist nicht generisch??" — Rainy, seori und Rosemary Winters
waren „fertig", obwohl die Figur nicht zum Körper passte; erst Edgar sah es im Browser. ERST wurde jede Ursache einzeln gefunden (Maßstab, Körper
ohne Beine, Körper ohne Kopf), die Folge war immer dieselbe: „Mesh to 3D" passte die Figur ins Leere. Diese Prüfungen hängen darum an der Folge,
nicht an der Ursache — eine neue Art, den Import zu verderben, hält sie genauso an:

    figurhoehe  nach „export" (5 s): die Figur aus Körper, Kleidung und Augen hat nach dem Maßstab eine menschliche Höhe
    abstand     im Schritt „haut", VOR dem Backen: die Haut der Figur liegt im Median nahe am Körper des Originals

Schwellen **gemessen** an allen zehn gespeicherten Läufen (`ProjektTemp/_wegwerf/blendimport_massstab/plausibel_messung.py`, 10.10.2026): Median des
Abstands bei den sieben passenden Läufen 0,77–1,62 mm (cute girl, Asian Female, Asian, Fallout ranger, Rainy, BP3D Mann, seori neu), bei den drei nicht
passenden 65,8 (seori alt), 87,0 (Rosemary alt) und 315,2 mm (hinako); Figurhöhe nach dem Maßstab (Läufe, deren Stand sie führt: Rainy, seori neu, Fallout ranger)
1,73–1,89 m, bei den nicht passenden 3,07–3,28 m. Die Schwelle 10 mm liegt zwischen den Gruppen (6× über dem größten guten, 6,6× unter dem kleinsten
schlechten Wert). Nicht gemessen: ob ein künftiges Modell mit gutem Maßstab und trotzdem 10 mm Abstand (etwa eine sehr eigenwillige Figur) fälschlich hält —
dann geht „Unvollständiger Körper = Trotzdem importieren" (`unvollstaendig`).

`befunde` liest dieselben Zahlen aus einem GESPEICHERTEN Stand: so zeigt die Modellliste ein Warnzeichen an Modellen, die vor einer Korrektur entstanden
(`markieren`, `G9figur.liste`) — ohne dass jemand die alten Läufe von Hand durchgehen muss.
"""

from ..daten.blendimportablage import Blendimportablage

__all__ = ['Blendimportplausibel']


class Blendimportplausibel:
    #: Höhe einer Figur nach dem Maßstab in Metern — wie `Blendexport.PLAUSIBEL_M` (läuft in Blender, ist von hier nicht zu importieren).
    FIGUR_M = (0.5, 2.5)
    #: Größter Median des Abstands zwischen Körper und Figur, den ein passender Import hat (gemessen: höchstens 1,62 mm).
    MAX_MEDIAN_MM = 10.0

    @classmethod
    def figurhoehe(cls, koerper):
        """Satz mit dem Befund oder `None`. `koerper`: `ergebnis.export.koerper` (`Blendimportkoerperpruefung.messen`)."""
        hoehe = (koerper or {}).get('hoehe_figur_m')
        if hoehe is None or cls.FIGUR_M[0] <= hoehe <= cls.FIGUR_M[1]:
            return None
        return ('Maßstab: die Figur ist %.2f m hoch (erlaubt %.1f–%.1f m) — „Mesh to 3D" passt sie ins Leere; neu importieren'
                % (hoehe, cls.FIGUR_M[0], cls.FIGUR_M[1])).replace('.', ',')

    @classmethod
    def abstand(cls, abstand):
        """Satz mit dem Befund oder `None`. `abstand`: `Blendimporthaut.abstand` (Median in mm, Anteil über 8 mm)."""
        median = (abstand or {}).get('median_mm')
        if median is None or median <= cls.MAX_MEDIAN_MM:
            return None
        return ('Die Figur passt nicht zum Körper: Haut-Abstand im Median %.0f mm (passende Importe: unter 2 mm), %.0f %% der Punkte über 8 mm; neu importieren'
                % (median, 100 * float(abstand.get('ueber_8mm') or 0)))

    @staticmethod
    def pruefen(befund, trotzdem=False):
        """`ValueError` mit dem Befund, wenn es einen gibt und der Nutzer ihn nicht übergeht (`unvollstaendig` = „weiter")."""
        if befund and not trotzdem:
            raise ValueError(befund + '. Der Import hält hier an, bevor er Stunden rechnet.')

    @classmethod
    def befunde(cls, stand):
        """Die Sätze für einen gespeicherten Stand (leer = nichts gefunden). Ein Lauf ohne die Zahl (älter als der Wächter) bleibt ohne Befund."""
        ergebnis = (stand or {}).get('ergebnis') or {}
        saetze = [cls.figurhoehe((ergebnis.get('export') or {}).get('koerper')), cls.abstand((ergebnis.get('haut') or {}).get('abstand'))]
        return [s for s in saetze if s]

    @classmethod
    def fuer_import(cls, kennung):
        """`befunde` des Imports mit dieser Kennung; eine ungültige oder unbekannte Kennung ergibt keinen Befund."""
        try:
            return cls.befunde(Blendimportablage(kennung).stand())
        except ValueError:
            return []

    @classmethod
    def markieren(cls, figuren):
        """Die gespeicherten Genesis-9-Modelle (`G9figur._gespeicherte`) mit `befund` — aus dem Stand des Imports, der sie angelegt hat (`herkunft.import`)."""
        for figur in figuren:
            figur['befund'] = cls.fuer_import((figur.get('herkunft') or {}).get('import'))
        return figuren
