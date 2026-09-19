# -*- coding: utf-8 -*-
"""Fassung 0.61 (19.09.2026) — Genesis 9 als Figurart; Modell aus Bildern; Kleidung über Kreuz."""

FASSUNG = {
    'version': '0.61',
    'date': '2026-09-19',
    'title': 'Genesis 9 als sechste Figurart; Modell aus Bildern; '
    'Kleidung über Kreuz; zwei Personen im Video',
    'author': 'edgar965',
    'body_md': (
        'HumanBodyWeb ab `d2432dc`, Wurzel ab `c63c044`, VideoToBVH ab '
        '`68c7d9c`, jeweils bis zum Commit „Version 0.61“.\n'
        '\n'
        '- **Genesis 9 als sechste Figurart**: Daz-Bibliothek gelesen (DSON, '
        'Formelgraph, Nähte, Anhänge), Garderobe, HD-Morphs, Schminke, Haar-Rig, '
        'JCMs in der Bewegung und auf der Kleidung, Lipsync (Rhubarb), '
        'Daz-Bewegungen als BVH; Unterteilungsstufen, Kaltstart-Ablagen und '
        'Aufwärmen; Strg+Alt+H in 1–2 s (Antwortvorrat, Vorausrechnung, '
        'Kollision in zwei Stufen), Reiter über Undo/F5, Sanduhr, Farbvarianten '
        'mit Bild; Hilfe → Andere Modelle.\n'
        '- **Kleidung über Kreuz**: Daz-Garderobe mit Kollision Stück gegen Stück '
        '(das Hemd liegt über der Jeans), GarmentCode auf Genesis 9 als Träger, '
        'Daz-Kleidung auf HumanBody (Paarung der Grundkörper, Bindung ans '
        'Rigify-Skelett).\n'
        '- **Modell aus Bildern** (`/humanbody/modell-aus-dateien/`): Auftrag als '
        'eigener Prozess; Zuschnitt (YOLO11-Pose), Sichtung mit vier Rigs '
        '(MediaPipe, YOLO, openpifpaf, ViTPose), SMPLest-X und PyMAF-X-FLAME, '
        'Drehvideo (GVHMR); Zielnetz über Verschiebungen, Reglerableitung, '
        'Ausgleichung, Restmorph als Eigenmorph; Personenangaben (Größe, '
        'Gewicht, Haar), Hautton und Fotofarbe als UDIM; Außenmaße; 19 '
        'Proportionen mit Vorher/Nachher je Ansicht und Popup; je Bild drei '
        'Boxen (Hauptbild, Nebenbild, Nutzung), Ersetzen/Löschen; Testfall mit '
        'Referenzfigur (Ursula, Flächen- und Punktabstand, Knopf „Testcase“); '
        'die Silhouette der Fotos formt das Zielnetz — 19 Fotomaße und der '
        'Umriss Zeile für Zeile (vorn, hinten, Seite).\n'
        '- **Studio**: Mimikspur (MB-Lab-Posen auf DEF-Gesichtsknochen), '
        'Script-Spur, Figurarten, SMPL-X mit Gesichtsknochen; Zeitleiste folgt '
        'beim Play, Lineal, Bildtakt; Auftragsseiten nach Datum und Uhrzeit; '
        'Bibliothekskanal.\n'
        '- Augenbraue als Zeichnung in der Haut, Retarget neben jedem BVH vorab, '
        'der Film mit Haut, Braue und Augen; Saumband hinter der Stoffkante, '
        'Hauteinzug ohne gekippte Randdreiecke.\n'
        '- **VideoToBVH**: zwei Personen im Video — Spurwahl, ein BVH je Spur, '
        'synchron (GEM, GVHMR), Szenenwechsel; 3DObjects als Video-Wurzel (der '
        'Pipeline-Start von der Uploadseite ging in 403).\n'
        '- Szene: „Charakter hinzufügen“ über den gemeinsamen Figurwahldialog; '
        'Einstellungen → Szene: Standard-Modell in jeder Figurart; '
        'Vergleichsseite: Genesis 9 als neunte Skelettspalte; Retarget: '
        'Halsknick auf UMA und Genesis 9, Hals/Kopf ohne Richtungskorrektur.\n'
        '- Jede Middleware beidseitig (sync + async): eine nur-synchrone '
        'Middleware vor den asynchronen aus djangoBase ließ den Server stehen, '
        'sobald ein Browser die Seite verließ (`py-spy dump`).\n'
        '- Code Review II und III: Language Server 604 auf 3, Werkzeugkasten '
        '1.263 auf 1.079 Befunde; ruff mit einfachen Anführungszeichen.'
    ),
}
