# -*- coding: utf-8 -*-
u"""Fassung 0.60 (13.09.2026) — eine Figur, eine Klasse; SMPL-X-Pipeline; Aufträge."""

FASSUNG = {
    'version': '0.60',
    'date': '2026-09-13',
    'title': 'Eine Figur, eine Klasse — Modell.bauen() für alle Seiten; '
             'SMPL-X-Pipeline; Aufträge als eigener Prozess',
    'author': 'edgar965',
    'body_md': (
        "HumanBodyWeb ab `9717489`, Wurzel ab `c861910`, VideoToBVH ab "
        "`84b4053`, jeweils bis zum Commit „Version 0.60“.\n"
        "\n"
        "- **Eine Figur, eine Klasse**: `Modell` mit `bauen()` in "
        "`static/viewer/gemeinsam/`; HumanBody, UMA, MakeHuman, SMPL und "
        "UMA-Python erben davon. BVH Studio, Theatre, Ergebnis-, Animations- "
        "und Modellseite und die Szene bauen keine Figur mehr selbst — Lippen, "
        "Brauen, Nägel, GarmentCode und Hautmaske kommen überall gleich an.\n"
        "- Modell-Reiter: Haut · Augen · Brauen · Mund · Nägel als klappbare "
        "Bereiche, Lippen aus der MB-Lab-Maske, Brauen mit Anker; in der Szene "
        "Lippen mit glattem Rand, Brauen mit Dichte/Dicke/Lage, "
        "MB-Lab-Hauttextur, Nähte in der Hauttextur weg.\n"
        "- Bodenfix: die Animation steht am tiefsten Punkt der animierten Figur "
        "auf dem Boden (Zehen und Fußsohle nicht mehr darunter); Radius für "
        "„Animation immer auf Ursprungspunkt“ einstellbar.\n"
        "- Ergebnisseite: der BVH-Pfad steht zum Kopieren auf jeder "
        "Ergebnisseite, das BVH wird nach `A_Results` kopiert; ein Rig und ein "
        "Retarget-Clip für alle Ansichten; GarmentCode-Stücke der Modellvorgabe.\n"
        "- VideoToBVH: SMPL-X als eigene Pipeline — Körper (GEM/GVHMR/DuoMo), "
        "Hände (SMPLest-X/GEM-X) und Gesicht in einem BVH; GEM-X (SOMA mit "
        "Händen), DuoMo und GEM-SMPL als Pipelines, Kamerabahn per "
        "DPVO/DROID-SLAM; Hybrid auf GEM-SMPL mit GEM-X-Fingern und "
        "SMPLest-X-Gesicht, Neubewertung 1–12; alle 14 Pipelines in einer "
        "sortierbaren Tabelle, die Uploadseite liefert ohne Umstellen Rang 1; "
        "Finger-, Ellbogen- und Handgelenkgrenzen im BVH-Schreiber.\n"
        "- Aufträge: laufen als eigener Prozess — ein Server-Neustart reißt sie "
        "nicht mehr mit; Auftragstabelle als djangoBase-Tabelle mit Kästchen, "
        "Shift-Bereich und Sammellöschen.\n"
        "- Retarget: Handausrichtung mit Eichfall (die Hand zeigt zum "
        "Mittelfinger, Finger erben); Gesichtsspuren auf der Ruhelage — das "
        "zermatschte Gesicht.\n"
        "- **BVH Studio**: Modell-Dialog, Animation unter dem Modell, Hautmaske, "
        "Abspielleiste links, Endlos, klebendes Lineal; Schuh: Fußpose auch "
        "unter Animation.\n"
        "- Effekte: Kleid + Wind (Blender) und HumanBody-Figur (DEF, pyrender) "
        "als Seite, Hilfe → Animationseffekte.\n"
        "- **Code Review I–III**: eine Klasse je Datei, kein JS-Modul über 300 "
        "Zeilen, Komplexität C auf 0, Testdeckung, Waisen; CLAUDE.md verdichtet "
        "— Themenregeln in `.claude/rules`, Tagebuch in `Docu/tagebuch`."
    ),
}
