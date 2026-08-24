# -*- coding: utf-8 -*-
"""Stoffantwort — ein angepasstes Kleidungsnetz als JSON für den Browser.

WARUM (17.08.2026, Kriterium 6)
===============================
Derselbe Block stand VIERMAL im Projekt: `api/kleidung.character_cloth`,
`api/schnittmuster.pattern_generate`, `api/schnittmuster.pattern_region_generate`
und `api/smpl.smpl_garment_fit`. Jedes Mal dieselben sieben Felder
(`vertex_count`, `vertices`, `face_count`, `faces`, `normals`, `color`) und
dieselbe Übertragung der Hautgewichte über die Nachbarsuche.

DIE HAUTGEWICHTE SIND DER TEIL, DER WIRKLICH WEHTUT
===================================================
Ein Kleidungsnetz hat eigene Punkte und deshalb keine eigenen Knochengewichte.
Jeder Stoffpunkt übernimmt sie vom NÄCHSTEN Körperpunkt — sonst bewegt sich das
Kleidungsstück beim Animieren nicht mit (es bliebe im Raum stehen, während die
Figur läuft).

Wichtig dabei: Die Nachbarsuche läuft gegen das GRUNDNETZ des Körpers, nicht
gegen die unterteilte Fassung. Die gespeicherten Gewichte
(`Skingewichte.arrays`) gehören zum Grundnetz; gegen die unterteilten Punkte
gesucht wären die Indexe verschoben, und die Kleidung würde von den falschen
Knochen bewegt — im Ruhezustand sieht man davon nichts (dort sind alle
Knochenmatrizen die Einheit), erst beim Drehen eines Arms.
"""

from .netzantwort import Netzantwort


class Stoffantwort:
    """Baut die JSON-Antwort für ein angepasstes Kleidungsnetz."""

    @classmethod
    def aus(cls, ergebnis, koerperpunkte, geschlecht, farbe=None, **weitere):
        """`ergebnis` ist die Rückgabe von `fit_garment`/`generate_from_pattern`.

        `farbe` überschreibt die Farbe aus dem Ergebnis (die SMPL-Anpassung
        bekommt sie aus der Anfrage). `weitere` geht unverändert mit — dort steht
        z. B. `garment_id`.
        """
        # Dictionary gewollt: geht unveraendert als JSON an den Browser.
        antwort = {
            'vertex_count': int(ergebnis['vertices'].shape[0]),
            'vertices': Netzantwort.feld(ergebnis['vertices'], 'vertices'),
            'face_count': int(ergebnis['faces'].shape[0]),
            'faces': Netzantwort.feld(ergebnis['faces'], 'faces'),
            'normals': Netzantwort.feld(ergebnis['normals'], 'normals'),
            'color': list(farbe if farbe is not None
                          else ergebnis.get('color') or ()),
        }
        antwort.update(weitere)
        antwort.update(cls.gewichte(ergebnis['vertices'], koerperpunkte,
                                    geschlecht))
        return antwort

    @classmethod
    def gewichte(cls, stoffpunkte, koerperpunkte, geschlecht):
        """Knochengewichte je Stoffpunkt — leer, wenn es keine gibt.

        Leer ist ein gültiger Fall: Für ein Geschlecht ohne gespeicherte
        Gewichte zeigt der Browser das Kleidungsstück statisch an. Ein Fehler
        wäre falsch, ein stilles Nullgewicht auch (dann läge die Kleidung im
        Ursprung).
        """
        from ..dienste.skingewichte import Skingewichte
        arrays = Skingewichte.arrays(geschlecht)
        if arrays is None or koerperpunkte is None:
            return {}
        from humanbody_core.nachbarsuche import Nachbarsuche
        indexe, gewichte = arrays
        _, naechste = Nachbarsuche(koerperpunkte).naechster(stoffpunkte)
        return {
            'skin_indices': Netzantwort.feld(indexe[naechste], 'skin_indices'),
            'skin_weights': Netzantwort.feld(gewichte[naechste], 'skin_weights'),
        }
