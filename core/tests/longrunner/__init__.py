# -*- coding: utf-8 -*-
u"""LongRunner — Tests ueber 1 Sekunde je Modul.

WARUM SIE HIER LIEGEN
=====================
Edgar, 08.09.2026: „alle tests die laenger als 5 s brauchen kriegen die
Kategorie LongRunner und werden nicht jedes Mal ausgefuehrt bei einer
automatischen Suite" — und am 09.09.2026, nach dem naechsten Sammellauf:
„baue die automatische Testsuite um, alles was mehr als 1 s dauert soll in
die Longrunner hinein, das dauert mir alles zu lange".

Die Schwelle liegt seither bei 1 Sekunde je Modul.

WAS HIER LANDET, IST GEMESSEN
=============================
`manage.py test --durations 3000`, die Zeiten je Testfall nach Modul
aufsummiert (`ProjektTemp/dauern.txt`). Der Lauf brauchte 113 s fuer 1.667
Faelle; ueber 1 Sekunde lagen 21 Module mit zusammen 108,6 s.

Beim ersten Durchgang (08.09.2026, Schwelle 5 s) kamen elf Module hierher:

    test_kleiderrigging   66,7 s     test_umafigur          10,9 s
    test_umabauer         39,5 s     test_uma_gegenprobe    10,7 s
    test_mhpfade          21,1 s     test_hilfe_kleidung     8,8 s
    test_charakterkanal   19,7 s     test_pipeline_process   8,6 s
    test_netzkette        (Bestand)  test_umatexturen        7,8 s
                                     test_endpunkte          7,4 s
                                     test_uma_gegenprobe_lauf 5,7 s

Beim zweiten (09.09.2026, Schwelle 1 s) neunzehn weitere:

    test_passform          5,94 s    test_escape_sequenzen   2,33 s
    test_oberflaeche       3,94 s    test_formregler         2,26 s
    test_garmentregler     3,94 s    test_hilfe_neu          2,17 s
    test_lokale_importe    3,81 s    test_v4lauf             1,57 s
    test_reglerhilfe       3,37 s    test_humanbody_importwege 1,41 s
    test_mhfigur           3,27 s    test_kollision_importwege 1,25 s
    test_addon_namen       3,22 s    test_umafigurkatalog    1,24 s
    test_addon_zugriffe    2,97 s    test_mhmodellieren      1,18 s
    test_halstreue         2,81 s    test_smplgelenke        1,01 s
    test_koerpermasse      2,57 s

`test_umafigurkatalog` hiess in `component` noch `test_umafigur` — hier
liegt unter dem Namen schon der Python-Figurbau. Zwei Dateien gleichen
Namens in einem Paket gehen nicht, und der zweite haette den ersten
verdeckt.

Die verschobenen Module holen ihre Helfer weiter aus `unit`
(`from ..unit._projektquellen import Projektquellen`) — die Hilfsdateien
mit `_`-Praefix bleiben dort, sie sind selbst keine Tests.

SIE LAUFEN NUR, WENN SIE GEMEINT SIND
=====================================
`manage.py test` ohne Ziel entdeckt sonst auch dieses Paket — und der
Sammellauf „Alles" in Hilfe -> Tests ruft genau das
(`djangobase/testkategorien.py`: `sammel(python, "alles", …, [])` mit
leerer Zielliste). Die Entscheidung steht in
:class:`core.tests.nurgemeint.Nurgemeint`; `core/tests/automated` und
`core/tests/performance` benutzen denselben Waechter.

DJANGOBASE BLEIBT UNBERUEHRT. Es ist in sechs Projekten als editable
Install eingebunden; eine Ausnahme fuer dieses Projekt dort einzubauen
wirkte sofort in allen (`A:/shared/djangoBase/CLAUDE.md`).
"""
import os

from ..nurgemeint import Nurgemeint

#: Das Wort, an dem ein ausdruecklicher Aufruf zu erkennen ist. Bleibt als
#: Modulname stehen: `test_longrunner_auswahl` prueft die Entscheidung
#: darueber, und `ui/settings/djangobase_tests.py` nennt dasselbe Ziel.
MARKE = 'longrunner'
SCHALTER = Nurgemeint.SCHALTER

WAECHTER = Nurgemeint(MARKE, os.path.dirname(__file__), dauer='250 s')


def angefordert(argumente=None, umgebung=None):
    u"""Sind die LongRunner ausdruecklich gemeint?"""
    return WAECHTER.angefordert(argumente, umgebung)


def load_tests(loader, standard_tests, pattern):
    return WAECHTER.sammeln(loader, pattern)
