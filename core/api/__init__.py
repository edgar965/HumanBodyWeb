# -*- coding: utf-8 -*-
"""Django-Endpunkte, nach Themen getrennt.

Jedes Modul hier ist eine duenne Schicht: Anfrage lesen, eine Klasse aus
`core/dienste/` rufen, Antwort bauen. Was rechnet, gehoert nicht hierher.

Warum Funktionen und keine View-Klassen: Die Dekoratoren (`require_POST`,
`csrf_exempt`, `xframe_options_sameorigin`) stapeln sich auf Methoden nur ueber
`method_decorator`, Stapelspuren zeigen dann `dispatch` statt des Endpunkts, und
`RequestFactory` kann Funktionen unmittelbar aufrufen. Die Kapselung passiert
dort, wo Zustand ist — in den Dienstklassen.
DIE HERKUNFT DIESER MODULE (15.08.2026)
=======================================
Sie stammen aus `core/character_api.py`: 6.495 Zeilen, 110 Endpunkte, die Themen
darin nur durch die Reihenfolge getrennt. Aufgeteilt wurde nach AUFGABE — Netz,
Kleidung, Posen, Retarget, SMPL, Foto, Schnittmuster —, und die Fachlogik ist
dabei in `core/dienste/` als Klassen gewandert.

Dieser Absatz stand am 17.08.2026 wortgleich in acht dieser Module (Befund
`doppelcode`). Ein Verweis pro Datei genügt.
"""
