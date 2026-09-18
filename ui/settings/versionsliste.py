# -*- coding: utf-8 -*-
"""Der handgepflegte Changelog: ein Eintrag je Fassung, aus `fassungen/`.

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

SEIT 13.09.2026 BEKOMMT JEDE FASSUNG EINEN EINTRAG (Edgar: „update
/hilfe/versionen/, da ist v0.57 nach v0.60 und viele Commits fehlen")
=====================================================================
Der Block „Handgepflegter Changelog" ist das, was man auf der Seite als
Changelog liest; die vier Repo-Listen darunter sind Rohmaterial, und zwar
nur die letzten 100 Commits je Repo (Seitengröße der GitHub-Schnittstelle,
`version_commits_per_page`, mehr gibt sie je Aufruf nicht her). Stand dort
nur 0.57, sah es aus, als fehle alles zwischen 0.57 und der laufenden 0.60.

Also beides beim Bump: die Marke in den Commit-Betreff (`.claude/rules/
projekt.md`, Abschnitt Deploy — daran hängt die Zuordnung der Commits) UND
ein Modul `fassungen/v0NN.py` mit dem Eintrag. `test_versionshistorie` hält
beides: die laufende Fassung braucht den Eintrag, und jede Fassung, die ein
Betreff seit 0.57 nennt, ebenso.

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

from .fassungen import ALLE

#: Ein Eintrag je Fassung, neueste zuerst; Schema: `version`, `date`,
#: `title`, `author`, `body_md` (Markdown-Bulletliste).
MANUELLE_FASSUNGEN = ALLE
