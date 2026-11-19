# -*- coding: utf-8 -*-
"""Meshgenesishaltungwahl — welche Haltung einer Ergebnisdatei (`ergebnis_Form_<g>`) die ANZEIGE nimmt (19.11.2026 abends).

3dtools-96 (Fußregel, Edgar meldete auf G_Generisch_3 eine Regression an Brust und Gürtel): `rig`/`dreh` bleiben die Haltung des Fotos —
daran legen Kostüm, Netzform und Fotoklassen die Figur ans Netz. Die Fußregel steht daneben als `rig_stand` (K, 3) und `dreh_stand`
(K, 3, 3), gleiche Form und gleicher Rahmen: Füße flach, die ganze Figur um die gemessene Höhe gesenkt (Goldprinzessin −75 mm).
Wo die Figur ALLEIN steht (`drehung_genesis`, `ausgabe_stand`/`dreh_stand` in `Meshgenesistest.daten` und `Fotogenesisfigur.daten`;
die Foto-Genesis-Figur `Fotogenesistestfigur`), gilt die Standhaltung, wenn BEIDE Felder in der Datei stehen, sonst die des Fotos. Wo sie
über dem Fotonetz liegt (`ausgabe`/`dreh`, Mesh-Genesis-Testseite) und in allen Rechnungen bleibt die Fotohaltung `rig`/`dreh`
(3dtools-96, 19.11.2026: „Dort, wo die Figur über dem Netz liegt, gehört die Fotohaltung hin“).

    rig, dreh, art = Meshgenesishaltungwahl.felder(e)    # e: geöffnete Ergebnisdatei (`Npztorch.lesen`) → Feldnamen, 'stand' | 'foto'
"""

__all__ = ['Meshgenesishaltungwahl']


class Meshgenesishaltungwahl:
    @staticmethod
    def felder(e):
        namen = set(e.files)
        if 'rig_stand' in namen and 'dreh_stand' in namen:
            return 'rig_stand', 'dreh_stand', 'stand'
        return 'rig', 'dreh', 'foto'
