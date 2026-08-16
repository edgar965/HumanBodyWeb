# -*- coding: utf-8 -*-
"""Pipeline-Laeufe: Video zu BVH, in mehreren Varianten.

Jede Pipeline startet Unterprozesse in der Python-3.10-Umgebung, verfolgt deren
Ausgabe als Fortschritt und legt das Ergebnis beim Auftrag ab. Die Endpunkte in
core/api/auftraege.py starten diese Laeufe in einem Faden.
"""
