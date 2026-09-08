# -*- coding: utf-8 -*-
u"""Der handgepflegte Changelog — für Fassungen, die kein Commit-Betreff nennt.

WARUM ES DIESE DATEI GIBT (Edgar, 08.09.2026: „warum steht in der Hilfe 0.58
als Version, im UI aber 0.57? 0.57 fehlt in der Hilfe - Versionen")
=====================================================================
Hilfe → Versionen liest die Fassungs-Historie aus den **Commit-Betreffs**, nicht
aus `wurzeln.VERSION` (`djangobase/views/versions.py`, `_fetch_commits`): Erkannt
wird ein Release nur, wenn im Betreff `v0.57` oder `Version 0.57` steht. Wo die
Marke fehlt, gilt der Commit als noch nicht ausgeliefert und bekommt von
`_next_dev_label` das Etikett der VERMUTETEN nächsten Fassung — bei laufender
0.57 also `v0.58-dev`.

Genau das war der Befund: Der Bump auf 0.57 steckt in `93b8fa1`, dessen Betreff
„UMA Python gegen Unity gemessen …" lautet. In HumanBodyBlender heißt der
Commit `c339cce` schlicht „Version 0.57" — dort steht 0.57 in der Liste, in den
drei anderen Repos nicht. Gemessen auf der Seite: 13× `v0.58-dev`, 1× `v0.57`.

Die Historie umzuschreiben (Rebase + Force-Push auf gepushten `master`) kommt
dafür nicht in Frage. Deshalb der von djangoBase vorgesehene Weg: ein Eintrag
hier, gerendert als eigener Block „Handgepflegter Changelog" über den Repos.

**Für die Zukunft ist die Datei kein Ersatz, sondern die Notbremse.** Der Bump
gehört in den Betreff des Commits, der ihn setzt — siehe `.claude/rules/
projekt.md`, Abschnitt Deploy. Nur ein Eintrag hier und dort ist Doppelpflege.

EIN EINZELWORT VOR DEM DOPPELPUNKT WIRD SCHON FETT GESETZT
==========================================================
`_render_body_html` hebt in einem Listenpunkt den Teil vor dem ersten
Doppelpunkt selbst hervor — aber nur, wenn dort kein Leerzeichen steht, und
dann über `html.escape` statt über den Markdown-Weg. Wer dort zusätzlich `**`
schreibt, sieht die Sternchen wörtlich: aus `**Texturen**: …` wurde
`<strong>**Texturen**</strong>`, aus `**GarmentCode: drei Knöpfe**` sogar
`<strong>**GarmentCode</strong>: drei Knöpfe**`. Also: Label aus einem Wort
ohne Sternchen, mehrwortige Hervorhebungen weiter mit `**`.
"""

#: Fassungen, die die Commit-Historie nicht selbst benennt.
#: Schema: `version`, `date`, `title`, `body_md` (Markdown-Bulletliste).
MANUELLE_FASSUNGEN = [
    {
        'version': '0.57',
        'date': '2026-09-08',
        'title': 'UMA Python gegen Unity gemessen — und die Ärmelfrage beantwortet',
        'author': 'edgar965',
        'body_md': (
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
    },
]
