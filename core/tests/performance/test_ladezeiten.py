# -*- coding: utf-8 -*-
"""Ladezeiten der wichtigen Seiten — Art „performance".

Die Messung steht in `djangobase.leistungstests`; hier wird sie nur eingesammelt.
Was sie tut: jede parameterlose Seite aufwärmen, mehrfach messen, den MEDIAN
nehmen, zusätzlich die Zahl der SQL-Abfragen zählen, alles nach
`.djangobase-leistung.json` im Projekt fortschreiben und gegen den letzten Lauf
vergleichen.

Ein Rückschritt gilt erst ab doppelter Zeit UND mindestens 150 ms mehr — ohne
diese zweite Bedingung meldet jeder Sprung von 4 auf 9 ms einen „Einbruch",
sobald nebenher etwas läuft.

Die Zahl der Abfragen ist dabei die verlässlichere Größe: Sie hängt nicht an
der Tageslast. Eine Seite, die von 12 auf 400 springt, hat ein N+1-Problem,
egal was die Uhr sagt.

Eingestellt über `DJANGOBASE["leistung"]` in `ui/settings.py`.
"""

from djangobase.leistungstests import *      # noqa: F401,F403
