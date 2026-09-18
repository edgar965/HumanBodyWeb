# -*- coding: utf-8 -*-
"""Fassung 0.57 (08.09.2026) — nachgetragen, der Bump-Commit trug keine Marke."""

FASSUNG = {
    "version": "0.57",
    "date": "2026-09-08",
    "title": "UMA Python gegen Unity gemessen — und die Ärmelfrage beantwortet",
    "author": "edgar965",
    "body_md": (
        "Nachgetragen, weil der Bump-Commit `93b8fa1` die Marke nicht im "
        "Betreff trug. Enthalten sind `a65d0cf` bis `fabfd8b`.\n"
        "\n"
        "- **UMA Python stimmt mit Unity überein**: 16.277 Punkte, 29.430 "
        "Dreiecke, 229 Knochen, Knochenlängen über alle 228 Paare exakt "
        "0,000000 mm. Fünf Fehler kamen dabei heraus, jeder stumm: der "
        "DNA-Lauf warf die Ruhedrehung weg (54 Gesichtsknochen je 179,7° "
        "daneben), `lodRanges` legte fünf Detailstufen übereinander "
        "(58.538 statt 29.430 Dreiecke), 73 `*_end`-Knochen rutschten in "
        "den Ursprung, die Ruhelage muss über die Weltlagen laufen, und "
        "die Normalen kamen vom Browser statt vom Server.\n"
        "- Texturen: UMAs Overlays verweisen auf PNG-Dateien, der Pfad "
        "genügt. Ohne `uv` in der Antwort bildet Three.js nichts ab — ohne "
        "Fehler; `flipY` bleibt beim Standard `true`, weil die UV roh aus "
        "Unity kommen.\n"
        "- Animation: `Umagelenke` reicht UMAs eigene Ruhedrehungen "
        "durch statt sie aus Kopf/Schwanz abzuleiten. Ruhe 0,00034 mm, "
        "Bewegung im Mittel 32,8 cm.\n"
        "- **Eine leere Kleiderliste heißt nackt** — vorher zog UMA "
        "seine Vorgabe an, das genaue Gegenteil der Eingabe.\n"
        "- GarmentCode, drei Knöpfe: 2D 4,6 s · 3D 23,1 s · beides "
        "~31 s. „2D“ legt die Panels an die Figur, gegen das Boxmesh des "
        "Upstream auf 0,0 cm geprüft.\n"
        "- **Die Ärmelfrage**: Der **Jumpsuit** wirft die wenigsten "
        "Falten — 0,19 % Median über 11 Läufe, gemessen NUR auf den "
        "Ärmelflächen (Kleid 0,83 %, Hemd 0,96 %, T-Shirt 1,00 %).\n"
        "- LongRunner: elf Module über 5 s aus dem Sammellauf heraus. "
        "Unit und Component zusammen von 266 s auf 98 s."
    ),
}
