# -*- coding: utf-8 -*-
"""Figurquellenblender — Blender-Modelle, die zum Import anstehen, als Zeilen der Rangliste „Andere Modelle".

Edgar (08.10.2026): „Füge das Modell auch in die Seite …/hilfe/architektur/andere-modelle/ ein mit den Infos" — das
Modell „cute girl" (Auto-Rig Pro), dessen Mesh-Typ, Rig und Konzept auf der Seite „ARP Modell"
(`core/dienste/arpmodell.py`) stehen. Aus `figurquellen.py` herausgehalten (432 Zeilen, Grenze 300): `Figurquellen.rangliste()`
hängt diese Zeilen an, `Netzmasse.rangfolge` rechnet Vergleichszahl und Rang wie bei allen.

Alle Zahlen sind gemessen (Blender 5.2.2 im Hintergrund, nur lesend, 08.10.2026; Belege auf der Seite „ARP Modell"):
54.369 Punkte und 108.545 Dreiecke des Körpernetzes, keine Vierecke. Die Marke `blend` färbt die Zeile blau
(`hilfe_andere_modelle.css`): ein fremdes Modell, nicht eine Figurart im Haus (rot) und nicht das MB-Lab-Original (orange).
"""

__all__ = ['Figurquellenblender']


class Figurquellenblender:
    #: RMS-Abstand der fertigen Genesis-Figur zum Original-Körpernetz in mm (Figur → Netz, Netz → Figur) NUR über die
    #: zugeordneten Punktpaare — Ausreißer sind ausgeschlossen —, Auftrag „Mesh to 3D" 2026.10.08.11.34.04, Schritt „vorschau".
    ENDABSTAND_RMS = ('0,78', '0,93')
    #: Dagegen ALLE 54.369 Körperpunkte (in Ruhe) gegen die FLÄCHE der Figur (Stufe 1, 104.480 Punkte), Import
    #: 2026.10.08.11.28.06, `ProjektTemp/_wegwerf/cutegirl/haltung_diag.py`: Median mm, p95 mm, Anteil über 8 mm in %.
    ALLE_PUNKTE = ('0,99', '14,4', '12,3')

    ZEILEN = [
        {
            'ordner': 'cute_girl_ARP',
            'linkschluessel': 'cute_girl_arp',
            'markierung': 'blend',
            'name': 'cute girl (Blender, Auto-Rig Pro)',
            'zusatz': 'Körper-Netz; Haar, Hemd, Shorts, Augen, Zähne sind eigene Netze',
            'punkte': 54_369,
            'dreiecke': 108_545,
            'stufen_text': 'keine (reines Dreiecksnetz: 0 Vierecke, 0 n-Ecke)',
            'texturen': 'Körper 8192² (Farbe, Rauheit, Normalen); Hemd, Shorts, Augen, Zähne 2048²; Haar 1024² (nur Alpha, '
            'die Farbe ist fest)',
            'geschlecht': 'Frau (ein Modell)',
            'rig': 'Auto-Rig Pro: 559 Knochen, 144 deformierend (62 Gesichtsgruppen mit Gewicht); keine Morphs (nur V_None)',
            'preis': 'unbekannt',
            'lizenz': 'unbekannt — Herkunft ungeklärt',
            'urteil': 'Zum Import als Genesis-Figur (Charakter → Datei → Modell importieren…): Die Endfigur liegt in den '
            'zugeordneten Punktpaaren (ohne Ausreißer) im Mittel %s mm (Figur → Netz) und %s mm (Netz → Figur) vom '
            'Original-Körper; gegen ALLE Körperpunkte Median %s mm, p95 %s mm, %s %% über 8 mm — Finger, Brustwarzen, '
            'Lippen, Schritt und Zehen sind in Genesis anders. Als eigene Figurart (Konzept C) bliebe das Original '
            'exakt, aber ohne Regler, Genesis-Bibliothek und Retarget-Ziel — Mesh-Typ, Rig und Vergleich der Wege auf '
            'der Seite „ARP Modell".' % (ENDABSTAND_RMS + ALLE_PUNKTE),
            'vorschau_statisch': [
                ('/static/img/arp_modell/original_vorn.jpg', 'Original von vorn (Blender EEVEE)'),
                ('/static/img/arp_modell/original_seite.jpg', 'Original von der Seite'),
                ('/static/img/arp_modell/original_gesicht.jpg', 'Original, Gesicht'),
                ('/static/img/arp_modell/genesis_import_vorn.jpg', 'nach dem Import: Genesis 9 in der Charakter-Seite'),
            ],
        },
    ]
